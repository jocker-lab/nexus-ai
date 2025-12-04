'use client'

import { useEffect, useState } from 'react'
import { motion } from 'framer-motion'
import Link from 'next/link'
import { getDashboardStats, type DashboardStats, type User } from '@/lib/admin/api'
import { useAuthStore } from '@/lib/stores/auth'

// 统计卡片组件
function StatCard({
  title,
  value,
  icon,
  gradient,
  delay = 0,
}: {
  title: string
  value: number | string
  icon: React.ReactNode
  gradient: string
  delay?: number
}) {
  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.5, delay }}
      className="relative overflow-hidden rounded-2xl p-6"
      style={{
        background: 'rgba(17, 24, 39, 0.6)',
        backdropFilter: 'blur(20px)',
        border: '1px solid var(--border-default)',
      }}
    >
      {/* 背景装饰 */}
      <div
        className="absolute top-0 right-0 w-32 h-32 opacity-10"
        style={{
          background: gradient,
          borderRadius: '50%',
          transform: 'translate(30%, -30%)',
          filter: 'blur(20px)',
        }}
      />

      <div className="relative flex items-start justify-between">
        <div>
          <p className="text-sm text-[var(--text-tertiary)] mb-1">{title}</p>
          <p
            className="text-3xl font-bold"
            style={{
              background: gradient,
              WebkitBackgroundClip: 'text',
              WebkitTextFillColor: 'transparent',
            }}
          >
            {value}
          </p>
        </div>
        <div
          className="w-12 h-12 rounded-xl flex items-center justify-center"
          style={{ background: gradient, opacity: 0.8 }}
        >
          {icon}
        </div>
      </div>
    </motion.div>
  )
}

// 最近用户列表组件
function RecentUsersList({ users }: { users: User[] }) {
  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.5, delay: 0.3 }}
      className="rounded-2xl overflow-hidden"
      style={{
        background: 'rgba(17, 24, 39, 0.6)',
        backdropFilter: 'blur(20px)',
        border: '1px solid var(--border-default)',
      }}
    >
      <div className="p-4 border-b border-[var(--border-subtle)]">
        <h3 className="text-lg font-semibold text-[var(--text-primary)]">最近注册用户</h3>
      </div>
      <div className="divide-y divide-[var(--border-subtle)]">
        {users.length === 0 ? (
          <div className="p-8 text-center text-[var(--text-tertiary)]">暂无用户数据</div>
        ) : (
          users.map((user, index) => (
            <motion.div
              key={user.id}
              initial={{ opacity: 0, x: -20 }}
              animate={{ opacity: 1, x: 0 }}
              transition={{ duration: 0.3, delay: 0.4 + index * 0.1 }}
              className="p-4 flex items-center gap-4 hover:bg-[var(--nexus-surface)] transition-colors"
            >
              <div
                className="w-10 h-10 rounded-full flex items-center justify-center text-white font-medium"
                style={{ background: 'var(--gradient-neural)' }}
              >
                {user.name?.charAt(0).toUpperCase() || 'U'}
              </div>
              <div className="flex-1 min-w-0">
                <p className="font-medium text-[var(--text-primary)] truncate">{user.name}</p>
                <p className="text-sm text-[var(--text-tertiary)] truncate">{user.email}</p>
              </div>
              <div className="flex items-center gap-2">
                <span
                  className={`px-2 py-1 rounded-full text-xs ${
                    user.is_active
                      ? 'bg-[rgba(16,185,129,0.1)] text-[var(--nexus-success)]'
                      : 'bg-[rgba(239,68,68,0.1)] text-[var(--nexus-error)]'
                  }`}
                >
                  {user.is_active ? '活跃' : '停用'}
                </span>
                {user.is_superadmin && (
                  <span className="px-2 py-1 rounded-full text-xs bg-[rgba(139,92,246,0.1)] text-[var(--nexus-purple)]">
                    超级管理员
                  </span>
                )}
              </div>
            </motion.div>
          ))
        )}
      </div>
      <div className="p-4 border-t border-[var(--border-subtle)]">
        <Link
          href="/admin/users"
          className="text-sm text-[var(--nexus-cyan)] hover:text-[var(--nexus-blue)] transition-colors flex items-center gap-1"
        >
          查看全部用户
          <svg className="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 5l7 7-7 7" />
          </svg>
        </Link>
      </div>
    </motion.div>
  )
}

// 快捷操作卡片
function QuickActions() {
  const { hasPermission } = useAuthStore()

  const actions = [
    {
      title: '创建用户',
      description: '添加新的系统用户',
      href: '/admin/users?action=create',
      icon: (
        <svg className="w-6 h-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M18 9v3m0 0v3m0-3h3m-3 0h-3m-2-5a4 4 0 11-8 0 4 4 0 018 0zM3 20a6 6 0 0112 0v1H3v-1z" />
        </svg>
      ),
      permission: 'user:create',
    },
    {
      title: '管理群组',
      description: '配置用户群组和权限',
      href: '/admin/groups',
      icon: (
        <svg className="w-6 h-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M17 20h5v-2a3 3 0 00-5.356-1.857M17 20H7m10 0v-2c0-.656-.126-1.283-.356-1.857M7 20H2v-2a3 3 0 015.356-1.857M7 20v-2c0-.656.126-1.283.356-1.857m0 0a5.002 5.002 0 019.288 0M15 7a3 3 0 11-6 0 3 3 0 016 0z" />
        </svg>
      ),
      permission: 'group:read',
    },
    {
      title: '角色配置',
      description: '管理角色和权限分配',
      href: '/admin/roles',
      icon: (
        <svg className="w-6 h-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M9 12l2 2 4-4m5.618-4.016A11.955 11.955 0 0112 2.944a11.955 11.955 0 01-8.618 3.04A12.02 12.02 0 003 9c0 5.591 3.824 10.29 9 11.622 5.176-1.332 9-6.03 9-11.622 0-1.042-.133-2.052-.382-3.016z" />
        </svg>
      ),
      permission: 'role:read',
    },
  ]

  const visibleActions = actions.filter(
    (action) => !action.permission || hasPermission(action.permission)
  )

  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.5, delay: 0.4 }}
      className="rounded-2xl overflow-hidden"
      style={{
        background: 'rgba(17, 24, 39, 0.6)',
        backdropFilter: 'blur(20px)',
        border: '1px solid var(--border-default)',
      }}
    >
      <div className="p-4 border-b border-[var(--border-subtle)]">
        <h3 className="text-lg font-semibold text-[var(--text-primary)]">快捷操作</h3>
      </div>
      <div className="p-4 grid gap-3">
        {visibleActions.map((action, index) => (
          <Link
            key={action.href}
            href={action.href}
            className="flex items-center gap-4 p-4 rounded-xl hover:bg-[var(--nexus-surface)] transition-all duration-200 group"
          >
            <div
              className="w-12 h-12 rounded-xl flex items-center justify-center text-[var(--nexus-cyan)] group-hover:scale-110 transition-transform"
              style={{ background: 'rgba(0, 212, 255, 0.1)' }}
            >
              {action.icon}
            </div>
            <div>
              <p className="font-medium text-[var(--text-primary)] group-hover:text-[var(--nexus-cyan)] transition-colors">
                {action.title}
              </p>
              <p className="text-sm text-[var(--text-tertiary)]">{action.description}</p>
            </div>
            <svg
              className="w-5 h-5 text-[var(--text-tertiary)] ml-auto opacity-0 group-hover:opacity-100 transition-opacity"
              fill="none"
              viewBox="0 0 24 24"
              stroke="currentColor"
            >
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 5l7 7-7 7" />
            </svg>
          </Link>
        ))}
      </div>
    </motion.div>
  )
}

export default function AdminDashboard() {
  const [stats, setStats] = useState<DashboardStats | null>(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState('')
  const { user } = useAuthStore()

  useEffect(() => {
    const fetchStats = async () => {
      try {
        const data = await getDashboardStats()
        setStats(data)
      } catch (err) {
        setError(err instanceof Error ? err.message : '获取统计数据失败')
      } finally {
        setLoading(false)
      }
    }

    fetchStats()
  }, [])

  if (loading) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <div
          className="w-10 h-10 rounded-full border-2 border-t-transparent animate-spin"
          style={{ borderColor: 'var(--nexus-cyan)', borderTopColor: 'transparent' }}
        />
      </div>
    )
  }

  return (
    <div className="p-6 lg:p-8">
      {/* 页面标题 */}
      <motion.div
        initial={{ opacity: 0, y: -20 }}
        animate={{ opacity: 1, y: 0 }}
        className="mb-8"
      >
        <h1 className="text-2xl lg:text-3xl font-bold text-[var(--text-primary)] mb-2">
          欢迎回来，{user?.name}
        </h1>
        <p className="text-[var(--text-secondary)]">这里是 Nexus AI 管理控制台的概览</p>
      </motion.div>

      {/* 错误提示 */}
      {error && (
        <motion.div
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          className="mb-6 p-4 rounded-xl"
          style={{
            background: 'rgba(239, 68, 68, 0.1)',
            border: '1px solid rgba(239, 68, 68, 0.3)',
          }}
        >
          <p className="text-[var(--nexus-error)]">{error}</p>
        </motion.div>
      )}

      {/* 统计卡片 */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4 lg:gap-6 mb-8">
        <StatCard
          title="总用户数"
          value={stats?.total_users ?? 0}
          gradient="var(--gradient-neural)"
          icon={
            <svg className="w-6 h-6 text-white" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M12 4.354a4 4 0 110 5.292M15 21H3v-1a6 6 0 0112 0v1zm0 0h6v-1a6 6 0 00-9-5.197M13 7a4 4 0 11-8 0 4 4 0 018 0z" />
            </svg>
          }
          delay={0}
        />
        <StatCard
          title="活跃用户"
          value={stats?.active_users ?? 0}
          gradient="linear-gradient(135deg, #10b981 0%, #059669 100%)"
          icon={
            <svg className="w-6 h-6 text-white" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
            </svg>
          }
          delay={0.1}
        />
        <StatCard
          title="用户群组"
          value={stats?.total_groups ?? 0}
          gradient="linear-gradient(135deg, #8b5cf6 0%, #7c3aed 100%)"
          icon={
            <svg className="w-6 h-6 text-white" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M17 20h5v-2a3 3 0 00-5.356-1.857M17 20H7m10 0v-2c0-.656-.126-1.283-.356-1.857M7 20H2v-2a3 3 0 015.356-1.857M7 20v-2c0-.656.126-1.283.356-1.857m0 0a5.002 5.002 0 019.288 0" />
            </svg>
          }
          delay={0.2}
        />
        <StatCard
          title="系统角色"
          value={stats?.total_roles ?? 0}
          gradient="linear-gradient(135deg, #f59e0b 0%, #d97706 100%)"
          icon={
            <svg className="w-6 h-6 text-white" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M9 12l2 2 4-4m5.618-4.016A11.955 11.955 0 0112 2.944a11.955 11.955 0 01-8.618 3.04A12.02 12.02 0 003 9c0 5.591 3.824 10.29 9 11.622 5.176-1.332 9-6.03 9-11.622 0-1.042-.133-2.052-.382-3.016z" />
            </svg>
          }
          delay={0.3}
        />
      </div>

      {/* 下方内容区域 */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* 最近用户 - 占据 2 列 */}
        <div className="lg:col-span-2">
          <RecentUsersList users={stats?.recent_users ?? []} />
        </div>

        {/* 快捷操作 */}
        <div>
          <QuickActions />
        </div>
      </div>
    </div>
  )
}
