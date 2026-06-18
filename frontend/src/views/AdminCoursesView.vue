<script setup lang="ts">
/*
 * AdminCoursesView.vue
 *
 * 这是管理员端页面。
 *
 * 本次修改后的管理员端不再只是“课程管理页面”，
 * 而是改成一个带左侧菜单的“管理功能入口”。
 *
 * 目前真正实现的功能：
 * 1. 课程管理：查询、新增、修改、删除。
 *
 * 暂时只在 UI 中列出、但没有实现的功能：
 * 1. 班级管理。
 * 2. 学生管理。
 * 3. 教师管理。
 * 4. 学生成绩管理。
 * 5. 选课结果管理。
 *
 * 这些待实现模块会显示占位说明，后续可以留给本科生仿照课程管理继续完成。
 */

import { computed, onMounted, reactive, ref } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage, ElMessageBox } from 'element-plus'
import { Delete, Edit, Plus, Refresh, Search } from '@element-plus/icons-vue'
import AppLayout from '../components/AppLayout.vue'
import ModulePlaceholder from '../components/ModulePlaceholder.vue'
import {
  createCourseApi,
  deleteCourseApi,
  listCoursesApi,
  updateCourseApi,
} from '../api/teaching'
import { getErrorMessage } from '../api/request'
import { clearCurrentUser, getCurrentUser } from '../utils/auth'
import type {
  Course,
  CourseForm,
  LoginUser,
  NavigationMenuItem,
} from '../types'

// useRouter 获取 Vue Router 对象。
// 退出登录时，需要用 router.push('/login') 跳回登录页。
const router = useRouter()

// currentUser 保存当前登录用户。
// getCurrentUser 会从 localStorage 中读取登录时保存的用户信息。
const currentUser = ref<LoginUser | null>(getCurrentUser())

// adminMenuItems 是管理员左侧菜单。
// implemented=true 的模块表示已经实现具体功能。
// implemented=false 的模块表示只在 UI 中展示，后续留给学生实现。
const adminMenuItems: NavigationMenuItem[] = [
  {
    key: 'courseManage',
    label: '课程管理',
    description: '维护课程基本信息，演示课程表的增删改查。',
    implemented: true,
  },
  {
    key: 'classManage',
    label: '班级管理',
    description: '维护教学班容量、教师、时间地点等信息。',
    implemented: false,
  },
  {
    key: 'studentManage',
    label: '学生管理',
    description: '维护学生基本信息，例如学号、姓名、专业。',
    implemented: false,
  },
  {
    key: 'teacherManage',
    label: '教师管理',
    description: '维护教师基本信息和授课关系。',
    implemented: false,
  },
  {
    key: 'gradeManage',
    label: '学生成绩管理',
    description: '录入、修改、查询学生课程成绩。',
    implemented: false,
  },
  {
    key: 'enrollmentManage',
    label: '选课结果管理',
    description: '查看学生选课结果，并处理特殊选课记录。',
    implemented: false,
  },
]

// activeMenuKey 表示当前左侧菜单选中了哪一项。
// 默认选中课程管理，因为这是管理员端目前真正实现的功能。
const activeMenuKey = ref('courseManage')

// activeMenuItem 根据 activeMenuKey 找到当前菜单对象。
// computed 是 Vue 的计算属性，依赖变化时会自动重新计算。
const activeMenuItem = computed(() => {
  return adminMenuItems.find((item) => item.key === activeMenuKey.value)
})

// pageTitle 是右侧页面顶部标题。
// 当前菜单变化时，标题也会变化。
const pageTitle = computed(() => {
  return activeMenuItem.value?.label ?? '管理功能'
})

// pageSubtitle 是右侧页面顶部说明。
const pageSubtitle = computed(() => {
  return activeMenuItem.value?.description ?? '请选择左侧管理模块'
})

// placeholderTasks 保存每个待实现模块的建议任务。
// 这些文字会显示在占位区域，告诉学生后续可以怎么扩展。
const placeholderTasks: Record<string, string[]> = {
  classManage: [
    '设计 teaching_classes 表的新增、修改、删除接口。',
    '在前端使用表格展示教学班容量、教师、时间、地点。',
    '修改教学班容量时，需要检查 selected_count 不能超过 capacity。',
  ],
  studentManage: [
    '设计 students 表的查询、新增、修改、删除接口。',
    '新增学生时，同时考虑是否创建 users 登录账号。',
    '删除学生时，注意 enrollments 表中的外键约束。',
  ],
  teacherManage: [
    '可以新增 teachers 表，保存教师编号、姓名、院系。',
    '教学班表 teaching_classes 中的 teacher_no 可关联 teachers 表。',
    '前端可以使用下拉框选择授课教师。',
  ],
  gradeManage: [
    '查询某门课程或教学班下的学生名单。',
    '使用 UPDATE enrollments SET grade = ... 修改成绩。',
    '增加成绩范围校验，例如成绩必须在 0 到 100 之间。',
  ],
  enrollmentManage: [
    '按课程、学生、学期查询选课记录。',
    '管理员可以处理特殊退课或补选记录。',
    '删除选课记录时，需要同步更新教学班已选人数。',
  ],
}

// keyword 保存课程查询关键字。
// 用户在搜索框中输入课程号或课程名时，这个变量会变化。
const keyword = ref('')

// courses 保存课程表格数据。
// 后端返回 Course[] 后，会赋值给 courses.value。
const courses = ref<Course[]>([])

// loading 表示课程列表是否正在加载。
// 它会绑定到 el-table 的 v-loading。
const loading = ref(false)

// dialogVisible 控制“新增/修改课程”弹窗是否显示。
const dialogVisible = ref(false)

// isEditMode 表示弹窗当前处于新增模式还是修改模式。
// false：新增课程。
// true：修改课程。
const isEditMode = ref(false)

// form 保存课程表单数据。
// reactive 会让对象中的每个字段都变成响应式数据。
const form = reactive<CourseForm>({
  course_no: '',
  course_name: '',
  credit: 3,
  prerequisite_no: null,
})

// normalizePrerequisite 用来处理先修课程号。
// 用户不填写先修课程时，前端把空字符串转换成 null。
// null 对应 MySQL 中的 NULL，更符合数据库表达。
function normalizePrerequisite(value: string | null): string | null {
  if (!value || !value.trim()) {
    return null
  }

  return value.trim()
}

// resetForm 把表单恢复成新增课程时的默认状态。
function resetForm(): void {
  form.course_no = ''
  form.course_name = ''
  form.credit = 3
  form.prerequisite_no = null
}

// handleMenuSelect 在点击左侧菜单时执行。
// 它只负责切换当前显示的模块，不会重新跳转路由。
function handleMenuSelect(key: string): void {
  activeMenuKey.value = key
}

// loadCourses 从后端查询课程列表。
async function loadCourses(): Promise<void> {
  loading.value = true

  try {
    // listCoursesApi 会请求：
    // GET http://127.0.0.1:8000/api/admin/courses?keyword=...
    courses.value = await listCoursesApi(keyword.value.trim())
  } catch (error) {
    ElMessage.error(getErrorMessage(error))
  } finally {
    loading.value = false
  }
}

// openCreateDialog 打开“新增课程”弹窗。
function openCreateDialog(): void {
  resetForm()
  isEditMode.value = false
  dialogVisible.value = true
}

// openEditDialog 打开“修改课程”弹窗。
// row 是表格中当前点击的课程记录。
function openEditDialog(row: Course): void {
  form.course_no = row.course_no
  form.course_name = row.course_name
  form.credit = Number(row.credit)
  form.prerequisite_no = row.prerequisite_no

  isEditMode.value = true
  dialogVisible.value = true
}

// validateForm 在提交前做简单前端校验。
// 注意：前端校验是为了用户体验，后端仍然要继续校验。
function validateForm(): boolean {
  if (!form.course_no.trim()) {
    ElMessage.warning('请输入课程号')
    return false
  }

  if (!form.course_name.trim()) {
    ElMessage.warning('请输入课程名')
    return false
  }

  if (form.credit <= 0) {
    ElMessage.warning('学分必须大于 0')
    return false
  }

  return true
}

// submitForm 提交新增或修改课程。
async function submitForm(): Promise<void> {
  if (!validateForm()) {
    return
  }

  // payload 是真正发给后端的 JSON 数据。
  const payload: CourseForm = {
    course_no: form.course_no.trim(),
    course_name: form.course_name.trim(),
    credit: Number(form.credit),
    prerequisite_no: normalizePrerequisite(form.prerequisite_no),
  }

  try {
    if (isEditMode.value) {
      // 修改课程时，请求：
      // PUT /api/admin/courses/{course_no}
      const result = await updateCourseApi(payload.course_no, {
        course_name: payload.course_name,
        credit: payload.credit,
        prerequisite_no: payload.prerequisite_no,
      })

      ElMessage.success(result.message)
    } else {
      // 新增课程时，请求：
      // POST /api/admin/courses
      const result = await createCourseApi(payload)
      ElMessage.success(result.message)
    }

    dialogVisible.value = false
    await loadCourses()
  } catch (error) {
    ElMessage.error(getErrorMessage(error))
  }
}

// removeCourse 删除课程。
async function removeCourse(row: Course): Promise<void> {
  try {
    await ElMessageBox.confirm(
      `确定删除课程 ${row.course_no} - ${row.course_name} 吗？`,
      '删除确认',
      {
        confirmButtonText: '删除',
        cancelButtonText: '取消',
        type: 'warning',
      },
    )

    // 删除课程时，请求：
    // DELETE /api/admin/courses/{course_no}
    const result = await deleteCourseApi(row.course_no)

    ElMessage.success(result.message)
    await loadCourses()
  } catch (error) {
    // 用户点击取消时，Element Plus 会把 'cancel' 或 'close' 传入 catch。
    // 这不是错误，所以直接 return。
    if (error === 'cancel' || error === 'close') {
      return
    }

    ElMessage.error(getErrorMessage(error))
  }
}

// handleLogout 退出登录。
function handleLogout(): void {
  clearCurrentUser()
  router.push('/login')
}

// 页面打开后，自动加载课程列表。
onMounted(() => {
  loadCourses()
})
</script>

<template>
  <AppLayout
    :active-key="activeMenuKey"
    menu-title="管理功能"
    :menu-items="adminMenuItems"
    :subtitle="pageSubtitle"
    :title="pageTitle"
    :user="currentUser"
    @logout="handleLogout"
    @select="handleMenuSelect"
  >
    <section v-if="activeMenuKey === 'courseManage'">
      <section class="toolbar">
        <el-input
          v-model="keyword"
          class="search-input"
          clearable
          placeholder="按课程号或课程名查询"
          @keyup.enter="loadCourses"
        >
          <template #prefix>
            <el-icon><Search /></el-icon>
          </template>
        </el-input>

        <div class="toolbar-actions">
          <el-button :icon="Search" type="primary" @click="loadCourses">
            查询
          </el-button>
          <el-button :icon="Refresh" @click="keyword = ''; loadCourses()">
            重置
          </el-button>
          <el-button :icon="Plus" type="success" @click="openCreateDialog">
            新增课程
          </el-button>
        </div>
      </section>

      <section class="table-section">
        <el-table
          v-loading="loading"
          border
          :data="courses"
          empty-text="暂无课程数据"
          stripe
        >
          <el-table-column label="课程号" min-width="110" prop="course_no" />
          <el-table-column label="课程名" min-width="180" prop="course_name" />
          <el-table-column label="学分" min-width="90" prop="credit" />
          <el-table-column label="先修课程" min-width="120">
            <template #default="{ row }">
              <el-tag v-if="row.prerequisite_no" type="info">
                {{ row.prerequisite_no }}
              </el-tag>
              <span v-else class="muted-text">无</span>
            </template>
          </el-table-column>
          <el-table-column fixed="right" label="操作" min-width="180">
            <template #default="{ row }">
              <el-button
                :icon="Edit"
                link
                type="primary"
                @click="openEditDialog(row)"
              >
                修改
              </el-button>
              <el-button
                :icon="Delete"
                link
                type="danger"
                @click="removeCourse(row)"
              >
                删除
              </el-button>
            </template>
          </el-table-column>
        </el-table>
      </section>
    </section>

    <ModulePlaceholder
      v-else
      :description="pageSubtitle"
      :tasks="placeholderTasks[activeMenuKey] ?? ['仿照课程管理模块补充接口和页面。']"
      :title="pageTitle"
    />

    <el-dialog
      v-model="dialogVisible"
      :title="isEditMode ? '修改课程' : '新增课程'"
      width="460px"
    >
      <el-form label-position="top">
        <el-form-item label="课程号">
          <el-input
            v-model="form.course_no"
            :disabled="isEditMode"
            placeholder="例如：C006"
          />
        </el-form-item>

        <el-form-item label="课程名">
          <el-input v-model="form.course_name" placeholder="例如：Python程序设计" />
        </el-form-item>

        <el-form-item label="学分">
          <el-input-number
            v-model="form.credit"
            :max="8"
            :min="0.5"
            :step="0.5"
            class="number-input"
          />
        </el-form-item>

        <el-form-item label="先修课程号">
          <el-input
            v-model="form.prerequisite_no"
            clearable
            placeholder="没有先修课程时可留空"
          />
        </el-form-item>
      </el-form>

      <template #footer>
        <el-button @click="dialogVisible = false">取消</el-button>
        <el-button type="primary" @click="submitForm">保存</el-button>
      </template>
    </el-dialog>
  </AppLayout>
</template>
