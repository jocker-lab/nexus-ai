/**
 * 应用配置
 * 从环境变量读取，支持动态配置后端地址
 */

// 判断是否在服务端运行
const isServer = typeof window === 'undefined'

// 后端 API 基础 URL
// - 浏览器端：使用相对路径（空字符串），由 Nginx 反向代理转发到后端
// - 服务端：使用完整地址（API Route 代理需要）
export const API_BASE_URL = isServer
  ? (process.env.API_SERVER_URL || 'http://127.0.0.1:8080')
  : ''

// API 路径
// 注意：不带尾部斜杠，因为会被继续拼接子路径（如 auth + /login）
export const API_ENDPOINTS = {
  // 认证相关
  auth: `${API_BASE_URL}/api/v1/auth`,

  // 用户管理
  users: `${API_BASE_URL}/api/v1/users`,
  groups: `${API_BASE_URL}/api/v1/groups`,
  roles: `${API_BASE_URL}/api/v1/roles`,

  // Chat 相关
  chats: `${API_BASE_URL}/api/v1/chats`,
  chatStream: `${API_BASE_URL}/api/v1/chats/stream`,

  // Documents 相关 (原 Reports)
  documents: `${API_BASE_URL}/api/v1/documents`,
  // 兼容性别名
  reports: `${API_BASE_URL}/api/v1/documents`,

  // Model Providers 相关
  modelProviders: `${API_BASE_URL}/api/v1/model-providers`,
} as const

// 构建带查询参数的 URL
export function buildUrl(baseUrl: string, params?: Record<string, string | number | boolean | undefined>): string {
  if (!params) return baseUrl

  const searchParams = new URLSearchParams()
  Object.entries(params).forEach(([key, value]) => {
    if (value !== undefined) {
      searchParams.append(key, String(value))
    }
  })

  const queryString = searchParams.toString()
  return queryString ? `${baseUrl}?${queryString}` : baseUrl
}
