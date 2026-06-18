/*
 * auth.ts
 *
 * 这个文件负责保存和读取“当前登录用户”。
 *
 * 正式系统通常会使用 Cookie、Session 或 JWT。
 * 但本 Demo 的重点是数据库和前后端基本流程，
 * 所以先使用浏览器自带的 localStorage 保存登录信息。
 *
 * localStorage 的特点：
 * 1. 数据保存在浏览器中。
 * 2. 刷新页面后仍然存在。
 * 3. 只适合教学 Demo，不适合作为正式权限安全方案。
 */

import type { LoginUser } from '../types'

// USER_KEY 是保存到 localStorage 时使用的键名。
// 可以把 localStorage 理解为一个简单的 key-value 存储。
const USER_KEY = 'teaching_demo_user'

// saveUser 在登录成功后调用，把用户信息保存到浏览器。
export function saveUser(user: LoginUser): void {
  // localStorage 只能保存字符串。
  // JSON.stringify 会把对象转换成字符串。
  localStorage.setItem(USER_KEY, JSON.stringify(user))
}

// getCurrentUser 用来读取当前登录用户。
export function getCurrentUser(): LoginUser | null {
  // 从 localStorage 中读取字符串。
  const raw = localStorage.getItem(USER_KEY)

  // 如果 raw 是 null，说明还没有登录。
  if (!raw) {
    return null
  }

  try {
    // JSON.parse 会把字符串还原成对象。
    return JSON.parse(raw) as LoginUser
  } catch {
    // 如果解析失败，说明 localStorage 中的数据被破坏了。
    // 清掉错误数据，然后认为当前没有登录。
    localStorage.removeItem(USER_KEY)
    return null
  }
}

// clearCurrentUser 在退出登录时调用。
export function clearCurrentUser(): void {
  localStorage.removeItem(USER_KEY)
}

// getHomePath 根据用户角色返回登录后应该进入的页面。
export function getHomePath(user: LoginUser): string {
  if (user.role === 'admin') {
    return '/admin/courses'
  }

  if (user.role === 'student') {
    return '/student/classes'
  }

  // 教师端在本 Demo 中作为扩展任务，所以暂时跳回登录页。
  return '/login'
}
