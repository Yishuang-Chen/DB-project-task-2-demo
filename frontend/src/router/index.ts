/*
 * router/index.ts
 *
 * 这个文件配置 Vue Router。
 *
 * Vue Router 的作用：
 * 1. 根据浏览器地址显示不同页面。
 * 2. 例如 /login 显示登录页，/admin/courses 显示管理员课程管理页。
 * 3. 在页面切换前做简单检查，例如未登录不能进入管理页面。
 */

import { createRouter, createWebHistory } from 'vue-router'
import type { RouteRecordRaw } from 'vue-router'
import LoginView from '../views/LoginView.vue'
import AdminCoursesView from '../views/AdminCoursesView.vue'
import StudentCoursesView from '../views/StudentCoursesView.vue'
import type { UserRole } from '../types'
import { getCurrentUser, getHomePath } from '../utils/auth'

// routes 是路由表。
// 每一项表示一个“地址”和一个“页面组件”的对应关系。
const routes: RouteRecordRaw[] = [
  {
    // 访问根路径时，直接跳转到登录页。
    path: '/',
    redirect: '/login',
  },
  {
    // 登录页。
    path: '/login',
    component: LoginView,
  },
  {
    // 管理员课程管理页。
    path: '/admin/courses',
    component: AdminCoursesView,
    meta: {
      // requiresAuth 表示这个页面必须登录后才能访问。
      requiresAuth: true,

      // roles 表示允许哪些角色访问。
      roles: ['admin'],
    },
  },
  {
    // 学生课程查询与选课页。
    path: '/student/classes',
    component: StudentCoursesView,
    meta: {
      requiresAuth: true,
      roles: ['student'],
    },
  },
  {
    // 如果访问了不存在的地址，就跳回登录页。
    path: '/:pathMatch(.*)*',
    redirect: '/login',
  },
]

// 创建 router 对象。
const router = createRouter({
  // createWebHistory 表示使用普通浏览器路径。
  // 例如 http://127.0.0.1:5173/login。
  history: createWebHistory(),
  routes,
})

// beforeEach 是全局路由守卫。
// 每次页面跳转前，它都会先执行。
router.beforeEach((to) => {
  // 从 localStorage 中读取当前登录用户。
  const user = getCurrentUser()

  // 如果用户已经登录，又访问 /login，就把他送到自己的首页。
  // 例如管理员再次访问 /login，会自动跳到 /admin/courses。
  if (to.path === '/login' && user) {
    const homePath = getHomePath(user)

    // 教师端在本 Demo 中留作扩展任务，getHomePath 会返回 /login。
    // 为了避免死循环，只有目标不是 /login 时才重定向。
    if (homePath !== '/login') {
      return homePath
    }
  }

  // 读取路由 meta 中的 requiresAuth。
  const requiresAuth = Boolean(to.meta.requiresAuth)

  // 如果页面需要登录，但当前没有用户，就跳转到登录页。
  if (requiresAuth && !user) {
    return '/login'
  }

  // 读取路由 meta 中允许访问的角色。
  const roles = to.meta.roles as UserRole[] | undefined

  // 如果页面设置了角色限制，并且当前用户角色不在允许列表中，就跳转回用户首页。
  if (user && roles && !roles.includes(user.role)) {
    return getHomePath(user)
  }

  // 不返回任何值，表示允许本次跳转。
  return true
})

export default router
