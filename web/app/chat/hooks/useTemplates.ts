'use client'

import { useState, useEffect, useCallback } from 'react'
import { createAuthHeaders } from '@/lib/api'
import { useAuthStore } from '@/lib/stores/auth'
import { API_ENDPOINTS, buildUrl } from '@/lib/config'

// 章节信息接口
export interface SectionInfo {
  title: string
  description?: string
  estimated_percentage?: number
  key_points?: string[]
}

// 写作模版接口
export interface WritingTemplate {
  id: string
  user_id: string
  title: string
  summary: string
  category?: string
  original_filename?: string
  markdown_content?: string
  writing_style: string
  writing_tone: string
  target_audience?: string
  sections?: SectionInfo[]
  status: 'pending' | 'parsing' | 'completed' | 'failed'
  error_message?: string
  scope: 'private' | 'shared' | 'public'
  usage_count: number
  created_at: string
  updated_at: string
}

// Hook 返回类型
export interface UseTemplatesReturn {
  templates: WritingTemplate[]
  loading: boolean
  error: string | null
  refetch: () => Promise<void>
  deleteTemplate: (templateId: string) => Promise<boolean>
  useTemplate: (templateId: string) => Promise<WritingTemplate | null>
  getTemplateById: (templateId: string) => Promise<WritingTemplate | null>
}

export function useTemplates(): UseTemplatesReturn {
  const [templates, setTemplates] = useState<WritingTemplate[]>([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)
  const { user } = useAuthStore()

  // 获取模版列表
  const fetchTemplates = useCallback(async () => {
    try {
      setLoading(true)
      setError(null)

      const url = buildUrl(API_ENDPOINTS.writingTemplates, {
        user_id: user?.id,
      })

      const response = await fetch(url, {
        headers: createAuthHeaders(),
      })

      if (!response.ok) {
        throw new Error(`获取模版列表失败: ${response.statusText}`)
      }

      const data = await response.json()
      // API 返回的是分页数据
      const templatesList = data.items || data.data || (Array.isArray(data) ? data : [])

      // 按更新时间降序排列
      templatesList.sort((a: WritingTemplate, b: WritingTemplate) =>
        new Date(b.updated_at).getTime() - new Date(a.updated_at).getTime()
      )

      setTemplates(templatesList)
    } catch (err: any) {
      console.error('Error fetching templates:', err)
      setError(err.message || '加载模版失败')
    } finally {
      setLoading(false)
    }
  }, [user?.id])

  // 删除模版
  const deleteTemplate = useCallback(async (templateId: string): Promise<boolean> => {
    try {
      const url = buildUrl(`${API_ENDPOINTS.writingTemplates}/${templateId}`, {
        user_id: user?.id,
      })

      const response = await fetch(url, {
        method: 'DELETE',
        headers: createAuthHeaders(),
      })

      if (!response.ok) {
        throw new Error('删除失败')
      }

      // 从本地状态移除
      setTemplates(prev => prev.filter(t => t.id !== templateId))
      return true
    } catch (err: any) {
      console.error('Error deleting template:', err)
      return false
    }
  }, [user?.id])

  // 使用模版（增加使用次数）
  const useTemplate = useCallback(async (templateId: string): Promise<WritingTemplate | null> => {
    try {
      const url = buildUrl(`${API_ENDPOINTS.writingTemplates}/${templateId}/use`, {
        user_id: user?.id,
      })

      const response = await fetch(url, {
        method: 'POST',
        headers: createAuthHeaders(),
      })

      if (!response.ok) {
        throw new Error('使用模版失败')
      }

      const result = await response.json()

      // 更新本地状态中的使用次数
      setTemplates(prev => prev.map(t =>
        t.id === templateId
          ? { ...t, usage_count: result.usage_count }
          : t
      ))

      // 返回更新后的模版
      const template = templates.find(t => t.id === templateId)
      return template ? { ...template, usage_count: result.usage_count } : null
    } catch (err: any) {
      console.error('Error using template:', err)
      return null
    }
  }, [user?.id, templates])

  // 获取单个模版详情
  const getTemplateById = useCallback(async (templateId: string): Promise<WritingTemplate | null> => {
    try {
      const url = buildUrl(`${API_ENDPOINTS.writingTemplates}/${templateId}`, {
        user_id: user?.id,
      })

      const response = await fetch(url, {
        headers: createAuthHeaders(),
      })

      if (!response.ok) {
        throw new Error('获取模版详情失败')
      }

      return await response.json()
    } catch (err: any) {
      console.error('Error getting template:', err)
      return null
    }
  }, [user?.id])

  // 初始加载
  useEffect(() => {
    fetchTemplates()
  }, [fetchTemplates])

  return {
    templates,
    loading,
    error,
    refetch: fetchTemplates,
    deleteTemplate,
    useTemplate,
    getTemplateById,
  }
}
