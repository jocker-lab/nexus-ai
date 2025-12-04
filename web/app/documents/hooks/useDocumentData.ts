'use client'

import { useState, useEffect, useCallback } from 'react'
import { createAuthHeaders } from '@/lib/api'
import { useAuthStore } from '@/lib/stores/auth'

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
  is_manually_edited: boolean
  word_count: number
  estimated_reading_time: number
  created_at: string
  updated_at: string
  published_at?: string
}

// 兼容性别名
export type Report = Document

interface UseDocumentDataReturn {
  document: Document | null
  loading: boolean
  error: string | null
  refetch: () => Promise<void>
}

// 兼容性别名
export interface UseReportDataReturn extends UseDocumentDataReturn {
  report: Document | null
}

export function useDocumentData(documentId: string): UseDocumentDataReturn {
  const [document, setDocument] = useState<Document | null>(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)

  // 从认证 store 获取用户 ID
  const { user } = useAuthStore()
  const userId = user?.id || ''

  const fetchDocument = useCallback(async () => {
    if (!userId) return

    try {
      setLoading(true)
      setError(null)

      // 通过Next.js API Route代理后端请求，附带认证头
      const response = await fetch(`/api/documents/${documentId}`, {
        headers: createAuthHeaders(),
      })

      if (!response.ok) {
        throw new Error(`Failed to fetch document: ${response.statusText}`)
      }

      const data = await response.json()
      setDocument(data)
    } catch (err: any) {
      console.error('Error fetching document:', err)
      setError(err.message || '加载文档失败')
    } finally {
      setLoading(false)
    }
  }, [documentId, userId])

  useEffect(() => {
    if (documentId && userId) {
      fetchDocument()
    }
  }, [documentId, userId, fetchDocument])

  return {
    document,
    loading,
    error,
    refetch: fetchDocument,
  }
}

// 兼容性别名 - 保持旧代码可用
export function useReportData(reportId: string): UseReportDataReturn {
  const result = useDocumentData(reportId)
  return {
    ...result,
    report: result.document,
  }
}
