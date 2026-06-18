<script setup lang="ts">
/*
 * StudentCoursesView.vue
 *
 * 这是学生端页面。
 *
 * 本次修改后的学生端采用“左侧查询菜单 + 右侧内容区域”的结构。
 *
 * 目前真正实现的功能：
 * 1. 选课：查询可选教学班，并调用后端事务接口完成选课。
 *
 * 只在界面中列出、暂时留给学生继续实现的功能：
 * 1. 学生课表查询。
 * 2. 学生成绩查询。
 * 3. 班级信息查询。
 * 4. 考试安排查询。
 * 5. 个人信息查询。
 *
 * 这样既能让 UI 看起来像一个较完整的教务系统，
 * 又不会把 Demo 做得过大，符合“只实现典型功能”的教学目标。
 */

import { computed, onMounted, ref } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import { Check, Refresh, Search } from '@element-plus/icons-vue'
import AppLayout from '../components/AppLayout.vue'
import ModulePlaceholder from '../components/ModulePlaceholder.vue'
import {
  listMyCoursesApi,
  listTeachingClassesApi,
  selectCourseApi,
} from '../api/teaching'
import { getErrorMessage } from '../api/request'
import { clearCurrentUser, getCurrentUser } from '../utils/auth'
import type {
  LoginUser,
  MyCourse,
  NavigationMenuItem,
  TeachingClass,
} from '../types'

// 获取路由对象。
// 退出登录时，需要通过 router.push('/login') 跳回登录页。
const router = useRouter()

// currentUser 保存当前登录用户。
const currentUser = ref<LoginUser | null>(getCurrentUser())

// studentNo 是当前登录学生的学号。
// 登录接口返回的 related_no 对应 students.student_no。
const studentNo = computed(() => currentUser.value?.related_no ?? '')

// studentMenuItems 是学生端左侧菜单。
// implemented=true 的“选课”已经实现。
// 其他菜单先显示在 UI 中，具体功能留给后续扩展。
const studentMenuItems: NavigationMenuItem[] = [
  {
    key: 'courseSelect',
    label: '选课',
    description: '查询可选教学班，并完成学生选课操作。',
    implemented: true,
  },
  {
    key: 'scheduleQuery',
    label: '学生课表查询',
    description: '查询当前学生已经选择的课程和上课时间。',
    implemented: false,
  },
  {
    key: 'gradeQuery',
    label: '学生成绩查询',
    description: '查询当前学生已经录入的课程成绩。',
    implemented: false,
  },
  {
    key: 'classQuery',
    label: '班级信息查询',
    description: '查询班级、教学班、任课教师等信息。',
    implemented: false,
  },
  {
    key: 'examQuery',
    label: '考试安排查询',
    description: '查询课程考试时间、地点和考试状态。',
    implemented: false,
  },
  {
    key: 'profileQuery',
    label: '个人信息查询',
    description: '查询学生个人基本信息，原则上学生只能查看不能修改。',
    implemented: false,
  },
]

// activeMenuKey 表示当前选中的学生端菜单。
// 默认进入“选课”，因为这是本 Demo 已经实现的功能。
const activeMenuKey = ref('courseSelect')

// activeMenuItem 根据 activeMenuKey 找到当前菜单对象。
const activeMenuItem = computed(() => {
  return studentMenuItems.find((item) => item.key === activeMenuKey.value)
})

// pageTitle 是右侧顶部标题。
const pageTitle = computed(() => {
  return activeMenuItem.value?.label ?? '学生查询功能'
})

// pageSubtitle 是右侧顶部说明。
const pageSubtitle = computed(() => {
  return activeMenuItem.value?.description ?? '请选择左侧查询模块'
})

// placeholderTasks 保存每个待实现模块的建议任务。
const placeholderTasks: Record<string, string[]> = {
  scheduleQuery: [
    '可以复用后端 GET /api/student/my-courses 接口。',
    '按星期和节次重新组织数据，做成课表网格。',
    '可以增加学期筛选条件，例如 2026春、2026秋。',
  ],
  gradeQuery: [
    '查询 enrollments 表中 grade 不为空的记录。',
    '使用 JOIN 连接 courses 表，显示课程名、学分和成绩。',
    '可以增加平均分、总学分等统计信息。',
  ],
  classQuery: [
    '查询 teaching_classes 表中的教学班信息。',
    '使用 JOIN 连接 courses 表，显示课程名、教师、容量。',
    '学生端只做查询，不提供修改按钮。',
  ],
  examQuery: [
    '可以新增 exam_arrangements 表保存考试时间和地点。',
    '按学生已选课程过滤考试安排。',
    '前端用表格展示考试课程、日期、教室。',
  ],
  profileQuery: [
    '根据当前 student_no 查询 students 表。',
    '学生端只显示个人信息，不提供修改入口。',
    '如果要修改个人信息，应由管理员端审核处理。',
  ],
}

// keyword 保存课程查询关键字。
const keyword = ref('')

// semester 保存学期筛选条件。
const semester = ref('')

// teachingClasses 保存可选教学班列表。
const teachingClasses = ref<TeachingClass[]>([])

// myCourses 保存当前学生已经选择的课程。
const myCourses = ref<MyCourse[]>([])

// loadingClasses 表示可选课程表格是否正在加载。
const loadingClasses = ref(false)

// loadingMyCourses 表示已选课程预览表格是否正在加载。
const loadingMyCourses = ref(false)

// selectingClassId 保存当前正在提交选课请求的教学班 id。
// 用它可以让对应行的“选课”按钮显示 loading。
const selectingClassId = ref<number | null>(null)

// semesterOptions 是学期下拉框选项。
const semesterOptions = [
  { label: '全部学期', value: '' },
  { label: '2026春', value: '2026春' },
  { label: '2026秋', value: '2026秋' },
]

// handleMenuSelect 在点击左侧菜单时执行。
function handleMenuSelect(key: string): void {
  activeMenuKey.value = key
}

// loadTeachingClasses 查询可选教学班。
async function loadTeachingClasses(): Promise<void> {
  if (!studentNo.value) {
    ElMessage.error('当前登录用户没有关联学号')
    return
  }

  loadingClasses.value = true

  try {
    // 请求后端：
    // GET /api/student/classes?student_no=S001&keyword=...&semester=...
    teachingClasses.value = await listTeachingClassesApi(
      studentNo.value,
      keyword.value.trim(),
      semester.value,
    )
  } catch (error) {
    ElMessage.error(getErrorMessage(error))
  } finally {
    loadingClasses.value = false
  }
}

// loadMyCourses 查询当前学生已经选择的课程。
async function loadMyCourses(): Promise<void> {
  if (!studentNo.value) {
    return
  }

  loadingMyCourses.value = true

  try {
    // 请求后端：
    // GET /api/student/my-courses?student_no=S001
    myCourses.value = await listMyCoursesApi(studentNo.value)
  } catch (error) {
    ElMessage.error(getErrorMessage(error))
  } finally {
    loadingMyCourses.value = false
  }
}

// loadAll 同时刷新可选课程和已选课程。
async function loadAll(): Promise<void> {
  await Promise.all([loadTeachingClasses(), loadMyCourses()])
}

// resetSearch 清空查询条件并重新加载可选课程。
function resetSearch(): void {
  keyword.value = ''
  semester.value = ''
  loadTeachingClasses()
}

// isFull 判断教学班是否已满。
function isFull(row: TeachingClass): boolean {
  return row.selected_count >= row.capacity
}

// canSelect 判断当前教学班是否可以点击“选课”。
function canSelect(row: TeachingClass): boolean {
  return row.is_selected === 0 && !isFull(row)
}

// getSelectButtonText 根据状态显示不同按钮文字。
function getSelectButtonText(row: TeachingClass): string {
  if (row.is_selected === 1) {
    return '已选'
  }

  if (isFull(row)) {
    return '已满'
  }

  return '选课'
}

// selectClass 执行选课操作。
async function selectClass(row: TeachingClass): Promise<void> {
  if (!studentNo.value) {
    ElMessage.error('当前登录用户没有关联学号')
    return
  }

  if (!canSelect(row)) {
    return
  }

  selectingClassId.value = row.class_id

  try {
    // 请求后端事务接口：
    // POST /api/student/select/{class_id}
    const result = await selectCourseApi(row.class_id, studentNo.value)

    ElMessage.success(result.message)

    // 选课成功后刷新两个表：
    // 1. 可选课程表中的 selected_count 会变化。
    // 2. 已选课程预览会增加一条记录。
    await loadAll()
  } catch (error) {
    ElMessage.error(getErrorMessage(error))
  } finally {
    selectingClassId.value = null
  }
}

// handleLogout 退出登录。
function handleLogout(): void {
  clearCurrentUser()
  router.push('/login')
}

// 页面打开后自动加载课程数据。
onMounted(() => {
  loadAll()
})
</script>

<template>
  <AppLayout
    :active-key="activeMenuKey"
    menu-title="查询功能"
    :menu-items="studentMenuItems"
    :subtitle="pageSubtitle"
    :title="pageTitle"
    :user="currentUser"
    @logout="handleLogout"
    @select="handleMenuSelect"
  >
    <section v-if="activeMenuKey === 'courseSelect'">
      <section class="student-summary">
        <div>
          <span class="summary-label">当前学生</span>
          <strong>{{ currentUser?.display_name }}</strong>
        </div>
        <div>
          <span class="summary-label">学号</span>
          <strong>{{ studentNo }}</strong>
        </div>
        <div>
          <span class="summary-label">已选课程</span>
          <strong>{{ myCourses.length }}</strong>
        </div>
      </section>

      <section class="content-card">
        <div class="section-heading">
          <h2>可选课程</h2>
          <p>学生在选课阶段可以修改自己的选课记录，其他信息仅提供查询入口。</p>
        </div>

        <section class="toolbar">
          <el-input
            v-model="keyword"
            class="search-input"
            clearable
            placeholder="按课程号或课程名查询"
            @keyup.enter="loadTeachingClasses"
          >
            <template #prefix>
              <el-icon><Search /></el-icon>
            </template>
          </el-input>

          <el-select v-model="semester" class="semester-select">
            <el-option
              v-for="item in semesterOptions"
              :key="item.value"
              :label="item.label"
              :value="item.value"
            />
          </el-select>

          <div class="toolbar-actions">
            <el-button :icon="Search" type="primary" @click="loadTeachingClasses">
              查询
            </el-button>
            <el-button :icon="Refresh" @click="resetSearch">
              重置
            </el-button>
          </div>
        </section>

        <section class="table-section">
          <el-table
            v-loading="loadingClasses"
            border
            :data="teachingClasses"
            empty-text="暂无可选课程"
            stripe
          >
            <el-table-column label="课程" min-width="170">
              <template #default="{ row }">
                <div class="course-name">{{ row.course_name }}</div>
                <div class="muted-text">{{ row.course_no }} / {{ row.credit }} 学分</div>
              </template>
            </el-table-column>
            <el-table-column label="教师" min-width="100" prop="teacher_name" />
            <el-table-column label="学期" min-width="90" prop="semester" />
            <el-table-column label="班级" min-width="90" prop="class_name" />
            <el-table-column label="时间地点" min-width="180">
              <template #default="{ row }">
                <div>{{ row.class_time }}</div>
                <div class="muted-text">{{ row.classroom }}</div>
              </template>
            </el-table-column>
            <el-table-column label="容量" min-width="110">
              <template #default="{ row }">
                {{ row.selected_count }} / {{ row.capacity }}
              </template>
            </el-table-column>
            <el-table-column label="状态" min-width="90">
              <template #default="{ row }">
                <el-tag v-if="row.is_selected === 1" type="success">已选</el-tag>
                <el-tag v-else-if="isFull(row)" type="danger">已满</el-tag>
                <el-tag v-else type="info">可选</el-tag>
              </template>
            </el-table-column>
            <el-table-column fixed="right" label="操作" min-width="110">
              <template #default="{ row }">
                <el-button
                  :disabled="!canSelect(row)"
                  :icon="Check"
                  :loading="selectingClassId === row.class_id"
                  type="primary"
                  @click="selectClass(row)"
                >
                  {{ getSelectButtonText(row) }}
                </el-button>
              </template>
            </el-table-column>
          </el-table>
        </section>
      </section>

      <section class="content-card">
        <div class="section-heading">
          <h2>已选课程预览</h2>
          <p>这里复用已实现接口展示选课结果，完整课表查询可留给学生扩展。</p>
        </div>

        <section class="table-section">
          <el-table
            v-loading="loadingMyCourses"
            border
            :data="myCourses"
            empty-text="暂无已选课程"
            stripe
          >
            <el-table-column label="课程" min-width="180">
              <template #default="{ row }">
                <div class="course-name">{{ row.course_name }}</div>
                <div class="muted-text">{{ row.course_no }} / {{ row.credit }} 学分</div>
              </template>
            </el-table-column>
            <el-table-column label="教师" min-width="100" prop="teacher_name" />
            <el-table-column label="学期" min-width="90" prop="semester" />
            <el-table-column label="班级" min-width="90" prop="class_name" />
            <el-table-column label="时间地点" min-width="180">
              <template #default="{ row }">
                <div>{{ row.class_time }}</div>
                <div class="muted-text">{{ row.classroom }}</div>
              </template>
            </el-table-column>
            <el-table-column label="成绩" min-width="90">
              <template #default="{ row }">
                <el-tag v-if="row.grade === null" type="info">未录入</el-tag>
                <span v-else>{{ row.grade }}</span>
              </template>
            </el-table-column>
          </el-table>
        </section>
      </section>
    </section>

    <ModulePlaceholder
      v-else
      :description="pageSubtitle"
      :tasks="placeholderTasks[activeMenuKey] ?? ['仿照选课模块补充查询接口和页面。']"
      :title="pageTitle"
    />
  </AppLayout>
</template>
