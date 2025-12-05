/**
 * 应用配置
 *
 * 使用 Next.js rewrites 代理 API 请求，前端统一使用相对路径
 * 后端地址在 next.config.ts 中配置
 */

// API 基础 URL：使用空字符串（相对路径）
// Next.js rewrites 会自动将 /api/v1/* 请求代理到后端
// 注意：这仅用于客户端组件，服务端 API Route 需使用 BACKEND_URL
export const API_BASE_URL = ''

// 后端服务器地址：用于 Next.js API Route（服务端）直接调用后端
// 服务端代码中使用 fetch 时必须提供完整 URL
export const BACKEND_URL = process.env.BACKEND_URL || 'http://127.0.0.1:8080'

// API 端点（相对路径，带尾部斜杠以匹配 FastAPI 路由）
export const API_ENDPOINTS = {
  // 认证相关
  auth: '/api/v1/auth',

  // 用户管理
  users: '/api/v1/users/',
  groups: '/api/v1/groups/',
  roles: '/api/v1/roles/',

  // Chat 相关
  chats: '/api/v1/chats/',
  chatStream: '/api/v1/chats/stream/',

  // Documents 相关 (原 Reports)
  documents: '/api/v1/documents/',
  // 兼容性别名
  reports: '/api/v1/documents/',

  // Model Providers 相关
  modelProviders: '/api/v1/model-providers/',

  // Writing Templates 相关
  writingTemplates: '/api/v1/writing-templates/',
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
