'use client'

import { useEffect, useState } from 'react'
import { checkAuth } from '@/lib/auth/api'

interface AuthProviderProps {
  children: React.ReactNode
}

/**
 * AuthProvider - 认证状态提供者
 *
 * 在应用启动时检查并恢复认证状态。
 * 应该包裹在应用的最外层。
 */
export function AuthProvider({ children }: AuthProviderProps) {
  const [isInitialized, setIsInitialized] = useState(false)

  useEffect(() => {
    let isMounted = true

    const initAuth = async () => {
      try {
        // 尝试恢复认证状态
        await checkAuth()
      } catch (error) {
        console.error('Auth initialization failed:', error)
      } finally {
        if (isMounted) {
          setIsInitialized(true)
        }
      }
    }

    initAuth()

    return () => {
      isMounted = false
    }
  }, []) // 空依赖数组，只在挂载时运行一次

  // 等待初始化完成
  if (!isInitialized) {
    return (
      <div className="min-h-screen flex items-center justify-center" style={{ background: 'var(--nexus-void)' }}>
        <div className="flex flex-col items-center gap-4">
          {/* Logo */}
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

          {/* Loading Spinner */}
          <div
            className="w-8 h-8 rounded-full border-2 border-t-transparent animate-spin"
            style={{ borderColor: 'var(--nexus-cyan)', borderTopColor: 'transparent' }}
          />

          <p className="text-[var(--text-secondary)] text-sm">初始化中...</p>
        </div>
      </div>
    )
  }

  return <>{children}</>
}

export default AuthProvider
