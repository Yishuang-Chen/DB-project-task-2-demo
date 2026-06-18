# 后端 Demo 说明

本目录是“高校教学管理系统 Demo”的 Python 后端。

技术栈：

```text
FastAPI + Uvicorn + PyMySQL + python-dotenv + MySQL
```

设计目标：

```text
1. 使用 Python 提供接口给 Vue 前端调用。
2. 使用 PyMySQL 连接 MySQL。
3. 保留原始手写 SQL，便于数据库课程教学。
4. 只实现示例功能，不追求完整教务系统。
```

## 1. 安装依赖

从项目根目录进入后端目录：

```powershell
cd backend
```

安装后端依赖：

```powershell
python -m pip install -r requirements.txt
```

说明：

```text
python -m pip
```

表示使用当前 Python 解释器对应的 pip，避免把依赖安装到其他 Python 环境中。

## 2. 配置数据库连接

后端通过 `.env` 文件读取数据库连接信息。

第一次运行时，可以复制示例配置：

```powershell
Copy-Item .env.example .env
```

然后根据自己的 MySQL 配置修改 `.env`：

```text
DB_HOST=127.0.0.1
DB_PORT=3306
DB_USER=root
DB_PASSWORD=123456
DB_NAME=teaching_demo
```

如果 MySQL 用户名、密码或数据库名不同，只需要修改 `.env`，不需要修改 Python 代码。

## 3. 启动后端

确保当前目录是 `backend`，然后执行：

```powershell
python -m uvicorn main:app --reload
```

命令说明：

```text
main:app
```

表示运行 `main.py` 文件中的 `app` 对象。

```text
--reload
```

表示开发模式下自动重载，修改后端代码后服务会自动重启。

启动成功后，浏览器打开：

```text
http://127.0.0.1:8000/docs
```

这是 FastAPI 自动生成的接口测试页面。

## 4. 推荐测试顺序

建议先在 `/docs` 页面依次测试：

```text
1. GET    /
2. POST   /api/login
3. GET    /api/admin/courses
4. POST   /api/admin/courses
5. PUT    /api/admin/courses/{course_no}
6. DELETE /api/admin/courses/{course_no}
7. GET    /api/student/classes
8. POST   /api/student/select/{class_id}
9. GET    /api/student/my-courses
```

## 5. 测试账号

```text
admin       / 123456   管理员
stu001      / 123456   学生：张三
stu002      / 123456   学生：李四
teacher001 / 123456   教师：王老师
```

本 Demo 暂时主要实现管理员和学生相关接口，教师接口可作为后续扩展任务。
