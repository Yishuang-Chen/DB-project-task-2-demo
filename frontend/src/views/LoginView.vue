<script setup lang="ts">
/*
 * LoginView.vue
 *
 * 这是登录页面。
 *
 * 本页面演示的完整流程：
 * 1. 用户在表单中输入账号和密码。
 * 2. 点击“登录”按钮。
 * 3. 前端调用 loginApi，也就是请求后端 POST /api/login。
 * 4. 后端查询 MySQL users 表。
 * 5. 后端返回用户角色 role。
 * 6. 前端根据 role 跳转到不同页面。
 */

import { reactive, ref } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import { Lock, Right, User } from '@element-plus/icons-vue'
import { loginApi } from '../api/teaching'
import { getErrorMessage } from '../api/request'
import { getHomePath, saveUser } from '../utils/auth'
import type { LoginRequest } from '../types'

// useRouter 用来获取路由对象。
// 后面登录成功后，需要调用 router.push(...) 跳转页面。
const router = useRouter()

// form 保存登录表单中的数据。
// reactive 会让这个对象变成响应式对象：
// 当输入框内容变化时，form.username 和 form.password 会自动更新。
const form = reactive<LoginRequest>({
  username: 'admin',
  password: '123456',
})

// loading 表示当前是否正在登录。
// ref(false) 表示创建一个响应式布尔值，初始值为 false。
const loading = ref(false)

// loginBrandImagePath 是登录页上方学校图片的路径。
//
// 后续如果你想在登录框上方显示校徽、校名或学校横版 logo，
// 只需要把图片放到：
//
//   frontend/public/school-login-logo.png
//
// Vite 会把 public 目录中的文件原样暴露到网站根路径，
// 所以前端代码中可以直接使用 /school-login-logo.png 访问它。
const loginBrandImagePath = '/school-login-logo.png'

// demoAccounts 是演示账号列表。
// 点击页面上的演示账号，可以快速填入用户名和密码。
const demoAccounts = [
  { label: '管理员', username: 'admin', password: '123456' },
  { label: '学生张三', username: 'stu001', password: '123456' },
  { label: '学生李四', username: 'stu002', password: '123456' },
]

// fillAccount 用来把演示账号填入表单。
function fillAccount(account: LoginRequest): void {
  form.username = account.username
  form.password = account.password
}

// handleLogin 是点击“登录”按钮后执行的函数。
async function handleLogin(): Promise<void> {
  // trim() 用来去掉字符串前后的空格。
  // 如果用户名或密码为空，就直接提示，不请求后端。
  if (!form.username.trim() || !form.password.trim()) {
    ElMessage.warning('请输入用户名和密码')
    return
  }

  // 开始请求前，把 loading 改成 true。
  // 页面上的按钮会显示加载状态，避免用户重复点击。
  loading.value = true

  try {
    // 调用登录接口。
    // await 表示等待后端返回结果后，再继续执行下一行。
    const user = await loginApi({
      username: form.username.trim(),
      password: form.password,
    })

    // 本 Demo 主要实现管理员端和学生端。
    // 教师端账号保留在数据库中，作为本科生后续扩展任务。
    if (user.role === 'teacher') {
      ElMessage.warning('教师端页面留作扩展任务，本 Demo 先演示管理员端和学生端')
      return
    }

    // 保存登录用户到 localStorage。
    // 这样刷新页面后，路由守卫仍然知道当前用户是谁。
    saveUser(user)

    // 根据角色计算跳转路径。
    // admin -> /admin/courses
    // student -> /student/classes
    const homePath = getHomePath(user)

    // 跳转页面。
    await router.push(homePath)

    ElMessage.success(`欢迎，${user.display_name}`)
  } catch (error) {
    // 如果后端返回 401 或其他错误，这里会显示具体错误原因。
    ElMessage.error(getErrorMessage(error))
  } finally {
    // 无论登录成功还是失败，请求结束后都关闭加载状态。
    loading.value = false
  }
}
</script>

<template>
  <main class="login-page">
    <!--
      登录框上方的学校标识区域。

      后续只需要把图片放到：
      frontend/public/school-login-logo.png
    -->
    <section class="login-school-brand" aria-label="学校标识">
      <img
        :src="loginBrandImagePath"
        alt="学校校徽或校名"
        class="login-school-image"
      />
    </section>

    <section class="login-panel">
      <div class="brand-block">
        <div class="brand-mark">DB</div>
        <div>
          <h1>高校教学管理系统 Demo</h1>
          <p>Vue3 + FastAPI + MySQL</p>
        </div>
      </div>

      <!-- el-form 是 Element Plus 提供的表单组件。 -->
      <el-form class="login-form" label-position="top" @keyup.enter="handleLogin">
        <el-form-item label="用户名">
          <!--
            v-model 表示双向绑定。
            输入框变化时，form.username 会更新；
            form.username 改变时，输入框也会更新。
          -->
          <el-input
            v-model="form.username"
            :prefix-icon="User"
            clearable
            placeholder="例如：admin"
          />
        </el-form-item>

        <el-form-item label="密码">
          <el-input
            v-model="form.password"
            :prefix-icon="Lock"
            clearable
            placeholder="示例密码：123456"
            show-password
            type="password"
          />
        </el-form-item>

        <el-button
          class="login-button"
          :icon="Right"
          :loading="loading"
          type="primary"
          @click="handleLogin"
        >
          登录
        </el-button>
      </el-form>

      <div class="demo-account-list">
        <span>演示账号</span>
        <button
          v-for="account in demoAccounts"
          :key="account.username"
          class="demo-account"
          type="button"
          @click="fillAccount(account)"
        >
          {{ account.label }}
        </button>
      </div>
    </section>
  </main>
</template>
