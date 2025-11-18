import { NextRequest, NextResponse } from 'next/server'

const BACKEND_URL = process.env.NEXT_PUBLIC_BACKEND_URL || 'http://localhost:8000'

export async function GET(
  request: NextRequest,
  { params }: { params: Promise<{ id: string }> }
) {
  try {
    const { id: reportId } = await params

    // 从后端API获取报告数据
    const response = await fetch(`${BACKEND_URL}/api/v1/reports/${reportId}`, {
      headers: {
        'Content-Type': 'application/json',
      },
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
