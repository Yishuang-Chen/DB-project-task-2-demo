/*
 * teaching.ts
 *
 * 这个文件把“具体后端接口”封装成“前端函数”。
 *
 * 例如页面中调用 loginApi(...)，
 * 实际上就是向后端 POST /api/login。
 *
 * 这样做的好处：
 * 1. 页面代码更容易读。
 * 2. 后端接口路径集中管理。
 * 3. 教学时可以清楚看到“页面动作 -> API 函数 -> 后端接口”的对应关系。
 */

import type {
  Course,
  CourseForm,
  LoginRequest,
  LoginUser,
  MessageResponse,
  MyCourse,
  TeachingClass,
} from '../types'
import { apiDelete, apiGet, apiPost, apiPut } from './request'

// 登录接口：POST /api/login
export function loginApi(data: LoginRequest): Promise<LoginUser> {
  return apiPost<LoginUser>('/login', data)
}

// 管理员查询课程：GET /api/admin/courses?keyword=xxx
export function listCoursesApi(keyword: string): Promise<Course[]> {
  return apiGet<Course[]>('/admin/courses', { keyword })
}

// 管理员新增课程：POST /api/admin/courses
export function createCourseApi(data: CourseForm): Promise<MessageResponse> {
  return apiPost<MessageResponse>('/admin/courses', data)
}

// 管理员修改课程：PUT /api/admin/courses/{course_no}
export function updateCourseApi(
  courseNo: string,
  data: Omit<CourseForm, 'course_no'>,
): Promise<MessageResponse> {
  return apiPut<MessageResponse>(`/admin/courses/${courseNo}`, data)
}

// 管理员删除课程：DELETE /api/admin/courses/{course_no}
export function deleteCourseApi(courseNo: string): Promise<MessageResponse> {
  return apiDelete<MessageResponse>(`/admin/courses/${courseNo}`)
}

// 学生查询教学班：GET /api/student/classes
export function listTeachingClassesApi(
  studentNo: string,
  keyword: string,
  semester: string,
): Promise<TeachingClass[]> {
  return apiGet<TeachingClass[]>('/student/classes', {
    student_no: studentNo,
    keyword,
    semester,
  })
}

// 学生查询自己的已选课程：GET /api/student/my-courses
export function listMyCoursesApi(studentNo: string): Promise<MyCourse[]> {
  return apiGet<MyCourse[]>('/student/my-courses', {
    student_no: studentNo,
  })
}

// 学生选课：POST /api/student/select/{class_id}
export function selectCourseApi(
  classId: number,
  studentNo: string,
): Promise<MessageResponse> {
  return apiPost<MessageResponse>(`/student/select/${classId}`, {
    student_no: studentNo,
  })
}
