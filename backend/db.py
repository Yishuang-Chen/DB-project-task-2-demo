"""
db.py

这个文件只做一件事：创建 MySQL 数据库连接。

为什么单独写一个 db.py？
1. 后端很多接口都要访问数据库。
2. 如果每个接口都重复写 host、user、password，会让代码很乱。
3. 把“连接数据库”的代码集中在这里，其他文件只需要调用 get_connection()。

注意：
本 Demo 为了体现数据库课程中“手写 SQL”的学习目标，只封装数据库连接，
不使用 ORM，不把 SELECT、INSERT、UPDATE、DELETE 隐藏起来。
"""

# os 用来读取环境变量，例如 DB_HOST、DB_USER。
import os

# pymysql 是 Python 连接 MySQL 的第三方库。
import pymysql

# DictCursor 是 PyMySQL 提供的一种游标类型。
# 普通游标查询结果类似元组，例如 ("admin", "管理员")。
# DictCursor 查询结果类似字典，例如 {"username": "admin", "display_name": "管理员"}。
# 字典形式更适合转换成 JSON 返回给前端。
from pymysql.cursors import DictCursor

# load_dotenv 用来读取 .env 文件中的配置。
# 这样数据库密码就不用直接写死在 Python 代码里。
from dotenv import load_dotenv


# 读取当前 backend 目录下的 .env 文件。
# 如果 .env 文件中有 DB_HOST=127.0.0.1，那么后面 os.getenv("DB_HOST") 就能读到它。
load_dotenv()


def get_connection():
    """
    创建并返回一个 MySQL 连接对象。

    每次需要访问数据库时，都调用这个函数：

        connection = get_connection()

    用完之后要调用：

        connection.close()

    这样可以释放数据库连接，避免连接数量越来越多。
    """

    # 从 .env 文件读取数据库主机地址。
    # 如果 .env 中没有 DB_HOST，就默认使用 127.0.0.1。
    host = os.getenv("DB_HOST", "127.0.0.1")

    # 从 .env 文件读取数据库端口。
    # os.getenv 读取到的是字符串，所以这里需要 int(...) 转成整数。
    port = int(os.getenv("DB_PORT", "3306"))

    # 从 .env 文件读取数据库用户名。
    user = os.getenv("DB_USER", "root")

    # 从 .env 文件读取数据库密码。
    password = os.getenv("DB_PASSWORD", "123456")

    # 从 .env 文件读取数据库名称。
    database = os.getenv("DB_NAME", "teaching_demo")

    # pymysql.connect 会真正连接 MySQL。
    # autocommit=False 表示默认不自动提交事务。
    # 对 INSERT、UPDATE、DELETE 操作，我们会在接口中手动 connection.commit()。
    # 这样可以演示“事务提交”和“事务回滚”。
    connection = pymysql.connect(
        host=host,
        port=port,
        user=user,
        password=password,
        database=database,
        charset="utf8mb4",
        cursorclass=DictCursor,
        autocommit=False,
    )

    # 返回连接对象，供 main.py 中的接口使用。
    return connection
