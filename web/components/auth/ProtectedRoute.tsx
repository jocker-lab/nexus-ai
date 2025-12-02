'use client'

import { useEffect, useRef, useCallback } from 'react'
import { useRouter } from 'next/navigation'
import { useAuthStore } from '@/lib/stores/auth'
import { checkAuth } from '@/lib/auth/api'

interface ProtectedRouteProps {
  children: React.ReactNode
  requiredPermissions?: string[]
  requireAll?: boolean // true: 需要所有权限, false: 满足任一即可
  fallbackUrl?: string
}

export function ProtectedRoute({
  children,
  requiredPermissions = [],
  requireAll = true,
  fallbackUrl = '/login',
}: ProtectedRouteProps) {
  const router = useRouter()
  // 只订阅状态值，不订阅函数（函数引用会导致无限循环）
  const isAuthenticated = useAuthStore((state) => state.isAuthenticated)
  const isLoading = useAuthStore((state) => state.isLoading)
  const user = useAuthStore((state) => state.user)

  // 使用 ref 防止重复调用
  const isCheckingRef = useRef(false)
  const hasCheckedRef = useRef(false)

  // 权限检查函数 - 直接从 store 获取，不作为依赖
  const checkPermissions = useCallback((permissions: string[]) => {
    const { hasAllPermissions, hasAnyPermission } = useAuthStore.getState()
    return requireAll
      ? hasAllPermissions(permissions)
      : hasAnyPermission(permissions)
  }, [requireAll])

  useEffect(() => {
    // 如果已经检查过且已认证，不再重复检查
    if (hasCheckedRef.current && isAuthenticated) {
      return
    }

    // 防止并发调用
    if (isCheckingRef.current) {
      return
    }

    const verifyAuth = async () => {
      isCheckingRef.current = true

      try {
        // 检查认证状态
        const authenticated = await checkAuth()
        hasCheckedRef.current = true

        if (!authenticated) {
          router.push(fallbackUrl)
          return
        }

        // 如果有权限要求，检查权限
        if (requiredPermissions.length > 0) {
          const hasPermission = checkPermissions(requiredPermissions)

          if (!hasPermission) {
            router.push('/unauthorized')
          }
        }
      } finally {
        isCheckingRef.current = false
      }
    }

    verifyAuth()
  }, [router, fallbackUrl, requiredPermissions, requireAll, checkPermissions, isAuthenticated])

  // 显示加载状态
  if (isLoading) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <div className="flex flex-col items-center gap-4">
          <div
            className="w-12 h-12 rounded-full border-2 border-t-transparent animate-spin"
            style={{ borderColor: 'var(--nexus-cyan)', borderTopColor: 'transparent' }}
          />
          <p className="text-[var(--text-secondary)]">加载中...</p>
        </div>
      </div>
    )
  }

  // 未认证时不显示内容（等待重定向）
  if (!isAuthenticated) {
    return null
  }

  // 检查权限
  if (requiredPermissions.length > 0) {
    const hasPermission = checkPermissions(requiredPermissions)

    if (!hasPermission) {
      return null // 等待重定向
    }
  }

  return <>{children}</>
}

export default ProtectedRoute
