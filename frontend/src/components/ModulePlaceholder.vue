<script setup lang="ts">
/*
 * ModulePlaceholder.vue
 *
 * 这是“暂未实现模块”的占位组件。
 *
 * 你的目标是做一个教学 Demo，不是完整实现所有功能。
 * 因此左侧菜单中可以列出真实系统中常见的功能，
 * 但只有 1-2 个典型功能真正写完整代码，其余功能用占位组件说明后续任务。
 *
 * 这样做有两个好处：
 * 1. UI 看起来接近现实系统，满足加分项 2 的展示需要。
 * 2. 本科生可以清楚知道哪些模块留给他们模仿实现。
 */

// defineProps 声明父组件传入的占位模块信息。
defineProps<{
  title: string
  description: string
  tasks: string[]
}>()
</script>

<template>
  <section class="placeholder-panel">
    <div class="placeholder-heading">
      <span class="placeholder-badge">扩展任务</span>
      <h2>{{ title }}</h2>
      <p>{{ description }}</p>
    </div>

    <div class="placeholder-task-list">
      <div v-for="task in tasks" :key="task" class="placeholder-task">
        {{ task }}
      </div>
    </div>
  </section>
</template>
