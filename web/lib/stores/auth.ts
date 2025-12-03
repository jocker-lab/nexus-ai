'use client'

import { create } from 'zustand'
import { persist, createJSONStorage } from 'zustand/middleware'

// 用户类型定义
export interface User {
  id: string
  name: string
  email: string
  role: string
  profile_image_url?: string
  is_superadmin?: boolean
  permissions?: string[]
  groups?: { id: string; name: string }[]
}

// 认证状态类型
interface AuthState {
  // 状态
  user: User | null
  accessToken: string | null
  refreshToken: string | null
  isAuthenticated: boolean
  isLoading: boolean

  // Actions
  setAuth: (user: User, accessToken: string, refreshToken: string) => void
  clearAuth: () => void
  setLoading: (loading: boolean) => void
  updateUser: (user: Partial<User>) => void
  setTokens: (accessToken: string, refreshToken: string) => void

  // 权限检查
  hasPermission: (permission: string) => boolean
  hasAnyPermission: (permissions: string[]) => boolean
  hasAllPermissions: (permissions: string[]) => boolean
}

export const useAuthStore = create<AuthState>()(
  persist(
    (set, get) => ({
      // 初始状态
      user: null,
      accessToken: null,
      refreshToken: null,
      isAuthenticated: false,
      isLoading: false, // 初始为 false，让 checkAuth 控制

      // 设置认证信息
      setAuth: (user, accessToken, refreshToken) => {
        set({
          user,
          accessToken,
          refreshToken,
          isAuthenticated: true,
          isLoading: false,
        })
      },

      // 清除认证信息
      clearAuth: () => {
        set({
          user: null,
          accessToken: null,
          refreshToken: null,
          isAuthenticated: false,
          isLoading: false,
        })
      },

      // 设置加载状态
      setLoading: (loading) => set({ isLoading: loading }),

      // 更新用户信息
      updateUser: (userData) => {
        const currentUser = get().user
        if (currentUser) {
          set({ user: { ...currentUser, ...userData } })
        }
      },

      // 更新 Token
      setTokens: (accessToken, refreshToken) => {
        set({ accessToken, refreshToken })
      },

      // 检查单个权限
      hasPermission: (permission) => {
        const { user } = get()
        if (!user) return false
        if (user.is_superadmin) return true
        return user.permissions?.includes(permission) ?? false
      },

      // 检查是否拥有任一权限
      hasAnyPermission: (permissions) => {
        const { user } = get()
        if (!user) return false
        if (user.is_superadmin) return true
        return permissions.some((p) => user.permissions?.includes(p))
      },

      // 检查是否拥有所有权限
      hasAllPermissions: (permissions) => {
        const { user } = get()
        if (!user) return false
        if (user.is_superadmin) return true
        return permissions.every((p) => user.permissions?.includes(p))
      },
    }),
    {
      name: 'nexus-auth',
      storage: createJSONStorage(() => localStorage),
      // 只持久化这些字段
      partialize: (state) => ({
        user: state.user,
        accessToken: state.accessToken,
        refreshToken: state.refreshToken,
        isAuthenticated: state.isAuthenticated,
      }),
      // hydration 完成后的回调（可选日志）
      onRehydrateStorage: () => (state) => {
        // hydration 完成，不需要额外处理
        // isLoading 初始值已经是 false
      },
    }
  )
)

// 导出便捷 hooks
export const useUser = () => useAuthStore((state) => state.user)
export const useIsAuthenticated = () => useAuthStore((state) => state.isAuthenticated)
export const useAccessToken = () => useAuthStore((state) => state.accessToken)
