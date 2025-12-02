'use client'

import { useEffect } from 'react'
import { useRouter } from 'next/navigation'
import { useAuthStore } from '@/lib/stores/auth'

export default function AuthLayout({
  children,
}: {
  children: React.ReactNode
}) {
  const router = useRouter()
  const { isAuthenticated, isLoading } = useAuthStore()

  useEffect(() => {
    // 如果已登录，重定向到聊天页面
    if (!isLoading && isAuthenticated) {
      router.push('/chat')
    }
  }, [isAuthenticated, isLoading, router])

  // 显示加载状态
  if (isLoading) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <div className="nexus-spinner w-10 h-10" />
      </div>
    )
  }

  // 已登录时不显示内容（等待重定向）
  if (isAuthenticated) {
    return null
  }

  return (
    <div className="min-h-screen relative overflow-hidden">
      {/* 动态背景效果 */}
      <div className="fixed inset-0 pointer-events-none overflow-hidden -z-10">
        {/* 主发光球 */}
        <div
          className="absolute w-[600px] h-[600px] rounded-full opacity-20 blur-[100px]"
          style={{
            background: 'radial-gradient(circle, rgba(6, 182, 212, 0.4) 0%, transparent 70%)',
            top: '5%',
            left: '15%',
            animation: 'float 20s ease-in-out infinite',
          }}
        />
        <div
          className="absolute w-[500px] h-[500px] rounded-full opacity-15 blur-[80px]"
          style={{
            background: 'radial-gradient(circle, rgba(139, 92, 246, 0.4) 0%, transparent 70%)',
            bottom: '10%',
            right: '10%',
            animation: 'float 25s ease-in-out infinite reverse',
          }}
        />
        <div
          className="absolute w-[300px] h-[300px] rounded-full opacity-10 blur-[60px]"
          style={{
            background: 'radial-gradient(circle, rgba(59, 130, 246, 0.4) 0%, transparent 70%)',
            top: '50%',
            left: '50%',
            transform: 'translate(-50%, -50%)',
            animation: 'pulse 8s ease-in-out infinite',
          }}
        />
      </div>

      {/* 网格背景 */}
      <div
        className="fixed inset-0 pointer-events-none opacity-[0.02] -z-10"
        style={{
          backgroundImage: `
            linear-gradient(var(--border-subtle) 1px, transparent 1px),
            linear-gradient(90deg, var(--border-subtle) 1px, transparent 1px)
          `,
          backgroundSize: '50px 50px',
        }}
      />

      {children}
    </div>
  )
}
