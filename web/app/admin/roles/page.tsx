'use client'

import { useEffect, useState, useCallback } from 'react'
import { motion, AnimatePresence } from 'framer-motion'
import {
  getRoles,
  getPermissions,
  createRole,
  updateRole,
  deleteRole,
  addPermissionToRole,
  removePermissionFromRole,
  type Role,
  type Permission,
  type PaginatedResponse,
} from '@/lib/admin/api'
import { useAuthStore } from '@/lib/stores/auth'

// 权限分类
const PERMISSION_CATEGORIES: Record<string, string> = {
  user: '用户管理',
  group: '群组管理',
  role: '角色管理',
  chat: '聊天功能',
  report: '报告管理',
  system: '系统设置',
}

// 角色表单对话框
function RoleFormDialog({
  isOpen,
  onClose,
  role,
  permissions,
  onSubmit,
}: {
  isOpen: boolean
  onClose: () => void
  role: Role | null
  permissions: Permission[]
  onSubmit: (data: { name: string; description: string; permission_ids: string[] }) => Promise<void>
}) {
  const [name, setName] = useState('')
  const [description, setDescription] = useState('')
  const [selectedPermissions, setSelectedPermissions] = useState<string[]>([])
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState('')

  useEffect(() => {
    if (role) {
      setName(role.name)
      setDescription(role.description || '')
      setSelectedPermissions(role.permissions?.map(p => p.id) || [])
    } else {
      setName('')
      setDescription('')
      setSelectedPermissions([])
    }
    setError('')
  }, [role, isOpen])

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    setError('')
    setLoading(true)

    try {
      await onSubmit({
        name,
        description,
        permission_ids: selectedPermissions,
      })
      onClose()
    } catch (err) {
      setError(err instanceof Error ? err.message : '操作失败')
    } finally {
      setLoading(false)
    }
  }

  const togglePermission = (permissionId: string) => {
    setSelectedPermissions(prev =>
      prev.includes(permissionId)
        ? prev.filter(id => id !== permissionId)
        : [...prev, permissionId]
    )
  }

  const toggleCategory = (category: string) => {
    const categoryPermissions = permissions
      .filter(p => p.category === category)
      .map(p => p.id)

    const allSelected = categoryPermissions.every(id => selectedPermissions.includes(id))

    if (allSelected) {
      setSelectedPermissions(prev => prev.filter(id => !categoryPermissions.includes(id)))
    } else {
      setSelectedPermissions(prev => [...new Set([...prev, ...categoryPermissions])])
    }
  }

  // 按分类组织权限
  const permissionsByCategory = permissions.reduce((acc, permission) => {
    const category = permission.category
    if (!acc[category]) {
      acc[category] = []
    }
    acc[category].push(permission)
    return acc
  }, {} as Record<string, Permission[]>)

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
        className="relative w-full max-w-2xl max-h-[90vh] rounded-2xl overflow-hidden flex flex-col"
        style={{
          background: 'rgba(17, 24, 39, 0.95)',
          backdropFilter: 'blur(20px)',
          border: '1px solid var(--border-default)',
        }}
      >
        <div className="p-6 border-b border-[var(--border-subtle)] flex-shrink-0">
          <h2 className="text-xl font-semibold text-[var(--text-primary)]">
            {role ? '编辑角色' : '创建角色'}
          </h2>
        </div>

        <form onSubmit={handleSubmit} className="flex flex-col flex-1 overflow-hidden">
          <div className="p-6 space-y-5 overflow-y-auto flex-1">
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

            {/* 角色名称 */}
            <div>
              <label className="block text-sm font-medium text-[var(--text-secondary)] mb-2">
                角色名称 <span className="text-[var(--nexus-error)]">*</span>
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
                placeholder="输入角色名称"
                required
                disabled={role?.is_system}
              />
              {role?.is_system && (
                <p className="text-xs text-[var(--text-tertiary)] mt-1">系统角色名称不可修改</p>
              )}
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
                placeholder="角色描述（可选）"
                rows={2}
              />
            </div>

            {/* 权限选择 */}
            <div>
              <label className="block text-sm font-medium text-[var(--text-secondary)] mb-3">
                分配权限
              </label>
              <div className="space-y-4">
                {Object.entries(permissionsByCategory).map(([category, categoryPermissions]) => {
                  const allSelected = categoryPermissions.every(p =>
                    selectedPermissions.includes(p.id)
                  )
                  const someSelected = categoryPermissions.some(p =>
                    selectedPermissions.includes(p.id)
                  )

                  return (
                    <div
                      key={category}
                      className="rounded-xl overflow-hidden"
                      style={{
                        background: 'var(--nexus-surface)',
                        border: '1px solid var(--border-subtle)',
                      }}
                    >
                      {/* 分类标题 */}
                      <button
                        type="button"
                        onClick={() => toggleCategory(category)}
                        className="w-full flex items-center gap-3 p-3 hover:bg-[var(--nexus-deep)] transition-colors"
                      >
                        <div
                          className={`w-5 h-5 rounded flex items-center justify-center ${
                            allSelected
                              ? 'bg-[var(--nexus-cyan)]'
                              : someSelected
                              ? 'bg-[var(--nexus-cyan)]/50'
                              : 'bg-[var(--nexus-deep)] border border-[var(--border-default)]'
                          }`}
                        >
                          {(allSelected || someSelected) && (
                            <svg
                              className="w-3 h-3 text-white"
                              fill="none"
                              viewBox="0 0 24 24"
                              stroke="currentColor"
                            >
                              <path
                                strokeLinecap="round"
                                strokeLinejoin="round"
                                strokeWidth={3}
                                d={someSelected && !allSelected ? 'M5 12h14' : 'M5 13l4 4L19 7'}
                              />
                            </svg>
                          )}
                        </div>
                        <span className="font-medium text-[var(--text-primary)]">
                          {PERMISSION_CATEGORIES[category] || category}
                        </span>
                        <span className="text-xs text-[var(--text-tertiary)] ml-auto">
                          {categoryPermissions.filter(p => selectedPermissions.includes(p.id)).length}
                          /{categoryPermissions.length}
                        </span>
                      </button>

                      {/* 权限列表 */}
                      <div className="px-3 pb-3 grid grid-cols-2 gap-2">
                        {categoryPermissions.map(permission => (
                          <button
                            key={permission.id}
                            type="button"
                            onClick={() => togglePermission(permission.id)}
                            className={`flex items-center gap-2 p-2 rounded-lg text-left transition-colors ${
                              selectedPermissions.includes(permission.id)
                                ? 'bg-[rgba(0,212,255,0.1)]'
                                : 'hover:bg-[var(--nexus-deep)]'
                            }`}
                          >
                            <div
                              className={`w-4 h-4 rounded flex-shrink-0 flex items-center justify-center ${
                                selectedPermissions.includes(permission.id)
                                  ? 'bg-[var(--nexus-cyan)]'
                                  : 'bg-[var(--nexus-deep)] border border-[var(--border-default)]'
                              }`}
                            >
                              {selectedPermissions.includes(permission.id) && (
                                <svg
                                  className="w-2.5 h-2.5 text-white"
                                  fill="none"
                                  viewBox="0 0 24 24"
                                  stroke="currentColor"
                                >
                                  <path
                                    strokeLinecap="round"
                                    strokeLinejoin="round"
                                    strokeWidth={3}
                                    d="M5 13l4 4L19 7"
                                  />
                                </svg>
                              )}
                            </div>
                            <div className="min-w-0">
                              <p className="text-sm text-[var(--text-primary)] truncate">
                                {permission.name}
                              </p>
                              <p className="text-xs text-[var(--text-tertiary)] truncate">
                                {permission.code}
                              </p>
                            </div>
                          </button>
                        ))}
                      </div>
                    </div>
                  )
                })}
                {Object.keys(permissionsByCategory).length === 0 && (
                  <p className="text-sm text-[var(--text-tertiary)] text-center py-4">
                    暂无可用权限
                  </p>
                )}
              </div>
            </div>
          </div>

          {/* 操作按钮 */}
          <div className="p-6 border-t border-[var(--border-subtle)] flex gap-3 flex-shrink-0">
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
              {loading ? '处理中...' : role ? '保存更改' : '创建角色'}
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

export default function RolesPage() {
  const [roles, setRoles] = useState<PaginatedResponse<Role> | null>(null)
  const [permissions, setPermissions] = useState<Permission[]>([])
  const [loading, setLoading] = useState(true)
  const [search, setSearch] = useState('')
  const [page, setPage] = useState(1)
  const [formOpen, setFormOpen] = useState(false)
  const [editingRole, setEditingRole] = useState<Role | null>(null)
  const [deleteTarget, setDeleteTarget] = useState<Role | null>(null)
  const [deleteLoading, setDeleteLoading] = useState(false)
  const [expandedRole, setExpandedRole] = useState<string | null>(null)
  const { hasPermission } = useAuthStore()

  const canCreate = hasPermission('role:create')
  const canUpdate = hasPermission('role:update')
  const canDelete = hasPermission('role:delete')

  const fetchRoles = useCallback(async () => {
    setLoading(true)
    try {
      const [rolesData, permissionsData] = await Promise.all([
        getRoles({ page, page_size: 10, search: search || undefined }),
        getPermissions(),
      ])
      setRoles(rolesData)
      setPermissions(permissionsData)
    } catch (err) {
      console.error('Failed to fetch roles:', err)
    } finally {
      setLoading(false)
    }
  }, [page, search])

  useEffect(() => {
    fetchRoles()
  }, [fetchRoles])

  const handleSearch = (e: React.FormEvent) => {
    e.preventDefault()
    setPage(1)
    fetchRoles()
  }

  const handleCreateOrUpdate = async (data: {
    name: string
    description: string
    permission_ids: string[]
  }) => {
    if (editingRole) {
      // 更新角色
      await updateRole(editingRole.id, {
        name: data.name,
        description: data.description,
      })

      // 更新权限关联
      const currentPermissions = editingRole.permissions?.map(p => p.id) || []
      const toAdd = data.permission_ids.filter(id => !currentPermissions.includes(id))
      const toRemove = currentPermissions.filter(id => !data.permission_ids.includes(id))

      for (const permissionId of toAdd) {
        await addPermissionToRole(editingRole.id, permissionId)
      }
      for (const permissionId of toRemove) {
        await removePermissionFromRole(editingRole.id, permissionId)
      }
    } else {
      // 创建角色
      const newRole = await createRole({
        name: data.name,
        description: data.description,
      })

      // 添加权限
      for (const permissionId of data.permission_ids) {
        await addPermissionToRole(newRole.id, permissionId)
      }
    }

    await fetchRoles()
  }

  const handleDelete = async () => {
    if (!deleteTarget) return

    setDeleteLoading(true)
    try {
      await deleteRole(deleteTarget.id)
      setDeleteTarget(null)
      await fetchRoles()
    } catch (err) {
      console.error('Failed to delete role:', err)
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
        <h1 className="text-2xl font-bold text-[var(--text-primary)]">角色权限管理</h1>
        <p className="text-[var(--text-secondary)] mt-1">管理系统角色和权限分配</p>
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
              placeholder="搜索角色名称..."
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
              setEditingRole(null)
              setFormOpen(true)
            }}
            className="px-4 py-2.5 rounded-xl font-medium text-white flex items-center gap-2 transition-all hover:scale-105"
            style={{ background: 'var(--gradient-neural)' }}
          >
            <svg className="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 4v16m8-8H4" />
            </svg>
            创建角色
          </button>
        )}
      </motion.div>

      {/* 角色列表 */}
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ delay: 0.2 }}
        className="space-y-4"
      >
        {loading ? (
          <div className="py-12 flex items-center justify-center">
            <div
              className="w-8 h-8 rounded-full border-2 border-t-transparent animate-spin"
              style={{ borderColor: 'var(--nexus-cyan)', borderTopColor: 'transparent' }}
            />
          </div>
        ) : roles?.items.length === 0 ? (
          <div className="py-12 text-center rounded-2xl" style={{ background: 'rgba(17, 24, 39, 0.6)', border: '1px solid var(--border-default)' }}>
            <svg
              className="w-16 h-16 mx-auto text-[var(--text-tertiary)] mb-4"
              fill="none"
              viewBox="0 0 24 24"
              stroke="currentColor"
            >
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1} d="M9 12l2 2 4-4m5.618-4.016A11.955 11.955 0 0112 2.944a11.955 11.955 0 01-8.618 3.04A12.02 12.02 0 003 9c0 5.591 3.824 10.29 9 11.622 5.176-1.332 9-6.03 9-11.622 0-1.042-.133-2.052-.382-3.016z" />
            </svg>
            <p className="text-[var(--text-tertiary)]">暂无角色数据</p>
          </div>
        ) : (
          roles?.items.map((role, index) => (
            <motion.div
              key={role.id}
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: index * 0.05 }}
              className="rounded-2xl overflow-hidden"
              style={{
                background: 'rgba(17, 24, 39, 0.6)',
                backdropFilter: 'blur(20px)',
                border: '1px solid var(--border-default)',
              }}
            >
              {/* 角色头部 */}
              <div className="p-4 flex items-center gap-4">
                <div
                  className="w-12 h-12 rounded-xl flex items-center justify-center flex-shrink-0"
                  style={{ background: role.is_system ? 'linear-gradient(135deg, #8b5cf6 0%, #7c3aed 100%)' : 'var(--gradient-neural)' }}
                >
                  <svg className="w-6 h-6 text-white" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M9 12l2 2 4-4m5.618-4.016A11.955 11.955 0 0112 2.944a11.955 11.955 0 01-8.618 3.04A12.02 12.02 0 003 9c0 5.591 3.824 10.29 9 11.622 5.176-1.332 9-6.03 9-11.622 0-1.042-.133-2.052-.382-3.016z" />
                  </svg>
                </div>

                <div className="flex-1 min-w-0">
                  <div className="flex items-center gap-2">
                    <h3 className="font-semibold text-[var(--text-primary)]">{role.name}</h3>
                    {role.is_system && (
                      <span className="px-2 py-0.5 rounded text-xs bg-[rgba(139,92,246,0.1)] text-[var(--nexus-purple)]">
                        系统角色
                      </span>
                    )}
                  </div>
                  {role.description && (
                    <p className="text-sm text-[var(--text-tertiary)] truncate">{role.description}</p>
                  )}
                </div>

                <div className="flex items-center gap-2">
                  <button
                    onClick={() => setExpandedRole(expandedRole === role.id ? null : role.id)}
                    className="px-3 py-1.5 rounded-lg text-sm text-[var(--text-secondary)] hover:bg-[var(--nexus-surface)] transition-colors flex items-center gap-1"
                  >
                    <span>{role.permissions?.length || 0} 个权限</span>
                    <svg
                      className={`w-4 h-4 transition-transform ${expandedRole === role.id ? 'rotate-180' : ''}`}
                      fill="none"
                      viewBox="0 0 24 24"
                      stroke="currentColor"
                    >
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 9l-7 7-7-7" />
                    </svg>
                  </button>

                  {canUpdate && (
                    <button
                      onClick={() => {
                        setEditingRole(role)
                        setFormOpen(true)
                      }}
                      className="p-2 rounded-lg text-[var(--text-tertiary)] hover:text-[var(--nexus-cyan)] hover:bg-[rgba(0,212,255,0.1)] transition-colors"
                    >
                      <svg className="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M11 5H6a2 2 0 00-2 2v11a2 2 0 002 2h11a2 2 0 002-2v-5m-1.414-9.414a2 2 0 112.828 2.828L11.828 15H9v-2.828l8.586-8.586z" />
                      </svg>
                    </button>
                  )}

                  {canDelete && !role.is_system && (
                    <button
                      onClick={() => setDeleteTarget(role)}
                      className="p-2 rounded-lg text-[var(--text-tertiary)] hover:text-[var(--nexus-error)] hover:bg-[rgba(239,68,68,0.1)] transition-colors"
                    >
                      <svg className="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16" />
                      </svg>
                    </button>
                  )}
                </div>
              </div>

              {/* 权限列表（展开） */}
              <AnimatePresence>
                {expandedRole === role.id && (
                  <motion.div
                    initial={{ height: 0, opacity: 0 }}
                    animate={{ height: 'auto', opacity: 1 }}
                    exit={{ height: 0, opacity: 0 }}
                    transition={{ duration: 0.2 }}
                    className="overflow-hidden"
                  >
                    <div className="px-4 pb-4 pt-2 border-t border-[var(--border-subtle)]">
                      {role.permissions && role.permissions.length > 0 ? (
                        <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-4 gap-2">
                          {role.permissions.map(permission => (
                            <div
                              key={permission.id}
                              className="px-3 py-2 rounded-lg bg-[var(--nexus-surface)]"
                            >
                              <p className="text-sm text-[var(--text-primary)]">{permission.name}</p>
                              <p className="text-xs text-[var(--text-tertiary)]">{permission.code}</p>
                            </div>
                          ))}
                        </div>
                      ) : (
                        <p className="text-sm text-[var(--text-tertiary)] text-center py-4">
                          该角色暂无任何权限
                        </p>
                      )}
                    </div>
                  </motion.div>
                )}
              </AnimatePresence>
            </motion.div>
          ))
        )}
      </motion.div>

      {/* 分页 */}
      {roles && roles.total_pages > 1 && (
        <div className="mt-6 flex items-center justify-center gap-2">
          <button
            onClick={() => setPage(p => Math.max(1, p - 1))}
            disabled={page === 1}
            className="px-4 py-2 rounded-lg text-sm font-medium text-[var(--text-secondary)] hover:bg-[var(--nexus-surface)] disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
          >
            上一页
          </button>
          <span className="text-sm text-[var(--text-tertiary)]">
            {page} / {roles.total_pages}
          </span>
          <button
            onClick={() => setPage(p => Math.min(roles.total_pages, p + 1))}
            disabled={page === roles.total_pages}
            className="px-4 py-2 rounded-lg text-sm font-medium text-[var(--text-secondary)] hover:bg-[var(--nexus-surface)] disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
          >
            下一页
          </button>
        </div>
      )}

      {/* 角色表单对话框 */}
      <AnimatePresence>
        {formOpen && (
          <RoleFormDialog
            isOpen={formOpen}
            onClose={() => {
              setFormOpen(false)
              setEditingRole(null)
            }}
            role={editingRole}
            permissions={permissions}
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
            title="确认删除角色"
            message={`确定要删除角色 "${deleteTarget.name}" 吗？拥有此角色的群组将失去相应权限。`}
            loading={deleteLoading}
          />
        )}
      </AnimatePresence>
    </div>
  )
}
