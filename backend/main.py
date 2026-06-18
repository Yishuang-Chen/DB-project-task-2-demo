"""
main.py

这是本 Demo 的后端入口文件。

本文件使用 FastAPI 编写 HTTP 接口，前端 Vue 页面会通过这些接口访问 MySQL。

为了适合数据库原理课程教学，本文件有三个设计原则：
1. 不使用 ORM，所有数据库操作都写成原始 SQL。
2. 不做复杂权限框架，只演示“登录后根据角色跳转”的基本思路。
3. 代码注释尽量详细，方便第一次接触全栈开发的同学逐步阅读。

运行命令：

    python -m uvicorn main:app --reload

运行后浏览器打开：

    http://127.0.0.1:8000/docs

FastAPI 会自动生成接口测试页面，适合在写前端之前先测试后端。
"""

# Optional 表示某个字段可以是字符串，也可以是 None。
# 例如课程的 prerequisite_no 可以为空，表示这门课没有先修课程。
from typing import Optional

# FastAPI 是 Python 后端框架，用来创建 Web 接口。
# HTTPException 用来返回错误状态码，例如 401 登录失败、404 数据不存在。
from fastapi import FastAPI, HTTPException

# CORSMiddleware 用来解决前后端端口不同导致的跨域问题。
# 后端通常运行在 8000 端口，前端 Vite 通常运行在 5173 端口。
from fastapi.middleware.cors import CORSMiddleware

# BaseModel 来自 Pydantic，用来描述前端传给后端的 JSON 数据结构。
# 例如登录接口需要 username 和 password，就可以定义一个 LoginRequest。
from pydantic import BaseModel

# IntegrityError 是 PyMySQL 提供的异常类型。
# 当插入重复主键、违反唯一约束时，MySQL 会报错，PyMySQL 会抛出 IntegrityError。
from pymysql.err import IntegrityError

# get_connection 是我们在 db.py 中写好的函数。
# 每次接口需要访问数据库时，就调用它创建一个 MySQL 连接。
from db import get_connection


# 创建 FastAPI 应用对象。
# title 会显示在 http://127.0.0.1:8000/docs 页面顶部。
app = FastAPI(title="高校教学管理系统 Demo 后端")


# 添加跨域配置。
# 解释：浏览器为了安全，会限制不同端口之间的请求。
# 例如 Vue 前端在 http://127.0.0.1:5173，FastAPI 后端在 http://127.0.0.1:8000。
# 如果不加 CORS，前端请求后端时可能会被浏览器拦截。
app.add_middleware(
    CORSMiddleware,
    # 允许这些前端地址访问后端。
    # localhost 和 127.0.0.1 都写上，是为了避免不同同学启动前端时地址不一致。
    allow_origins=[
        "http://localhost:5173",
        "http://127.0.0.1:5173",
    ],
    # 允许浏览器携带认证信息。
    # 本 Demo 暂时没有使用 Cookie，但保留这个配置便于后续扩展。
    allow_credentials=True,
    # 允许所有 HTTP 方法，例如 GET、POST、PUT、DELETE。
    allow_methods=["*"],
    # 允许所有请求头，例如 Content-Type。
    allow_headers=["*"],
)


# -----------------------------
# 一、请求数据模型
# -----------------------------
# 下面这些类不是数据库表。
# 它们只是描述“前端传来的 JSON 应该长什么样”。


class LoginRequest(BaseModel):
    """登录接口的请求体。"""

    # 用户名，例如 admin、stu001。
    username: str

    # 密码。本 Demo 为了教学简单，数据库中保存的是明文 123456。
    # 正式系统不应该保存明文密码，而应该保存加密后的哈希值。
    password: str


class CourseCreateRequest(BaseModel):
    """管理员新增课程时，前端需要提交的数据。"""

    # 课程号，例如 C006。它是 courses 表的主键。
    course_no: str

    # 课程名，例如 Python程序设计。
    course_name: str

    # 学分，例如 3.0。
    credit: float

    # 先修课程号，可以为空。
    prerequisite_no: Optional[str] = None


class CourseUpdateRequest(BaseModel):
    """管理员修改课程时，前端需要提交的数据。"""

    # 修改课程时，课程号放在 URL 路径里，所以这里不再写 course_no。
    course_name: str
    credit: float
    prerequisite_no: Optional[str] = None


class SelectCourseRequest(BaseModel):
    """学生选课时，前端需要提交的数据。"""

    # 学号，例如 S001。
    # 本 Demo 暂时不做复杂 token 认证，所以让前端直接把登录学生的学号传回来。
    student_no: str


# -----------------------------
# 二、基础测试接口
# -----------------------------


@app.get("/")
def index():
    """
    根路径接口。

    作用：
    1. 测试后端服务是否启动成功。
    2. 浏览器访问 http://127.0.0.1:8000 时能看到一条简单信息。
    """

    # FastAPI 会自动把 Python 字典转换成 JSON。
    return {
        "message": "高校教学管理系统 Demo 后端已启动",
        "docs": "http://127.0.0.1:8000/docs",
    }


# -----------------------------
# 三、登录接口
# -----------------------------


@app.post("/api/login")
def login(data: LoginRequest):
    """
    用户登录接口。

    前端请求示例：

        POST /api/login
        {
          "username": "stu001",
          "password": "123456"
        }

    后端处理逻辑：
    1. 根据用户名和密码查询 users 表。
    2. 如果查不到，说明用户名或密码错误。
    3. 如果查到了，把用户角色 role 返回给前端。
    4. 前端根据 role 跳转到不同页面。

    这个接口对应的核心 SQL：

        SELECT id, username, role, related_no, display_name
        FROM users
        WHERE username = %s AND password = %s
    """

    # 创建数据库连接。
    connection = get_connection()

    try:
        # cursor 是游标对象。
        # 可以把它理解成“用来向 MySQL 发送 SQL 语句的工具”。
        with connection.cursor() as cursor:
            # 这里使用三引号写多行 SQL，格式更接近课堂上手写的 SQL。
            # %s 是参数占位符，不是 Python 的字符串格式化。
            # PyMySQL 会把 data.username 和 data.password 安全地填入 SQL。
            sql = """
                SELECT
                    id,
                    username,
                    role,
                    related_no,
                    display_name
                FROM users
                WHERE username = %s AND password = %s
            """

            # 执行 SQL。
            # 注意：参数必须写在元组里，所以这里是 (data.username, data.password)。
            cursor.execute(sql, (data.username, data.password))

            # fetchone() 表示只取一条查询结果。
            # 因为 username 是唯一的，所以最多只会查到一个用户。
            user = cursor.fetchone()

        # 如果 user 是 None，表示数据库中没有符合条件的用户。
        if user is None:
            # 401 表示未认证，常用于登录失败。
            raise HTTPException(status_code=401, detail="用户名或密码错误")

        # 查询成功后，把用户信息返回给前端。
        # 前端会根据 role 判断跳转到管理员页面还是学生页面。
        return {
            "id": user["id"],
            "username": user["username"],
            "role": user["role"],
            "related_no": user["related_no"],
            "display_name": user["display_name"],
        }

    finally:
        # 无论登录成功还是失败，都关闭数据库连接。
        connection.close()


# -----------------------------
# 四、管理员：课程管理 CRUD
# -----------------------------


@app.get("/api/admin/courses")
def list_courses(keyword: str = ""):
    """
    查询课程列表。

    前端请求示例：

        GET /api/admin/courses
        GET /api/admin/courses?keyword=数据库

    参数说明：
    - keyword 为空时，查询全部课程。
    - keyword 不为空时，按课程号或课程名模糊查询。

    这个接口演示 SELECT 和 LIKE 查询。
    """

    connection = get_connection()

    try:
        with connection.cursor() as cursor:
            # 为了让 SQL 结构固定、容易教学，这里没有动态拼接 SQL。
            # 下面的 WHERE 条件含义是：
            # 1. 如果 keyword 为空字符串，就返回所有课程。
            # 2. 如果 keyword 不为空，就匹配 course_no 或 course_name。
            sql = """
                SELECT
                    course_no,
                    course_name,
                    credit,
                    prerequisite_no
                FROM courses
                WHERE
                    (%s = '')
                    OR course_no LIKE %s
                    OR course_name LIKE %s
                ORDER BY course_no
            """

            # LIKE 查询需要使用 %关键字%。
            # 例如 keyword 是 "数据"，like_keyword 就是 "%数据%"。
            like_keyword = f"%{keyword}%"

            cursor.execute(sql, (keyword, like_keyword, like_keyword))

            # fetchall() 表示取出全部查询结果。
            courses = cursor.fetchall()

        # 直接返回列表，FastAPI 会自动转成 JSON 数组。
        return courses

    finally:
        connection.close()


@app.post("/api/admin/courses")
def create_course(data: CourseCreateRequest):
    """
    新增课程。

    前端请求示例：

        POST /api/admin/courses
        {
          "course_no": "C006",
          "course_name": "Python程序设计",
          "credit": 3.0,
          "prerequisite_no": null
        }

    这个接口演示 INSERT 语句。
    """

    connection = get_connection()

    try:
        with connection.cursor() as cursor:
            # 先查询课程号是否已经存在。
            # 这样可以给前端返回更友好的错误信息。
            check_sql = """
                SELECT course_no
                FROM courses
                WHERE course_no = %s
            """
            cursor.execute(check_sql, (data.course_no,))
            exists = cursor.fetchone()

            if exists is not None:
                raise HTTPException(status_code=400, detail="课程号已存在")

            # 执行 INSERT，把一门新课程插入 courses 表。
            insert_sql = """
                INSERT INTO courses
                    (course_no, course_name, credit, prerequisite_no)
                VALUES
                    (%s, %s, %s, %s)
            """
            cursor.execute(
                insert_sql,
                (
                    data.course_no,
                    data.course_name,
                    data.credit,
                    data.prerequisite_no,
                ),
            )

        # INSERT、UPDATE、DELETE 修改了数据库，必须提交事务。
        connection.commit()

        return {"message": "课程新增成功"}

    except HTTPException:
        # 如果是我们主动抛出的 HTTPException，也要回滚事务。
        connection.rollback()
        raise

    except IntegrityError as error:
        # IntegrityError 通常表示违反主键、外键、唯一约束等完整性约束。
        connection.rollback()
        raise HTTPException(status_code=400, detail=f"数据库完整性约束错误：{error}")

    finally:
        connection.close()


@app.put("/api/admin/courses/{course_no}")
def update_course(course_no: str, data: CourseUpdateRequest):
    """
    修改课程。

    URL 中的 {course_no} 表示要修改哪一门课程。

    前端请求示例：

        PUT /api/admin/courses/C001
        {
          "course_name": "数据库系统原理",
          "credit": 3.5,
          "prerequisite_no": null
        }

    这个接口演示 UPDATE 语句。
    """

    connection = get_connection()

    try:
        with connection.cursor() as cursor:
            # 修改前先确认这门课是否存在。
            check_sql = """
                SELECT course_no
                FROM courses
                WHERE course_no = %s
            """
            cursor.execute(check_sql, (course_no,))
            exists = cursor.fetchone()

            if exists is None:
                raise HTTPException(status_code=404, detail="课程不存在")

            # 执行 UPDATE。
            # 注意 WHERE course_no = %s 很重要。
            # 如果 UPDATE 语句没有 WHERE，可能会把整张表的课程都改掉。
            update_sql = """
                UPDATE courses
                SET
                    course_name = %s,
                    credit = %s,
                    prerequisite_no = %s
                WHERE course_no = %s
            """
            cursor.execute(
                update_sql,
                (
                    data.course_name,
                    data.credit,
                    data.prerequisite_no,
                    course_no,
                ),
            )

        connection.commit()

        return {"message": "课程修改成功"}

    except HTTPException:
        connection.rollback()
        raise

    except IntegrityError as error:
        connection.rollback()
        raise HTTPException(status_code=400, detail=f"数据库完整性约束错误：{error}")

    finally:
        connection.close()


@app.delete("/api/admin/courses/{course_no}")
def delete_course(course_no: str):
    """
    删除课程。

    前端请求示例：

        DELETE /api/admin/courses/C006

    这个接口演示 DELETE 语句。

    注意：
    courses 表和 teaching_classes 表之间设置了 ON DELETE CASCADE。
    所以删除课程时，相关教学班也会被数据库自动删除。
    这可以用于演示外键级联删除，但正式系统中应谨慎使用。
    """

    connection = get_connection()

    try:
        with connection.cursor() as cursor:
            # 先查询课程是否存在。
            check_sql = """
                SELECT course_no
                FROM courses
                WHERE course_no = %s
            """
            cursor.execute(check_sql, (course_no,))
            exists = cursor.fetchone()

            if exists is None:
                raise HTTPException(status_code=404, detail="课程不存在")

            # 执行 DELETE。
            # 同样要注意 WHERE 条件，避免误删整张表。
            delete_sql = """
                DELETE FROM courses
                WHERE course_no = %s
            """
            cursor.execute(delete_sql, (course_no,))

        connection.commit()

        return {"message": "课程删除成功"}

    except HTTPException:
        connection.rollback()
        raise

    except IntegrityError as error:
        connection.rollback()
        raise HTTPException(status_code=400, detail=f"数据库完整性约束错误：{error}")

    finally:
        connection.close()


# -----------------------------
# 五、学生：课程查询与选课
# -----------------------------


@app.get("/api/student/classes")
def list_teaching_classes(
    student_no: str = "",
    keyword: str = "",
    semester: str = "",
):
    """
    学生查询可选教学班。

    前端请求示例：

        GET /api/student/classes?student_no=S001
        GET /api/student/classes?student_no=S001&keyword=数据库
        GET /api/student/classes?student_no=S001&semester=2026春

    参数说明：
    - student_no 用来判断当前学生是否已经选过某个教学班。
    - keyword 用来按课程号或课程名模糊查询。
    - semester 用来按学期筛选。

    这个接口演示：
    1. JOIN 多表连接。
    2. LEFT JOIN 判断“是否已选”。
    3. CASE WHEN 生成前端需要的状态字段。
    """

    connection = get_connection()

    try:
        with connection.cursor() as cursor:
            # 这条 SQL 同时查询 teaching_classes 和 courses。
            #
            # JOIN courses c ON tc.course_no = c.course_no：
            #   把教学班表和课程表连接起来，因为课程名和学分在 courses 表中。
            #
            # LEFT JOIN enrollments e：
            #   用来判断当前学生是否已经选了这个教学班。
            #   如果已经选了，e.enrollment_id 不为空。
            #   如果没选，e.enrollment_id 为空。
            #
            # CASE WHEN：
            #   把数据库中的空值判断转换成 0 或 1，方便前端显示按钮状态。
            sql = """
                SELECT
                    tc.class_id,
                    c.course_no,
                    c.course_name,
                    c.credit,
                    tc.teacher_name,
                    tc.semester,
                    tc.class_name,
                    tc.capacity,
                    tc.selected_count,
                    tc.class_time,
                    tc.classroom,
                    CASE
                        WHEN e.enrollment_id IS NULL THEN 0
                        ELSE 1
                    END AS is_selected
                FROM teaching_classes tc
                JOIN courses c
                    ON tc.course_no = c.course_no
                LEFT JOIN enrollments e
                    ON e.class_id = tc.class_id
                    AND e.student_no = %s
                WHERE
                    (
                        %s = ''
                        OR c.course_no LIKE %s
                        OR c.course_name LIKE %s
                    )
                    AND
                    (
                        %s = ''
                        OR tc.semester = %s
                    )
                ORDER BY tc.class_id
            """

            like_keyword = f"%{keyword}%"

            cursor.execute(
                sql,
                (
                    student_no,
                    keyword,
                    like_keyword,
                    like_keyword,
                    semester,
                    semester,
                ),
            )

            classes = cursor.fetchall()

        return classes

    finally:
        connection.close()


@app.get("/api/student/my-courses")
def list_my_courses(student_no: str):
    """
    查询某个学生已经选择的课程。

    前端请求示例：

        GET /api/student/my-courses?student_no=S001

    这个接口演示多表连接查询：
    enrollments -> students -> teaching_classes -> courses
    """

    connection = get_connection()

    try:
        with connection.cursor() as cursor:
            sql = """
                SELECT
                    e.enrollment_id,
                    s.student_no,
                    s.student_name,
                    c.course_no,
                    c.course_name,
                    c.credit,
                    tc.teacher_name,
                    tc.semester,
                    tc.class_name,
                    tc.class_time,
                    tc.classroom,
                    e.grade,
                    e.selected_at
                FROM enrollments e
                JOIN students s
                    ON e.student_no = s.student_no
                JOIN teaching_classes tc
                    ON e.class_id = tc.class_id
                JOIN courses c
                    ON tc.course_no = c.course_no
                WHERE s.student_no = %s
                ORDER BY e.selected_at DESC
            """

            cursor.execute(sql, (student_no,))
            courses = cursor.fetchall()

        return courses

    finally:
        connection.close()


@app.post("/api/student/select/{class_id}")
def select_course(class_id: int, data: SelectCourseRequest):
    """
    学生选课。

    前端请求示例：

        POST /api/student/select/1
        {
          "student_no": "S001"
        }

    这个接口是本 Demo 中最适合重点讲解的部分，因为它不是简单 INSERT。

    选课需要满足几个业务规则：
    1. 学生必须存在。
    2. 教学班必须存在。
    3. 教学班人数不能超过容量。
    4. 同一个学生不能重复选择同一个教学班。
    5. 插入选课记录后，要同步更新教学班已选人数。

    因此这个接口使用事务：
    - 如果所有步骤都成功，就 commit。
    - 如果中间任何一步失败，就 rollback。

    这个接口对应的典型 SQL 包括：
    - SELECT
    - SELECT ... FOR UPDATE
    - INSERT
    - UPDATE
    """

    connection = get_connection()

    try:
        # 显式开启事务。
        # 虽然 autocommit=False 时 MySQL 会自动开始事务，
        # 但这里写 connection.begin() 更方便教学说明。
        connection.begin()

        with connection.cursor() as cursor:
            # 第一步：检查学生是否存在。
            # 如果学号不存在，说明前端传来的 student_no 有问题。
            check_student_sql = """
                SELECT student_no
                FROM students
                WHERE student_no = %s
            """
            cursor.execute(check_student_sql, (data.student_no,))
            student = cursor.fetchone()

            if student is None:
                raise HTTPException(status_code=404, detail="学生不存在")

            # 第二步：检查教学班是否存在，并锁定这条教学班记录。
            #
            # FOR UPDATE 的作用：
            #   在事务提交前，其他事务不能同时修改这条教学班记录。
            #
            # 为什么这里要锁？
            #   假设某个教学班只剩 1 个名额。
            #   如果两个学生同时点击选课，都看到还有 1 个名额，
            #   就可能造成超过容量。
            #   FOR UPDATE 可以避免这种并发问题。
            check_class_sql = """
                SELECT
                    class_id,
                    capacity,
                    selected_count
                FROM teaching_classes
                WHERE class_id = %s
                FOR UPDATE
            """
            cursor.execute(check_class_sql, (class_id,))
            teaching_class = cursor.fetchone()

            if teaching_class is None:
                raise HTTPException(status_code=404, detail="教学班不存在")

            # 第三步：判断教学班是否已满。
            # selected_count 表示已选人数，capacity 表示容量。
            if teaching_class["selected_count"] >= teaching_class["capacity"]:
                raise HTTPException(status_code=400, detail="教学班人数已满")

            # 第四步：判断是否重复选课。
            # enrollments 表中设置了 UNIQUE(student_no, class_id)，
            # 数据库层面也能阻止重复选课。
            # 这里提前查询，是为了给前端返回更清楚的错误信息。
            check_selected_sql = """
                SELECT enrollment_id
                FROM enrollments
                WHERE student_no = %s AND class_id = %s
            """
            cursor.execute(check_selected_sql, (data.student_no, class_id))
            selected = cursor.fetchone()

            if selected is not None:
                raise HTTPException(status_code=400, detail="不能重复选课")

            # 第五步：插入选课记录。
            # grade 暂时不填，表示学生刚选课，还没有成绩。
            insert_sql = """
                INSERT INTO enrollments
                    (student_no, class_id, grade)
                VALUES
                    (%s, %s, NULL)
            """
            cursor.execute(insert_sql, (data.student_no, class_id))

            # 第六步：更新教学班已选人数。
            # 这里使用 selected_count = selected_count + 1，
            # 让数据库在原有数值基础上自增 1。
            update_count_sql = """
                UPDATE teaching_classes
                SET selected_count = selected_count + 1
                WHERE class_id = %s
            """
            cursor.execute(update_count_sql, (class_id,))

        # 所有步骤都成功，提交事务。
        connection.commit()

        return {"message": "选课成功"}

    except HTTPException:
        # 如果是业务错误，例如课程已满、重复选课，也要回滚。
        connection.rollback()
        raise

    except IntegrityError as error:
        # 如果数据库唯一约束或外键约束报错，也要回滚。
        connection.rollback()
        raise HTTPException(status_code=400, detail=f"数据库完整性约束错误：{error}")

    except Exception as error:
        # 捕获其他未预料到的错误，避免后端直接崩溃。
        connection.rollback()
        raise HTTPException(status_code=500, detail=f"服务器内部错误：{error}")

    finally:
        # 最后一定关闭数据库连接。
        connection.close()
