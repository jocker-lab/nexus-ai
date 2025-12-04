'use client'

import { use, useState, useEffect, useCallback } from 'react'
import { motion, AnimatePresence } from 'framer-motion'
import Link from 'next/link'
import { useReportData } from '../hooks/useReportData'
import ReactMarkdown from 'react-markdown'
import remarkGfm from 'remark-gfm'
import remarkMath from 'remark-math'
import rehypeKatex from 'rehype-katex'
import rehypeRaw from 'rehype-raw'
import { exportToPDF } from '../utils/pdf-export'
import 'katex/dist/katex.min.css'
import '../styles/report-light.css'

interface PageProps {
  params: Promise<{ id: string }>
}

interface TocItem {
  id: string
  text: string
  level: number
}

// Nexus Logo Component - Light Theme
const NexusLogo = ({ size = 32 }: { size?: number }) => (
  <div
    className="nexus-logo-light"
    style={{ width: size, height: size }}
  >
    <svg
      style={{ width: size * 0.6, height: size * 0.6 }}
      viewBox="0 0 24 24"
      fill="none"
      stroke="currentColor"
      strokeWidth="1.5"
    >
      <circle cx="12" cy="12" r="3" />
      <path d="M12 2v4m0 12v4M2 12h4m12 0h4" />
      <path d="M4.93 4.93l2.83 2.83m8.48 8.48l2.83 2.83M4.93 19.07l2.83-2.83m8.48-8.48l2.83-2.83" opacity="0.5" />
    </svg>
  </div>
)

// Preprocess markdown content to fix common issues with bold text
function preprocessMarkdown(content: string): string {
  if (!content) return ''

  let processed = content

  // Debug: log first 200 chars to console in development
  if (typeof window !== 'undefined' && process.env.NODE_ENV === 'development') {
    console.log('[Markdown Debug] Original first 200 chars:', JSON.stringify(content.slice(0, 200)))
  }

  // 1. 修复全角星号为半角星号 (用于加粗)
  processed = processed.replace(/＊＊/g, '**')
  processed = processed.replace(/＊/g, '*')

  // 2. 移除加粗标记周围可能存在的零宽字符
  const zeroWidthChars = /[\u200B\u200C\u200D\uFEFF\u00A0]/g
  processed = processed.replace(zeroWidthChars, '')

  // 3. 标准化换行符
  processed = processed.replace(/\r\n/g, '\n')

  // 4. 使用 HTML 标签直接替换 markdown 格式
  // 这是最可靠的解决方案，因为 rehype-raw 会处理 HTML 标签

  // 4a. 替换 **text** 为 <strong>text</strong>
  processed = processed.replace(/\*\*([^*\n]+?)\*\*/g, '<strong>$1</strong>')

  // 4b. 替换 *text* 为 <em>text</em> (确保不匹配已转换的 strong 标签)
  processed = processed.replace(/(?<!<)\*([^*\n<>]+?)\*(?!>)/g, '<em>$1</em>')

  // Debug: log processed first 200 chars
  if (typeof window !== 'undefined' && process.env.NODE_ENV === 'development') {
    console.log('[Markdown Debug] Processed first 200 chars:', JSON.stringify(processed.slice(0, 200)))
  }

  return processed
}

// Extract headings from markdown content
function extractHeadings(content: string): TocItem[] {
  const headings: TocItem[] = []
  const lines = content.split('\n')

  lines.forEach((line) => {
    const match = line.match(/^(#{1,3})\s+(.+)$/)
    if (match) {
      const level = match[1].length
      const text = match[2].trim()
      const id = text
        .toLowerCase()
        .replace(/[^\w\u4e00-\u9fa5]+/g, '-')
        .replace(/^-|-$/g, '')
      headings.push({ id, text, level })
    }
  })

  return headings
}

export default function ReportPage({ params }: PageProps) {
  const resolvedParams = use(params)
  const { report, loading, error } = useReportData(resolvedParams.id)
  const [isExporting, setIsExporting] = useState(false)
  const [activeHeading, setActiveHeading] = useState<string>('')
  const [showMobileToc, setShowMobileToc] = useState(false)
  const [showExportMenu, setShowExportMenu] = useState(false)
  const [readingProgress, setReadingProgress] = useState(0)
  const [showBackToTop, setShowBackToTop] = useState(false)

  // Reading progress tracking
  useEffect(() => {
    const handleScroll = () => {
      const scrollTop = window.scrollY
      const docHeight = document.documentElement.scrollHeight - window.innerHeight
      const progress = docHeight > 0 ? (scrollTop / docHeight) * 100 : 0
      setReadingProgress(Math.min(progress, 100))
      setShowBackToTop(scrollTop > 500)
    }

    window.addEventListener('scroll', handleScroll)
    return () => window.removeEventListener('scroll', handleScroll)
  }, [])

  // Active heading tracking (scroll spy)
  useEffect(() => {
    if (!report) return

    const headings = extractHeadings(report.content)
    const observerCallback: IntersectionObserverCallback = (entries) => {
      entries.forEach((entry) => {
        if (entry.isIntersecting) {
          setActiveHeading(entry.target.id)
        }
      })
    }

    const observer = new IntersectionObserver(observerCallback, {
      rootMargin: '-100px 0px -60% 0px',
      threshold: 0
    })

    headings.forEach(({ id }) => {
      const element = document.getElementById(id)
      if (element) observer.observe(element)
    })

    return () => observer.disconnect()
  }, [report])

  const handleExportPDF = async () => {
    if (!report) return

    try {
      setIsExporting(true)
      const filename = `${report.title.replace(/[^a-zA-Z0-9\u4e00-\u9fa5]/g, '_')}.pdf`
      await exportToPDF('report-content', {
        filename,
        onProgress: (progress) => console.log('Export progress:', progress)
      })
    } catch (err) {
      console.error('Export failed:', err)
      alert('导出失败，请重试')
    } finally {
      setIsExporting(false)
    }
  }

  const scrollToHeading = useCallback((id: string) => {
    const element = document.getElementById(id)
    if (element) {
      const offset = 120
      const elementPosition = element.getBoundingClientRect().top + window.scrollY
      window.scrollTo({ top: elementPosition - offset, behavior: 'smooth' })
      setShowMobileToc(false)
    }
  }, [])

  // Loading State
  if (loading) {
    return (
      <div className="report-page-light">
        <div className="report-loading-light">
          <motion.div
            initial={{ opacity: 0, scale: 0.9 }}
            animate={{ opacity: 1, scale: 1 }}
            className="report-loading-card-light"
          >
            <div className="report-loading-spinner">
              <div className="spinner-ring"></div>
              <NexusLogo size={40} />
            </div>
            <h2>正在加载报告</h2>
            <p>智能分析系统处理中...</p>
          </motion.div>
        </div>
      </div>
    )
  }

  // Error State
  if (error || !report) {
    return (
      <div className="report-page-light">
        <div className="report-loading-light">
          <motion.div
            initial={{ opacity: 0, scale: 0.9 }}
            animate={{ opacity: 1, scale: 1 }}
            className="report-error-card-light"
          >
            <div className="report-error-icon-light">
              <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.5">
                <path strokeLinecap="round" strokeLinejoin="round" d="M12 8v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
              </svg>
            </div>
            <h2>加载失败</h2>
            <p>{error || '未找到报告数据'}</p>
            <div className="report-error-actions-light">
              <button onClick={() => window.location.reload()} className="btn-secondary-light">
                重试
              </button>
              <Link href="/">
                <button className="btn-primary-light">返回首页</button>
              </Link>
            </div>
          </motion.div>
        </div>
      </div>
    )
  }

  const tocItems = extractHeadings(report.content)

  return (
    <div className="report-page-light">
      {/* Reading Progress Bar */}
      <div className="progress-bar-light">
        <motion.div
          className="progress-fill-light"
          style={{ width: `${readingProgress}%` }}
          initial={{ width: 0 }}
        />
      </div>

      {/* Navigation Header */}
      <motion.nav
        initial={{ opacity: 0, y: -20 }}
        animate={{ opacity: 1, y: 0 }}
        className="nav-light"
      >
        <div className="nav-container-light">
          <Link href="/" className="nav-brand-light">
            <NexusLogo size={36} />
            <span>NEXUS AI</span>
          </Link>

          <div className="nav-actions-light">
            <button
              className="nav-btn-light toc-toggle-light"
              onClick={() => setShowMobileToc(!showMobileToc)}
            >
              <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                <path d="M4 6h16M4 12h16M4 18h10" />
              </svg>
              <span>目录</span>
            </button>

            {/* Export Dropdown */}
            <div className="export-dropdown-container">
              <button
                onClick={() => setShowExportMenu(!showExportMenu)}
                disabled={isExporting}
                className="nav-btn-light export-btn-light"
              >
                {isExporting ? (
                  <>
                    <svg className="spin" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                      <circle cx="12" cy="12" r="10" opacity="0.25" />
                      <path d="M12 2a10 10 0 0 1 10 10" />
                    </svg>
                    <span>导出中...</span>
                  </>
                ) : (
                  <>
                    <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                      <path d="M21 15v4a2 2 0 01-2 2H5a2 2 0 01-2-2v-4" />
                      <polyline points="7 10 12 15 17 10" />
                      <line x1="12" y1="15" x2="12" y2="3" />
                    </svg>
                    <span>导出</span>
                    <svg className="dropdown-arrow" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                      <polyline points="6 9 12 15 18 9" />
                    </svg>
                  </>
                )}
              </button>

              <AnimatePresence>
                {showExportMenu && (
                  <>
                    {/* Backdrop */}
                    <motion.div
                      initial={{ opacity: 0 }}
                      animate={{ opacity: 1 }}
                      exit={{ opacity: 0 }}
                      className="export-backdrop"
                      onClick={() => setShowExportMenu(false)}
                    />
                    {/* Dropdown Menu */}
                    <motion.div
                      initial={{ opacity: 0, y: -10, scale: 0.95 }}
                      animate={{ opacity: 1, y: 0, scale: 1 }}
                      exit={{ opacity: 0, y: -10, scale: 0.95 }}
                      transition={{ duration: 0.15, ease: 'easeOut' }}
                      className="export-dropdown-menu"
                    >
                      <div className="export-menu-header">
                        <span>选择导出格式</span>
                      </div>

                      <button
                        className="export-menu-item"
                        onClick={() => {
                          setShowExportMenu(false)
                          // TODO: Implement MD export
                          console.log('Export as Markdown')
                        }}
                      >
                        <div className="export-icon export-icon-md">
                          <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.5">
                            <path d="M3 3v18h18V6l-5-3H3z" />
                            <path d="M14 3v5h5" />
                            <path d="M7 13l2 2 4-4" strokeLinecap="round" strokeLinejoin="round" />
                          </svg>
                        </div>
                        <div className="export-item-content">
                          <span className="export-item-title">Markdown</span>
                          <span className="export-item-desc">适合二次编辑和版本控制</span>
                        </div>
                        <span className="export-item-ext">.md</span>
                      </button>

                      <button
                        className="export-menu-item"
                        onClick={() => {
                          setShowExportMenu(false)
                          // TODO: Implement Word export
                          console.log('Export as Word')
                        }}
                      >
                        <div className="export-icon export-icon-word">
                          <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.5">
                            <path d="M4 4v16a2 2 0 002 2h12a2 2 0 002-2V8l-6-6H6a2 2 0 00-2 2z" />
                            <path d="M14 2v6h6" />
                            <path d="M8 13h8M8 17h5" strokeLinecap="round" />
                          </svg>
                        </div>
                        <div className="export-item-content">
                          <span className="export-item-title">Word 文档</span>
                          <span className="export-item-desc">便于分享和打印</span>
                        </div>
                        <span className="export-item-ext">.docx</span>
                      </button>

                      <button
                        className="export-menu-item"
                        onClick={() => {
                          setShowExportMenu(false)
                          handleExportPDF()
                        }}
                      >
                        <div className="export-icon export-icon-pdf">
                          <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.5">
                            <path d="M4 4v16a2 2 0 002 2h12a2 2 0 002-2V8l-6-6H6a2 2 0 00-2 2z" />
                            <path d="M14 2v6h6" />
                            <path d="M10 12v6M10 15h2a1.5 1.5 0 000-3h-2" strokeLinecap="round" strokeLinejoin="round" />
                          </svg>
                        </div>
                        <div className="export-item-content">
                          <span className="export-item-title">PDF 文档</span>
                          <span className="export-item-desc">保持排版，适合正式发布</span>
                        </div>
                        <span className="export-item-ext">.pdf</span>
                      </button>
                    </motion.div>
                  </>
                )}
              </AnimatePresence>
            </div>
          </div>
        </div>
      </motion.nav>

      {/* Mobile TOC Drawer */}
      <AnimatePresence>
        {showMobileToc && (
          <>
            <motion.div
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              exit={{ opacity: 0 }}
              className="mobile-toc-overlay-light"
              onClick={() => setShowMobileToc(false)}
            />
            <motion.div
              initial={{ x: '100%' }}
              animate={{ x: 0 }}
              exit={{ x: '100%' }}
              transition={{ type: 'tween', duration: 0.3 }}
              className="mobile-toc-light"
            >
              <div className="mobile-toc-header-light">
                <h3>目录导航</h3>
                <button onClick={() => setShowMobileToc(false)}>
                  <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                    <path d="M6 18L18 6M6 6l12 12" />
                  </svg>
                </button>
              </div>
              <nav className="mobile-toc-nav-light">
                {tocItems.map((item) => (
                  <button
                    key={item.id}
                    onClick={() => scrollToHeading(item.id)}
                    className={`toc-item-light toc-level-${item.level} ${activeHeading === item.id ? 'active' : ''}`}
                  >
                    {item.text}
                  </button>
                ))}
              </nav>
            </motion.div>
          </>
        )}
      </AnimatePresence>

      {/* Main Content Area */}
      <main className="main-light">
        <div className="content-wrapper-light">
          {/* Center Column: Header + Content */}
          <div className="center-column-light">
            {/* Report Header */}
            <motion.header
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.5 }}
              className="header-card-light"
            >
              {report.category && (
                <span className="category-badge-light">{report.category}</span>
              )}
              <h1 className="report-title-light">{report.title}</h1>
              {report.description && (
                <p className="report-desc-light">{report.description}</p>
              )}
              <div className="meta-row-light">
                <div className="meta-item-light">
                  <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                    <rect x="3" y="4" width="18" height="18" rx="2" ry="2" />
                    <line x1="16" y1="2" x2="16" y2="6" />
                    <line x1="8" y1="2" x2="8" y2="6" />
                    <line x1="3" y1="10" x2="21" y2="10" />
                  </svg>
                  <span suppressHydrationWarning>
                    {new Date(report.created_at).toLocaleDateString('zh-CN', {
                      year: 'numeric',
                      month: 'long',
                      day: 'numeric'
                    })}
                  </span>
                </div>
                <div className="meta-item-light">
                  <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                    <path d="M14 2H6a2 2 0 00-2 2v16a2 2 0 002 2h12a2 2 0 002-2V8z" />
                    <polyline points="14,2 14,8 20,8" />
                  </svg>
                  <span>{report.word_count?.toLocaleString() || 0} 字</span>
                </div>
                <div className="meta-item-light">
                  <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                    <circle cx="12" cy="12" r="10" />
                    <polyline points="12 6 12 12 16 14" />
                  </svg>
                  <span>约 {report.estimated_reading_time || 1} 分钟</span>
                </div>
              </div>
              {report.tags && (
                <div className="tags-row-light">
                  {(typeof report.tags === 'string' ? report.tags.split(',') : report.tags)
                    .filter((tag: string) => tag.trim())
                    .map((tag: string, index: number) => (
                      <span key={index} className="tag-light">{tag.trim()}</span>
                    ))}
                </div>
              )}
            </motion.header>

            {/* Report Content */}
            <motion.article
              id="report-content"
              className="content-card-light"
              initial={{ opacity: 0, y: 30 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.6, delay: 0.2 }}
            >
              <div className="markdown-light">
                <ReactMarkdown
                  remarkPlugins={[remarkGfm, remarkMath]}
                  rehypePlugins={[rehypeKatex, rehypeRaw]}
                  components={{
                    h1: ({ children, ...props }) => {
                      const text = String(children)
                      const id = text.toLowerCase().replace(/[^\w\u4e00-\u9fa5]+/g, '-').replace(/^-|-$/g, '')
                      return <h1 id={id} {...props}>{children}</h1>
                    },
                    h2: ({ children, ...props }) => {
                      const text = String(children)
                      const id = text.toLowerCase().replace(/[^\w\u4e00-\u9fa5]+/g, '-').replace(/^-|-$/g, '')
                      return <h2 id={id} {...props}>{children}</h2>
                    },
                    h3: ({ children, ...props }) => {
                      const text = String(children)
                      const id = text.toLowerCase().replace(/[^\w\u4e00-\u9fa5]+/g, '-').replace(/^-|-$/g, '')
                      return <h3 id={id} {...props}>{children}</h3>
                    },
                    strong: ({ children, ...props }) => (
                      <strong className="text-emphasis" {...props}>{children}</strong>
                    ),
                    em: ({ children, ...props }) => (
                      <em className="text-italic" {...props}>{children}</em>
                    ),
                    a: ({ href, children, ...props }) => (
                      <a href={href} target="_blank" rel="noopener noreferrer" className="link-light" {...props}>
                        {children}
                      </a>
                    ),
                    img: ({ src, alt, ...props }) => (
                      <img src={src} alt={alt || ''} loading="lazy" className="img-light" {...props} />
                    ),
                    blockquote: ({ children, ...props }) => (
                      <blockquote className="blockquote-light" {...props}>{children}</blockquote>
                    ),
                    ul: ({ children, ...props }) => (
                      <ul className="list-light" {...props}>{children}</ul>
                    ),
                    ol: ({ children, ...props }) => (
                      <ol className="list-ordered-light" {...props}>{children}</ol>
                    ),
                    table: ({ children, ...props }) => (
                      <div className="table-wrapper-light">
                        <table className="table-light" {...props}>{children}</table>
                      </div>
                    ),
                    pre: ({ children, ...props }) => (
                      <pre className="code-block-light" {...props}>{children}</pre>
                    ),
                    code: ({ className, children, ...props }) => {
                      const isInline = !className
                      return isInline ? (
                        <code className="code-inline-light" {...props}>{children}</code>
                      ) : (
                        <code className={className} {...props}>{children}</code>
                      )
                    }
                  }}
                >
                  {preprocessMarkdown(report.content)}
                </ReactMarkdown>
              </div>
            </motion.article>

            {/* Report Meta Footer */}
            <motion.section
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: 0.4 }}
              className="meta-card-light"
            >
              <div className="meta-grid-light">
                <div className="meta-block-light">
                  <span className="meta-label-light">报告状态</span>
                  <div className="status-light">
                    <span className={`status-dot-light ${report.status}`} />
                    <span>
                      {report.status === 'published' ? '已发布' : report.status === 'draft' ? '草稿' : '已归档'}
                    </span>
                  </div>
                </div>
                <div className="meta-block-light">
                  <span className="meta-label-light">当前版本</span>
                  <span className="meta-value-light">v{report.current_version}</span>
                </div>
                <div className="meta-block-light">
                  <span className="meta-label-light">最后更新</span>
                  <span className="meta-value-light" suppressHydrationWarning>
                    {new Date(report.updated_at).toLocaleString('zh-CN')}
                  </span>
                </div>
              </div>
            </motion.section>
          </div>

          {/* Right Sidebar: TOC */}
          <aside className="toc-sidebar-light">
            <div className="toc-wrapper-light">
              <h3 className="toc-title-light">
                <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                  <path d="M4 6h16M4 12h12M4 18h8" />
                </svg>
                目录导航
              </h3>
              <nav className="toc-nav-light">
                {tocItems.map((item, index) => (
                  <motion.button
                    key={item.id}
                    initial={{ opacity: 0, x: 20 }}
                    animate={{ opacity: 1, x: 0 }}
                    transition={{ delay: index * 0.03 }}
                    onClick={() => scrollToHeading(item.id)}
                    className={`toc-item-light toc-level-${item.level} ${activeHeading === item.id ? 'active' : ''}`}
                  >
                    <span className="toc-indicator" />
                    <span className="toc-text">{item.text}</span>
                  </motion.button>
                ))}
              </nav>
            </div>
          </aside>
        </div>
      </main>

      {/* Back to Top Button */}
      <AnimatePresence>
        {showBackToTop && (
          <motion.button
            initial={{ opacity: 0, scale: 0.8 }}
            animate={{ opacity: 1, scale: 1 }}
            exit={{ opacity: 0, scale: 0.8 }}
            whileHover={{ scale: 1.1 }}
            whileTap={{ scale: 0.9 }}
            className="back-to-top-light"
            onClick={() => window.scrollTo({ top: 0, behavior: 'smooth' })}
          >
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
              <path d="M5 10l7-7m0 0l7 7m-7-7v18" />
            </svg>
          </motion.button>
        )}
      </AnimatePresence>

      {/* Footer */}
      <footer className="footer-light">
        <div className="footer-container-light">
          <div className="footer-brand-light">
            <NexusLogo size={28} />
            <span>Nexus AI · 智能研究分析平台</span>
          </div>
          <nav className="footer-nav-light">
            <Link href="/chat">开始对话</Link>
            <Link href="/">返回首页</Link>
          </nav>
        </div>
      </footer>
    </div>
  )
}
