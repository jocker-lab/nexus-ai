'use client'

import { use, useState } from 'react'
import { motion } from 'framer-motion'
import Link from 'next/link'
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

// Nexus Logo Component
const NexusLogo = ({ size = 32 }: { size?: number }) => (
  <div
    className="rounded-xl bg-gradient-to-br from-cyan-500 via-blue-500 to-violet-500 flex items-center justify-center"
    style={{
      width: size,
      height: size,
      boxShadow: '0 0 20px rgba(6, 182, 212, 0.3)',
    }}
  >
    <svg
      className="text-white"
      style={{ width: size * 0.6, height: size * 0.6 }}
      viewBox="0 0 24 24"
      fill="none"
      stroke="currentColor"
      strokeWidth="1.5"
    >
      <circle cx="12" cy="12" r="3" />
      <path d="M12 2v4m0 12v4M2 12h4m12 0h4" />
    </svg>
  </div>
)

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

  // Loading State
  if (loading) {
    return (
      <div className="min-h-screen animated-gradient-bg flex items-center justify-center p-4">
        <motion.div
          initial={{ opacity: 0, scale: 0.9 }}
          animate={{ opacity: 1, scale: 1 }}
          className="glass-content p-10 rounded-2xl text-center"
        >
          <div className="relative mb-6">
            <div className="w-20 h-20 mx-auto rounded-2xl bg-gradient-to-br from-cyan-500 via-blue-500 to-violet-500 flex items-center justify-center pulse-glow">
              <svg className="w-10 h-10 text-white spin" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.5">
                <circle cx="12" cy="12" r="3" />
                <path d="M12 2v4m0 12v4M2 12h4m12 0h4" />
              </svg>
            </div>
          </div>
          <h2 className="text-xl font-bold text-gray-100 mb-2" style={{ fontFamily: 'Orbitron, sans-serif' }}>
            <span className="text-shimmer">正在加载报告</span>
          </h2>
          <p className="text-sm text-gray-400">
            神经网络正在处理数据...
          </p>
        </motion.div>
      </div>
    )
  }

  // Error State
  if (error || !report) {
    return (
      <div className="min-h-screen animated-gradient-bg flex items-center justify-center p-4">
        <motion.div
          initial={{ opacity: 0, scale: 0.9 }}
          animate={{ opacity: 1, scale: 1 }}
          className="glass-content p-10 rounded-2xl text-center max-w-md"
        >
          <div className="w-20 h-20 mx-auto mb-6 rounded-2xl bg-gradient-to-br from-red-500 to-rose-500 flex items-center justify-center">
            <svg
              className="w-10 h-10 text-white"
              fill="none"
              stroke="currentColor"
              viewBox="0 0 24 24"
            >
              <path
                strokeLinecap="round"
                strokeLinejoin="round"
                strokeWidth={1.5}
                d="M12 8v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z"
              />
            </svg>
          </div>
          <h2 className="text-xl font-bold text-gray-100 mb-3" style={{ fontFamily: 'Orbitron, sans-serif' }}>
            加载失败
          </h2>
          <p className="text-gray-400 mb-8">
            {error || '未找到报告数据'}
          </p>
          <div className="flex gap-3 justify-center">
            <button
              onClick={() => window.location.reload()}
              className="glass-button px-6 py-2.5 rounded-xl text-sm"
            >
              重试
            </button>
            <Link href="/">
              <button className="px-6 py-2.5 rounded-xl text-sm bg-gradient-to-r from-cyan-500 to-blue-500 text-white hover:shadow-lg hover:shadow-cyan-500/25 transition-all">
                返回首页
              </button>
            </Link>
          </div>
        </motion.div>
      </div>
    )
  }

  return (
    <div className="min-h-screen animated-gradient-bg">
      {/* Reading Progress */}
      <ReadingProgress
        wordCount={report.word_count}
        estimatedReadingTime={report.estimated_reading_time}
      />

      {/* Navigation Header */}
      <motion.header
        initial={{ opacity: 0, y: -20 }}
        animate={{ opacity: 1, y: 0 }}
        className="fixed top-0 left-0 right-0 z-50 px-6 py-4"
      >
        <div className="max-w-7xl mx-auto flex items-center justify-between">
          <Link href="/" className="flex items-center gap-3 group">
            <NexusLogo size={36} />
            <span
              className="text-base font-semibold text-gray-100 group-hover:text-cyan-400 transition-colors"
              style={{ fontFamily: 'Orbitron, sans-serif' }}
            >
              NEXUS AI
            </span>
          </Link>

          <div className="flex items-center gap-3">
            <button
              onClick={handleExportPDF}
              disabled={isExporting}
              className="glass-button px-4 py-2 rounded-xl text-sm flex items-center gap-2 disabled:opacity-50"
            >
              {isExporting ? (
                <>
                  <svg className="w-4 h-4 spin" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                    <path d="M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
                    <path d="M9 12l2 2 4-4" />
                  </svg>
                  导出中...
                </>
              ) : (
                <>
                  <svg className="w-4 h-4" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                    <path d="M21 15v4a2 2 0 01-2 2H5a2 2 0 01-2-2v-4" />
                    <polyline points="7 10 12 15 17 10" />
                    <line x1="12" y1="15" x2="12" y2="3" />
                  </svg>
                  导出 PDF
                </>
              )}
            </button>
          </div>
        </div>
      </motion.header>

      {/* Main Container */}
      <div className="container mx-auto px-6 pt-24 pb-16 max-w-7xl relative z-10">
        {/* Report Header */}
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

        {/* Content Area */}
        <div className="relative mt-8">
          {/* Main Content */}
          <motion.div
            id="report-content"
            className="glass-content p-8 lg:p-12 rounded-2xl"
            initial={{ opacity: 0, y: 30 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.6, delay: 0.2 }}
          >
            <MarkdownRenderer content={report.content} />
          </motion.div>

          {/* Report Meta Info */}
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.4 }}
            className="mt-8 glass-card p-6 rounded-xl"
          >
            <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
              <div className="text-center md:text-left">
                <p className="text-xs text-gray-500 uppercase tracking-wider mb-2">报告状态</p>
                <div className="flex items-center gap-2 justify-center md:justify-start">
                  <span
                    className={`w-2.5 h-2.5 rounded-full ${
                      report.status === 'published'
                        ? 'bg-emerald-500 shadow-lg shadow-emerald-500/50'
                        : report.status === 'draft'
                        ? 'bg-amber-500 shadow-lg shadow-amber-500/50'
                        : 'bg-gray-500'
                    }`}
                  />
                  <span className="font-medium text-gray-200">
                    {report.status === 'published'
                      ? '已发布'
                      : report.status === 'draft'
                      ? '草稿'
                      : '已归档'}
                  </span>
                </div>
              </div>

              <div className="text-center">
                <p className="text-xs text-gray-500 uppercase tracking-wider mb-2">当前版本</p>
                <p className="font-medium text-gray-200">
                  v{report.current_version}
                </p>
              </div>

              <div className="text-center md:text-right">
                <p className="text-xs text-gray-500 uppercase tracking-wider mb-2">最后更新</p>
                <p className="font-medium text-gray-200" suppressHydrationWarning>
                  {new Date(report.updated_at).toLocaleString('zh-CN')}
                </p>
              </div>
            </div>
          </motion.div>

          {/* Export Button (Mobile) */}
          <div className="lg:hidden fixed bottom-6 right-6 z-40">
            <ExportButton reportTitle={report.title} />
          </div>

          {/* Table of Contents (Desktop Sidebar) */}
          <TableOfContents content={report.content} />
        </div>
      </div>

      {/* Back to Top Button */}
      <motion.button
        initial={{ opacity: 0, scale: 0.8 }}
        animate={{ opacity: 1, scale: 1 }}
        whileHover={{ scale: 1.1 }}
        whileTap={{ scale: 0.9 }}
        className="fixed bottom-24 lg:bottom-8 left-6 w-12 h-12 rounded-xl glass-button flex items-center justify-center z-40"
        onClick={() => window.scrollTo({ top: 0, behavior: 'smooth' })}
      >
        <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 10l7-7m0 0l7 7m-7-7v18" />
        </svg>
      </motion.button>

      {/* Footer */}
      <footer className="relative z-10 py-8 px-6 border-t border-white/5">
        <div className="max-w-7xl mx-auto flex flex-col md:flex-row items-center justify-between gap-4">
          <div className="flex items-center gap-3">
            <NexusLogo size={28} />
            <span className="text-sm text-gray-400">
              Nexus AI · 神经智能研究平台
            </span>
          </div>
          <div className="flex items-center gap-6 text-sm text-gray-500">
            <Link href="/chat" className="hover:text-cyan-400 transition-colors">
              开始对话
            </Link>
            <Link href="/" className="hover:text-cyan-400 transition-colors">
              返回首页
            </Link>
          </div>
        </div>
      </footer>
    </div>
  )
}
