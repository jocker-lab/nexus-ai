'use client'

import { useEffect, useState, useCallback } from 'react'
import { motion, AnimatePresence } from 'framer-motion'
import {
  getUsers,
  getGroups,
  createUser,
  updateUser,
  deleteUser,
  addUserToGroup,
  removeUserFromGroup,
  type User,
  type Group,
  type PaginatedResponse,
} from '@/lib/admin/api'
import { useAuthStore } from '@/lib/stores/auth'

// 用户表单对话框
function UserFormDialog({
  isOpen,
  onClose,
  user,
  groups,
  onSubmit,
}: {
  isOpen: boolean
  onClose: () => void
  user: User | null
  groups: Group[]
  onSubmit: (data: { name: string; email: string; password?: string; is_active: boolean; group_ids: string[] }) => Promise<void>
}) {
  const [name, setName] = useState('')
  const [email, setEmail] = useState('')
  const [password, setPassword] = useState('')
  const [isActive, setIsActive] = useState(true)
  const [selectedGroups, setSelectedGroups] = useState<string[]>([])
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState('')

  useEffect(() => {
    if (user) {
      setName(user.name)
      setEmail(user.email)
      setPassword('')
      setIsActive(user.is_active)
      setSelectedGroups(user.groups?.map(g => g.id) || [])
    } else {
      setName('')
      setEmail('')
      setPassword('')
      setIsActive(true)
      setSelectedGroups([])
    }
    setError('')
  }, [user, isOpen])

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    setError('')
    setLoading(true)

    try {
      await onSubmit({
        name,
        email,
        password: password || undefined,
        is_active: isActive,
        group_ids: selectedGroups,
      })
      onClose()
    } catch (err) {
      setError(err instanceof Error ? err.message : '操作失败')
    } finally {
      setLoading(false)
    }
  }

  const toggleGroup = (groupId: string) => {
    setSelectedGroups(prev =>
      prev.includes(groupId)
        ? prev.filter(id => id !== groupId)
        : [...prev, groupId]
    )
  }

  if (!isOpen) return null

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4">
      {/* 背景遮罩 */}
      <motion.div
        initial={{ opacity: 0 }}
        animate={{ opacity: 1 }}
        exit={{ opacity: 0 }}
        className="absolute inset-0 bg-black/60 backdrop-blur-sm"
        onClick={onClose}
      />

      {/* 对话框 */}
      <motion.div
        initial={{ opacity: 0, scale: 0.95, y: 20 }}
        animate={{ opacity: 1, scale: 1, y: 0 }}
        exit={{ opacity: 0, scale: 0.95, y: 20 }}
        className="relative w-full max-w-lg rounded-2xl overflow-hidden"
        style={{
          background: 'rgba(17, 24, 39, 0.95)',
          backdropFilter: 'blur(20px)',
          border: '1px solid var(--border-default)',
        }}
      >
        {/* 标题栏 */}
        <div className="p-6 border-b border-[var(--border-subtle)]">
          <h2 className="text-xl font-semibold text-[var(--text-primary)]">
            {user ? '编辑用户' : '创建用户'}
          </h2>
        </div>

        {/* 表单 */}
        <form onSubmit={handleSubmit} className="p-6 space-y-5">
          {error && (
            <div
              className="p-4 rounded-xl"
              style={{
                background: 'rgba(239, 68, 68, 0.1)',
                border: '1px solid rgba(239, 68, 68, 0.3)',
              }}
            >
              <p className="text-[var(--nexus-error)] text-sm">{error}</p>
            </div>
          )}

          {/* 用户名 */}
          <div>
            <label className="block text-sm font-medium text-[var(--text-secondary)] mb-2">
              用户名 <span className="text-[var(--nexus-error)]">*</span>
            </label>
            <input
              type="text"
              value={name}
              onChange={(e) => setName(e.target.value)}
              className="w-full px-4 py-3 rounded-xl text-[var(--text-primary)] placeholder-[var(--text-tertiary)] focus:outline-none focus:ring-2 focus:ring-[var(--nexus-cyan)]/50"
              style={{
                background: 'var(--nexus-deep)',
                border: '1px solid var(--border-default)',
              }}
              placeholder="输入用户名"
              required
            />
          </div>

          {/* 邮箱 */}
          <div>
            <label className="block text-sm font-medium text-[var(--text-secondary)] mb-2">
              邮箱 <span className="text-[var(--nexus-error)]">*</span>
            </label>
            <input
              type="email"
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              className="w-full px-4 py-3 rounded-xl text-[var(--text-primary)] placeholder-[var(--text-tertiary)] focus:outline-none focus:ring-2 focus:ring-[var(--nexus-cyan)]/50"
              style={{
                background: 'var(--nexus-deep)',
                border: '1px solid var(--border-default)',
              }}
              placeholder="user@example.com"
              required
            />
          </div>

          {/* 密码 */}
          <div>
            <label className="block text-sm font-medium text-[var(--text-secondary)] mb-2">
              密码 {!user && <span className="text-[var(--nexus-error)]">*</span>}
            </label>
            <input
              type="password"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              className="w-full px-4 py-3 rounded-xl text-[var(--text-primary)] placeholder-[var(--text-tertiary)] focus:outline-none focus:ring-2 focus:ring-[var(--nexus-cyan)]/50"
              style={{
                background: 'var(--nexus-deep)',
                border: '1px solid var(--border-default)',
              }}
              placeholder={user ? '留空保持不变' : '至少 8 位字符'}
              required={!user}
              minLength={user ? 0 : 8}
            />
          </div>

          {/* 状态 */}
          <div className="flex items-center gap-3">
            <button
              type="button"
              onClick={() => setIsActive(!isActive)}
              className={`relative w-12 h-6 rounded-full transition-colors ${
                isActive ? 'bg-[var(--nexus-cyan)]' : 'bg-[var(--nexus-surface)]'
              }`}
            >
              <span
                className={`absolute top-1 w-4 h-4 rounded-full bg-white transition-transform ${
                  isActive ? 'left-7' : 'left-1'
                }`}
              />
            </button>
            <span className="text-sm text-[var(--text-secondary)]">
              {isActive ? '账户启用' : '账户停用'}
            </span>
          </div>

          {/* 群组选择 */}
          <div>
            <label className="block text-sm font-medium text-[var(--text-secondary)] mb-2">
              所属群组
            </label>
            <div className="flex flex-wrap gap-2">
              {groups.map(group => (
                <button
                  key={group.id}
                  type="button"
                  onClick={() => toggleGroup(group.id)}
                  className={`px-3 py-1.5 rounded-lg text-sm transition-colors ${
                    selectedGroups.includes(group.id)
                      ? 'bg-[var(--nexus-cyan)] text-white'
                      : 'bg-[var(--nexus-surface)] text-[var(--text-secondary)] hover:bg-[var(--nexus-surface)]/80'
                  }`}
                >
                  {group.name}
                </button>
              ))}
              {groups.length === 0 && (
                <p className="text-sm text-[var(--text-tertiary)]">暂无可用群组</p>
              )}
            </div>
          </div>

          {/* 操作按钮 */}
          <div className="flex gap-3 pt-4">
            <button
              type="button"
              onClick={onClose}
              className="flex-1 py-3 rounded-xl font-medium text-[var(--text-secondary)] hover:text-[var(--text-primary)] hover:bg-[var(--nexus-surface)] transition-colors"
            >
              取消
            </button>
            <button
              type="submit"
              disabled={loading}
              className="flex-1 py-3 rounded-xl font-medium text-white transition-all"
              style={{
                background: 'var(--gradient-neural)',
                opacity: loading ? 0.7 : 1,
              }}
            >
              {loading ? '处理中...' : user ? '保存更改' : '创建用户'}
            </button>
          </div>
        </form>
      </motion.div>
    </div>
  )
}

// 确认删除对话框
function ConfirmDialog({
  isOpen,
  onClose,
  onConfirm,
  title,
  message,
  loading,
}: {
  isOpen: boolean
  onClose: () => void
  onConfirm: () => void
  title: string
  message: string
  loading: boolean
}) {
  if (!isOpen) return null

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4">
      <motion.div
        initial={{ opacity: 0 }}
        animate={{ opacity: 1 }}
        exit={{ opacity: 0 }}
        className="absolute inset-0 bg-black/60 backdrop-blur-sm"
        onClick={onClose}
      />

      <motion.div
        initial={{ opacity: 0, scale: 0.95 }}
        animate={{ opacity: 1, scale: 1 }}
        exit={{ opacity: 0, scale: 0.95 }}
        className="relative w-full max-w-md rounded-2xl p-6"
        style={{
          background: 'rgba(17, 24, 39, 0.95)',
          backdropFilter: 'blur(20px)',
          border: '1px solid var(--border-default)',
        }}
      >
        <h3 className="text-lg font-semibold text-[var(--text-primary)] mb-2">{title}</h3>
        <p className="text-[var(--text-secondary)] mb-6">{message}</p>

        <div className="flex gap-3">
          <button
            onClick={onClose}
            className="flex-1 py-2.5 rounded-xl font-medium text-[var(--text-secondary)] hover:bg-[var(--nexus-surface)] transition-colors"
          >
            取消
          </button>
          <button
            onClick={onConfirm}
            disabled={loading}
            className="flex-1 py-2.5 rounded-xl font-medium text-white bg-[var(--nexus-error)] hover:bg-[var(--nexus-error)]/80 transition-colors"
          >
            {loading ? '处理中...' : '确认删除'}
          </button>
        </div>
      </motion.div>
    </div>
  )
}

export default function UsersPage() {
  const [users, setUsers] = useState<PaginatedResponse<User> | null>(null)
  const [groups, setGroups] = useState<Group[]>([])
  const [loading, setLoading] = useState(true)
  const [search, setSearch] = useState('')
  const [page, setPage] = useState(1)
  const [formOpen, setFormOpen] = useState(false)
  const [editingUser, setEditingUser] = useState<User | null>(null)
  const [deleteTarget, setDeleteTarget] = useState<User | null>(null)
  const [deleteLoading, setDeleteLoading] = useState(false)
  const { hasPermission } = useAuthStore()

  const canCreate = hasPermission('user:create')
  const canUpdate = hasPermission('user:update')
  const canDelete = hasPermission('user:delete')

  const fetchUsers = useCallback(async () => {
    setLoading(true)
    try {
      const [usersData, groupsData] = await Promise.all([
        getUsers({ page, page_size: 10, search: search || undefined }),
        getGroups({ page: 1, page_size: 100 }),
      ])
      setUsers(usersData)
      setGroups(groupsData.items)
    } catch (err) {
      console.error('Failed to fetch users:', err)
    } finally {
      setLoading(false)
    }
  }, [page, search])

  useEffect(() => {
    fetchUsers()
  }, [fetchUsers])

  const handleSearch = (e: React.FormEvent) => {
    e.preventDefault()
    setPage(1)
    fetchUsers()
  }

  const handleCreateOrUpdate = async (data: {
    name: string
    email: string
    password?: string
    is_active: boolean
    group_ids: string[]
  }) => {
    if (editingUser) {
      // 更新用户
      await updateUser(editingUser.id, {
        name: data.name,
        email: data.email,
        password: data.password,
        is_active: data.is_active,
      })

      // 更新群组关联
      const currentGroups = editingUser.groups?.map(g => g.id) || []
      const toAdd = data.group_ids.filter(id => !currentGroups.includes(id))
      const toRemove = currentGroups.filter(id => !data.group_ids.includes(id))

      for (const groupId of toAdd) {
        await addUserToGroup(editingUser.id, groupId)
      }
      for (const groupId of toRemove) {
        await removeUserFromGroup(editingUser.id, groupId)
      }
    } else {
      // 创建用户
      const newUser = await createUser({
        name: data.name,
        email: data.email,
        password: data.password!,
        is_active: data.is_active,
      })

      // 添加到群组
      for (const groupId of data.group_ids) {
        await addUserToGroup(newUser.id, groupId)
      }
    }

    await fetchUsers()
  }

  const handleDelete = async () => {
    if (!deleteTarget) return

    setDeleteLoading(true)
    try {
      await deleteUser(deleteTarget.id)
      setDeleteTarget(null)
      await fetchUsers()
    } catch (err) {
      console.error('Failed to delete user:', err)
    } finally {
      setDeleteLoading(false)
    }
  }

  return (
    <div className="p-6 lg:p-8">
      {/* 页面标题 */}
      <motion.div
        initial={{ opacity: 0, y: -20 }}
        animate={{ opacity: 1, y: 0 }}
        className="mb-6"
      >
        <h1 className="text-2xl font-bold text-[var(--text-primary)]">用户管理</h1>
        <p className="text-[var(--text-secondary)] mt-1">管理系统中的所有用户账户</p>
      </motion.div>

      {/* 工具栏 */}
      <motion.div
        initial={{ opacity: 0, y: 10 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ delay: 0.1 }}
        className="flex flex-col sm:flex-row gap-4 mb-6"
      >
        {/* 搜索 */}
        <form onSubmit={handleSearch} className="flex-1">
          <div className="relative">
            <input
              type="text"
              value={search}
              onChange={(e) => setSearch(e.target.value)}
              className="w-full px-4 py-2.5 pl-10 rounded-xl text-[var(--text-primary)] placeholder-[var(--text-tertiary)] focus:outline-none focus:ring-2 focus:ring-[var(--nexus-cyan)]/50"
              style={{
                background: 'rgba(17, 24, 39, 0.6)',
                border: '1px solid var(--border-default)',
              }}
              placeholder="搜索用户名或邮箱..."
            />
            <svg
              className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-[var(--text-tertiary)]"
              fill="none"
              viewBox="0 0 24 24"
              stroke="currentColor"
            >
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z" />
            </svg>
          </div>
        </form>

        {/* 创建按钮 */}
        {canCreate && (
          <button
            onClick={() => {
              setEditingUser(null)
              setFormOpen(true)
            }}
            className="px-4 py-2.5 rounded-xl font-medium text-white flex items-center gap-2 transition-all hover:scale-105"
            style={{ background: 'var(--gradient-neural)' }}
          >
            <svg className="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 4v16m8-8H4" />
            </svg>
            创建用户
          </button>
        )}
      </motion.div>

      {/* 用户列表 */}
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ delay: 0.2 }}
        className="rounded-2xl overflow-hidden"
        style={{
          background: 'rgba(17, 24, 39, 0.6)',
          backdropFilter: 'blur(20px)',
          border: '1px solid var(--border-default)',
        }}
      >
        {loading ? (
          <div className="p-12 flex items-center justify-center">
            <div
              className="w-8 h-8 rounded-full border-2 border-t-transparent animate-spin"
              style={{ borderColor: 'var(--nexus-cyan)', borderTopColor: 'transparent' }}
            />
          </div>
        ) : users?.items.length === 0 ? (
          <div className="p-12 text-center">
            <svg
              className="w-16 h-16 mx-auto text-[var(--text-tertiary)] mb-4"
              fill="none"
              viewBox="0 0 24 24"
              stroke="currentColor"
            >
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1} d="M12 4.354a4 4 0 110 5.292M15 21H3v-1a6 6 0 0112 0v1zm0 0h6v-1a6 6 0 00-9-5.197M13 7a4 4 0 11-8 0 4 4 0 018 0z" />
            </svg>
            <p className="text-[var(--text-tertiary)]">暂无用户数据</p>
          </div>
        ) : (
          <>
            {/* 表格头 */}
            <div className="hidden md:grid grid-cols-12 gap-4 p-4 border-b border-[var(--border-subtle)] text-sm font-medium text-[var(--text-tertiary)]">
              <div className="col-span-4">用户</div>
              <div className="col-span-2">角色</div>
              <div className="col-span-2">群组</div>
              <div className="col-span-2">状态</div>
              <div className="col-span-2 text-right">操作</div>
            </div>

            {/* 用户列表 */}
            <div className="divide-y divide-[var(--border-subtle)]">
              {users?.items.map((user, index) => (
                <motion.div
                  key={user.id}
                  initial={{ opacity: 0, x: -20 }}
                  animate={{ opacity: 1, x: 0 }}
                  transition={{ delay: index * 0.05 }}
                  className="p-4 hover:bg-[var(--nexus-surface)] transition-colors"
                >
                  <div className="md:grid md:grid-cols-12 md:gap-4 md:items-center space-y-3 md:space-y-0">
                    {/* 用户信息 */}
                    <div className="col-span-4 flex items-center gap-3">
                      <div
                        className="w-10 h-10 rounded-full flex items-center justify-center text-white font-medium flex-shrink-0"
                        style={{ background: 'var(--gradient-neural)' }}
                      >
                        {user.name?.charAt(0).toUpperCase() || 'U'}
                      </div>
                      <div className="min-w-0">
                        <p className="font-medium text-[var(--text-primary)] truncate">
                          {user.name}
                          {user.is_superadmin && (
                            <span className="ml-2 px-1.5 py-0.5 rounded text-xs bg-[rgba(139,92,246,0.1)] text-[var(--nexus-purple)]">
                              超管
                            </span>
                          )}
                        </p>
                        <p className="text-sm text-[var(--text-tertiary)] truncate">{user.email}</p>
                      </div>
                    </div>

                    {/* 角色 */}
                    <div className="col-span-2">
                      <span className="text-sm text-[var(--text-secondary)]">{user.role || '普通用户'}</span>
                    </div>

                    {/* 群组 */}
                    <div className="col-span-2">
                      <div className="flex flex-wrap gap-1">
                        {user.groups?.slice(0, 2).map(group => (
                          <span
                            key={group.id}
                            className="px-2 py-0.5 rounded text-xs bg-[var(--nexus-surface)] text-[var(--text-secondary)]"
                          >
                            {group.name}
                          </span>
                        ))}
                        {(user.groups?.length || 0) > 2 && (
                          <span className="text-xs text-[var(--text-tertiary)]">
                            +{(user.groups?.length || 0) - 2}
                          </span>
                        )}
                        {!user.groups?.length && (
                          <span className="text-xs text-[var(--text-tertiary)]">无群组</span>
                        )}
                      </div>
                    </div>

                    {/* 状态 */}
                    <div className="col-span-2">
                      <span
                        className={`inline-flex items-center gap-1.5 px-2.5 py-1 rounded-full text-xs ${
                          user.is_active
                            ? 'bg-[rgba(16,185,129,0.1)] text-[var(--nexus-success)]'
                            : 'bg-[rgba(239,68,68,0.1)] text-[var(--nexus-error)]'
                        }`}
                      >
                        <span className={`w-1.5 h-1.5 rounded-full ${user.is_active ? 'bg-[var(--nexus-success)]' : 'bg-[var(--nexus-error)]'}`} />
                        {user.is_active ? '活跃' : '停用'}
                      </span>
                    </div>

                    {/* 操作 */}
                    <div className="col-span-2 flex items-center justify-end gap-2">
                      {canUpdate && (
                        <button
                          onClick={() => {
                            setEditingUser(user)
                            setFormOpen(true)
                          }}
                          className="p-2 rounded-lg text-[var(--text-tertiary)] hover:text-[var(--nexus-cyan)] hover:bg-[rgba(0,212,255,0.1)] transition-colors"
                          title="编辑"
                        >
                          <svg className="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M11 5H6a2 2 0 00-2 2v11a2 2 0 002 2h11a2 2 0 002-2v-5m-1.414-9.414a2 2 0 112.828 2.828L11.828 15H9v-2.828l8.586-8.586z" />
                          </svg>
                        </button>
                      )}
                      {canDelete && !user.is_superadmin && (
                        <button
                          onClick={() => setDeleteTarget(user)}
                          className="p-2 rounded-lg text-[var(--text-tertiary)] hover:text-[var(--nexus-error)] hover:bg-[rgba(239,68,68,0.1)] transition-colors"
                          title="删除"
                        >
                          <svg className="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16" />
                          </svg>
                        </button>
                      )}
                    </div>
                  </div>
                </motion.div>
              ))}
            </div>

            {/* 分页 */}
            {users && users.total_pages > 1 && (
              <div className="p-4 border-t border-[var(--border-subtle)] flex items-center justify-between">
                <p className="text-sm text-[var(--text-tertiary)]">
                  共 {users.total} 个用户，第 {users.page} / {users.total_pages} 页
                </p>
                <div className="flex gap-2">
                  <button
                    onClick={() => setPage(p => Math.max(1, p - 1))}
                    disabled={page === 1}
                    className="px-3 py-1.5 rounded-lg text-sm font-medium text-[var(--text-secondary)] hover:bg-[var(--nexus-surface)] disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
                  >
                    上一页
                  </button>
                  <button
                    onClick={() => setPage(p => Math.min(users.total_pages, p + 1))}
                    disabled={page === users.total_pages}
                    className="px-3 py-1.5 rounded-lg text-sm font-medium text-[var(--text-secondary)] hover:bg-[var(--nexus-surface)] disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
                  >
                    下一页
                  </button>
                </div>
              </div>
            )}
          </>
        )}
      </motion.div>

      {/* 用户表单对话框 */}
      <AnimatePresence>
        {formOpen && (
          <UserFormDialog
            isOpen={formOpen}
            onClose={() => {
              setFormOpen(false)
              setEditingUser(null)
            }}
            user={editingUser}
            groups={groups}
            onSubmit={handleCreateOrUpdate}
          />
        )}
      </AnimatePresence>

      {/* 确认删除对话框 */}
      <AnimatePresence>
        {deleteTarget && (
          <ConfirmDialog
            isOpen={!!deleteTarget}
            onClose={() => setDeleteTarget(null)}
            onConfirm={handleDelete}
            title="确认删除用户"
            message={`确定要删除用户 "${deleteTarget.name}" 吗？此操作无法撤销。`}
            loading={deleteLoading}
          />
        )}
      </AnimatePresence>
    </div>
  )
}
