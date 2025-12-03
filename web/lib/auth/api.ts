'use client'

import { API_ENDPOINTS } from '@/lib/config'
import { useAuthStore, User } from '@/lib/stores/auth'

// ==================== 类型定义 ====================

export interface LoginCredentials {
  email: string
  password: string
}

export interface RegisterData {
  name: string
  email: string
  password: string
}

export interface AuthResponse {
  access_token: string
  refresh_token: string
  token_type: string
  expires_in: number
  user: User
}

export interface UserInfoResponse extends User {
  permissions: string[]
  groups: { id: string; name: string }[]
}

// ==================== API 函数 ====================

/**
 * 获取带认证头的 fetch 选项
 */
export function getAuthHeaders(): HeadersInit {
  const { accessToken } = useAuthStore.getState()
  return {
    'Content-Type': 'application/json',
    ...(accessToken ? { Authorization: `Bearer ${accessToken}` } : {}),
  }
}

/**
 * 认证请求封装（自动处理 Token 刷新）
 */
export async function authFetch(
  url: string,
  options: RequestInit = {}
): Promise<Response> {
  const headers = {
    ...getAuthHeaders(),
    ...(options.headers || {}),
  }

  let response = await fetch(url, { ...options, headers })

  // 如果 401，尝试刷新 Token
  if (response.status === 401) {
    const refreshed = await refreshToken()
    if (refreshed) {
      // 使用新 Token 重试
      const newHeaders = {
        ...getAuthHeaders(),
        ...(options.headers || {}),
      }
      response = await fetch(url, { ...options, headers: newHeaders })
    }
  }

  return response
}

/**
 * 用户登录
 */
export async function login(credentials: LoginCredentials): Promise<AuthResponse> {
  const response = await fetch(`${API_ENDPOINTS.auth}/login`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(credentials),
  })

  if (!response.ok) {
    const error = await response.json()
    throw new Error(error.detail || '登录失败')
  }

  const data: AuthResponse = await response.json()

  // 更新状态
  useAuthStore.getState().setAuth(
    data.user,
    data.access_token,
    data.refresh_token
  )

  return data
}

/**
 * 用户注册
 */
export async function register(data: RegisterData): Promise<AuthResponse> {
  const response = await fetch(`${API_ENDPOINTS.auth}/register`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(data),
  })

  if (!response.ok) {
    const error = await response.json()
    throw new Error(error.detail || '注册失败')
  }

  const result: AuthResponse = await response.json()

  // 更新状态
  useAuthStore.getState().setAuth(
    result.user,
    result.access_token,
    result.refresh_token
  )

  return result
}

/**
 * 刷新 Token
 */
export async function refreshToken(): Promise<boolean> {
  const { refreshToken: currentRefreshToken, clearAuth, setAuth } = useAuthStore.getState()

  if (!currentRefreshToken) {
    clearAuth()
    return false
  }

  try {
    const response = await fetch(`${API_ENDPOINTS.auth}/refresh`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ refresh_token: currentRefreshToken }),
    })

    if (!response.ok) {
      clearAuth()
      return false
    }

    const data: AuthResponse = await response.json()
    setAuth(data.user, data.access_token, data.refresh_token)
    return true
  } catch {
    clearAuth()
    return false
  }
}

/**
 * 用户登出
 */
export async function logout(): Promise<void> {
  const { accessToken, clearAuth } = useAuthStore.getState()

  try {
    if (accessToken) {
      await fetch(`${API_ENDPOINTS.auth}/logout`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          Authorization: `Bearer ${accessToken}`,
        },
      })
    }
  } catch {
    // 忽略登出错误
  } finally {
    clearAuth()
  }
}

/**
 * 获取当前用户信息
 */
export async function getCurrentUser(): Promise<UserInfoResponse | null> {
  const { accessToken, updateUser, clearAuth } = useAuthStore.getState()

  if (!accessToken) {
    return null
  }

  try {
    const response = await authFetch(`${API_ENDPOINTS.auth}/me`)

    if (!response.ok) {
      if (response.status === 401) {
        clearAuth()
      }
      return null
    }

    const data: UserInfoResponse = await response.json()
    updateUser(data)
    return data
  } catch {
    return null
  }
}

/**
 * 更新个人资料
 */
export async function updateProfile(data: {
  name?: string
  profile_image_url?: string
}): Promise<User | null> {
  const response = await authFetch(`${API_ENDPOINTS.auth}/me`, {
    method: 'PUT',
    body: JSON.stringify(data),
  })

  if (!response.ok) {
    const error = await response.json()
    throw new Error(error.detail || '更新失败')
  }

  const result: User = await response.json()
  useAuthStore.getState().updateUser(result)
  return result
}

/**
 * 修改密码
 */
export async function changePassword(data: {
  current_password: string
  new_password: string
}): Promise<void> {
  const response = await authFetch(`${API_ENDPOINTS.auth}/change-password`, {
    method: 'POST',
    body: JSON.stringify(data),
  })

  if (!response.ok) {
    const error = await response.json()
    throw new Error(error.detail || '修改密码失败')
  }

  // 修改密码后需要重新登录
  useAuthStore.getState().clearAuth()
}

/**
 * 检查认证状态并刷新用户信息
 */
export async function checkAuth(): Promise<boolean> {
  const { accessToken, refreshToken: currentRefreshToken, setLoading } = useAuthStore.getState()

  setLoading(true)

  try {
    // 如果没有 Token，直接返回
    if (!accessToken && !currentRefreshToken) {
      setLoading(false)
      return false
    }

    // 尝试获取用户信息
    const user = await getCurrentUser()
    if (user) {
      setLoading(false)
      return true
    }

    // 如果获取失败，尝试刷新 Token
    if (currentRefreshToken) {
      const refreshed = await refreshToken()
      if (refreshed) {
        setLoading(false)
        return true
      }
    }

    setLoading(false)
    return false
  } catch {
    setLoading(false)
    return false
  }
}
