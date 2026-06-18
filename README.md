# 数据库课程实验加分项 2 Demo

本项目是一个用于教学演示的“高校教学管理系统 Demo”，用于说明如何通过 Web 界面访问 MySQL 数据库。

项目结构：

```text
backend/   Python 后端，使用 FastAPI + PyMySQL
frontend/  Vue 前端，使用 Vue 3 + TypeScript + Vite
sql/       建库、建表、插入示例数据的 SQL 脚本
```

保留的课程材料：

```text
数据库原理课程实验 2026 内容与要求.pdf
数据库原理课程实验加分项2教程.docx
```

上述 PDF 和 Word 文件为课程材料，清理项目时不要删除或修改。

## 快速运行

1. 初始化数据库：

```powershell
mysql -uroot -p --default-character-set=utf8mb4 < sql/init_teaching_demo.sql
```

2. 启动后端：

```powershell
cd backend
python -m pip install -r requirements.txt
Copy-Item .env.example .env
python -m uvicorn main:app --reload
```

3. 启动前端：

```powershell
cd frontend
npm install
npm run dev
```

4. 浏览器访问：

```text
http://127.0.0.1:5173/login
```

## 说明

本项目刻意保留手写 SQL，没有使用 ORM，目的是让同学们能清楚看到：

```text
页面操作 -> 前端请求 -> 后端接口 -> SQL 语句 -> MySQL 数据库
```
