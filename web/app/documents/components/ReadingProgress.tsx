'use client'

import { useState, useEffect } from 'react'
import { motion } from 'framer-motion'

interface ReadingProgressProps {
  wordCount?: number
  estimatedReadingTime?: number
}

export default function ReadingProgress({
  wordCount = 0,
  estimatedReadingTime = 0,
}: ReadingProgressProps) {
  const [progress, setProgress] = useState(0)
  const [remainingTime, setRemainingTime] = useState(estimatedReadingTime)
  const [topOffset, setTopOffset] = useState(112) // 默认7rem = 112px

  // 计算header glass-content的顶部位置
  useEffect(() => {
    const calculateOffset = () => {
      const headerGlass = document.getElementById('header-glass-content')
      if (headerGlass) {
        const rect = headerGlass.getBoundingClientRect()
        const scrollTop = window.scrollY
        setTopOffset(rect.top + scrollTop)
      }
    }

    // 延迟计算以确保DOM完全加载
    setTimeout(calculateOffset, 100)
    window.addEventListener('resize', calculateOffset)
    return () => window.removeEventListener('resize', calculateOffset)
  }, [])

  useEffect(() => {
    const handleScroll = () => {
      const windowHeight = window.innerHeight
      const documentHeight = document.documentElement.scrollHeight - windowHeight
      const scrollTop = window.scrollY

      const scrollProgress = (scrollTop / documentHeight) * 100
      setProgress(Math.min(scrollProgress, 100))

      // 计算剩余阅读时间（基于滚动进度）
      const remaining = Math.ceil(estimatedReadingTime * (1 - scrollProgress / 100))
      setRemainingTime(Math.max(remaining, 0))
    }

    window.addEventListener('scroll', handleScroll)
    handleScroll() // 初始化

    return () => window.removeEventListener('scroll', handleScroll)
  }, [estimatedReadingTime])

  return (
    <>
      {/* 顶部进度条 - 改为蓝色渐变 */}
      <div className="fixed top-0 left-0 right-0 z-50 h-1">
        <motion.div
          className="h-full bg-gradient-to-r from-blue-500 via-sky-500 to-cyan-500"
          style={{ width: `${progress}%` }}
          initial={{ width: 0 }}
          animate={{ width: `${progress}%` }}
          transition={{ duration: 0.1 }}
        />
      </div>

      {/* 阅读信息卡片（桌面端）- 固定在容器左边缘外 */}
      <motion.div
        initial={{ opacity: 0, y: -20 }}
        animate={{ opacity: 1, y: 0 }}
        className="hidden xl:flex fixed glass-sidebar px-4 py-3 rounded-lg items-center gap-4 z-40"
        style={{
          right: 'calc(50% + 640px + 2rem)',
          top: `${topOffset}px`
        }}
      >
        {/* 进度环 */}
        <div className="relative w-12 h-12">
          <svg className="w-full h-full transform -rotate-90">
            <circle
              cx="24"
              cy="24"
              r="20"
              stroke="currentColor"
              strokeWidth="3"
              fill="none"
              className="text-slate-300 dark:text-slate-700"
            />
            <circle
              cx="24"
              cy="24"
              r="20"
              stroke="url(#progress-gradient)"
              strokeWidth="3"
              fill="none"
              strokeDasharray={`${2 * Math.PI * 20}`}
              strokeDashoffset={`${2 * Math.PI * 20 * (1 - progress / 100)}`}
              strokeLinecap="round"
              className="transition-all duration-300"
            />
            <defs>
              <linearGradient id="progress-gradient" x1="0%" y1="0%" x2="100%" y2="100%">
                <stop offset="0%" stopColor="#3b82f6" />
                <stop offset="50%" stopColor="#0ea5e9" />
                <stop offset="100%" stopColor="#06b6d4" />
              </linearGradient>
            </defs>
          </svg>
          <div className="absolute inset-0 flex items-center justify-center">
            <span className="text-xs font-bold text-slate-700 dark:text-slate-200">
              {Math.round(progress)}%
            </span>
          </div>
        </div>

        {/* 阅读信息 */}
        <div className="text-sm">
          <div className="flex items-center gap-2 text-slate-600 dark:text-slate-400">
            <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path
                strokeLinecap="round"
                strokeLinejoin="round"
                strokeWidth={2}
                d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z"
              />
            </svg>
            <span>
              {remainingTime > 0
                ? `${remainingTime} 分钟剩余`
                : '阅读完成'}
            </span>
          </div>
          {wordCount > 0 && (
            <div className="text-xs text-slate-500 dark:text-slate-500 mt-1">
              共 {wordCount.toLocaleString()} 字
            </div>
          )}
        </div>
      </motion.div>

      {/* 移动端简化版 */}
      <motion.div
        initial={{ opacity: 0 }}
        animate={{ opacity: 1 }}
        className="lg:hidden fixed top-16 left-4 right-4 z-40"
      >
        <div className="glass-card px-3 py-2 rounded-lg flex items-center justify-between">
          <div className="flex items-center gap-2">
            <div className="relative w-8 h-8">
              <svg className="w-full h-full transform -rotate-90">
                <circle
                  cx="16"
                  cy="16"
                  r="14"
                  stroke="currentColor"
                  strokeWidth="2.5"
                  fill="none"
                  className="text-slate-300 dark:text-slate-700"
                />
                <circle
                  cx="16"
                  cy="16"
                  r="14"
                  stroke="url(#progress-gradient-mobile)"
                  strokeWidth="2.5"
                  fill="none"
                  strokeDasharray={`${2 * Math.PI * 14}`}
                  strokeDashoffset={`${2 * Math.PI * 14 * (1 - progress / 100)}`}
                  strokeLinecap="round"
                  className="transition-all duration-300"
                />
                <defs>
                  <linearGradient id="progress-gradient-mobile" x1="0%" y1="0%" x2="100%" y2="100%">
                    <stop offset="0%" stopColor="#3b82f6" />
                    <stop offset="100%" stopColor="#06b6d4" />
                  </linearGradient>
                </defs>
              </svg>
              <div className="absolute inset-0 flex items-center justify-center">
                <span className="text-[10px] font-bold text-slate-700 dark:text-slate-200">
                  {Math.round(progress)}%
                </span>
              </div>
            </div>
            <span className="text-xs text-slate-600 dark:text-slate-400">
              {remainingTime > 0 ? `${remainingTime}分钟` : '完成'}
            </span>
          </div>

          {wordCount > 0 && (
            <span className="text-xs text-slate-500 dark:text-slate-500">
              {wordCount.toLocaleString()} 字
            </span>
          )}
        </div>
      </motion.div>
    </>
  )
}
