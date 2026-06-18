<script setup lang="ts">
/*
 * AppLayout.vue
 *
 * 这是登录后页面共用的布局组件。
 *
 * 本次修改把原来的“顶部栏布局”改成更接近真实教务系统的“左侧导航 + 右侧内容”布局：
 *
 * 左侧：
 * 1. 左上角显示学校校徽。
 * 2. 校徽下方显示系统名称。
 * 3. 左侧下方纵向排列功能菜单。
 *
 * 右侧：
 * 1. 顶部显示当前模块标题、说明、当前登录用户、退出按钮。
 * 2. 下方显示具体页面内容。
 *
 * 为什么要做成组件？
 * 管理员页面和学生页面都需要类似的整体布局。
 * 抽成 AppLayout 后，管理员和学生页面只需要传入不同的菜单即可。
 */

import { SwitchButton } from '@element-plus/icons-vue'
import type { LoginUser, NavigationMenuItem } from '../types'

// defineProps 用来声明父组件传进来的数据。
// 管理员页和学生页都会使用 AppLayout，但传入的标题、菜单、用户不同。
defineProps<{
  title: string
  subtitle: string
  user: LoginUser | null
  menuTitle: string
  menuItems: NavigationMenuItem[]
  activeKey: string
}>()

// defineEmits 用来声明本组件会向父组件发出的事件。
// select：点击左侧菜单时触发。
// logout：点击退出登录按钮时触发。
const emit = defineEmits<{
  select: [key: string]
  logout: []
}>()

// schoolLogoPath 是校徽图片路径。
//
// 使用 public 目录的好处：
// 1. 以后你只需要把图片命名为 school-logo.png。
// 2. 然后放到 frontend/public/school-logo.png。
// 3. 不需要修改 Vue 代码，浏览器会自动从 /school-logo.png 加载。
const schoolLogoPath = '/school-logo.png'

// handleSelect 在点击菜单项时执行。
// 它不直接修改 activeKey，因为 activeKey 是父组件传进来的。
// 子组件通过 emit 通知父组件：“用户点了某个菜单”。
function handleSelect(key: string): void {
  emit('select', key)
}
</script>

<template>
  <div class="layout-shell">
    <aside class="layout-sidebar">
      <div class="sidebar-brand">
        <!-- 左上角显示 public/school-logo.png 中的学校校徽。 -->
        <img
          :src="schoolLogoPath"
          alt="学校校徽"
          class="school-logo"
        />

        <div class="brand-text">
          <strong>高校教学管理系统</strong>
          <span>Database Course Demo</span>
        </div>
      </div>

      <nav class="sidebar-menu" aria-label="系统功能菜单">
        <div class="sidebar-menu-title">{{ menuTitle }}</div>

        <!--
          v-for 用来循环渲染菜单数组。
          menuItems 中有几项，这里就生成几个菜单按钮。
        -->
        <button
          v-for="item in menuItems"
          :key="item.key"
          class="sidebar-menu-item"
          :class="{ active: item.key === activeKey }"
          type="button"
          @click="handleSelect(item.key)"
        >
          <span>{{ item.label }}</span>

          <!-- implemented=false 的模块显示“待实现”，告诉学生这是后续扩展。 -->
          <small v-if="!item.implemented">待实现</small>
        </button>
      </nav>
    </aside>

    <section class="layout-main">
      <header class="layout-topbar">
        <div>
          <h1>{{ title }}</h1>
          <p>{{ subtitle }}</p>
        </div>

        <div class="topbar-user">
          <div class="user-info">
            <span class="user-name">{{ user?.display_name }}</span>
            <span class="user-role">{{ user?.role }}</span>
          </div>

          <el-button :icon="SwitchButton" plain @click="emit('logout')">
            退出登录
          </el-button>
        </div>
      </header>

      <main class="layout-content">
        <!--
          slot 表示“插槽”。
          AppLayout 只负责外层布局，具体内容由父页面传进来。
          管理员页会把课程管理表格放到这里。
          学生页会把选课表格放到这里。
        -->
        <slot />
      </main>
    </section>
  </div>
</template>
