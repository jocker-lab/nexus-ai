'use client'

import { useState } from 'react'
import { motion, AnimatePresence } from 'framer-motion'
import { exportToPDF } from '../utils/pdf-export'

interface ExportButtonProps {
  reportTitle: string
  contentElementId?: string
}

export default function ExportButton({
  reportTitle,
  contentElementId = 'report-content',
}: ExportButtonProps) {
  const [isExporting, setIsExporting] = useState(false)
  const [progress, setProgress] = useState(0)
  const [showMenu, setShowMenu] = useState(false)

  const handleExportPDF = async () => {
    try {
      setIsExporting(true)
      setProgress(0)

      const filename = `${reportTitle.replace(/[^a-zA-Z0-9\u4e00-\u9fa5]/g, '_')}.pdf`

      await exportToPDF(contentElementId, {
        filename,
        onProgress: (p) => setProgress(p),
      })

      // 导出成功提示
      setTimeout(() => {
        setIsExporting(false)
        setProgress(0)
        setShowMenu(false)
      }, 500)
    } catch (error) {
      console.error('Export failed:', error)
      alert('导出失败，请重试')
      setIsExporting(false)
      setProgress(0)
    }
  }

  return (
    <div className="relative">
      <button
        onClick={() => setShowMenu(!showMenu)}
        disabled={isExporting}
        className="flex items-center gap-2 px-4 py-2 rounded-lg glass-button
          hover:shadow-lg transition-all duration-200 disabled:opacity-50
          disabled:cursor-not-allowed"
      >
        {isExporting ? (
          <>
            <svg className="w-4 h-4 animate-spin" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2}
                d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15" />
            </svg>
            <span className="text-sm font-medium">导出中 {Math.round(progress)}%</span>
          </>
        ) : (
          <>
            <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2}
                d="M12 10v6m0 0l-3-3m3 3l3-3m2 8H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
            </svg>
            <span className="text-sm font-medium">导出</span>
          </>
        )}
      </button>

      {/* 导出选项菜单 */}
      <AnimatePresence>
        {showMenu && !isExporting && (
          <motion.div
            initial={{ opacity: 0, scale: 0.95, y: -10 }}
            animate={{ opacity: 1, scale: 1, y: 0 }}
            exit={{ opacity: 0, scale: 0.95, y: -10 }}
            className="absolute top-full right-0 mt-2 w-48 glass-content rounded-lg shadow-xl
              overflow-hidden z-50"
          >
            <button
              onClick={handleExportPDF}
              className="w-full px-4 py-3 text-left hover:bg-white/20 dark:hover:bg-white/5
                transition-colors flex items-center gap-3"
            >
              <svg className="w-5 h-5 text-red-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2}
                  d="M7 21h10a2 2 0 002-2V9.414a1 1 0 00-.293-.707l-5.414-5.414A1 1 0 0012.586 3H7a2 2 0 00-2 2v14a2 2 0 002 2z" />
              </svg>
              <div>
                <div className="text-sm font-medium text-slate-700 dark:text-slate-200">
                  导出为 PDF
                </div>
                <div className="text-xs text-slate-500 dark:text-slate-400">
                  保留所有样式
                </div>
              </div>
            </button>

            <button
              onClick={() => {
                // 复制Markdown
                const content = document.querySelector('.markdown-body')?.textContent || ''
                navigator.clipboard.writeText(content)
                setShowMenu(false)
              }}
              className="w-full px-4 py-3 text-left hover:bg-white/20 dark:hover:bg-white/5
                transition-colors flex items-center gap-3 border-t border-white/10"
            >
              <svg className="w-5 h-5 text-blue-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2}
                  d="M8 16H6a2 2 0 01-2-2V6a2 2 0 012-2h8a2 2 0 012 2v2m-6 12h8a2 2 0 002-2v-8a2 2 0 00-2-2h-8a2 2 0 00-2 2v8a2 2 0 002 2z" />
              </svg>
              <div>
                <div className="text-sm font-medium text-slate-700 dark:text-slate-200">
                  复制内容
                </div>
                <div className="text-xs text-slate-500 dark:text-slate-400">
                  纯文本格式
                </div>
              </div>
            </button>
          </motion.div>
        )}
      </AnimatePresence>

      {/* 进度条 */}
      {isExporting && (
        <div className="absolute top-full left-0 right-0 mt-2 glass-content p-3 rounded-lg">
          <div className="flex items-center gap-2 mb-2">
            <svg className="w-4 h-4 text-blue-500 animate-spin" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2}
                d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15" />
            </svg>
            <span className="text-xs text-slate-600 dark:text-slate-400">
              正在生成PDF...
            </span>
          </div>
          <div className="w-full h-2 bg-slate-200 dark:bg-slate-700 rounded-full overflow-hidden">
            <motion.div
              className="h-full bg-gradient-to-r from-purple-500 to-blue-500"
              initial={{ width: 0 }}
              animate={{ width: `${progress}%` }}
              transition={{ duration: 0.3 }}
            />
          </div>
        </div>
      )}
    </div>
  )
}
