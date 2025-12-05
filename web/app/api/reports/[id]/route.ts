import { NextRequest, NextResponse } from 'next/server'
import { BACKEND_URL } from '@/lib/config'

export async function GET(
  request: NextRequest,
  { params }: { params: Promise<{ id: string }> }
) {
  try {
    const { id: reportId } = await params

    // 获取请求中的认证头
    const authHeader = request.headers.get('Authorization')

    // 构建请求头
    const headers: HeadersInit = {
      'Content-Type': 'application/json',
    }
    if (authHeader) {
      headers['Authorization'] = authHeader
    }

    // 从后端API获取报告数据（服务端需要完整 URL）
    const response = await fetch(`${BACKEND_URL}/api/v1/reports/${reportId}`, {
      headers,
      cache: 'no-store', // 不缓存，确保获取最新数据
    })

    if (!response.ok) {
      return NextResponse.json(
        { error: 'Failed to fetch report from backend' },
        { status: response.status }
      )
    }

    const data = await response.json()

    return NextResponse.json(data)
  } catch (error: any) {
    console.error('Error in API route:', error)
    return NextResponse.json(
      { error: error.message || 'Internal server error' },
      { status: 500 }
    )
  }
}
