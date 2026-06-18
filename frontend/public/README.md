# public 目录说明

`public` 目录用于存放不需要经过代码导入、但需要被浏览器直接访问的静态资源。

本项目目前使用两个图片文件。

## 1. 登录页学校标识图片

登录框上方显示学校校徽、校名或横版 logo，文件名为：

```text
public/school-login-logo.png
```

前端代码中的访问路径是：

```text
/school-login-logo.png
```

## 2. 系统左侧栏校徽图片

登录后的系统左上角显示校徽，文件名为：

```text
public/school-logo.png
```

前端代码中的访问路径是：

```text
/school-logo.png
```

代码会直接按上述路径加载图片。
