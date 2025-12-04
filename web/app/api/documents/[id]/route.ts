import { NextRequest, NextResponse } from 'next/server'
import { API_BASE_URL } from '@/lib/config'

export async function GET(
  request: NextRequest,
  { params }: { params: Promise<{ id: string }> }
) {
  try {
    const { id: documentId } = await params

    // 获取请求中的认证头
    const authHeader = request.headers.get('Authorization')

    // 构建请求头
    const headers: HeadersInit = {
      'Content-Type': 'application/json',
    }
    if (authHeader) {
      headers['Authorization'] = authHeader
    }

    // 从后端API获取文档数据
    const response = await fetch(`${API_BASE_URL}/api/v1/documents/${documentId}`, {
      headers,
      cache: 'no-store', // 不缓存，确保获取最新数据
    })

    if (!response.ok) {
      return NextResponse.json(
        { error: 'Failed to fetch document from backend' },
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
