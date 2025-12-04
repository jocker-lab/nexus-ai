'use client'

import { motion } from 'framer-motion'
import ThemeToggle from './ThemeToggle'

interface DocumentHeaderProps {
  title: string
  description?: string
  category?: string
  tags?: string
  createdAt?: string
  wordCount?: number
  estimatedReadingTime?: number
  onExportPDF?: () => void
}

// 兼容性别名
export type ReportHeaderProps = DocumentHeaderProps

export default function DocumentHeader({
  title,
  description,
  category,
  tags,
  createdAt,
  wordCount,
  estimatedReadingTime,
  onExportPDF,
}: DocumentHeaderProps) {
  const tagList = tags ? tags.split(',').filter(Boolean) : []

  return (
    <motion.header
      initial={{ opacity: 0, y: -20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.6 }}
      className="relative mb-12"
    >
      {/* 背景装饰 - 改为蓝色系 */}
      <div className="absolute inset-0 -z-10 overflow-hidden">
        <div className="absolute top-0 left-1/4 w-96 h-96 bg-blue-500/15 rounded-full blur-3xl" />
        <div className="absolute top-0 right-1/4 w-96 h-96 bg-sky-500/15 rounded-full blur-3xl" />
      </div>

      <div className="glass-content p-10 lg:p-12" id="header-glass-content">
        {/* 顶部操作栏 - 优化对齐 */}
        <div className="flex items-center justify-between mb-8">
          <div className="flex items-center gap-3">
            {category && (
              <span className="px-4 py-1.5 text-xs font-semibold rounded-full glass-button text-blue-700 dark:text-blue-300">
                {category}
              </span>
            )}
            {tagList.map((tag, index) => (
              <span
                key={index}
                className="px-3 py-1 text-xs rounded-md glass-button text-slate-600 dark:text-slate-400"
              >
                #{tag.trim()}
              </span>
            ))}
          </div>

          <div className="flex items-center gap-4">
            <ThemeToggle />
            {onExportPDF && (
              <button
                onClick={onExportPDF}
                className="flex items-center gap-2 px-5 py-2.5 rounded-lg glass-button
                  hover:shadow-lg transition-all duration-200 text-blue-700 dark:text-blue-300 font-medium"
              >
                <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path
                    strokeLinecap="round"
                    strokeLinejoin="round"
                    strokeWidth={2}
                    d="M12 10v6m0 0l-3-3m3 3l3-3m2 8H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z"
                  />
                </svg>
                <span className="text-sm">导出PDF</span>
              </button>
            )}
          </div>
        </div>

        {/* 标题和描述 - 改为蓝色渐变 */}
        <div className="mb-8">
          <h1 className="text-4xl lg:text-5xl font-bold mb-5 bg-gradient-to-r from-blue-600 via-sky-600 to-cyan-500 bg-clip-text text-transparent leading-tight">
            {title}
          </h1>
          {description && (
            <p className="text-lg text-slate-600 dark:text-slate-400 leading-relaxed max-w-4xl">
              {description}
            </p>
          )}
        </div>

        {/* 元数据 - 使用网格布局确保对齐 */}
        <div className="grid grid-cols-2 md:grid-cols-4 gap-6 text-sm">
          {createdAt && (
            <div className="flex items-center gap-2 text-slate-600 dark:text-slate-400">
              <svg className="w-4 h-4 text-blue-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path
                  strokeLinecap="round"
                  strokeLinejoin="round"
                  strokeWidth={2}
                  d="M8 7V3m8 4V3m-9 8h10M5 21h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v12a2 2 0 002 2z"
                />
              </svg>
              <span className="font-medium" suppressHydrationWarning>
                {new Date(createdAt).toLocaleDateString('zh-CN')}
              </span>
            </div>
          )}

          {wordCount && wordCount > 0 && (
            <div className="flex items-center gap-2 text-slate-600 dark:text-slate-400">
              <svg className="w-4 h-4 text-blue-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path
                  strokeLinecap="round"
                  strokeLinejoin="round"
                  strokeWidth={2}
                  d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z"
                />
              </svg>
              <span className="font-medium" suppressHydrationWarning>
                {wordCount.toLocaleString()} 字
              </span>
            </div>
          )}

          {estimatedReadingTime && estimatedReadingTime > 0 && (
            <div className="flex items-center gap-2 text-slate-600 dark:text-slate-400">
              <svg className="w-4 h-4 text-blue-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path
                  strokeLinecap="round"
                  strokeLinejoin="round"
                  strokeWidth={2}
                  d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z"
                />
              </svg>
              <span className="font-medium">约 {estimatedReadingTime} 分钟</span>
            </div>
          )}
        </div>

        {/* 渐变分割线 - 改为蓝色 */}
        <div className="mt-10 h-px w-full bg-gradient-to-r from-transparent via-blue-500/30 to-transparent" />
      </div>
    </motion.header>
  )
}
