/*
 * types.ts
 *
 * 这个文件集中保存前端会用到的 TypeScript 类型。
 *
 * 为什么要写类型？
 * 1. 后端返回的是 JSON，前端需要知道 JSON 里有哪些字段。
 * 2. TypeScript 可以在写代码时检查字段名是否写错。
 * 3. 类型定义相当于“前后端数据约定”，适合教学时对照后端接口阅读。
 */

// UserRole 表示用户角色。
// 这里用联合类型，意思是 role 只能是下面三个字符串之一。
export type UserRole = 'admin' | 'student' | 'teacher'

// LoginRequest 表示登录时前端发送给后端的数据。
export interface LoginRequest {
  // username 对应后端 LoginRequest 中的 username。
  username: string

  // password 对应后端 LoginRequest 中的 password。
  password: string
}

// LoginUser 表示登录成功后，后端返回给前端的用户信息。
export interface LoginUser {
  id: number
  username: string
  role: UserRole

  // related_no 用来关联具体身份。
  // 学生用户对应 students.student_no，例如 S001。
  // 管理员没有对应学生或教师编号，所以可能是 null。
  related_no: string | null

  // display_name 是页面上显示的姓名，例如“张三”。
  display_name: string
}

// Course 表示课程表 courses 中的一条课程记录。
export interface Course {
  course_no: string
  course_name: string
  credit: number
  prerequisite_no: string | null
}

// CourseForm 表示新增或修改课程时，表单中的数据。
// 它和 Course 很像，但单独命名可以让代码更容易读。
export interface CourseForm {
  course_no: string
  course_name: string
  credit: number
  prerequisite_no: string | null
}

// TeachingClass 表示学生查询课程时，后端返回的教学班记录。
export interface TeachingClass {
  class_id: number
  course_no: string
  course_name: string
  credit: number
  teacher_name: string
  semester: string
  class_name: string
  capacity: number
  selected_count: number
  class_time: string
  classroom: string

  // is_selected 由后端 SQL 中的 CASE WHEN 生成。
  // 0 表示当前学生没有选择这个教学班。
  // 1 表示当前学生已经选择这个教学班。
  is_selected: 0 | 1
}

// MyCourse 表示“我的课表”中的一条已选课程。
export interface MyCourse {
  enrollment_id: number
  student_no: string
  student_name: string
  course_no: string
  course_name: string
  credit: number
  teacher_name: string
  semester: string
  class_name: string
  class_time: string
  classroom: string
  grade: number | null
  selected_at: string
}

// MessageResponse 表示后端常见的成功响应。
// 例如 { "message": "课程新增成功" }。
export interface MessageResponse {
  message: string
}

// NavigationMenuItem 表示左侧导航菜单中的一项。
// 它会被管理员页面和学生页面共同使用。
export interface NavigationMenuItem {
  // key 是程序内部使用的唯一标识，不能重复。
  key: string

  // label 是显示在左侧菜单上的文字。
  label: string

  // description 用来说明这个模块的用途。
  description: string

  // implemented 表示这个模块是否已经写了具体功能。
  // true：点击后显示真实功能页面。
  // false：点击后显示“待实现”占位说明。
  implemented: boolean
}
