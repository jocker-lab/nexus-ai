/**
 * 应用配置
 *
 * 使用 Next.js rewrites 代理 API 请求，前端统一使用相对路径
 * 后端地址在 next.config.ts 中配置
 */

// API 基础 URL：使用空字符串（相对路径）
// Next.js rewrites 会自动将 /api/v1/* 请求代理到后端
export const API_BASE_URL = ''

// API 端点（相对路径）
export const API_ENDPOINTS = {
  // 认证相关
  auth: '/api/v1/auth',

  // 用户管理
  users: '/api/v1/users',
  groups: '/api/v1/groups',
  roles: '/api/v1/roles',

  // Chat 相关
  chats: '/api/v1/chats',
  chatStream: '/api/v1/chats/stream',

  // Documents 相关 (原 Reports)
  documents: '/api/v1/documents',
  // 兼容性别名
  reports: '/api/v1/documents',

  // Model Providers 相关
  modelProviders: '/api/v1/model-providers',

  // Writing Templates 相关
  writingTemplates: '/api/v1/writing-templates',
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
