'use client'

import { useState, useEffect } from 'react'
import { motion, AnimatePresence } from 'framer-motion'

interface TocItem {
  id: string
  title: string
  level: number
}

interface TableOfContentsProps {
  content: string
}

export default function TableOfContents({ content }: TableOfContentsProps) {
  const [tocItems, setTocItems] = useState<TocItem[]>([])
  const [activeId, setActiveId] = useState<string>('')
  const [isOpen, setIsOpen] = useState(true)
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

  // 解析Markdown生成目录
  useEffect(() => {
    const headingRegex = /^(#{1,4})\s+(.+)$/gm
    const items: TocItem[] = []
    let match

    while ((match = headingRegex.exec(content)) !== null) {
      const level = match[1].length
      const title = match[2]
      const id = title.toLowerCase().replace(/\s+/g, '-')

      items.push({ id, title, level })
    }

    setTocItems(items)
  }, [content])

  // 监听滚动，高亮当前章节
  useEffect(() => {
    const handleScroll = () => {
      const headings = tocItems.map((item) => ({
        id: item.id,
        element: document.getElementById(item.id),
      }))

      // 找到当前可见的标题
      for (let i = headings.length - 1; i >= 0; i--) {
        const heading = headings[i]
        if (heading.element) {
          const rect = heading.element.getBoundingClientRect()
          if (rect.top <= 100) {
            setActiveId(heading.id)
            break
          }
        }
      }
    }

    window.addEventListener('scroll', handleScroll)
    handleScroll() // 初始化

    return () => window.removeEventListener('scroll', handleScroll)
  }, [tocItems])

  const scrollToHeading = (id: string) => {
    const element = document.getElementById(id)
    if (element) {
      const offsetTop = element.offsetTop - 80
      window.scrollTo({
        top: offsetTop,
        behavior: 'smooth',
      })
    }
  }

  if (tocItems.length === 0) return null

  return (
    <>
      {/* 桌面端侧边栏 - 固定在视口右侧，计算位置在容器右边缘外 */}
      <div className="hidden xl:block fixed w-64 z-40" style={{
        left: 'calc(50% + 640px + 2rem)',
        top: `${topOffset}px`
      }}>
        <div className="glass-sidebar p-6 max-h-[calc(100vh-160px)] overflow-y-auto glass-scrollbar">
          <div className="flex items-center justify-between mb-5">
            <h3 className="text-base font-semibold text-slate-800 dark:text-slate-100">
              目录导航
            </h3>
            <button
              onClick={() => setIsOpen(!isOpen)}
              className="p-1 rounded hover:bg-white/20 transition-colors"
            >
              <svg
                className={`w-4 h-4 text-slate-600 dark:text-slate-300 transition-transform ${
                  isOpen ? 'rotate-180' : ''
                }`}
                fill="none"
                stroke="currentColor"
                viewBox="0 0 24 24"
              >
                <path
                  strokeLinecap="round"
                  strokeLinejoin="round"
                  strokeWidth={2}
                  d="M19 9l-7 7-7-7"
                />
              </svg>
            </button>
          </div>

          <AnimatePresence>
            {isOpen && (
              <motion.nav
                initial={{ height: 0, opacity: 0 }}
                animate={{ height: 'auto', opacity: 1 }}
                exit={{ height: 0, opacity: 0 }}
                transition={{ duration: 0.3 }}
                className="space-y-1"
              >
                {tocItems.map((item, index) => (
                  <motion.button
                    key={item.id}
                    onClick={() => scrollToHeading(item.id)}
                    initial={{ opacity: 0, x: -10 }}
                    animate={{ opacity: 1, x: 0 }}
                    transition={{ delay: index * 0.05 }}
                    className={`
                      w-full text-left py-2.5 px-4 rounded-lg transition-all duration-200
                      ${activeId === item.id
                        ? 'bg-blue-50 dark:bg-blue-900/20 text-blue-700 dark:text-blue-400 font-semibold border-l-3 border-blue-600 shadow-sm'
                        : 'text-slate-600 dark:text-slate-400 hover:bg-slate-100/60 dark:hover:bg-white/10 hover:text-slate-900 dark:hover:text-slate-100 hover:border-l-3 hover:border-slate-300 dark:hover:border-slate-600'
                      }
                      ${item.level === 1 ? 'text-base font-medium' : item.level === 2 ? 'text-sm' : 'text-xs'}
                    `}
                    style={{
                      paddingLeft: `${(item.level - 1) * 16 + 16}px`,
                      borderLeftWidth: activeId === item.id ? '3px' : '0px',
                    }}
                  >
                    <span className="line-clamp-2 leading-relaxed">{item.title}</span>
                  </motion.button>
                ))}
              </motion.nav>
            )}
          </AnimatePresence>
        </div>
      </div>

      {/* 移动端悬浮按钮 */}
      <div className="lg:hidden fixed bottom-20 right-6 z-40">
        <button
          onClick={() => setIsOpen(!isOpen)}
          className="p-4 rounded-full glass-button shadow-lg"
        >
          <svg className="w-6 h-6 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path
              strokeLinecap="round"
              strokeLinejoin="round"
              strokeWidth={2}
              d="M4 6h16M4 12h16M4 18h16"
            />
          </svg>
        </button>

        <AnimatePresence>
          {isOpen && (
            <motion.div
              initial={{ opacity: 0, scale: 0.9, y: 10 }}
              animate={{ opacity: 1, scale: 1, y: 0 }}
              exit={{ opacity: 0, scale: 0.9, y: 10 }}
              className="absolute bottom-16 right-0 w-72 glass-content p-4 rounded-lg shadow-2xl max-h-96 overflow-y-auto glass-scrollbar"
            >
              <div className="flex items-center justify-between mb-3">
                <h3 className="text-sm font-semibold text-slate-700 dark:text-slate-200">
                  目录导航
                </h3>
                <button
                  onClick={() => setIsOpen(false)}
                  className="p-1 rounded hover:bg-white/20 transition-colors"
                >
                  <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
                  </svg>
                </button>
              </div>

              <nav className="space-y-1">
                {tocItems.map((item) => (
                  <button
                    key={item.id}
                    onClick={() => {
                      scrollToHeading(item.id)
                      setIsOpen(false)
                    }}
                    className={`
                      w-full text-left py-2.5 px-4 rounded-lg transition-all duration-200
                      ${activeId === item.id
                        ? 'bg-blue-50 dark:bg-blue-900/20 text-blue-700 dark:text-blue-400 font-semibold'
                        : 'text-slate-600 dark:text-slate-400 hover:bg-slate-100/60 dark:hover:bg-white/10'
                      }
                      ${item.level === 1 ? 'text-base font-medium' : item.level === 2 ? 'text-sm' : 'text-xs'}
                    `}
                    style={{
                      paddingLeft: `${(item.level - 1) * 16 + 16}px`,
                    }}
                  >
                    <span className="line-clamp-2 leading-relaxed">{item.title}</span>
                  </button>
                ))}
              </nav>
            </motion.div>
          )}
        </AnimatePresence>
      </div>
    </>
  )
}
