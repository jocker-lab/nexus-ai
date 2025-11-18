'use client'

import { useState, useEffect } from 'react'

export interface Report {
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

interface UseReportDataReturn {
  report: Report | null
  loading: boolean
  error: string | null
  refetch: () => Promise<void>
}

export function useReportData(reportId: string): UseReportDataReturn {
  const [report, setReport] = useState<Report | null>(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)

  const fetchReport = async () => {
    try {
      setLoading(true)
      setError(null)

      // 通过Next.js API Route代理后端请求
      const response = await fetch(`/api/reports/${reportId}`)

      if (!response.ok) {
        throw new Error(`Failed to fetch report: ${response.statusText}`)
      }

      const data = await response.json()
      setReport(data)
    } catch (err: any) {
      console.error('Error fetching report:', err)
      setError(err.message || '加载报告失败')
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => {
    if (reportId) {
      fetchReport()
    }
  }, [reportId])

  return {
    report,
    loading,
    error,
    refetch: fetchReport,
  }
}
