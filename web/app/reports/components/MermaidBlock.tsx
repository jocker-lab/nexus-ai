'use client'

import { useEffect, useRef, useState } from 'react'
import mermaid from 'mermaid'

interface MermaidBlockProps {
  chart: string
}

// 初始化Mermaid配置
mermaid.initialize({
  startOnLoad: false,
  theme: 'dark',
  themeVariables: {
    primaryColor: '#6366f1',
    primaryTextColor: '#fff',
    primaryBorderColor: '#8b5cf6',
    lineColor: '#a78bfa',
    secondaryColor: '#8b5cf6',
    tertiaryColor: '#c4b5fd',
  },
  flowchart: {
    curve: 'basis',
    padding: 20,
  },
})

export default function MermaidBlock({ chart }: MermaidBlockProps) {
  const containerRef = useRef<HTMLDivElement>(null)
  const [svg, setSvg] = useState<string>('')
  const [error, setError] = useState<string>('')
  const [isFullscreen, setIsFullscreen] = useState(false)

  useEffect(() => {
    const renderChart = async () => {
      if (!containerRef.current) return

      try {
        const id = `mermaid-${Math.random().toString(36).slice(2, 9)}`
        const { svg: renderedSvg } = await mermaid.render(id, chart)
        setSvg(renderedSvg)
        setError('')
      } catch (err: any) {
        console.error('Mermaid rendering error:', err)
        setError(err.message || '图表渲染失败')
      }
    }

    renderChart()
  }, [chart])

  const handleFullscreen = () => {
    setIsFullscreen(!isFullscreen)
  }

  const handleDownload = () => {
    // 创建SVG文件并下载
    const blob = new Blob([svg], { type: 'image/svg+xml' })
    const url = URL.createObjectURL(blob)
    const a = document.createElement('a')
    a.href = url
    a.download = `mermaid-diagram-${Date.now()}.svg`
    a.click()
    URL.revokeObjectURL(url)
  }

  if (error) {
    return (
      <div className="my-6 p-4 rounded-lg bg-red-500/10 border border-red-500/30">
        <div className="flex items-start gap-2">
          <svg className="w-5 h-5 text-red-400 mt-0.5 flex-shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2}
              d="M12 8v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
          </svg>
          <div>
            <p className="text-sm font-medium text-red-300">图表渲染失败</p>
            <p className="text-xs text-red-400/80 mt-1">{error}</p>
          </div>
        </div>
      </div>
    )
  }

  return (
    <>
      <div className="group relative my-6 rounded-lg overflow-hidden glass-card p-6">
        {/* 工具栏 */}
        <div className="absolute top-3 right-3 flex gap-2 opacity-0 group-hover:opacity-100 transition-opacity">
          <button
            onClick={handleFullscreen}
            className="p-2 rounded-lg bg-white/10 hover:bg-white/20 border border-white/20
              transition-all duration-200"
            title="全屏查看"
          >
            <svg className="w-4 h-4 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2}
                d="M4 8V4m0 0h4M4 4l5 5m11-1V4m0 0h-4m4 0l-5 5M4 16v4m0 0h4m-4 0l5-5m11 5l-5-5m5 5v-4m0 4h-4" />
            </svg>
          </button>
          <button
            onClick={handleDownload}
            className="p-2 rounded-lg bg-white/10 hover:bg-white/20 border border-white/20
              transition-all duration-200"
            title="下载SVG"
          >
            <svg className="w-4 h-4 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2}
                d="M4 16v1a3 3 0 003 3h10a3 3 0 003-3v-1m-4-4l-4 4m0 0l-4-4m4 4V4" />
            </svg>
          </button>
        </div>

        {/* SVG内容 */}
        <div
          ref={containerRef}
          className="flex items-center justify-center overflow-x-auto"
          dangerouslySetInnerHTML={{ __html: svg }}
        />
      </div>

      {/* 全屏模态框 */}
      {isFullscreen && (
        <div
          className="fixed inset-0 z-50 flex items-center justify-center p-4 glass-modal-backdrop"
          onClick={handleFullscreen}
        >
          <div
            className="relative max-w-7xl w-full max-h-[90vh] overflow-auto glass-content p-8"
            onClick={(e) => e.stopPropagation()}
          >
            <button
              onClick={handleFullscreen}
              className="absolute top-4 right-4 p-2 rounded-lg bg-white/10 hover:bg-white/20
                border border-white/20 transition-all duration-200"
            >
              <svg className="w-5 h-5 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
              </svg>
            </button>
            <div
              className="flex items-center justify-center"
              dangerouslySetInnerHTML={{ __html: svg }}
            />
          </div>
        </div>
      )}
    </>
  )
}
