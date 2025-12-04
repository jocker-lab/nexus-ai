'use client'

import { useAuthStore } from '@/lib/stores/auth'
import { API_ENDPOINTS } from '@/lib/config'

/**
 * 带认证的 fetch 函数
 * 自动添加 Authorization header，处理 token 刷新
 */
export async function authFetch<T = any>(
  url: string,
  options: RequestInit = {}
): Promise<T> {
  const { accessToken, refreshToken, setTokens, clearAuth } = useAuthStore.getState()

  // 添加认证头
  const headers: HeadersInit = {
    ...options.headers,
  }

  if (accessToken) {
    ;(headers as Record<string, string>)['Authorization'] = `Bearer ${accessToken}`
  }

  // 如果没有设置 Content-Type 且有 body，默认使用 JSON
  if (options.body && !(headers as Record<string, string>)['Content-Type']) {
    ;(headers as Record<string, string>)['Content-Type'] = 'application/json'
  }

  let response = await fetch(url, {
    ...options,
    headers,
  })

  // 如果 401 且有 refresh token，尝试刷新
  if (response.status === 401 && refreshToken) {
    try {
      const refreshResponse = await fetch(`${API_ENDPOINTS.auth}/refresh`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ refresh_token: refreshToken }),
      })

      if (refreshResponse.ok) {
        const data = await refreshResponse.json()
        setTokens(data.access_token, data.refresh_token)

        // 使用新 token 重试请求
        ;(headers as Record<string, string>)['Authorization'] = `Bearer ${data.access_token}`
        response = await fetch(url, {
          ...options,
          headers,
        })
      } else {
        // 刷新失败，清除认证状态
        clearAuth()
        throw new Error('认证已过期，请重新登录')
      }
    } catch (error) {
      clearAuth()
      throw new Error('认证已过期，请重新登录')
    }
  }

  if (!response.ok) {
    const errorData = await response.json().catch(() => ({}))
    throw new Error(errorData.detail || `请求失败: ${response.status}`)
  }

  // 处理空响应
  const text = await response.text()
  if (!text) {
    return {} as T
  }

  return JSON.parse(text)
}

/**
 * 获取当前用户 ID
 */
export function getCurrentUserId(): string | null {
  const { user } = useAuthStore.getState()
  return user?.id || null
}

/**
 * 获取 access token
 */
export function getAccessToken(): string | null {
  const { accessToken } = useAuthStore.getState()
  return accessToken
}

/**
 * 创建带认证的请求头
 */
export function createAuthHeaders(): HeadersInit {
  const accessToken = getAccessToken()
  const headers: HeadersInit = {
    'Content-Type': 'application/json',
  }

  if (accessToken) {
    ;(headers as Record<string, string>)['Authorization'] = `Bearer ${accessToken}`
  }

  return headers
}
