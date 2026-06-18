# 前端 Demo 说明

本目录是“高校教学管理系统 Demo”的 Vue 前端。

技术栈：

```text
Vue 3 + TypeScript + Vite + Element Plus + Vue Router + Axios
```

代码特点：

```text
1. 所有页面都使用 <script setup lang="ts">。
2. 使用 Axios 调用 FastAPI 后端接口。
3. 使用 Vue Router 根据角色跳转页面。
4. 不使用复杂状态管理库，登录信息暂时保存在 localStorage。
5. 登录后页面使用左侧导航栏，左上角预留学校校徽。
6. 代码中保留详细中文注释，便于第一次接触前端的同学阅读。
```

## 1. 安装依赖

从项目根目录进入前端目录：

```powershell
cd frontend
```

安装前端依赖：

```powershell
npm install
```

说明：

```text
npm install
```

会根据 `package.json` 和 `package-lock.json` 安装 Vue、Vite、Element Plus、Vue Router、Axios 等依赖。

如果终端提示无法识别 `npm`，说明 Node.js 没有安装或没有加入 PATH。请先手动安装 Node.js LTS 版本，然后重新打开终端。

## 2. 启动后端

前端需要调用后端接口，因此建议先启动后端。

从项目根目录执行：

```powershell
cd backend
python -m uvicorn main:app --reload
```

后端接口文档地址：

```text
http://127.0.0.1:8000/docs
```

## 3. 启动前端

另开一个终端，从项目根目录执行：

```powershell
cd frontend
npm run dev
```

启动成功后，浏览器访问：

```text
http://127.0.0.1:5173/login
```

## 4. 测试账号

```text
admin  / 123456   管理员
stu001 / 123456   学生：张三
stu002 / 123456   学生：李四
```

教师账号在数据库中保留，但教师端页面留作扩展任务。

## 5. 主要文件

```text
src/main.ts                         Vue 应用入口
src/App.vue                         根组件，只负责显示当前路由页面
src/router/index.ts                 路由配置与简单登录检查
src/api/request.ts                  Axios 请求封装
src/api/teaching.ts                 后端接口函数
src/utils/auth.ts                   localStorage 登录信息读写
src/views/LoginView.vue             登录页
src/views/AdminCoursesView.vue      管理员课程管理页
src/views/StudentCoursesView.vue    学生课程查询与选课页
src/components/AppLayout.vue        登录后页面的左侧导航布局
src/components/ModulePlaceholder.vue 未实现模块的占位说明
src/types.ts                        TypeScript 类型定义
public/README.md                    校徽图片放置说明
```

## 6. 当前实现和待实现模块

管理员端已实现：

```text
课程管理
```

管理员端待实现：

```text
班级管理
学生管理
教师管理
学生成绩管理
选课结果管理
```

学生端已实现：

```text
选课
```

学生端待实现：

```text
学生课表查询
学生成绩查询
班级信息查询
考试安排查询
个人信息查询
```

## 7. 推荐阅读顺序

```text
1. src/types.ts
2. src/api/request.ts
3. src/api/teaching.ts
4. src/router/index.ts
5. src/components/AppLayout.vue
6. src/components/ModulePlaceholder.vue
7. src/views/LoginView.vue
8. src/views/AdminCoursesView.vue
9. src/views/StudentCoursesView.vue
```
