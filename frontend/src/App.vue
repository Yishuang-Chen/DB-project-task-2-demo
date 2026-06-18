<template>
  <!--
    App.vue 是整个前端应用的根组件。

    router-view 的作用：
    根据当前浏览器地址，显示对应的页面组件。

    例如：
    /login            -> LoginView.vue
    /admin/courses    -> AdminCoursesView.vue
    /student/classes  -> StudentCoursesView.vue
  -->
  <router-view />
</template>
