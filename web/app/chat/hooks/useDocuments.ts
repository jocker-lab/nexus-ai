'use client'

import { useState, useEffect, useCallback } from 'react'
import { createAuthHeaders } from '@/lib/api'
import { useAuthStore } from '@/lib/stores/auth'
import { API_ENDPOINTS } from '@/lib/config'

export interface Document {
  id: string
  user_id: string
  title: string
  description?: string
  content: string
  status: 'draft' | 'published' | 'archived'
  category?: string
  tags?: string
  chat_id?: string
  outline?: any
  current_version: number
  is_manually_edited?: boolean
  word_count: number
  estimated_reading_time: number
  created_at: string
  updated_at: string
  published_at?: string
}

// 兼容性别名
export type Report = Document

interface UseDocumentsReturn {
  documents: Document[]
  loading: boolean
  error: string | null
  refetch: () => Promise<void>
  deleteDocument: (documentId: string) => Promise<boolean>
}

// 兼容性别名
export interface UseReportsReturn extends UseDocumentsReturn {
  reports: Document[]
  deleteReport: (reportId: string) => Promise<boolean>
}

export function useDocuments(): UseDocumentsReturn {
  const [documents, setDocuments] = useState<Document[]>([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)
  const { user } = useAuthStore()

  const fetchDocuments = useCallback(async () => {
    if (!user?.id) {
      setLoading(false)
      return
    }

    try {
      setLoading(true)
      setError(null)

      const response = await fetch(API_ENDPOINTS.documents, {
        headers: createAuthHeaders(),
      })

      if (!response.ok) {
        throw new Error(`获取文档列表失败: ${response.statusText}`)
      }

      const data = await response.json()
      // API 返回的是分页数据，取 items
      const documentsList = Array.isArray(data) ? data : (data.items || data.data || [])

      // 按更新时间降序排列
      documentsList.sort((a: Document, b: Document) =>
        new Date(b.updated_at).getTime() - new Date(a.updated_at).getTime()
      )

      setDocuments(documentsList)
    } catch (err: any) {
      console.error('Error fetching documents:', err)
      setError(err.message || '加载文档失败')
    } finally {
      setLoading(false)
    }
  }, [user?.id])

  const deleteDocument = useCallback(async (documentId: string): Promise<boolean> => {
    try {
      const response = await fetch(`${API_ENDPOINTS.documents}/${documentId}`, {
        method: 'DELETE',
        headers: createAuthHeaders(),
      })

      if (!response.ok) {
        throw new Error('删除失败')
      }

      // 从本地状态移除
      setDocuments(prev => prev.filter(d => d.id !== documentId))
      return true
    } catch (err: any) {
      console.error('Error deleting document:', err)
      return false
    }
  }, [])

  useEffect(() => {
    fetchDocuments()
  }, [fetchDocuments])

  return {
    documents,
    loading,
    error,
    refetch: fetchDocuments,
    deleteDocument,
  }
}

// 兼容性别名 - 保持旧代码可用
export function useReports(): UseReportsReturn {
  const result = useDocuments()
  return {
    ...result,
    reports: result.documents,
    deleteReport: result.deleteDocument,
  }
}
