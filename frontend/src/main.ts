/*
 * main.ts
 *
 * 这是 Vue 前端项目的入口文件。
 *
 * 浏览器打开页面后，Vite 会先加载 main.ts。
 * main.ts 的主要任务是：
 * 1. 创建 Vue 应用。
 * 2. 加载全局 CSS。
 * 3. 安装 Element Plus 组件库。
 * 4. 安装 Vue Router 路由。
 * 5. 把整个 Vue 应用挂载到 index.html 中的 <div id="app"></div>。
 */

import { createApp } from 'vue'
import ElementPlus from 'element-plus'
import 'element-plus/dist/index.css'
import App from './App.vue'
import router from './router'
import './style.css'

// createApp(App) 表示用 App.vue 作为根组件创建一个 Vue 应用。
const app = createApp(App)

// app.use(ElementPlus) 表示安装 Element Plus。
// 安装后，页面中就可以使用 <el-button>、<el-table>、<el-dialog> 等组件。
app.use(ElementPlus)

// app.use(router) 表示安装路由。
// 安装后，App.vue 中的 <router-view /> 才能根据地址显示不同页面。
app.use(router)

// mount('#app') 表示把 Vue 应用渲染到 index.html 的 #app 节点中。
app.mount('#app')
