'use client'

import { API_ENDPOINTS, buildUrl } from '@/lib/config'
import { useAuthStore } from '@/lib/stores/auth'

// ============= 类型定义 =============

export interface User {
  id: string
  name: string
  email: string
  role: string
  profile_image_url?: string
  is_active: boolean
  is_superadmin: boolean
  created_at: string
  updated_at?: string
  groups?: Group[]
}

export interface Group {
  id: string
  name: string
  description?: string
  is_default: boolean
  created_at: string
  updated_at?: string
  roles?: Role[]
  user_count?: number
}

export interface Role {
  id: string
  name: string
  description?: string
  is_system: boolean
  created_at: string
  permissions?: Permission[]
}

export interface Permission {
  id: string
  code: string
  name: string
  description?: string
  category: string
}

export interface PaginatedResponse<T> {
  items: T[]
  total: number
  page: number
  page_size: number
  total_pages: number
}

export interface DashboardStats {
  total_users: number
  active_users: number
  total_groups: number
  total_roles: number
  recent_users: User[]
}

// ============= 基础请求函数 =============

async function authFetch<T>(
  url: string,
  options: RequestInit = {}
): Promise<T> {
  const accessToken = useAuthStore.getState().accessToken

  const response = await fetch(url, {
    ...options,
    headers: {
      'Content-Type': 'application/json',
      ...(accessToken && { Authorization: `Bearer ${accessToken}` }),
      ...options.headers,
    },
  })

  if (!response.ok) {
    const error = await response.json().catch(() => ({}))
    throw new Error(error.detail || `请求失败: ${response.status}`)
  }

  return response.json()
}

// ============= 仪表盘 API =============

export async function getDashboardStats(): Promise<DashboardStats> {
  // 并行获取统计数据
  const [usersRes, groupsRes, rolesRes] = await Promise.all([
    authFetch<PaginatedResponse<User>>(buildUrl(`${API_ENDPOINTS.users}`, { page: 1, page_size: 5 })),
    authFetch<PaginatedResponse<Group>>(buildUrl(`${API_ENDPOINTS.groups}`, { page: 1, page_size: 100 })),
    authFetch<PaginatedResponse<Role>>(buildUrl(`${API_ENDPOINTS.roles}`, { page: 1, page_size: 100 })),
  ])

  const activeUsers = usersRes.items.filter(u => u.is_active).length

  return {
    total_users: usersRes.total,
    active_users: activeUsers,
    total_groups: groupsRes.total,
    total_roles: rolesRes.total,
    recent_users: usersRes.items,
  }
}

// ============= 用户管理 API =============

export async function getUsers(params?: {
  page?: number
  page_size?: number
  search?: string
  is_active?: boolean
}): Promise<PaginatedResponse<User>> {
  return authFetch(buildUrl(API_ENDPOINTS.users, params))
}

export async function getUser(id: string): Promise<User> {
  return authFetch(`${API_ENDPOINTS.users}/${id}`)
}

export async function createUser(data: {
  name: string
  email: string
  password: string
  role?: string
  is_active?: boolean
}): Promise<User> {
  return authFetch(API_ENDPOINTS.users, {
    method: 'POST',
    body: JSON.stringify(data),
  })
}

export async function updateUser(
  id: string,
  data: {
    name?: string
    email?: string
    password?: string
    role?: string
    is_active?: boolean
  }
): Promise<User> {
  return authFetch(`${API_ENDPOINTS.users}/${id}`, {
    method: 'PUT',
    body: JSON.stringify(data),
  })
}

export async function deleteUser(id: string): Promise<void> {
  await authFetch(`${API_ENDPOINTS.users}/${id}`, { method: 'DELETE' })
}

export async function addUserToGroup(userId: string, groupId: string): Promise<void> {
  await authFetch(`${API_ENDPOINTS.users}/${userId}/groups/${groupId}`, {
    method: 'POST',
  })
}

export async function removeUserFromGroup(userId: string, groupId: string): Promise<void> {
  await authFetch(`${API_ENDPOINTS.users}/${userId}/groups/${groupId}`, {
    method: 'DELETE',
  })
}

// ============= 群组管理 API =============

export async function getGroups(params?: {
  page?: number
  page_size?: number
  search?: string
}): Promise<PaginatedResponse<Group>> {
  return authFetch(buildUrl(API_ENDPOINTS.groups, params))
}

export async function getGroup(id: string): Promise<Group> {
  return authFetch(`${API_ENDPOINTS.groups}/${id}`)
}

export async function createGroup(data: {
  name: string
  description?: string
  is_default?: boolean
}): Promise<Group> {
  return authFetch(API_ENDPOINTS.groups, {
    method: 'POST',
    body: JSON.stringify(data),
  })
}

export async function updateGroup(
  id: string,
  data: {
    name?: string
    description?: string
    is_default?: boolean
  }
): Promise<Group> {
  return authFetch(`${API_ENDPOINTS.groups}/${id}`, {
    method: 'PUT',
    body: JSON.stringify(data),
  })
}

export async function deleteGroup(id: string): Promise<void> {
  await authFetch(`${API_ENDPOINTS.groups}/${id}`, { method: 'DELETE' })
}

export async function addRoleToGroup(groupId: string, roleId: string): Promise<void> {
  await authFetch(`${API_ENDPOINTS.groups}/${groupId}/roles/${roleId}`, {
    method: 'POST',
  })
}

export async function removeRoleFromGroup(groupId: string, roleId: string): Promise<void> {
  await authFetch(`${API_ENDPOINTS.groups}/${groupId}/roles/${roleId}`, {
    method: 'DELETE',
  })
}

export async function getGroupMembers(groupId: string): Promise<User[]> {
  return authFetch(`${API_ENDPOINTS.groups}/${groupId}/members`)
}

// ============= 角色管理 API =============

export async function getRoles(params?: {
  page?: number
  page_size?: number
  search?: string
}): Promise<PaginatedResponse<Role>> {
  return authFetch(buildUrl(API_ENDPOINTS.roles, params))
}

export async function getRole(id: string): Promise<Role> {
  return authFetch(`${API_ENDPOINTS.roles}/${id}`)
}

export async function createRole(data: {
  name: string
  description?: string
}): Promise<Role> {
  return authFetch(API_ENDPOINTS.roles, {
    method: 'POST',
    body: JSON.stringify(data),
  })
}

export async function updateRole(
  id: string,
  data: {
    name?: string
    description?: string
  }
): Promise<Role> {
  return authFetch(`${API_ENDPOINTS.roles}/${id}`, {
    method: 'PUT',
    body: JSON.stringify(data),
  })
}

export async function deleteRole(id: string): Promise<void> {
  await authFetch(`${API_ENDPOINTS.roles}/${id}`, { method: 'DELETE' })
}

export async function addPermissionToRole(roleId: string, permissionId: string): Promise<void> {
  await authFetch(`${API_ENDPOINTS.roles}/${roleId}/permissions/${permissionId}`, {
    method: 'POST',
  })
}

export async function removePermissionFromRole(roleId: string, permissionId: string): Promise<void> {
  await authFetch(`${API_ENDPOINTS.roles}/${roleId}/permissions/${permissionId}`, {
    method: 'DELETE',
  })
}

// ============= 权限管理 API =============

export async function getPermissions(): Promise<Permission[]> {
  return authFetch(`${API_ENDPOINTS.roles}/permissions`)
}
