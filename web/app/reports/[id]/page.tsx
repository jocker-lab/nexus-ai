'use client'

import { use, useState } from 'react'
import { motion } from 'framer-motion'
import { useReportData } from '../hooks/useReportData'
import MarkdownRenderer from '../components/MarkdownRenderer'
import TableOfContents from '../components/TableOfContents'
import ReadingProgress from '../components/ReadingProgress'
import ReportHeader from '../components/ReportHeader'
import ExportButton from '../components/ExportButton'
import { exportToPDF } from '../utils/pdf-export'
import '../styles/markdown.css'
import '../styles/glassmorphism.css'
import '../styles/animations.css'

interface PageProps {
  params: Promise<{ id: string }>
}

export default function ReportPage({ params }: PageProps) {
  const resolvedParams = use(params)
  const { report, loading, error } = useReportData(resolvedParams.id)
  const [isExporting, setIsExporting] = useState(false)

  const handleExportPDF = async () => {
    if (!report) {
      console.log('No report data available')
      return
    }

    try {
      console.log('Starting PDF export...')
      setIsExporting(true)
      const filename = `${report.title.replace(/[^a-zA-Z0-9\u4e00-\u9fa5]/g, '_')}.pdf`
      console.log('Export filename:', filename)
      await exportToPDF('report-content', {
        filename,
        onProgress: (progress) => console.log('Export progress:', progress)
      })
      console.log('PDF export completed successfully')
    } catch (error) {
      console.error('Export failed:', error)
      alert('导出失败，请重试')
    } finally {
      setIsExporting(false)
    }
  }

  // 加载状态
  if (loading) {
    return (
      <div className="min-h-screen animated-gradient-bg flex items-center justify-center p-4">
        <motion.div
          initial={{ opacity: 0, scale: 0.9 }}
          animate={{ opacity: 1, scale: 1 }}
          className="glass-content p-8 rounded-2xl text-center"
        >
          <div className="w-16 h-16 mx-auto mb-4 border-4 border-purple-500 border-t-transparent rounded-full animate-spin" />
          <p className="text-lg font-medium text-slate-700 dark:text-slate-200">
            正在加载报告...
          </p>
          <p className="text-sm text-slate-500 dark:text-slate-400 mt-2">
            请稍候
          </p>
        </motion.div>
      </div>
    )
  }

  // 错误状态
  if (error || !report) {
    return (
      <div className="min-h-screen animated-gradient-bg flex items-center justify-center p-4">
        <motion.div
          initial={{ opacity: 0, scale: 0.9 }}
          animate={{ opacity: 1, scale: 1 }}
          className="glass-content p-8 rounded-2xl text-center max-w-md"
        >
          <svg
            className="w-16 h-16 mx-auto mb-4 text-red-500"
            fill="none"
            stroke="currentColor"
            viewBox="0 0 24 24"
          >
            <path
              strokeLinecap="round"
              strokeLinejoin="round"
              strokeWidth={2}
              d="M12 8v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z"
            />
          </svg>
          <h2 className="text-xl font-bold text-slate-800 dark:text-slate-100 mb-2">
            加载失败
          </h2>
          <p className="text-slate-600 dark:text-slate-400 mb-6">
            {error || '未找到报告'}
          </p>
          <button
            onClick={() => window.location.reload()}
            className="px-6 py-2 rounded-lg glass-button hover:shadow-lg transition-all"
          >
            重试
          </button>
        </motion.div>
      </div>
    )
  }

  return (
    <div className="min-h-screen animated-gradient-bg">
      {/* 阅读进度条 */}
      <ReadingProgress
        wordCount={report.word_count}
        estimatedReadingTime={report.estimated_reading_time}
      />

      {/* 主容器 - 统一网格系统 */}
      <div className="container mx-auto px-8 py-12 max-w-7xl">
        {/* 报告头部 */}
        <ReportHeader
          title={report.title}
          description={report.description}
          category={report.category}
          tags={report.tags}
          createdAt={report.created_at}
          wordCount={report.word_count}
          estimatedReadingTime={report.estimated_reading_time}
          onExportPDF={handleExportPDF}
        />

        {/* 内容区域 */}
        <div className="relative">
          {/* 主内容 - glass-content 全宽保持与 header 对齐 */}
          <div id="report-content" className="glass-content p-10 lg:p-16 rounded-2xl">
            <MarkdownRenderer content={report.content} />
          </div>

            {/* 报告元信息 */}
            <motion.div
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              transition={{ delay: 0.5 }}
              className="mt-8 glass-card p-6 rounded-xl"
            >
              <div className="grid grid-cols-1 md:grid-cols-3 gap-4 text-sm">
                <div>
                  <p className="text-slate-500 dark:text-slate-400 mb-1">报告状态</p>
                  <div className="flex items-center gap-2">
                    <span
                      className={`w-2 h-2 rounded-full ${
                        report.status === 'published'
                          ? 'bg-green-500'
                          : report.status === 'draft'
                          ? 'bg-yellow-500'
                          : 'bg-gray-500'
                      }`}
                    />
                    <span className="font-medium text-slate-700 dark:text-slate-200">
                      {report.status === 'published'
                        ? '已发布'
                        : report.status === 'draft'
                        ? '草稿'
                        : '已归档'}
                    </span>
                  </div>
                </div>

                <div>
                  <p className="text-slate-500 dark:text-slate-400 mb-1">当前版本</p>
                  <p className="font-medium text-slate-700 dark:text-slate-200">
                    v{report.current_version}
                  </p>
                </div>

                <div>
                  <p className="text-slate-500 dark:text-slate-400 mb-1">最后更新</p>
                  <p className="font-medium text-slate-700 dark:text-slate-200" suppressHydrationWarning>
                    {new Date(report.updated_at).toLocaleString('zh-CN')}
                  </p>
                </div>
              </div>
            </motion.div>

          {/* 导出按钮（移动端） */}
          <div className="lg:hidden fixed bottom-6 right-6 z-40">
            <ExportButton reportTitle={report.title} />
          </div>

          {/* 目录导航（桌面端侧边栏） */}
          <TableOfContents content={report.content} />
        </div>
      </div>

      {/* 返回顶部按钮 */}
      <motion.button
        initial={{ opacity: 0 }}
        animate={{ opacity: 1 }}
        className="fixed bottom-24 lg:bottom-6 left-6 p-4 rounded-full glass-button shadow-lg
          hover:shadow-xl transition-all z-40"
        onClick={() => window.scrollTo({ top: 0, behavior: 'smooth' })}
      >
        <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 10l7-7m0 0l7 7m-7-7v18" />
        </svg>
      </motion.button>
    </div>
  )
}
