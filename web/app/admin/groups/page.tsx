'use client'

import { useEffect, useState, useCallback } from 'react'
import { motion, AnimatePresence } from 'framer-motion'
import {
  getGroups,
  getRoles,
  getGroupMembers,
  createGroup,
  updateGroup,
  deleteGroup,
  addRoleToGroup,
  removeRoleFromGroup,
  type Group,
  type Role,
  type User,
  type PaginatedResponse,
} from '@/lib/admin/api'
import { useAuthStore } from '@/lib/stores/auth'

// 群组表单对话框
function GroupFormDialog({
  isOpen,
  onClose,
  group,
  roles,
  onSubmit,
}: {
  isOpen: boolean
  onClose: () => void
  group: Group | null
  roles: Role[]
  onSubmit: (data: { name: string; description: string; is_default: boolean; role_ids: string[] }) => Promise<void>
}) {
  const [name, setName] = useState('')
  const [description, setDescription] = useState('')
  const [isDefault, setIsDefault] = useState(false)
  const [selectedRoles, setSelectedRoles] = useState<string[]>([])
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState('')

  useEffect(() => {
    if (group) {
      setName(group.name)
      setDescription(group.description || '')
      setIsDefault(group.is_default)
      setSelectedRoles(group.roles?.map(r => r.id) || [])
    } else {
      setName('')
      setDescription('')
      setIsDefault(false)
      setSelectedRoles([])
    }
    setError('')
  }, [group, isOpen])

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    setError('')
    setLoading(true)

    try {
      await onSubmit({
        name,
        description,
        is_default: isDefault,
        role_ids: selectedRoles,
      })
      onClose()
    } catch (err) {
      setError(err instanceof Error ? err.message : '操作失败')
    } finally {
      setLoading(false)
    }
  }

  const toggleRole = (roleId: string) => {
    setSelectedRoles(prev =>
      prev.includes(roleId)
        ? prev.filter(id => id !== roleId)
        : [...prev, roleId]
    )
  }

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
        <div className="p-6 border-b border-[var(--border-subtle)]">
          <h2 className="text-xl font-semibold text-[var(--text-primary)]">
            {group ? '编辑群组' : '创建群组'}
          </h2>
        </div>

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

          {/* 群组名称 */}
          <div>
            <label className="block text-sm font-medium text-[var(--text-secondary)] mb-2">
              群组名称 <span className="text-[var(--nexus-error)]">*</span>
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
              placeholder="输入群组名称"
              required
            />
          </div>

          {/* 描述 */}
          <div>
            <label className="block text-sm font-medium text-[var(--text-secondary)] mb-2">
              描述
            </label>
            <textarea
              value={description}
              onChange={(e) => setDescription(e.target.value)}
              className="w-full px-4 py-3 rounded-xl text-[var(--text-primary)] placeholder-[var(--text-tertiary)] focus:outline-none focus:ring-2 focus:ring-[var(--nexus-cyan)]/50 resize-none"
              style={{
                background: 'var(--nexus-deep)',
                border: '1px solid var(--border-default)',
              }}
              placeholder="群组描述（可选）"
              rows={3}
            />
          </div>

          {/* 默认群组 */}
          <div className="flex items-center gap-3">
            <button
              type="button"
              onClick={() => setIsDefault(!isDefault)}
              className={`relative w-12 h-6 rounded-full transition-colors ${
                isDefault ? 'bg-[var(--nexus-cyan)]' : 'bg-[var(--nexus-surface)]'
              }`}
            >
              <span
                className={`absolute top-1 w-4 h-4 rounded-full bg-white transition-transform ${
                  isDefault ? 'left-7' : 'left-1'
                }`}
              />
            </button>
            <span className="text-sm text-[var(--text-secondary)]">
              设为默认群组（新注册用户自动加入）
            </span>
          </div>

          {/* 角色选择 */}
          <div>
            <label className="block text-sm font-medium text-[var(--text-secondary)] mb-2">
              分配角色
            </label>
            <div className="space-y-2 max-h-48 overflow-y-auto p-1">
              {roles.map(role => (
                <button
                  key={role.id}
                  type="button"
                  onClick={() => toggleRole(role.id)}
                  className={`w-full flex items-center gap-3 p-3 rounded-xl transition-colors ${
                    selectedRoles.includes(role.id)
                      ? 'bg-[rgba(0,212,255,0.1)] border border-[var(--nexus-cyan)]'
                      : 'bg-[var(--nexus-surface)] border border-transparent hover:border-[var(--border-default)]'
                  }`}
                >
                  <div
                    className={`w-5 h-5 rounded flex items-center justify-center ${
                      selectedRoles.includes(role.id)
                        ? 'bg-[var(--nexus-cyan)]'
                        : 'bg-[var(--nexus-deep)] border border-[var(--border-default)]'
                    }`}
                  >
                    {selectedRoles.includes(role.id) && (
                      <svg className="w-3 h-3 text-white" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={3} d="M5 13l4 4L19 7" />
                      </svg>
                    )}
                  </div>
                  <div className="text-left">
                    <p className="text-sm font-medium text-[var(--text-primary)]">{role.name}</p>
                    {role.description && (
                      <p className="text-xs text-[var(--text-tertiary)]">{role.description}</p>
                    )}
                  </div>
                  {role.is_system && (
                    <span className="ml-auto px-2 py-0.5 rounded text-xs bg-[rgba(139,92,246,0.1)] text-[var(--nexus-purple)]">
                      系统
                    </span>
                  )}
                </button>
              ))}
              {roles.length === 0 && (
                <p className="text-sm text-[var(--text-tertiary)] text-center py-4">暂无可用角色</p>
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
              {loading ? '处理中...' : group ? '保存更改' : '创建群组'}
            </button>
          </div>
        </form>
      </motion.div>
    </div>
  )
}

// 群组成员对话框
function MembersDialog({
  isOpen,
  onClose,
  group,
  members,
  loading,
}: {
  isOpen: boolean
  onClose: () => void
  group: Group | null
  members: User[]
  loading: boolean
}) {
  if (!isOpen || !group) return null

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
        initial={{ opacity: 0, scale: 0.95, y: 20 }}
        animate={{ opacity: 1, scale: 1, y: 0 }}
        exit={{ opacity: 0, scale: 0.95, y: 20 }}
        className="relative w-full max-w-md rounded-2xl overflow-hidden"
        style={{
          background: 'rgba(17, 24, 39, 0.95)',
          backdropFilter: 'blur(20px)',
          border: '1px solid var(--border-default)',
        }}
      >
        <div className="p-6 border-b border-[var(--border-subtle)]">
          <h2 className="text-xl font-semibold text-[var(--text-primary)]">
            {group.name} - 成员列表
          </h2>
        </div>

        <div className="p-4 max-h-96 overflow-y-auto">
          {loading ? (
            <div className="py-8 flex items-center justify-center">
              <div
                className="w-6 h-6 rounded-full border-2 border-t-transparent animate-spin"
                style={{ borderColor: 'var(--nexus-cyan)', borderTopColor: 'transparent' }}
              />
            </div>
          ) : members.length === 0 ? (
            <p className="text-center text-[var(--text-tertiary)] py-8">该群组暂无成员</p>
          ) : (
            <div className="space-y-2">
              {members.map(member => (
                <div
                  key={member.id}
                  className="flex items-center gap-3 p-3 rounded-xl bg-[var(--nexus-surface)]"
                >
                  <div
                    className="w-8 h-8 rounded-full flex items-center justify-center text-white text-sm font-medium"
                    style={{ background: 'var(--gradient-neural)' }}
                  >
                    {member.name?.charAt(0).toUpperCase() || 'U'}
                  </div>
                  <div className="flex-1 min-w-0">
                    <p className="text-sm font-medium text-[var(--text-primary)] truncate">
                      {member.name}
                    </p>
                    <p className="text-xs text-[var(--text-tertiary)] truncate">{member.email}</p>
                  </div>
                </div>
              ))}
            </div>
          )}
        </div>

        <div className="p-4 border-t border-[var(--border-subtle)]">
          <button
            onClick={onClose}
            className="w-full py-2.5 rounded-xl font-medium text-[var(--text-secondary)] hover:bg-[var(--nexus-surface)] transition-colors"
          >
            关闭
          </button>
        </div>
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

export default function GroupsPage() {
  const [groups, setGroups] = useState<PaginatedResponse<Group> | null>(null)
  const [roles, setRoles] = useState<Role[]>([])
  const [loading, setLoading] = useState(true)
  const [search, setSearch] = useState('')
  const [page, setPage] = useState(1)
  const [formOpen, setFormOpen] = useState(false)
  const [editingGroup, setEditingGroup] = useState<Group | null>(null)
  const [deleteTarget, setDeleteTarget] = useState<Group | null>(null)
  const [deleteLoading, setDeleteLoading] = useState(false)
  const [membersGroup, setMembersGroup] = useState<Group | null>(null)
  const [members, setMembers] = useState<User[]>([])
  const [membersLoading, setMembersLoading] = useState(false)
  const { hasPermission } = useAuthStore()

  const canCreate = hasPermission('group:create')
  const canUpdate = hasPermission('group:update')
  const canDelete = hasPermission('group:delete')

  const fetchGroups = useCallback(async () => {
    setLoading(true)
    try {
      const [groupsData, rolesData] = await Promise.all([
        getGroups({ page, page_size: 10, search: search || undefined }),
        getRoles({ page: 1, page_size: 100 }),
      ])
      setGroups(groupsData)
      setRoles(rolesData.items)
    } catch (err) {
      console.error('Failed to fetch groups:', err)
    } finally {
      setLoading(false)
    }
  }, [page, search])

  useEffect(() => {
    fetchGroups()
  }, [fetchGroups])

  const fetchMembers = async (group: Group) => {
    setMembersGroup(group)
    setMembersLoading(true)
    try {
      const data = await getGroupMembers(group.id)
      setMembers(data)
    } catch (err) {
      console.error('Failed to fetch members:', err)
    } finally {
      setMembersLoading(false)
    }
  }

  const handleSearch = (e: React.FormEvent) => {
    e.preventDefault()
    setPage(1)
    fetchGroups()
  }

  const handleCreateOrUpdate = async (data: {
    name: string
    description: string
    is_default: boolean
    role_ids: string[]
  }) => {
    if (editingGroup) {
      // 更新群组
      await updateGroup(editingGroup.id, {
        name: data.name,
        description: data.description,
        is_default: data.is_default,
      })

      // 更新角色关联
      const currentRoles = editingGroup.roles?.map(r => r.id) || []
      const toAdd = data.role_ids.filter(id => !currentRoles.includes(id))
      const toRemove = currentRoles.filter(id => !data.role_ids.includes(id))

      for (const roleId of toAdd) {
        await addRoleToGroup(editingGroup.id, roleId)
      }
      for (const roleId of toRemove) {
        await removeRoleFromGroup(editingGroup.id, roleId)
      }
    } else {
      // 创建群组
      const newGroup = await createGroup({
        name: data.name,
        description: data.description,
        is_default: data.is_default,
      })

      // 添加角色
      for (const roleId of data.role_ids) {
        await addRoleToGroup(newGroup.id, roleId)
      }
    }

    await fetchGroups()
  }

  const handleDelete = async () => {
    if (!deleteTarget) return

    setDeleteLoading(true)
    try {
      await deleteGroup(deleteTarget.id)
      setDeleteTarget(null)
      await fetchGroups()
    } catch (err) {
      console.error('Failed to delete group:', err)
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
        <h1 className="text-2xl font-bold text-[var(--text-primary)]">群组管理</h1>
        <p className="text-[var(--text-secondary)] mt-1">管理用户群组和角色分配</p>
      </motion.div>

      {/* 工具栏 */}
      <motion.div
        initial={{ opacity: 0, y: 10 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ delay: 0.1 }}
        className="flex flex-col sm:flex-row gap-4 mb-6"
      >
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
              placeholder="搜索群组名称..."
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

        {canCreate && (
          <button
            onClick={() => {
              setEditingGroup(null)
              setFormOpen(true)
            }}
            className="px-4 py-2.5 rounded-xl font-medium text-white flex items-center gap-2 transition-all hover:scale-105"
            style={{ background: 'var(--gradient-neural)' }}
          >
            <svg className="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 4v16m8-8H4" />
            </svg>
            创建群组
          </button>
        )}
      </motion.div>

      {/* 群组列表 - 卡片布局 */}
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ delay: 0.2 }}
        className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4"
      >
        {loading ? (
          <div className="col-span-full py-12 flex items-center justify-center">
            <div
              className="w-8 h-8 rounded-full border-2 border-t-transparent animate-spin"
              style={{ borderColor: 'var(--nexus-cyan)', borderTopColor: 'transparent' }}
            />
          </div>
        ) : groups?.items.length === 0 ? (
          <div className="col-span-full py-12 text-center">
            <svg
              className="w-16 h-16 mx-auto text-[var(--text-tertiary)] mb-4"
              fill="none"
              viewBox="0 0 24 24"
              stroke="currentColor"
            >
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1} d="M17 20h5v-2a3 3 0 00-5.356-1.857M17 20H7m10 0v-2c0-.656-.126-1.283-.356-1.857M7 20H2v-2a3 3 0 015.356-1.857M7 20v-2c0-.656.126-1.283.356-1.857m0 0a5.002 5.002 0 019.288 0" />
            </svg>
            <p className="text-[var(--text-tertiary)]">暂无群组数据</p>
          </div>
        ) : (
          groups?.items.map((group, index) => (
            <motion.div
              key={group.id}
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: index * 0.05 }}
              className="rounded-2xl p-5 transition-all hover:scale-[1.02]"
              style={{
                background: 'rgba(17, 24, 39, 0.6)',
                backdropFilter: 'blur(20px)',
                border: '1px solid var(--border-default)',
              }}
            >
              {/* 群组头部 */}
              <div className="flex items-start justify-between mb-4">
                <div className="flex items-center gap-3">
                  <div
                    className="w-10 h-10 rounded-xl flex items-center justify-center"
                    style={{ background: 'var(--gradient-neural)' }}
                  >
                    <svg className="w-5 h-5 text-white" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M17 20h5v-2a3 3 0 00-5.356-1.857M17 20H7m10 0v-2c0-.656-.126-1.283-.356-1.857M7 20H2v-2a3 3 0 015.356-1.857M7 20v-2c0-.656.126-1.283.356-1.857m0 0a5.002 5.002 0 019.288 0" />
                    </svg>
                  </div>
                  <div>
                    <h3 className="font-semibold text-[var(--text-primary)]">{group.name}</h3>
                    {group.is_default && (
                      <span className="text-xs text-[var(--nexus-cyan)]">默认群组</span>
                    )}
                  </div>
                </div>

                <div className="flex gap-1">
                  {canUpdate && (
                    <button
                      onClick={() => {
                        setEditingGroup(group)
                        setFormOpen(true)
                      }}
                      className="p-1.5 rounded-lg text-[var(--text-tertiary)] hover:text-[var(--nexus-cyan)] hover:bg-[rgba(0,212,255,0.1)] transition-colors"
                    >
                      <svg className="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M11 5H6a2 2 0 00-2 2v11a2 2 0 002 2h11a2 2 0 002-2v-5m-1.414-9.414a2 2 0 112.828 2.828L11.828 15H9v-2.828l8.586-8.586z" />
                      </svg>
                    </button>
                  )}
                  {canDelete && !group.is_default && (
                    <button
                      onClick={() => setDeleteTarget(group)}
                      className="p-1.5 rounded-lg text-[var(--text-tertiary)] hover:text-[var(--nexus-error)] hover:bg-[rgba(239,68,68,0.1)] transition-colors"
                    >
                      <svg className="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16" />
                      </svg>
                    </button>
                  )}
                </div>
              </div>

              {/* 描述 */}
              {group.description && (
                <p className="text-sm text-[var(--text-tertiary)] mb-4 line-clamp-2">
                  {group.description}
                </p>
              )}

              {/* 角色标签 */}
              <div className="mb-4">
                <p className="text-xs text-[var(--text-tertiary)] mb-2">分配的角色</p>
                <div className="flex flex-wrap gap-1.5">
                  {group.roles?.slice(0, 3).map(role => (
                    <span
                      key={role.id}
                      className="px-2 py-0.5 rounded text-xs bg-[var(--nexus-surface)] text-[var(--text-secondary)]"
                    >
                      {role.name}
                    </span>
                  ))}
                  {(group.roles?.length || 0) > 3 && (
                    <span className="text-xs text-[var(--text-tertiary)]">
                      +{(group.roles?.length || 0) - 3}
                    </span>
                  )}
                  {!group.roles?.length && (
                    <span className="text-xs text-[var(--text-tertiary)]">暂无角色</span>
                  )}
                </div>
              </div>

              {/* 成员数量和查看按钮 */}
              <div className="flex items-center justify-between pt-3 border-t border-[var(--border-subtle)]">
                <span className="text-sm text-[var(--text-tertiary)]">
                  {group.user_count ?? 0} 个成员
                </span>
                <button
                  onClick={() => fetchMembers(group)}
                  className="text-sm text-[var(--nexus-cyan)] hover:text-[var(--nexus-blue)] transition-colors"
                >
                  查看成员
                </button>
              </div>
            </motion.div>
          ))
        )}
      </motion.div>

      {/* 分页 */}
      {groups && groups.total_pages > 1 && (
        <div className="mt-6 flex items-center justify-center gap-2">
          <button
            onClick={() => setPage(p => Math.max(1, p - 1))}
            disabled={page === 1}
            className="px-4 py-2 rounded-lg text-sm font-medium text-[var(--text-secondary)] hover:bg-[var(--nexus-surface)] disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
          >
            上一页
          </button>
          <span className="text-sm text-[var(--text-tertiary)]">
            {page} / {groups.total_pages}
          </span>
          <button
            onClick={() => setPage(p => Math.min(groups.total_pages, p + 1))}
            disabled={page === groups.total_pages}
            className="px-4 py-2 rounded-lg text-sm font-medium text-[var(--text-secondary)] hover:bg-[var(--nexus-surface)] disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
          >
            下一页
          </button>
        </div>
      )}

      {/* 群组表单对话框 */}
      <AnimatePresence>
        {formOpen && (
          <GroupFormDialog
            isOpen={formOpen}
            onClose={() => {
              setFormOpen(false)
              setEditingGroup(null)
            }}
            group={editingGroup}
            roles={roles}
            onSubmit={handleCreateOrUpdate}
          />
        )}
      </AnimatePresence>

      {/* 成员列表对话框 */}
      <AnimatePresence>
        {membersGroup && (
          <MembersDialog
            isOpen={!!membersGroup}
            onClose={() => {
              setMembersGroup(null)
              setMembers([])
            }}
            group={membersGroup}
            members={members}
            loading={membersLoading}
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
            title="确认删除群组"
            message={`确定要删除群组 "${deleteTarget.name}" 吗？该群组下的用户将失去相应的权限。`}
            loading={deleteLoading}
          />
        )}
      </AnimatePresence>
    </div>
  )
}
