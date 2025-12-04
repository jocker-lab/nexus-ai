'use client'

import { useEffect, useRef } from 'react'
import { useRouter } from 'next/navigation'
import { useAuthStore } from '@/lib/stores/auth'
import { checkAuth } from '@/lib/auth/api'

export default function ReportsLayout({
  children,
}: {
  children: React.ReactNode
}) {
  const router = useRouter()
  const isAuthenticated = useAuthStore((state) => state.isAuthenticated)
  const isLoading = useAuthStore((state) => state.isLoading)

  // 使用 ref 防止重复调用
  const isCheckingRef = useRef(false)
  const hasCheckedRef = useRef(false)

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
        const authenticated = await checkAuth()
        hasCheckedRef.current = true

        if (!authenticated) {
          router.push('/login')
        }
      } finally {
        isCheckingRef.current = false
      }
    }

    verifyAuth()
  }, [router, isAuthenticated])

  // 加载中状态
  if (isLoading) {
    return (
      <div
        className="min-h-screen flex items-center justify-center"
        style={{ background: 'var(--nexus-void)' }}
      >
        <div className="flex flex-col items-center gap-4">
          <div
            className="w-16 h-16 rounded-2xl flex items-center justify-center"
            style={{
              background: 'var(--gradient-neural)',
              boxShadow: 'var(--shadow-neural)',
            }}
          >
            <svg
              className="w-8 h-8 text-white animate-pulse"
              viewBox="0 0 24 24"
              fill="none"
              stroke="currentColor"
              strokeWidth="1.5"
            >
              <circle cx="12" cy="12" r="3" />
              <path d="M12 2v4m0 12v4M2 12h4m12 0h4" />
            </svg>
          </div>
          <div
            className="w-8 h-8 rounded-full border-2 border-t-transparent animate-spin"
            style={{ borderColor: 'var(--nexus-cyan)', borderTopColor: 'transparent' }}
          />
          <p className="text-[var(--text-secondary)] text-sm">验证登录状态...</p>
        </div>
      </div>
    )
  }

  // 未认证时显示空白（等待重定向）
  if (!isAuthenticated) {
    return (
      <div
        className="min-h-screen flex items-center justify-center"
        style={{ background: 'var(--nexus-void)' }}
      >
        <div className="flex flex-col items-center gap-4">
          <div
            className="w-8 h-8 rounded-full border-2 border-t-transparent animate-spin"
            style={{ borderColor: 'var(--nexus-cyan)', borderTopColor: 'transparent' }}
          />
          <p className="text-[var(--text-secondary)] text-sm">正在跳转到登录页...</p>
        </div>
      </div>
    )
  }

  return <>{children}</>
}
