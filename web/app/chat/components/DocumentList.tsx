'use client'

import { useState, useRef, useEffect } from 'react'
import { motion, AnimatePresence } from 'framer-motion'
import { useRouter } from 'next/navigation'
import { useDocuments, Document } from '../hooks/useDocuments'

// ============================================
// STATUS BADGE COMPONENT
// ============================================
const StatusBadge = ({ status }: { status: Document['status'] }) => {
  const config = {
    draft: {
      label: '草稿',
      bg: 'bg-[var(--text-tertiary)]/20',
      text: 'text-[var(--text-tertiary)]',
      dot: 'bg-[var(--text-tertiary)]'
    },
    published: {
      label: '已发布',
      bg: 'bg-[var(--nexus-cyan)]/15',
      text: 'text-[var(--nexus-cyan)]',
      dot: 'bg-[var(--nexus-cyan)]'
    },
    archived: {
      label: '已归档',
      bg: 'bg-[var(--nexus-violet)]/15',
      text: 'text-[var(--nexus-violet)]',
      dot: 'bg-[var(--nexus-violet)]'
    }
  }

  const { label, bg, text, dot } = config[status]

  return (
    <span className={`inline-flex items-center gap-1 px-1.5 py-0.5 rounded text-[10px] font-medium ${bg} ${text}`}>
      <span className={`w-1.5 h-1.5 rounded-full ${dot}`} />
      {label}
    </span>
  )
}

// ============================================
// DOCUMENT CARD COMPONENT
// ============================================
interface DocumentCardProps {
  doc: Document
  isCollapsed: boolean
  onPreview: (documentId: string) => void
  onDelete: (documentId: string) => void
}

const DocumentCard = ({ doc, isCollapsed, onPreview, onDelete }: DocumentCardProps) => {
  const [showMenu, setShowMenu] = useState(false)
  const menuRef = useRef<HTMLDivElement>(null)

  useEffect(() => {
    const handleClickOutside = (event: MouseEvent) => {
      if (menuRef.current && !menuRef.current.contains(event.target as Node)) {
        setShowMenu(false)
      }
    }
    window.document.addEventListener('mousedown', handleClickOutside)
    return () => window.document.removeEventListener('mousedown', handleClickOutside)
  }, [])

  const formatDate = (dateStr: string) => {
    const date = new Date(dateStr)
    const now = new Date()
    const diff = now.getTime() - date.getTime()
    const days = Math.floor(diff / (1000 * 60 * 60 * 24))

    if (days === 0) return '今天'
    if (days === 1) return '昨天'
    if (days < 7) return `${days}天前`
    return date.toLocaleDateString('zh-CN', { month: 'short', day: 'numeric' })
  }

  if (isCollapsed) {
    return (
      <motion.button
        whileHover={{ scale: 1.05 }}
        whileTap={{ scale: 0.95 }}
        onClick={() => onPreview(doc.id)}
        className="w-10 h-10 rounded-xl bg-[var(--nexus-surface)] flex items-center justify-center group relative"
        title={doc.title}
      >
        <svg className="w-5 h-5 text-[var(--text-tertiary)] group-hover:text-[var(--nexus-cyan)]" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.5">
          <path d="M9 12h6M9 16h6M17 21H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
        </svg>
        {/* Status indicator dot */}
        <span className={`absolute -top-0.5 -right-0.5 w-2.5 h-2.5 rounded-full border-2 border-[var(--nexus-abyss)] ${
          doc.status === 'published' ? 'bg-[var(--nexus-cyan)]' :
          doc.status === 'archived' ? 'bg-[var(--nexus-violet)]' : 'bg-[var(--text-tertiary)]'
        }`} />
      </motion.button>
    )
  }

  return (
    <motion.div
      initial={{ opacity: 0, x: -10 }}
      animate={{ opacity: 1, x: 0 }}
      className="group relative"
    >
      <div
        onClick={() => onPreview(doc.id)}
        className="flex items-start gap-3 px-3 py-2.5 rounded-lg cursor-pointer transition-all duration-200 hover:bg-[var(--nexus-surface)] border-l-2 border-l-transparent hover:border-l-[var(--nexus-cyan)]"
      >
        {/* Document Icon */}
        <div className="flex-shrink-0 w-8 h-8 rounded-lg bg-gradient-to-br from-[var(--nexus-cyan)]/10 to-[var(--nexus-violet)]/10 flex items-center justify-center mt-0.5">
          <svg className="w-4 h-4 text-[var(--nexus-cyan)]" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.5">
            <path d="M9 12h6M9 16h6M17 21H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
            <path d="M13 3v6h6" />
          </svg>
        </div>

        {/* Content */}
        <div className="flex-1 min-w-0">
          <div className="flex items-center gap-2 mb-0.5">
            <h4 className="text-sm font-medium text-[var(--text-primary)] truncate flex-1">
              {doc.title || '未命名文档'}
            </h4>
          </div>
          <div className="flex items-center gap-2">
            <StatusBadge status={doc.status} />
            <span className="text-[10px] text-[var(--text-tertiary)]">
              {formatDate(doc.updated_at)}
            </span>
            {doc.word_count > 0 && (
              <span className="text-[10px] text-[var(--text-tertiary)]">
                {doc.word_count.toLocaleString()} 字
              </span>
            )}
          </div>
        </div>

        {/* Actions */}
        <div className="relative" ref={menuRef}>
          <button
            onClick={(e) => { e.stopPropagation(); setShowMenu(!showMenu) }}
            className="w-6 h-6 rounded flex items-center justify-center text-[var(--text-tertiary)] opacity-0 group-hover:opacity-100 hover:bg-[var(--nexus-elevated)] hover:text-[var(--text-primary)] transition-all"
          >
            <svg className="w-4 h-4" viewBox="0 0 24 24" fill="currentColor">
              <circle cx="12" cy="12" r="1.5"/>
              <circle cx="19" cy="12" r="1.5"/>
              <circle cx="5" cy="12" r="1.5"/>
            </svg>
          </button>

          {/* Dropdown Menu */}
          <AnimatePresence>
            {showMenu && (
              <motion.div
                initial={{ opacity: 0, scale: 0.95, y: -5 }}
                animate={{ opacity: 1, scale: 1, y: 0 }}
                exit={{ opacity: 0, scale: 0.95, y: -5 }}
                className="absolute right-0 top-full mt-1 w-36 py-1 bg-[var(--nexus-elevated)] border border-[var(--border-subtle)] rounded-lg shadow-xl z-50"
              >
                <button
                  onClick={(e) => { e.stopPropagation(); onPreview(doc.id); setShowMenu(false) }}
                  className="w-full flex items-center gap-2 px-3 py-2 text-sm text-[var(--text-secondary)] hover:text-[var(--text-primary)] hover:bg-[var(--nexus-surface)] transition-colors"
                >
                  <svg className="w-4 h-4" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                    <path d="M1 12s4-8 11-8 11 8 11 8-4 8-11 8-11-8-11-8z"/>
                    <circle cx="12" cy="12" r="3"/>
                  </svg>
                  预览
                </button>
                <button
                  onClick={(e) => { e.stopPropagation(); onDelete(doc.id); setShowMenu(false) }}
                  className="w-full flex items-center gap-2 px-3 py-2 text-sm text-[var(--nexus-error)] hover:bg-[var(--nexus-error)]/10 transition-colors"
                >
                  <svg className="w-4 h-4" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                    <path d="M3 6h18M19 6v14a2 2 0 01-2 2H7a2 2 0 01-2-2V6m3 0V4a2 2 0 012-2h4a2 2 0 012 2v2"/>
                  </svg>
                  删除
                </button>
              </motion.div>
            )}
          </AnimatePresence>
        </div>
      </div>
    </motion.div>
  )
}

// ============================================
// MAIN DOCUMENT LIST COMPONENT
// ============================================
interface DocumentListProps {
  isCollapsed: boolean
}

export function DocumentList({ isCollapsed }: DocumentListProps) {
  const router = useRouter()
  const { documents, loading, error, refetch, deleteDocument } = useDocuments()
  const [searchQuery, setSearchQuery] = useState('')
  const [statusFilter, setStatusFilter] = useState<'all' | Document['status']>('all')

  const handlePreview = (documentId: string) => {
    router.push(`/documents/${documentId}`)
  }

  const handleDelete = async (documentId: string) => {
    if (confirm('确定要删除这份文档吗？此操作无法撤销。')) {
      await deleteDocument(documentId)
    }
  }

  // Filter documents
  const filteredDocuments = documents.filter(doc => {
    const matchesSearch = doc.title?.toLowerCase().includes(searchQuery.toLowerCase())
    const matchesStatus = statusFilter === 'all' || doc.status === statusFilter
    return matchesSearch && matchesStatus
  })

  // Group by time
  const groupDocumentsByTime = () => {
    const grouped: { [key: string]: Document[] } = {}
    const now = new Date()
    const today = new Date(now.getFullYear(), now.getMonth(), now.getDate())
    const yesterday = new Date(today.getTime() - 24 * 60 * 60 * 1000)
    const weekAgo = new Date(today.getTime() - 7 * 24 * 60 * 60 * 1000)

    filteredDocuments.forEach(doc => {
      const date = new Date(doc.updated_at)
      let key: string

      if (date >= today) {
        key = '今天'
      } else if (date >= yesterday) {
        key = '昨天'
      } else if (date >= weekAgo) {
        key = '本周'
      } else {
        key = '更早'
      }

      if (!grouped[key]) grouped[key] = []
      grouped[key].push(doc)
    })

    return grouped
  }

  const groupedDocuments = groupDocumentsByTime()

  // Collapsed view
  if (isCollapsed) {
    return (
      <div className="flex flex-col items-center py-4 gap-3">
        <div className="w-10 h-10 rounded-xl bg-[var(--nexus-surface)] flex items-center justify-center" title={`${documents.length} 份文档`}>
          <svg className="w-5 h-5 text-[var(--text-tertiary)]" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.5">
            <path d="M9 12h6M9 16h6M17 21H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
          </svg>
        </div>
        <span className="text-[10px] text-[var(--text-tertiary)]">{documents.length}</span>
      </div>
    )
  }

  // Loading state
  if (loading) {
    return (
      <div className="flex items-center justify-center py-8">
        <div className="nexus-spinner w-6 h-6" />
      </div>
    )
  }

  // Error state
  if (error) {
    return (
      <div className="text-center py-8 px-4">
        <div className="w-12 h-12 mx-auto mb-3 rounded-xl bg-[var(--nexus-error)]/10 flex items-center justify-center">
          <svg className="w-6 h-6 text-[var(--nexus-error)]" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
            <circle cx="12" cy="12" r="10"/>
            <line x1="12" y1="8" x2="12" y2="12"/>
            <line x1="12" y1="16" x2="12.01" y2="16"/>
          </svg>
        </div>
        <p className="text-sm text-[var(--nexus-error)]">{error}</p>
        <button
          onClick={refetch}
          className="mt-3 text-sm text-[var(--nexus-cyan)] hover:underline"
        >
          重试
        </button>
      </div>
    )
  }

  // Empty state
  if (documents.length === 0) {
    return (
      <div className="text-center py-8 px-4">
        <div className="w-14 h-14 mx-auto mb-4 rounded-2xl bg-gradient-to-br from-[var(--nexus-cyan)]/10 to-[var(--nexus-violet)]/10 flex items-center justify-center">
          <svg className="w-7 h-7 text-[var(--text-tertiary)]" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.5">
            <path d="M9 12h6M9 16h6M17 21H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
            <path d="M13 3v6h6" />
          </svg>
        </div>
        <p className="text-sm text-[var(--text-tertiary)] mb-1">暂无文档</p>
        <p className="text-xs text-[var(--text-tertiary)]/60">
          在对话中生成您的第一份文档
        </p>
      </div>
    )
  }

  return (
    <div className="flex flex-col h-full">
      {/* Search & Filter */}
      <div className="px-3 py-2 space-y-2">
        {/* Search Input */}
        <div className="relative">
          <svg className="absolute left-2.5 top-1/2 -translate-y-1/2 w-4 h-4 text-[var(--text-tertiary)]" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
            <circle cx="11" cy="11" r="8"/>
            <path d="m21 21-4.3-4.3"/>
          </svg>
          <input
            type="text"
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            placeholder="搜索文档..."
            className="w-full pl-8 pr-3 py-1.5 text-sm bg-[var(--nexus-surface)] border border-transparent rounded-lg text-[var(--text-primary)] placeholder:text-[var(--text-tertiary)] focus:border-[var(--nexus-cyan)]/30 focus:outline-none transition-colors"
          />
        </div>

        {/* Status Filter */}
        <div className="flex gap-1">
          {(['all', 'published', 'draft', 'archived'] as const).map(status => (
            <button
              key={status}
              onClick={() => setStatusFilter(status)}
              className={`flex-1 px-2 py-1 text-[10px] font-medium rounded transition-colors ${
                statusFilter === status
                  ? 'bg-[var(--nexus-cyan)]/15 text-[var(--nexus-cyan)]'
                  : 'text-[var(--text-tertiary)] hover:bg-[var(--nexus-surface)]'
              }`}
            >
              {status === 'all' ? '全部' : status === 'published' ? '已发布' : status === 'draft' ? '草稿' : '已归档'}
            </button>
          ))}
        </div>
      </div>

      {/* Documents List */}
      <div className="flex-1 overflow-y-auto px-2">
        {filteredDocuments.length === 0 ? (
          <div className="text-center py-6">
            <p className="text-sm text-[var(--text-tertiary)]">未找到匹配的文档</p>
          </div>
        ) : (
          Object.entries(groupedDocuments).map(([groupKey, groupDocs]) => (
            <div key={groupKey} className="mb-4">
              <div className="px-3 py-1.5">
                <span className="text-[10px] font-semibold text-[var(--text-tertiary)] uppercase tracking-wider">
                  {groupKey}
                </span>
              </div>
              <div className="space-y-0.5">
                {groupDocs.map((d) => (
                  <DocumentCard
                    key={d.id}
                    doc={d}
                    isCollapsed={false}
                    onPreview={handlePreview}
                    onDelete={handleDelete}
                  />
                ))}
              </div>
            </div>
          ))
        )}
      </div>

      {/* Footer Stats */}
      <div className="px-3 py-2 border-t border-[var(--border-subtle)]">
        <div className="flex items-center justify-between text-[10px] text-[var(--text-tertiary)]">
          <span>共 {documents.length} 份文档</span>
          <button
            onClick={refetch}
            className="hover:text-[var(--nexus-cyan)] transition-colors"
          >
            刷新
          </button>
        </div>
      </div>
    </div>
  )
}

// 兼容性别名
export const ReportList = DocumentList

export default DocumentList
