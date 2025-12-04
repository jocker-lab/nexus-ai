/**
 * 应用配置
 * 从环境变量读取，支持动态配置后端地址
 */

// 后端 API 基础 URL
export const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8080'

// API 路径
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
