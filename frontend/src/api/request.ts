/*
 * request.ts
 *
 * 这个文件只负责一件事：封装 axios 请求。
 *
 * axios 是前端常用的 HTTP 请求库。
 * Vue 页面不能直接访问 MySQL，它只能向 Python 后端发送 HTTP 请求。
 *
 * 请求路径示例：
 *   前端页面 -> http://127.0.0.1:8000/api/login -> FastAPI 后端 -> MySQL
 */

import axios from 'axios'

// 创建一个 axios 实例。
// 这样后面所有请求都会自动带上相同的后端基础地址。
const apiClient = axios.create({
  // baseURL 是后端接口的公共前缀。
  // 后端 main.py 中接口都以 /api 开头，例如 /api/login。
  baseURL: 'http://127.0.0.1:8000/api',

  // timeout 表示请求最多等待 10 秒。
  // 如果后端没有启动或网络异常，超过 10 秒就报错。
  timeout: 10000,
})

// apiGet 用来发送 GET 请求。
// T 是泛型，表示“这个接口返回的数据类型”。
export async function apiGet<T>(url: string, params?: object): Promise<T> {
  // axios.get 返回的是完整响应对象，真正的数据在 response.data 中。
  const response = await apiClient.get<T>(url, { params })

  // 只把 data 返回给页面，页面就不用每次都写 response.data。
  return response.data
}

// apiPost 用来发送 POST 请求。
// body 是要发送给后端的 JSON 数据。
export async function apiPost<T>(url: string, body?: object): Promise<T> {
  const response = await apiClient.post<T>(url, body)
  return response.data
}

// apiPut 用来发送 PUT 请求，通常用于修改数据。
export async function apiPut<T>(url: string, body?: object): Promise<T> {
  const response = await apiClient.put<T>(url, body)
  return response.data
}

// apiDelete 用来发送 DELETE 请求，通常用于删除数据。
export async function apiDelete<T>(url: string): Promise<T> {
  const response = await apiClient.delete<T>(url)
  return response.data
}

// getErrorMessage 用来从异常对象中提取适合显示给用户的错误信息。
// 后端抛出 HTTPException 时，FastAPI 通常会返回 { detail: "错误信息" }。
export function getErrorMessage(error: unknown): string {
  // axios.isAxiosError 可以判断这个错误是不是 axios 请求产生的。
  if (axios.isAxiosError(error)) {
    // response?.data 表示：
    // 如果 response 存在，就取 response.data；
    // 如果 response 不存在，就返回 undefined，避免程序报错。
    const data = error.response?.data as { detail?: string } | undefined

    // 如果后端返回了 detail，就优先显示后端给出的错误原因。
    if (data?.detail) {
      return data.detail
    }

    // 如果没有 detail，就显示 axios 自己的错误信息。
    return error.message
  }

  // 如果是普通 Error 对象，就显示它的 message。
  if (error instanceof Error) {
    return error.message
  }

  // 如果错误类型无法识别，就显示一个通用提示。
  return '请求失败，请检查后端服务是否已启动'
}
