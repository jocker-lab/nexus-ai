'use client'

import { useEffect, useState, useRef, useCallback } from 'react'
import { useRouter, usePathname } from 'next/navigation'
import Link from 'next/link'
import { motion, AnimatePresence } from 'framer-motion'
import { useAuthStore } from '@/lib/stores/auth'
import { checkAuth, logout } from '@/lib/auth/api'

const navItems = [
  {
    name: '仪表盘',
    href: '/admin',
    icon: (
      <svg className="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M4 5a1 1 0 011-1h14a1 1 0 011 1v2a1 1 0 01-1 1H5a1 1 0 01-1-1V5zM4 13a1 1 0 011-1h6a1 1 0 011 1v6a1 1 0 01-1 1H5a1 1 0 01-1-1v-6zM16 13a1 1 0 011-1h2a1 1 0 011 1v6a1 1 0 01-1 1h-2a1 1 0 01-1-1v-6z" />
      </svg>
    ),
  },
  {
    name: '用户管理',
    href: '/admin/users',
    icon: (
      <svg className="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M12 4.354a4 4 0 110 5.292M15 21H3v-1a6 6 0 0112 0v1zm0 0h6v-1a6 6 0 00-9-5.197M13 7a4 4 0 11-8 0 4 4 0 018 0z" />
      </svg>
    ),
    permission: 'user:read',
  },
  {
    name: '群组管理',
    href: '/admin/groups',
    icon: (
      <svg className="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M17 20h5v-2a3 3 0 00-5.356-1.857M17 20H7m10 0v-2c0-.656-.126-1.283-.356-1.857M7 20H2v-2a3 3 0 015.356-1.857M7 20v-2c0-.656.126-1.283.356-1.857m0 0a5.002 5.002 0 019.288 0M15 7a3 3 0 11-6 0 3 3 0 016 0zm6 3a2 2 0 11-4 0 2 2 0 014 0zM7 10a2 2 0 11-4 0 2 2 0 014 0z" />
      </svg>
    ),
    permission: 'group:read',
  },
  {
    name: '角色权限',
    href: '/admin/roles',
    icon: (
      <svg className="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M9 12l2 2 4-4m5.618-4.016A11.955 11.955 0 0112 2.944a11.955 11.955 0 01-8.618 3.04A12.02 12.02 0 003 9c0 5.591 3.824 10.29 9 11.622 5.176-1.332 9-6.03 9-11.622 0-1.042-.133-2.052-.382-3.016z" />
      </svg>
    ),
    permission: 'role:read',
  },
]

export default function AdminLayout({
  children,
}: {
  children: React.ReactNode
}) {
  const router = useRouter()
  const pathname = usePathname()
  // 只订阅状态值，不订阅函数（函数引用会导致无限循环）
  const user = useAuthStore((state) => state.user)
  const isAuthenticated = useAuthStore((state) => state.isAuthenticated)
  const isLoading = useAuthStore((state) => state.isLoading)
  const [sidebarOpen, setSidebarOpen] = useState(true)

  // 使用 ref 防止重复调用
  const isCheckingRef = useRef(false)
  const hasCheckedRef = useRef(false)

  // 权限检查函数 - 直接从 store 获取，不作为依赖
  const checkPermission = useCallback((permission: string) => {
    const { hasPermission } = useAuthStore.getState()
    return hasPermission(permission)
  }, [])

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
          return
        }

        // 检查是否有管理权限
        const hasAdminAccess =
          checkPermission('system:admin') ||
          checkPermission('user:read') ||
          checkPermission('group:read') ||
          checkPermission('role:read')

        if (!hasAdminAccess) {
          router.push('/unauthorized')
        }
      } finally {
        isCheckingRef.current = false
      }
    }

    verifyAuth()
  }, [router, checkPermission, isAuthenticated])

  const handleLogout = async () => {
    await logout()
    router.push('/login')
  }

  // 加载中状态
  if (isLoading || !isAuthenticated) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <div
          className="w-10 h-10 rounded-full border-2 border-t-transparent animate-spin"
          style={{ borderColor: 'var(--nexus-cyan)', borderTopColor: 'transparent' }}
        />
      </div>
    )
  }

  // 过滤有权限的导航项
  const visibleNavItems = navItems.filter(
    (item) => !item.permission || checkPermission(item.permission)
  )

  return (
    <div className="min-h-screen flex">
      {/* 侧边栏 */}
      <motion.aside
        initial={false}
        animate={{ width: sidebarOpen ? 256 : 72 }}
        transition={{ duration: 0.3, ease: 'easeInOut' }}
        className="fixed left-0 top-0 bottom-0 z-30 flex flex-col"
        style={{
          background: 'rgba(17, 24, 39, 0.95)',
          backdropFilter: 'blur(20px)',
          borderRight: '1px solid var(--border-default)',
        }}
      >
        {/* Logo */}
        <div className="h-16 flex items-center justify-between px-4 border-b border-[var(--border-subtle)]">
          <AnimatePresence mode="wait">
            {sidebarOpen && (
              <motion.div
                initial={{ opacity: 0 }}
                animate={{ opacity: 1 }}
                exit={{ opacity: 0 }}
                className="flex items-center gap-3"
              >
                <div
                  className="w-8 h-8 rounded-lg flex items-center justify-center"
                  style={{ background: 'var(--gradient-neural)' }}
                >
                  <svg
                    className="w-4 h-4 text-white"
                    viewBox="0 0 24 24"
                    fill="none"
                    stroke="currentColor"
                    strokeWidth="2"
                  >
                    <circle cx="12" cy="12" r="3" />
                    <path d="M12 2v4m0 12v4" />
                  </svg>
                </div>
                <span
                  className="text-lg font-bold"
                  style={{
                    fontFamily: 'Orbitron, sans-serif',
                    background: 'var(--gradient-neural)',
                    WebkitBackgroundClip: 'text',
                    WebkitTextFillColor: 'transparent',
                  }}
                >
                  管理后台
                </span>
              </motion.div>
            )}
          </AnimatePresence>

          <button
            onClick={() => setSidebarOpen(!sidebarOpen)}
            className="p-2 rounded-lg hover:bg-[var(--nexus-surface)] transition-colors"
          >
            <svg
              className="w-5 h-5 text-[var(--text-secondary)]"
              fill="none"
              viewBox="0 0 24 24"
              stroke="currentColor"
            >
              <path
                strokeLinecap="round"
                strokeLinejoin="round"
                strokeWidth={1.5}
                d={sidebarOpen ? 'M11 19l-7-7 7-7m8 14l-7-7 7-7' : 'M13 5l7 7-7 7M5 5l7 7-7 7'}
              />
            </svg>
          </button>
        </div>

        {/* 导航 */}
        <nav className="flex-1 py-4 px-3 space-y-1 overflow-y-auto">
          {visibleNavItems.map((item) => {
            const isActive = pathname === item.href || (item.href !== '/admin' && pathname.startsWith(item.href))

            return (
              <Link
                key={item.href}
                href={item.href}
                className={`flex items-center gap-3 px-3 py-2.5 rounded-xl transition-all duration-200 group ${
                  isActive
                    ? 'text-white'
                    : 'text-[var(--text-secondary)] hover:text-[var(--text-primary)] hover:bg-[var(--nexus-surface)]'
                }`}
                style={
                  isActive
                    ? {
                        background: 'var(--gradient-neural)',
                        boxShadow: 'var(--shadow-glow-sm)',
                      }
                    : {}
                }
              >
                <span className={isActive ? 'text-white' : 'text-[var(--text-tertiary)] group-hover:text-[var(--nexus-cyan)]'}>
                  {item.icon}
                </span>
                <AnimatePresence mode="wait">
                  {sidebarOpen && (
                    <motion.span
                      initial={{ opacity: 0, width: 0 }}
                      animate={{ opacity: 1, width: 'auto' }}
                      exit={{ opacity: 0, width: 0 }}
                      className="font-medium whitespace-nowrap overflow-hidden"
                    >
                      {item.name}
                    </motion.span>
                  )}
                </AnimatePresence>
              </Link>
            )
          })}
        </nav>

        {/* 用户信息和退出 */}
        <div className="p-3 border-t border-[var(--border-subtle)]">
          <div className="flex items-center gap-3 px-3 py-2 rounded-xl bg-[var(--nexus-surface)]">
            <div
              className="w-8 h-8 rounded-full flex items-center justify-center text-white text-sm font-medium"
              style={{ background: 'var(--gradient-neural)' }}
            >
              {user?.name?.charAt(0).toUpperCase() || 'U'}
            </div>
            <AnimatePresence mode="wait">
              {sidebarOpen && (
                <motion.div
                  initial={{ opacity: 0 }}
                  animate={{ opacity: 1 }}
                  exit={{ opacity: 0 }}
                  className="flex-1 min-w-0"
                >
                  <p className="text-sm font-medium text-[var(--text-primary)] truncate">
                    {user?.name}
                  </p>
                  <p className="text-xs text-[var(--text-tertiary)] truncate">
                    {user?.email}
                  </p>
                </motion.div>
              )}
            </AnimatePresence>
          </div>

          <div className="mt-2 flex gap-2">
            <Link
              href="/chat"
              className="flex-1 flex items-center justify-center gap-2 px-3 py-2 rounded-xl text-sm text-[var(--text-secondary)] hover:text-[var(--text-primary)] hover:bg-[var(--nexus-surface)] transition-colors"
            >
              <svg className="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M8 12h.01M12 12h.01M16 12h.01M21 12c0 4.418-4.03 8-9 8a9.863 9.863 0 01-4.255-.949L3 20l1.395-3.72C3.512 15.042 3 13.574 3 12c0-4.418 4.03-8 9-8s9 3.582 9 8z" />
              </svg>
              {sidebarOpen && <span>聊天</span>}
            </Link>
            <button
              onClick={handleLogout}
              className="flex-1 flex items-center justify-center gap-2 px-3 py-2 rounded-xl text-sm text-[var(--nexus-error)] hover:bg-[rgba(239,68,68,0.1)] transition-colors"
            >
              <svg className="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M17 16l4-4m0 0l-4-4m4 4H7m6 4v1a3 3 0 01-3 3H6a3 3 0 01-3-3V7a3 3 0 013-3h4a3 3 0 013 3v1" />
              </svg>
              {sidebarOpen && <span>退出</span>}
            </button>
          </div>
        </div>
      </motion.aside>

      {/* 主内容区 */}
      <main
        className="flex-1 transition-all duration-300"
        style={{ marginLeft: sidebarOpen ? 256 : 72 }}
      >
        {children}
      </main>
    </div>
  )
}
