'use client'

import { useState, useCallback, useRef, useEffect } from 'react'
import { createAuthHeaders } from '@/lib/api'
import { useAuthStore } from '@/lib/stores/auth'
import { API_BASE_URL } from '@/lib/config'

// API 端点
const TEMPLATES_API = `${API_BASE_URL}/api/v1/writing-templates`

// 解析记录接口
export interface ParseRecord {
  id: string
  templateId: string
  fileName: string
  progress: number
  status: 'pending' | 'parsing' | 'completed' | 'failed'
  taskId: string
  errorMessage?: string
  title?: string
  category?: string
  createdAt: string
}

// 上传响应接口
interface UploadResponse {
  template_id: string
  task_id: string
  filename: string
  status: string
  message: string
}

// 进度查询响应接口
interface ProgressResponse {
  template_id: string
  status: string
  progress: number
  current_step: string
  error_message?: string
  title?: string
  category?: string
}

// Hook 返回类型
export interface UseTemplateUploadReturn {
  parseRecords: ParseRecord[]
  uploading: boolean
  uploadFile: (file: File) => Promise<ParseRecord | null>
  clearRecords: () => void
  removeRecord: (id: string) => void
}

// 轮询间隔（毫秒）
const POLL_INTERVAL = 2000

export function useTemplateUpload(): UseTemplateUploadReturn {
  const [parseRecords, setParseRecords] = useState<ParseRecord[]>([])
  const [uploading, setUploading] = useState(false)
  const { user } = useAuthStore()
  const pollTimersRef = useRef<Map<string, NodeJS.Timeout>>(new Map())

  // 清理轮询定时器
  const clearPollTimer = useCallback((templateId: string) => {
    const timer = pollTimersRef.current.get(templateId)
    if (timer) {
      clearInterval(timer)
      pollTimersRef.current.delete(templateId)
    }
  }, [])

  // 组件卸载时清理所有定时器
  useEffect(() => {
    return () => {
      pollTimersRef.current.forEach((timer) => clearInterval(timer))
      pollTimersRef.current.clear()
    }
  }, [])

  // 查询解析进度
  const fetchProgress = useCallback(async (templateId: string): Promise<ProgressResponse | null> => {
    try {
      const url = new URL(`${TEMPLATES_API}/${templateId}/progress`)
      if (user?.id) {
        url.searchParams.set('user_id', user.id)
      }

      const response = await fetch(url.toString(), {
        headers: createAuthHeaders(),
      })

      if (!response.ok) {
        throw new Error('获取进度失败')
      }

      return await response.json()
    } catch (err) {
      console.error('Error fetching progress:', err)
      return null
    }
  }, [user?.id])

  // 开始轮询进度
  const startPolling = useCallback((templateId: string) => {
    // 避免重复轮询
    if (pollTimersRef.current.has(templateId)) {
      return
    }

    const timer = setInterval(async () => {
      const progress = await fetchProgress(templateId)

      if (progress) {
        setParseRecords(prev => prev.map(record =>
          record.templateId === templateId
            ? {
                ...record,
                status: progress.status as ParseRecord['status'],
                progress: progress.progress,
                errorMessage: progress.error_message,
                title: progress.title,
                category: progress.category,
              }
            : record
        ))

        // 如果完成或失败，停止轮询
        if (progress.status === 'completed' || progress.status === 'failed') {
          clearPollTimer(templateId)
        }
      }
    }, POLL_INTERVAL)

    pollTimersRef.current.set(templateId, timer)
  }, [fetchProgress, clearPollTimer])

  // 上传文件
  const uploadFile = useCallback(async (file: File): Promise<ParseRecord | null> => {
    try {
      setUploading(true)

      // 构建 FormData
      const formData = new FormData()
      formData.append('file', file)

      // 构建 URL
      const url = new URL(`${TEMPLATES_API}/upload`)
      if (user?.id) {
        url.searchParams.set('user_id', user.id)
      }

      // 构建不包含 Content-Type 的 headers（FormData 需要浏览器自动设置 multipart/form-data）
      const authHeaders = createAuthHeaders() as Record<string, string>
      const { 'Content-Type': _, ...headersWithoutContentType } = authHeaders

      // 发送请求
      const response = await fetch(url.toString(), {
        method: 'POST',
        headers: headersWithoutContentType,
        body: formData,
      })

      if (!response.ok) {
        const errorData = await response.json().catch(() => ({}))
        throw new Error(errorData.detail || `上传失败: ${response.statusText}`)
      }

      const data: UploadResponse = await response.json()

      // 创建解析记录
      const record: ParseRecord = {
        id: data.template_id,
        templateId: data.template_id,
        fileName: file.name,
        progress: 0,
        status: 'pending',
        taskId: data.task_id,
        createdAt: new Date().toISOString(),
      }

      // 添加到记录列表
      setParseRecords(prev => [record, ...prev])

      // 开始轮询进度
      startPolling(data.template_id)

      return record
    } catch (err: any) {
      console.error('Error uploading file:', err)
      throw err
    } finally {
      setUploading(false)
    }
  }, [user?.id, startPolling])

  // 清除所有记录
  const clearRecords = useCallback(() => {
    // 停止所有轮询
    pollTimersRef.current.forEach((timer) => clearInterval(timer))
    pollTimersRef.current.clear()

    setParseRecords([])
  }, [])

  // 移除单个记录
  const removeRecord = useCallback((id: string) => {
    clearPollTimer(id)
    setParseRecords(prev => prev.filter(r => r.id !== id))
  }, [clearPollTimer])

  return {
    parseRecords,
    uploading,
    uploadFile,
    clearRecords,
    removeRecord,
  }
}
