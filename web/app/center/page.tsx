'use client'

import { useState, useRef, useMemo, useEffect } from 'react'
import { motion, AnimatePresence } from 'framer-motion'
import Link from 'next/link'
import { useRouter } from 'next/navigation'
import { useAuthStore } from '@/lib/stores/auth'
import { useReports, Report } from '../chat/hooks/useReports'
import { useTemplates, WritingTemplate } from '../chat/hooks/useTemplates'
import { useTemplateUpload, ParseRecord } from '../chat/hooks/useTemplateUpload'
import TemplateDetailModal from './components/TemplateDetailModal'

// ============================================
// TEMPLATE CATEGORIES (动态生成将基于模版数据)
// ============================================
const DEFAULT_TEMPLATE_CATEGORIES = [
  { id: 'all', name: '全部', icon: '◈' },
]

// ============================================
// ANIMATED BACKGROUND
// ============================================
const NeuralBackground = () => (
  <div className="fixed inset-0 pointer-events-none overflow-hidden">
    <div className="absolute inset-0 bg-gradient-to-br from-[#0a0a0f] via-[#0d0d14] to-[#0a0f14]" />
    <div
      className="absolute inset-0 opacity-[0.03]"
      style={{
        backgroundImage: `
          linear-gradient(rgba(0, 245, 255, 0.3) 1px, transparent 1px),
          linear-gradient(90deg, rgba(0, 245, 255, 0.3) 1px, transparent 1px)
        `,
        backgroundSize: '60px 60px',
      }}
    />
    <div className="absolute top-0 left-1/4 w-[600px] h-[600px] bg-[#00F5FF]/5 rounded-full blur-[120px]" />
    <div className="absolute bottom-0 right-1/4 w-[500px] h-[500px] bg-[#8B5CF6]/5 rounded-full blur-[100px]" />
  </div>
)

// ============================================
// NEXUS LOGO
// ============================================
const NexusLogo = ({ size = 40 }: { size?: number }) => (
  <motion.div
    className="relative"
    whileHover={{ scale: 1.05 }}
    transition={{ type: "spring", stiffness: 400 }}
  >
    <div
      className="absolute inset-[-2px] rounded-xl opacity-60 blur-sm"
      style={{ background: 'linear-gradient(135deg, #00F5FF, #8B5CF6)' }}
    />
    <div
      className="relative rounded-xl flex items-center justify-center"
      style={{
        width: size,
        height: size,
        background: 'linear-gradient(135deg, #00F5FF 0%, #8B5CF6 100%)',
      }}
    >
      <svg
        className="text-white"
        style={{ width: size * 0.55, height: size * 0.55 }}
        viewBox="0 0 24 24"
        fill="none"
        stroke="currentColor"
        strokeWidth="2"
      >
        <circle cx="12" cy="12" r="3" />
        <path d="M12 2v4m0 12v4M2 12h4m12 0h4" />
        <path d="M4.93 4.93l2.83 2.83m8.48 8.48l2.83 2.83M4.93 19.07l2.83-2.83m8.48-8.48l2.83-2.83" opacity="0.5" />
      </svg>
    </div>
  </motion.div>
)

// ============================================
// STATUS INDICATOR
// ============================================
const StatusIndicator = ({ status }: { status: 'draft' | 'published' | 'archived' }) => {
  const config = {
    draft: { label: '草稿', color: '#F59E0B', glow: 'rgba(245, 158, 11, 0.4)' },
    published: { label: '已发布', color: '#00F5FF', glow: 'rgba(0, 245, 255, 0.4)' },
    archived: { label: '已归档', color: '#8B5CF6', glow: 'rgba(139, 92, 246, 0.4)' },
  }
  const { label, color, glow } = config[status]

  return (
    <div className="flex items-center gap-2">
      <motion.span
        className="w-2 h-2 rounded-full"
        style={{ backgroundColor: color, boxShadow: `0 0 8px ${glow}` }}
        animate={{ opacity: [1, 0.5, 1] }}
        transition={{ duration: 2, repeat: Infinity }}
      />
      <span className="text-xs font-medium" style={{ color }}>{label}</span>
    </div>
  )
}

// ============================================
// DOCUMENT CARD
// ============================================
interface DocumentCardProps {
  report: Report
  index: number
  onView: (id: string) => void
  onDelete: (id: string) => void
}

const DocumentCard = ({ report, index, onView, onDelete }: DocumentCardProps) => {
  const [isHovered, setIsHovered] = useState(false)

  // Parse tags string to array
  const tags = report.tags ? report.tags.split(',').map(t => t.trim()).filter(Boolean) : []

  return (
    <motion.div
      initial={{ opacity: 0, y: 30 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ delay: index * 0.06, duration: 0.5, ease: [0.23, 1, 0.32, 1] }}
      onMouseEnter={() => setIsHovered(true)}
      onMouseLeave={() => setIsHovered(false)}
      className="group relative"
    >
      <motion.div
        className="absolute inset-0 rounded-2xl opacity-0 group-hover:opacity-100 transition-opacity duration-500"
        style={{
          background: 'linear-gradient(135deg, rgba(0, 245, 255, 0.1), rgba(139, 92, 246, 0.1))',
          filter: 'blur(20px)',
        }}
      />

      <motion.div
        className="relative rounded-2xl overflow-hidden"
        animate={{ y: isHovered ? -4 : 0 }}
        transition={{ duration: 0.3 }}
        style={{
          background: 'linear-gradient(135deg, rgba(255,255,255,0.03) 0%, rgba(255,255,255,0.01) 100%)',
          backdropFilter: 'blur(20px)',
          border: '1px solid rgba(255,255,255,0.06)',
        }}
      >
        <motion.div
          className="absolute inset-0 rounded-2xl pointer-events-none"
          style={{
            background: `linear-gradient(135deg,
              ${isHovered ? 'rgba(0, 245, 255, 0.3)' : 'rgba(0, 245, 255, 0.1)'} 0%,
              transparent 50%,
              ${isHovered ? 'rgba(139, 92, 246, 0.3)' : 'rgba(139, 92, 246, 0.1)'} 100%)`,
            padding: '1px',
            WebkitMask: 'linear-gradient(#fff 0 0) content-box, linear-gradient(#fff 0 0)',
            WebkitMaskComposite: 'xor',
            maskComposite: 'exclude',
          }}
          animate={{ opacity: isHovered ? 1 : 0.5 }}
        />

        <div className="p-5">
          {/* Header */}
          <div className="flex items-start justify-between mb-3">
            <StatusIndicator status={report.status} />
            <motion.button
              onClick={(e) => { e.stopPropagation(); onDelete(report.id); }}
              className="w-7 h-7 rounded-lg flex items-center justify-center opacity-0 group-hover:opacity-100 transition-all"
              style={{ background: 'rgba(239, 68, 68, 0.1)' }}
              whileHover={{ scale: 1.1, background: 'rgba(239, 68, 68, 0.2)' }}
              whileTap={{ scale: 0.95 }}
            >
              <svg className="w-3.5 h-3.5 text-red-400" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                <path d="M3 6h18M19 6v14a2 2 0 01-2 2H7a2 2 0 01-2-2V6m3 0V4a2 2 0 012-2h4a2 2 0 012 2v2" />
              </svg>
            </motion.button>
          </div>

          {/* Category Badge */}
          {report.category && (
            <div
              className="inline-flex items-center gap-1 px-2 py-0.5 rounded text-[10px] font-medium mb-2"
              style={{ background: 'rgba(0, 245, 255, 0.1)', color: '#00F5FF' }}
            >
              {report.category}
            </div>
          )}

          {/* Title */}
          <h3
            className="text-base font-semibold mb-2 line-clamp-2 transition-colors duration-300"
            style={{ color: isHovered ? '#00F5FF' : 'rgba(255,255,255,0.9)' }}
          >
            {report.title}
          </h3>

          {/* Description */}
          <p className="text-sm text-white/40 line-clamp-2 mb-3 min-h-[36px]">
            {report.description || '暂无描述'}
          </p>

          {/* Tags */}
          {tags.length > 0 && (
            <div className="flex flex-wrap gap-1.5 mb-3">
              {tags.slice(0, 3).map((tag, i) => (
                <span
                  key={i}
                  className="px-2 py-0.5 rounded text-[10px] text-white/50"
                  style={{ background: 'rgba(139, 92, 246, 0.1)' }}
                >
                  #{tag}
                </span>
              ))}
              {tags.length > 3 && (
                <span className="text-[10px] text-white/30">+{tags.length - 3}</span>
              )}
            </div>
          )}

          {/* Meta */}
          <div className="flex items-center gap-3 mb-4 text-[11px] text-white/30">
            <span>{new Date(report.created_at).toLocaleDateString('zh-CN')}</span>
            <span>·</span>
            <span>{(report.word_count || 0).toLocaleString()} 字</span>
            <span>·</span>
            <span>约 {report.estimated_reading_time || 1} 分钟</span>
          </div>

          {/* Action */}
          <motion.button
            onClick={() => onView(report.id)}
            className="w-full py-2.5 rounded-xl font-medium text-sm transition-all duration-300"
            style={{
              background: isHovered
                ? 'linear-gradient(135deg, #00F5FF 0%, #8B5CF6 100%)'
                : 'rgba(255,255,255,0.05)',
              color: isHovered ? '#0a0a0f' : 'rgba(255,255,255,0.6)',
              border: isHovered ? 'none' : '1px solid rgba(255,255,255,0.1)',
            }}
            whileHover={{ scale: 1.02 }}
            whileTap={{ scale: 0.98 }}
          >
            查看文档
          </motion.button>
        </div>
      </motion.div>
    </motion.div>
  )
}

// ============================================
// TEMPLATE CARD
// ============================================
interface TemplateCardProps {
  template: WritingTemplate
  index: number
  onViewDetail: (template: WritingTemplate) => void
  onDelete: (id: string) => void
}

const TemplateCard = ({ template, index, onViewDetail, onDelete }: TemplateCardProps) => {
  const [isHovered, setIsHovered] = useState(false)

  // 根据状态确定样式
  const isPending = template.status === 'pending' || template.status === 'parsing'
  const isFailed = template.status === 'failed'

  // 提取章节标题作为内容展示
  const contents = template.sections?.slice(0, 3).map(s => s.title) || []

  return (
    <motion.div
      initial={{ opacity: 0, y: 30 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ delay: index * 0.06, duration: 0.5, ease: [0.23, 1, 0.32, 1] }}
      onMouseEnter={() => setIsHovered(true)}
      onMouseLeave={() => setIsHovered(false)}
      className="group relative"
    >
      <motion.div
        className="relative rounded-2xl overflow-hidden h-full"
        animate={{ y: isHovered ? -4 : 0 }}
        style={{
          background: isPending
            ? 'linear-gradient(135deg, rgba(245, 158, 11, 0.05) 0%, rgba(245, 158, 11, 0.02) 100%)'
            : isFailed
              ? 'linear-gradient(135deg, rgba(239, 68, 68, 0.05) 0%, rgba(239, 68, 68, 0.02) 100%)'
              : 'linear-gradient(135deg, rgba(139, 92, 246, 0.05) 0%, rgba(0, 245, 255, 0.02) 100%)',
          backdropFilter: 'blur(20px)',
          border: isPending
            ? '1px solid rgba(245, 158, 11, 0.15)'
            : isFailed
              ? '1px solid rgba(239, 68, 68, 0.15)'
              : '1px solid rgba(139, 92, 246, 0.15)',
        }}
      >
        <div className="p-5">
          {/* Header with status and delete */}
          <div className="flex items-start justify-between mb-3">
            <div
              className="inline-flex items-center gap-1.5 px-2.5 py-1 rounded-full text-[10px] font-medium"
              style={{
                background: isPending
                  ? 'rgba(245, 158, 11, 0.15)'
                  : isFailed
                    ? 'rgba(239, 68, 68, 0.15)'
                    : 'rgba(139, 92, 246, 0.15)',
                color: isPending ? '#F59E0B' : isFailed ? '#EF4444' : '#A78BFA',
              }}
            >
              {isPending ? '解析中' : isFailed ? '解析失败' : '模板'}
            </div>
            <motion.button
              onClick={(e) => { e.stopPropagation(); onDelete(template.id); }}
              className="w-7 h-7 rounded-lg flex items-center justify-center opacity-0 group-hover:opacity-100 transition-all"
              style={{ background: 'rgba(239, 68, 68, 0.1)' }}
              whileHover={{ scale: 1.1, background: 'rgba(239, 68, 68, 0.2)' }}
              whileTap={{ scale: 0.95 }}
            >
              <svg className="w-3.5 h-3.5 text-red-400" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                <path d="M3 6h18M19 6v14a2 2 0 01-2 2H7a2 2 0 01-2-2V6m3 0V4a2 2 0 012-2h4a2 2 0 012 2v2" />
              </svg>
            </motion.button>
          </div>

          {/* Category Badge */}
          {template.category && (
            <div
              className="inline-flex items-center gap-1 px-2 py-0.5 rounded text-[10px] font-medium mb-2"
              style={{ background: 'rgba(0, 245, 255, 0.1)', color: '#00F5FF' }}
            >
              {template.category}
            </div>
          )}

          <h3
            className="text-base font-semibold mb-2 transition-colors line-clamp-2"
            style={{ color: isHovered ? '#A78BFA' : 'rgba(255,255,255,0.9)' }}
          >
            {template.title}
          </h3>

          <p className="text-sm text-white/40 mb-3 line-clamp-2">{template.summary}</p>

          {/* Sections preview */}
          {contents.length > 0 && (
            <div className="space-y-1.5 mb-4">
              {contents.map((content, i) => (
                <div key={i} className="flex items-center gap-2 text-[11px] text-white/50">
                  <span className="w-1 h-1 rounded-full bg-[#8B5CF6]" />
                  <span className="truncate">{content}</span>
                </div>
              ))}
              {(template.sections?.length || 0) > 3 && (
                <div className="text-[10px] text-white/30 pl-3">
                  +{(template.sections?.length || 0) - 3} 个章节
                </div>
              )}
            </div>
          )}

          {/* Meta info */}
          <div className="flex items-center gap-3 mb-4 text-[11px] text-white/30">
            <span>{new Date(template.created_at).toLocaleDateString('zh-CN')}</span>
            {template.usage_count > 0 && (
              <>
                <span>·</span>
                <span>使用 {template.usage_count} 次</span>
              </>
            )}
          </div>

          <motion.button
            onClick={() => onViewDetail(template)}
            disabled={isPending || isFailed}
            className="w-full py-2 rounded-xl text-sm font-medium transition-all disabled:opacity-50 disabled:cursor-not-allowed"
            style={{
              background: isPending || isFailed ? 'rgba(255,255,255,0.05)' : 'rgba(139, 92, 246, 0.1)',
              border: isPending || isFailed ? '1px solid rgba(255,255,255,0.1)' : '1px solid rgba(139, 92, 246, 0.3)',
              color: isPending || isFailed ? 'rgba(255,255,255,0.3)' : '#A78BFA',
            }}
            whileHover={!isPending && !isFailed ? { background: 'rgba(139, 92, 246, 0.2)', borderColor: 'rgba(139, 92, 246, 0.5)' } : {}}
            whileTap={!isPending && !isFailed ? { scale: 0.98 } : {}}
          >
            {isPending ? '解析中...' : isFailed ? '解析失败' : '模版详情'}
          </motion.button>
        </div>
      </motion.div>
    </motion.div>
  )
}

// ============================================
// PROGRESS BAR COMPONENT
// ============================================
const ProgressBar = ({ progress, status }: { progress: number; status: 'parsing' | 'completed' | 'failed' }) => {
  const getBarColor = () => {
    if (status === 'failed') return 'bg-red-500'
    if (status === 'completed') return 'bg-emerald-500'
    return 'bg-gradient-to-r from-[#00F5FF] to-[#8B5CF6]'
  }

  return (
    <div className="flex items-center gap-3">
      <span className="text-xs text-white/60 whitespace-nowrap min-w-[52px]">
        {status === 'parsing' ? `解析中 ${progress}%` : status === 'completed' ? '已完成' : '解析失败'}
      </span>
      <div className="flex-1 h-1.5 bg-white/5 rounded-full overflow-hidden min-w-[80px]">
        <motion.div
          className={`h-full rounded-full ${getBarColor()}`}
          initial={{ width: 0 }}
          animate={{ width: `${progress}%` }}
          transition={{ duration: 0.8, ease: 'easeOut' }}
        />
      </div>
    </div>
  )
}

// ============================================
// UPLOAD MODAL
// ============================================
interface UploadModalProps {
  isOpen: boolean
  onClose: () => void
  templates: WritingTemplate[]
  uploading: boolean
  onUpload: (file: File) => Promise<void>
  onDeleteTemplate: (id: string) => Promise<void>
  onRefetch: () => Promise<void>
}

const RECORDS_PER_PAGE = 10

const UploadModal = ({ isOpen, onClose, templates, uploading, onUpload, onDeleteTemplate, onRefetch }: UploadModalProps) => {
  const [isDragging, setIsDragging] = useState(false)
  const [pendingFiles, setPendingFiles] = useState<File[]>([])
  const [currentPage, setCurrentPage] = useState(1)
  const fileInputRef = useRef<HTMLInputElement>(null)

  // 按创建时间降序排序，最新的在前面
  const sortedTemplates = [...templates].sort(
    (a, b) => new Date(b.created_at).getTime() - new Date(a.created_at).getTime()
  )

  // 分页计算
  const totalPages = Math.ceil(sortedTemplates.length / RECORDS_PER_PAGE)
  const paginatedTemplates = sortedTemplates.slice(
    (currentPage - 1) * RECORDS_PER_PAGE,
    currentPage * RECORDS_PER_PAGE
  )

  // 当有新模板时，自动刷新数据
  useEffect(() => {
    if (!isOpen) return

    // 检查是否有正在解析的模板
    const hasParsingTemplates = templates.some(t => t.status === 'pending' || t.status === 'parsing')
    if (!hasParsingTemplates) return

    // 每2秒刷新一次数据
    const interval = setInterval(() => {
      onRefetch()
    }, 2000)

    return () => clearInterval(interval)
  }, [isOpen, templates, onRefetch])

  const handleFileSelect = (files: FileList | null) => {
    if (!files) return
    const newFiles = Array.from(files)
    setPendingFiles(prev => [...prev, ...newFiles])
  }

  const handleDrop = (e: React.DragEvent) => {
    e.preventDefault()
    setIsDragging(false)
    handleFileSelect(e.dataTransfer.files)
  }

  const removePendingFile = (index: number) => {
    setPendingFiles(prev => prev.filter((_, i) => i !== index))
  }

  const handleUploadFile = async (file: File, index: number) => {
    try {
      await onUpload(file)
      // Remove from pending after successful upload start
      removePendingFile(index)
    } catch (err) {
      console.error('Upload failed:', err)
    }
  }

  const formatFileSize = (bytes: number) => {
    if (bytes < 1024) return bytes + ' B'
    if (bytes < 1024 * 1024) return (bytes / 1024).toFixed(1) + ' KB'
    return (bytes / (1024 * 1024)).toFixed(1) + ' MB'
  }

  if (!isOpen) return null

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4">
      {/* Backdrop */}
      <motion.div
        initial={{ opacity: 0 }}
        animate={{ opacity: 1 }}
        exit={{ opacity: 0 }}
        className="absolute inset-0 bg-black/80 backdrop-blur-md"
        onClick={onClose}
      />

      {/* Modal */}
      <motion.div
        initial={{ opacity: 0, scale: 0.95, y: 20 }}
        animate={{ opacity: 1, scale: 1, y: 0 }}
        exit={{ opacity: 0, scale: 0.95, y: 20 }}
        transition={{ type: 'spring', damping: 25, stiffness: 300 }}
        className="relative w-full max-w-4xl overflow-hidden rounded-2xl flex flex-col"
        style={{
          background: 'linear-gradient(180deg, rgba(18, 18, 28, 0.98) 0%, rgba(12, 12, 20, 0.99) 100%)',
          border: '1px solid rgba(255,255,255,0.08)',
          boxShadow: '0 25px 50px -12px rgba(0, 0, 0, 0.8), 0 0 0 1px rgba(255,255,255,0.05), inset 0 1px 0 rgba(255,255,255,0.05)',
          maxHeight: '85vh',
        }}
      >
        {/* Header */}
        <div className="flex items-center justify-between px-6 py-4 border-b border-white/5 flex-shrink-0">
          <h2 className="text-lg font-semibold text-white tracking-tight">上传文件</h2>
          <motion.button
            onClick={onClose}
            className="w-8 h-8 rounded-lg flex items-center justify-center text-white/40 hover:text-white hover:bg-white/5 transition-colors"
            whileHover={{ scale: 1.1 }}
            whileTap={{ scale: 0.9 }}
          >
            <svg className="w-5 h-5" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
              <path d="M18 6L6 18M6 6l12 12" />
            </svg>
          </motion.button>
        </div>

        {/* Fixed Upload Section */}
        <div className="px-6 py-5 flex-shrink-0">
          <div className="flex items-center gap-2 mb-4">
            <div className="w-1 h-4 rounded-full bg-gradient-to-b from-[#00F5FF] to-[#8B5CF6]" />
            <span className="text-sm font-medium text-white">上传文档</span>
          </div>

          {/* Drop Zone */}
          <motion.div
            onDragOver={(e) => { e.preventDefault(); setIsDragging(true) }}
            onDragLeave={() => setIsDragging(false)}
            onDrop={handleDrop}
            onClick={() => fileInputRef.current?.click()}
            className="relative rounded-xl cursor-pointer transition-all overflow-hidden"
            animate={{
              borderColor: isDragging ? 'rgba(0, 245, 255, 0.5)' : 'rgba(255,255,255,0.1)',
              background: isDragging ? 'rgba(0, 245, 255, 0.05)' : 'rgba(255,255,255,0.02)',
            }}
            style={{ border: '2px dashed' }}
            whileHover={{ borderColor: 'rgba(0, 245, 255, 0.3)' }}
          >
            <input
              ref={fileInputRef}
              type="file"
              className="hidden"
              accept=".pdf,.doc,.docx,.md,.epub,.mobi,.png,.jpg,.jpeg,.html"
              multiple
              onChange={(e) => handleFileSelect(e.target.files)}
            />

            <div className="py-8 px-6 text-center">
              {/* Upload Icon */}
              <motion.div
                className="w-14 h-14 mx-auto mb-3 rounded-2xl flex items-center justify-center"
                style={{ background: 'linear-gradient(135deg, rgba(0, 245, 255, 0.15) 0%, rgba(139, 92, 246, 0.1) 100%)' }}
                animate={{ y: isDragging ? -5 : 0 }}
              >
                <svg className="w-7 h-7 text-[#00F5FF]" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.5">
                  <path d="M21 15v4a2 2 0 01-2 2H5a2 2 0 01-2-2v-4" />
                  <polyline points="17 8 12 3 7 8" />
                  <line x1="12" y1="3" x2="12" y2="15" />
                </svg>
              </motion.div>

              <p className="text-white/80 font-medium mb-2">点击或将文件拖拽到此处上传</p>

              <div className="space-y-0.5 text-xs text-white/40">
                <p>文档格式：支持PDF（含扫描件）/Word/图片/HTML/Markdown/EPUB/Mobi</p>
                <p>文档大小：文件最大支持100M，图片最大支持20M</p>
                <p>文档页数：PDF/Word最多支持1000页</p>
              </div>
            </div>
          </motion.div>

          {/* Pending Files - waiting to be uploaded */}
          {pendingFiles.length > 0 && (
            <motion.div
              className="mt-3 space-y-2"
              initial={{ opacity: 0, y: 10 }}
              animate={{ opacity: 1, y: 0 }}
            >
              {pendingFiles.map((file, index) => (
                <motion.div
                  key={`${file.name}-${index}`}
                  className="flex items-center justify-between px-4 py-2.5 rounded-xl"
                  style={{ background: 'rgba(255,255,255,0.03)', border: '1px solid rgba(255,255,255,0.05)' }}
                  initial={{ opacity: 0, x: -10 }}
                  animate={{ opacity: 1, x: 0 }}
                  transition={{ delay: index * 0.05 }}
                >
                  <div className="flex items-center gap-3">
                    <div className="w-8 h-8 rounded-lg flex items-center justify-center" style={{ background: 'rgba(0, 245, 255, 0.1)' }}>
                      <svg className="w-4 h-4 text-[#00F5FF]" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                        <path d="M13 2H6a2 2 0 00-2 2v16a2 2 0 002 2h12a2 2 0 002-2V9z" />
                        <polyline points="13 2 13 9 20 9" />
                      </svg>
                    </div>
                    <div>
                      <p className="text-sm text-white/80 truncate max-w-[300px]">{file.name}</p>
                      <p className="text-xs text-white/30">{formatFileSize(file.size)}</p>
                    </div>
                  </div>
                  <div className="flex items-center gap-2">
                    <motion.button
                      onClick={(e) => { e.stopPropagation(); removePendingFile(index) }}
                      className="w-7 h-7 rounded-lg flex items-center justify-center text-white/30 hover:text-red-400 hover:bg-red-500/10 transition-colors"
                      whileHover={{ scale: 1.1 }}
                      whileTap={{ scale: 0.9 }}
                      disabled={uploading}
                    >
                      <svg className="w-4 h-4" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                        <polyline points="3 6 5 6 21 6" />
                        <path d="M19 6v14a2 2 0 01-2 2H7a2 2 0 01-2-2V6m3 0V4a2 2 0 012-2h4a2 2 0 012 2v2" />
                      </svg>
                    </motion.button>
                    <motion.button
                      onClick={() => handleUploadFile(file, index)}
                      disabled={uploading}
                      className="px-3 py-1.5 rounded-lg text-xs font-medium disabled:opacity-50"
                      style={{
                        background: 'rgba(0, 245, 255, 0.1)',
                        color: '#00F5FF',
                        border: '1px solid rgba(0, 245, 255, 0.3)',
                      }}
                      whileHover={!uploading ? { background: 'rgba(0, 245, 255, 0.2)' } : {}}
                      whileTap={!uploading ? { scale: 0.95 } : {}}
                    >
                      {uploading ? '上传中...' : '立即解析'}
                    </motion.button>
                  </div>
                </motion.div>
              ))}
            </motion.div>
          )}
        </div>

        {/* Parse Records Section - Scrollable */}
        <div className="px-6 pb-4 flex-1 min-h-0 flex flex-col">
          <div className="flex items-center justify-between mb-3 flex-shrink-0">
            <div className="flex items-center gap-2">
              <div className="w-1 h-4 rounded-full bg-gradient-to-b from-[#00F5FF] to-[#8B5CF6]" />
              <span className="text-sm font-medium text-white">解析记录</span>
            </div>
            <motion.button
              className="flex items-center gap-1 text-xs text-white/50 hover:text-[#00F5FF] transition-colors"
              whileHover={{ x: 3 }}
            >
              查看更多
              <svg className="w-3.5 h-3.5" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                <polyline points="9 18 15 12 9 6" />
              </svg>
            </motion.button>
          </div>

          {/* Table with internal scroll */}
          <div
            className="rounded-xl overflow-hidden flex-1 min-h-0 flex flex-col"
            style={{ background: 'rgba(255,255,255,0.02)', border: '1px solid rgba(255,255,255,0.05)' }}
          >
            {/* Table Header - Fixed */}
            <div
              className="grid grid-cols-[1.5fr_1.2fr_0.8fr_1fr_0.6fr] gap-4 px-4 py-3 text-xs text-white/40 font-medium border-b border-white/5 flex-shrink-0"
              style={{ background: 'rgba(255,255,255,0.02)' }}
            >
              <span>文件名称</span>
              <span>解析进度</span>
              <span>分类</span>
              <span>创建时间</span>
              <span className="text-center">操作</span>
            </div>

            {/* Table Body - Scrollable */}
            <div className="flex-1 overflow-y-auto custom-scrollbar divide-y divide-white/5">
              {sortedTemplates.length === 0 ? (
                <div className="py-8 text-center text-white/30 text-sm">
                  暂无解析记录
                </div>
              ) : (
                paginatedTemplates.map((template, index) => {
                  const isParsing = template.status === 'pending' || template.status === 'parsing'
                  const isFailed = template.status === 'failed'
                  const isCompleted = template.status === 'completed'
                  // 模拟进度：pending=10%, parsing=50%, completed=100%, failed=0%
                  const progress = isCompleted ? 100 : isFailed ? 0 : isParsing ? 50 : 10

                  return (
                    <motion.div
                      key={template.id}
                      className="grid grid-cols-[1.5fr_1.2fr_0.8fr_1fr_0.6fr] gap-4 px-4 py-3 items-center hover:bg-white/[0.02] transition-colors"
                      initial={{ opacity: 0, y: 10 }}
                      animate={{ opacity: 1, y: 0 }}
                      transition={{ delay: index * 0.03 }}
                    >
                      {/* File Name */}
                      <div className="flex items-center gap-2 min-w-0">
                        <div
                          className="w-7 h-7 rounded-lg flex items-center justify-center flex-shrink-0"
                          style={{
                            background: isCompleted
                              ? 'rgba(16, 185, 129, 0.1)'
                              : isFailed
                                ? 'rgba(239, 68, 68, 0.1)'
                                : 'rgba(0, 245, 255, 0.1)',
                          }}
                        >
                          <svg
                            className="w-3.5 h-3.5"
                            style={{
                              color: isCompleted
                                ? '#10B981'
                                : isFailed
                                  ? '#EF4444'
                                  : '#00F5FF',
                            }}
                            viewBox="0 0 24 24"
                            fill="none"
                            stroke="currentColor"
                            strokeWidth="2"
                          >
                            <path d="M13 2H6a2 2 0 00-2 2v16a2 2 0 002 2h12a2 2 0 002-2V9z" />
                            <polyline points="13 2 13 9 20 9" />
                          </svg>
                        </div>
                        <div className="min-w-0">
                          <span className="text-sm text-white/70 truncate block">
                            {template.original_filename || template.title}
                          </span>
                          {template.title && isCompleted && template.original_filename && (
                            <span className="text-xs text-white/40 truncate block">{template.title}</span>
                          )}
                          {template.error_message && isFailed && (
                            <span className="text-xs text-red-400 truncate block">{template.error_message}</span>
                          )}
                        </div>
                      </div>

                      {/* Progress */}
                      <ProgressBar
                        progress={progress}
                        status={isParsing ? 'parsing' : isCompleted ? 'completed' : 'failed'}
                      />

                      {/* Category */}
                      <span className="text-xs text-white/50">{template.category || '-'}</span>

                      {/* Created At */}
                      <span className="text-xs text-white/40">
                        {new Date(template.created_at).toLocaleString('zh-CN', {
                          month: '2-digit',
                          day: '2-digit',
                          hour: '2-digit',
                          minute: '2-digit',
                        })}
                      </span>

                      {/* Actions */}
                      <div className="flex justify-center">
                        <motion.button
                          onClick={() => onDeleteTemplate(template.id)}
                          className="text-xs text-red-400 hover:text-red-300 transition-colors"
                          whileHover={{ scale: 1.05 }}
                          whileTap={{ scale: 0.95 }}
                        >
                          删除
                        </motion.button>
                      </div>
                    </motion.div>
                  )
                })
              )}
            </div>

            {/* Pagination */}
            {totalPages > 1 && (
              <div className="flex items-center justify-between px-4 py-3 border-t border-white/5 flex-shrink-0">
                <span className="text-xs text-white/40">
                  共 {sortedTemplates.length} 条记录，第 {currentPage}/{totalPages} 页
                </span>
                <div className="flex items-center gap-2">
                  <motion.button
                    onClick={() => setCurrentPage(p => Math.max(1, p - 1))}
                    disabled={currentPage === 1}
                    className="px-3 py-1.5 rounded-lg text-xs font-medium disabled:opacity-30 disabled:cursor-not-allowed"
                    style={{ background: 'rgba(255,255,255,0.05)', color: 'rgba(255,255,255,0.7)' }}
                    whileHover={currentPage !== 1 ? { background: 'rgba(255,255,255,0.1)' } : {}}
                    whileTap={currentPage !== 1 ? { scale: 0.95 } : {}}
                  >
                    上一页
                  </motion.button>
                  <motion.button
                    onClick={() => setCurrentPage(p => Math.min(totalPages, p + 1))}
                    disabled={currentPage === totalPages}
                    className="px-3 py-1.5 rounded-lg text-xs font-medium disabled:opacity-30 disabled:cursor-not-allowed"
                    style={{ background: 'rgba(255,255,255,0.05)', color: 'rgba(255,255,255,0.7)' }}
                    whileHover={currentPage !== totalPages ? { background: 'rgba(255,255,255,0.1)' } : {}}
                    whileTap={currentPage !== totalPages ? { scale: 0.95 } : {}}
                  >
                    下一页
                  </motion.button>
                </div>
              </div>
            )}
          </div>
        </div>

        {/* Footer */}
        <div
          className="flex justify-center gap-4 px-6 py-4 border-t border-white/5"
          style={{ background: 'rgba(0,0,0,0.2)' }}
        >
          <motion.button
            onClick={onClose}
            className="px-8 py-2.5 rounded-full text-sm font-medium text-white/60 hover:text-white transition-colors"
            style={{ border: '1px solid rgba(255,255,255,0.1)' }}
            whileHover={{ borderColor: 'rgba(255,255,255,0.2)', background: 'rgba(255,255,255,0.03)' }}
            whileTap={{ scale: 0.98 }}
          >
            取消
          </motion.button>
          <motion.button
            className="px-8 py-2.5 rounded-full text-sm font-medium"
            style={{
              background: 'linear-gradient(135deg, #00F5FF 0%, #8B5CF6 100%)',
              color: '#0a0a0f',
              boxShadow: '0 4px 15px rgba(0, 245, 255, 0.3)',
            }}
            whileHover={{ scale: 1.02, boxShadow: '0 6px 20px rgba(0, 245, 255, 0.4)' }}
            whileTap={{ scale: 0.98 }}
          >
            确定
          </motion.button>
        </div>
      </motion.div>

      {/* Custom Scrollbar Styles */}
      <style jsx global>{`
        .custom-scrollbar::-webkit-scrollbar {
          width: 6px;
        }
        .custom-scrollbar::-webkit-scrollbar-track {
          background: rgba(255, 255, 255, 0.02);
        }
        .custom-scrollbar::-webkit-scrollbar-thumb {
          background: rgba(255, 255, 255, 0.1);
          border-radius: 3px;
        }
        .custom-scrollbar::-webkit-scrollbar-thumb:hover {
          background: rgba(255, 255, 255, 0.15);
        }
      `}</style>
    </div>
  )
}

// ============================================
// MAIN PAGE
// ============================================
export default function CenterPage() {
  const router = useRouter()
  const user = useAuthStore((state) => state.user)
  const { reports, loading: reportsLoading, deleteReport } = useReports()
  const { templates, loading: templatesLoading, deleteTemplate, refetch: refetchTemplates } = useTemplates()
  const { parseRecords, uploading, uploadFile, removeRecord } = useTemplateUpload()

  const [activeTab, setActiveTab] = useState<'documents' | 'templates'>('documents')
  const [searchQuery, setSearchQuery] = useState('')
  const [selectedCategory, setSelectedCategory] = useState<string | null>(null)
  const [selectedTemplateCategory, setSelectedTemplateCategory] = useState('all')
  const [showUploadModal, setShowUploadModal] = useState(false)
  const [searchFocused, setSearchFocused] = useState(false)
  const [sidebarCollapsed, setSidebarCollapsed] = useState(false)
  const [selectedTemplate, setSelectedTemplate] = useState<WritingTemplate | null>(null)
  const [showTemplateDetail, setShowTemplateDetail] = useState(false)

  // Refetch templates when parse records change (new upload completed)
  useEffect(() => {
    const hasCompleted = parseRecords.some(r => r.status === 'completed')
    if (hasCompleted) {
      refetchTemplates()
    }
  }, [parseRecords, refetchTemplates])

  // Extract unique categories from reports
  const categories = useMemo(() => {
    const cats = new Set<string>()
    reports.forEach(report => {
      if (report.category) cats.add(report.category)
    })
    return Array.from(cats)
  }, [reports])

  // Extract unique categories from templates
  const templateCategories = useMemo(() => {
    const cats = new Set<string>()
    templates.forEach(template => {
      if (template.category) cats.add(template.category)
    })
    return Array.from(cats)
  }, [templates])

  // Filter reports
  const filteredReports = useMemo(() => {
    return reports.filter(report => {
      // Search filter
      const matchesSearch = !searchQuery ||
        report.title?.toLowerCase().includes(searchQuery.toLowerCase()) ||
        report.description?.toLowerCase().includes(searchQuery.toLowerCase())

      // Category filter
      const matchesCategory = !selectedCategory || report.category === selectedCategory

      return matchesSearch && matchesCategory
    })
  }, [reports, searchQuery, selectedCategory])

  // Filter templates
  const filteredTemplates = useMemo(() => {
    return templates.filter(template => {
      const matchesSearch = !searchQuery ||
        template.title.toLowerCase().includes(searchQuery.toLowerCase()) ||
        template.summary?.toLowerCase().includes(searchQuery.toLowerCase())
      const matchesCategory = selectedTemplateCategory === 'all' || template.category === selectedTemplateCategory
      return matchesSearch && matchesCategory
    })
  }, [templates, searchQuery, selectedTemplateCategory])

  const handleViewReport = (id: string) => router.push(`/reports/${id}`)
  const handleDeleteReport = async (id: string) => {
    if (confirm('确定要删除这份文档吗？')) {
      await deleteReport(id)
    }
  }
  const handleViewTemplateDetail = (template: WritingTemplate) => {
    setSelectedTemplate(template)
    setShowTemplateDetail(true)
  }
  const handleUseTemplate = (id: string) => {
    // Navigate to chat with template pre-selected
    setShowTemplateDetail(false)
    router.push(`/chat?template=${id}`)
  }
  const handleDeleteTemplate = async (id: string) => {
    if (confirm('确定要删除这个模板吗？')) {
      await deleteTemplate(id)
    }
  }
  const handleUploadFile = async (file: File) => {
    await uploadFile(file)
  }

  const hasActiveFilters = selectedCategory || searchQuery

  return (
    <div className="min-h-screen relative overflow-hidden">
      <NeuralBackground />

      <AnimatePresence>
        {showUploadModal && (
          <UploadModal
            isOpen={showUploadModal}
            onClose={() => setShowUploadModal(false)}
            templates={templates}
            uploading={uploading}
            onUpload={handleUploadFile}
            onDeleteTemplate={handleDeleteTemplate}
            onRefetch={refetchTemplates}
          />
        )}
      </AnimatePresence>

      <AnimatePresence>
        {showTemplateDetail && (
          <TemplateDetailModal
            isOpen={showTemplateDetail}
            template={selectedTemplate}
            onClose={() => setShowTemplateDetail(false)}
            onUseTemplate={handleUseTemplate}
          />
        )}
      </AnimatePresence>

      {/* Sidebar */}
      <motion.aside
        className="fixed left-0 top-0 bottom-0 z-40 flex flex-col"
        style={{
          background: 'linear-gradient(180deg, rgba(15, 15, 25, 0.95) 0%, rgba(10, 10, 18, 0.98) 100%)',
          backdropFilter: 'blur(20px)',
          borderRight: '1px solid rgba(255,255,255,0.05)',
        }}
        initial={false}
        animate={{ width: sidebarCollapsed ? 72 : 240 }}
        transition={{ duration: 0.3, ease: [0.4, 0, 0.2, 1] }}
      >
        {/* Logo */}
        <div className={`p-4 ${sidebarCollapsed ? 'flex justify-center' : 'px-6'}`}>
          <Link href="/" className="flex items-center gap-3">
            <motion.div onClick={(e) => { if (sidebarCollapsed) { e.preventDefault(); setSidebarCollapsed(false); } }}>
              <NexusLogo size={sidebarCollapsed ? 40 : 42} />
            </motion.div>
            {!sidebarCollapsed && (
              <motion.div initial={{ opacity: 0, x: -10 }} animate={{ opacity: 1, x: 0 }}>
                <span
                  className="text-xl font-bold tracking-tight block"
                  style={{
                    fontFamily: '"Orbitron", sans-serif',
                    background: 'linear-gradient(135deg, #00F5FF 0%, #8B5CF6 100%)',
                    WebkitBackgroundClip: 'text',
                    WebkitTextFillColor: 'transparent',
                  }}
                >
                  NEXUS
                </span>
                <span className="text-[10px] text-white/30 tracking-[0.3em] uppercase">AI Platform</span>
              </motion.div>
            )}
          </Link>
        </div>

        {/* Collapse Toggle */}
        <motion.div
          className="absolute right-0 top-1/2 -translate-y-1/2 z-50 group cursor-pointer"
          onClick={() => setSidebarCollapsed(!sidebarCollapsed)}
        >
          <div className="py-8 px-1">
            <motion.div className="w-1 h-10 rounded-full bg-white/10 group-hover:bg-gradient-to-b group-hover:from-[#00F5FF] group-hover:to-[#8B5CF6] transition-all" whileHover={{ scale: 1.1 }} />
          </div>
        </motion.div>

        {/* Navigation - Only Document Center */}
        <nav className={`flex-1 ${sidebarCollapsed ? 'px-2' : 'px-3'} py-4`}>
          {sidebarCollapsed ? (
            <div className="flex flex-col items-center">
              <motion.div
                className="relative w-12 h-12 rounded-xl flex items-center justify-center cursor-pointer"
                style={{ background: 'rgba(0, 245, 255, 0.1)' }}
                whileHover={{ scale: 1.05 }}
                title="创作中心"
              >
                <div
                  className="absolute left-0 top-1/2 -translate-y-1/2 w-1 h-6 rounded-r-full"
                  style={{ background: 'linear-gradient(180deg, #00F5FF 0%, #8B5CF6 100%)' }}
                />
                <svg className="w-5 h-5 text-[#00F5FF]" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                  <path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z" />
                  <polyline points="14 2 14 8 20 8" />
                  <line x1="16" y1="13" x2="8" y2="13" />
                  <line x1="16" y1="17" x2="8" y2="17" />
                </svg>
              </motion.div>
            </div>
          ) : (
            <motion.div
              className="flex items-center gap-3 px-4 py-3 rounded-xl relative text-[#00F5FF]"
              style={{ background: 'rgba(0, 245, 255, 0.08)' }}
            >
              <div
                className="absolute left-0 top-1/2 -translate-y-1/2 w-1 h-6 rounded-r-full"
                style={{ background: 'linear-gradient(180deg, #00F5FF 0%, #8B5CF6 100%)' }}
              />
              <svg className="w-5 h-5" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                <path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z" />
                <polyline points="14 2 14 8 20 8" />
                <line x1="16" y1="13" x2="8" y2="13" />
                <line x1="16" y1="17" x2="8" y2="17" />
              </svg>
              <span className="text-sm font-medium">创作中心</span>
            </motion.div>
          )}
        </nav>

        {/* User */}
        <div className={`p-3 ${sidebarCollapsed ? 'flex justify-center' : ''}`}>
          <motion.div className={`flex items-center gap-3 rounded-xl hover:bg-white/5 cursor-pointer ${sidebarCollapsed ? 'w-12 h-12 justify-center' : 'px-3 py-2'}`}>
            <div
              className="w-9 h-9 rounded-full flex items-center justify-center text-sm font-semibold flex-shrink-0"
              style={{ background: 'linear-gradient(135deg, #00F5FF 0%, #8B5CF6 100%)', color: '#0a0a0f' }}
            >
              {user?.name?.charAt(0).toUpperCase() || 'U'}
            </div>
            {!sidebarCollapsed && (
              <div className="flex-1 min-w-0">
                <p className="text-sm text-white/80 truncate">{user?.name || 'User'}</p>
                <p className="text-xs text-white/30">在线</p>
              </div>
            )}
          </motion.div>
        </div>
      </motion.aside>

      {/* Main Content */}
      <motion.main
        className="min-h-screen relative z-10"
        initial={false}
        animate={{ marginLeft: sidebarCollapsed ? 72 : 240 }}
        transition={{ duration: 0.3, ease: [0.4, 0, 0.2, 1] }}
      >
        {/* Header */}
        <motion.header
          className="sticky top-0 z-30 px-8 py-5"
          style={{
            background: 'rgba(10, 10, 15, 0.6)',
            backdropFilter: 'blur(20px)',
            borderBottom: '1px solid rgba(255,255,255,0.03)',
          }}
          initial={{ opacity: 0, y: -20 }}
          animate={{ opacity: 1, y: 0 }}
        >
          <div className="flex items-center justify-between">
            <motion.div
              className="relative w-[360px]"
              animate={{ boxShadow: searchFocused ? '0 0 0 2px rgba(0, 245, 255, 0.2)' : 'none' }}
              style={{ borderRadius: '14px' }}
            >
              <svg className="absolute left-4 top-1/2 -translate-y-1/2 w-5 h-5 text-white/30" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                <circle cx="11" cy="11" r="8" />
                <path d="m21 21-4.3-4.3" />
              </svg>
              <input
                type="text"
                value={searchQuery}
                onChange={(e) => setSearchQuery(e.target.value)}
                onFocus={() => setSearchFocused(true)}
                onBlur={() => setSearchFocused(false)}
                placeholder="搜索文档或模板..."
                className="w-full pl-12 pr-4 py-3 rounded-xl text-sm text-white placeholder:text-white/30 outline-none"
                style={{ background: 'rgba(255,255,255,0.03)', border: '1px solid rgba(255,255,255,0.08)' }}
              />
            </motion.div>

            <motion.button
              onClick={() => setShowUploadModal(true)}
              className="flex items-center gap-2 px-5 py-3 rounded-xl text-sm font-medium"
              style={{
                background: 'linear-gradient(135deg, #00F5FF 0%, #8B5CF6 100%)',
                color: '#0a0a0f',
                boxShadow: '0 4px 20px rgba(0, 245, 255, 0.25)',
              }}
              whileHover={{ scale: 1.02 }}
              whileTap={{ scale: 0.98 }}
            >
              <svg className="w-4 h-4" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5">
                <path d="M21 15v4a2 2 0 01-2 2H5a2 2 0 01-2-2v-4" />
                <polyline points="17 8 12 3 7 8" />
                <line x1="12" y1="3" x2="12" y2="15" />
              </svg>
              上传模板
            </motion.button>
          </div>
        </motion.header>

        {/* Content */}
        <div className="px-8 py-6">
          {/* Tabs */}
          <div className="flex items-center gap-2 mb-6">
            {[
              { id: 'documents', label: '我的文档', count: reports.length },
              { id: 'templates', label: '写作模板', count: templates.length },
            ].map((tab) => (
              <motion.button
                key={tab.id}
                onClick={() => setActiveTab(tab.id as 'documents' | 'templates')}
                className="relative px-6 py-3 rounded-xl text-sm font-medium transition-all"
                style={{
                  color: activeTab === tab.id ? '#00F5FF' : 'rgba(255,255,255,0.5)',
                  background: activeTab === tab.id ? 'rgba(0, 245, 255, 0.08)' : 'transparent',
                  border: activeTab === tab.id ? '1px solid rgba(0, 245, 255, 0.2)' : '1px solid transparent',
                }}
                whileHover={{ background: 'rgba(0, 245, 255, 0.05)' }}
              >
                {tab.label}
                <span className="ml-2 px-2 py-0.5 rounded-full text-xs" style={{ background: activeTab === tab.id ? 'rgba(0, 245, 255, 0.15)' : 'rgba(255,255,255,0.05)' }}>
                  {tab.count}
                </span>
              </motion.button>
            ))}
          </div>

          {/* Category Filter Bar for Documents - 像截图那样的按钮行 */}
          {activeTab === 'documents' && categories.length > 0 && (
            <motion.div
              className="flex items-center gap-2 mb-6 flex-wrap"
              initial={{ opacity: 0, y: 10 }}
              animate={{ opacity: 1, y: 0 }}
            >
              {/* 全部按钮 */}
              <motion.button
                onClick={() => setSelectedCategory(null)}
                className="px-5 py-2.5 rounded-lg text-sm font-medium transition-all flex items-center gap-2"
                style={{
                  background: !selectedCategory
                    ? 'linear-gradient(135deg, rgba(139, 92, 246, 0.2) 0%, rgba(139, 92, 246, 0.1) 100%)'
                    : 'rgba(255,255,255,0.03)',
                  color: !selectedCategory ? '#A78BFA' : 'rgba(255,255,255,0.5)',
                  border: !selectedCategory
                    ? '1px solid rgba(139, 92, 246, 0.4)'
                    : '1px solid rgba(255,255,255,0.08)',
                }}
                whileHover={{ scale: 1.02, background: !selectedCategory ? undefined : 'rgba(255,255,255,0.05)' }}
                whileTap={{ scale: 0.98 }}
              >
                <span style={{ color: !selectedCategory ? '#A78BFA' : 'rgba(255,255,255,0.4)' }}>◈</span>
                全部
              </motion.button>

              {/* 各分类按钮 */}
              {categories.map((cat, index) => {
                const icons = ['◇', '◆', '▣', '◎', '◉', '◈', '◇', '◆']
                const icon = icons[index % icons.length]
                const isActive = selectedCategory === cat

                return (
                  <motion.button
                    key={cat}
                    onClick={() => setSelectedCategory(isActive ? null : cat)}
                    className="px-5 py-2.5 rounded-lg text-sm font-medium transition-all flex items-center gap-2"
                    style={{
                      background: isActive
                        ? 'linear-gradient(135deg, rgba(139, 92, 246, 0.2) 0%, rgba(139, 92, 246, 0.1) 100%)'
                        : 'rgba(255,255,255,0.03)',
                      color: isActive ? '#A78BFA' : 'rgba(255,255,255,0.5)',
                      border: isActive
                        ? '1px solid rgba(139, 92, 246, 0.4)'
                        : '1px solid rgba(255,255,255,0.08)',
                    }}
                    whileHover={{ scale: 1.02, background: isActive ? undefined : 'rgba(255,255,255,0.05)' }}
                    whileTap={{ scale: 0.98 }}
                  >
                    <span style={{ color: isActive ? '#A78BFA' : 'rgba(255,255,255,0.4)' }}>{icon}</span>
                    {cat}
                  </motion.button>
                )
              })}
            </motion.div>
          )}

          {/* Template Category Filter */}
          {activeTab === 'templates' && (
            <motion.div className="flex items-center gap-2 mb-6 flex-wrap" initial={{ opacity: 0, y: 10 }} animate={{ opacity: 1, y: 0 }}>
              {/* 全部按钮 */}
              <motion.button
                onClick={() => setSelectedTemplateCategory('all')}
                className="px-4 py-2 rounded-lg text-sm transition-all flex items-center gap-1.5"
                style={{
                  background: selectedTemplateCategory === 'all' ? 'rgba(139, 92, 246, 0.15)' : 'rgba(255,255,255,0.03)',
                  color: selectedTemplateCategory === 'all' ? '#A78BFA' : 'rgba(255,255,255,0.4)',
                  border: selectedTemplateCategory === 'all' ? '1px solid rgba(139, 92, 246, 0.3)' : '1px solid rgba(255,255,255,0.05)',
                }}
                whileHover={{ background: 'rgba(139, 92, 246, 0.1)' }}
              >
                <span>◈</span>
                全部
              </motion.button>

              {/* 各分类按钮 */}
              {templateCategories.map((cat, index) => {
                const icons = ['◇', '◆', '▣', '◎', '◉', '◈', '◇', '◆']
                const icon = icons[index % icons.length]
                const isActive = selectedTemplateCategory === cat

                return (
                  <motion.button
                    key={cat}
                    onClick={() => setSelectedTemplateCategory(isActive ? 'all' : cat)}
                    className="px-4 py-2 rounded-lg text-sm transition-all flex items-center gap-1.5"
                    style={{
                      background: isActive ? 'rgba(139, 92, 246, 0.15)' : 'rgba(255,255,255,0.03)',
                      color: isActive ? '#A78BFA' : 'rgba(255,255,255,0.4)',
                      border: isActive ? '1px solid rgba(139, 92, 246, 0.3)' : '1px solid rgba(255,255,255,0.05)',
                    }}
                    whileHover={{ background: 'rgba(139, 92, 246, 0.1)' }}
                  >
                    <span>{icon}</span>
                    {cat}
                  </motion.button>
                )
              })}
            </motion.div>
          )}
        </div>

        {/* Grid */}
        <div className="px-8 pb-8">
          <AnimatePresence mode="wait">
            {activeTab === 'documents' ? (
              reportsLoading ? (
                <motion.div key="loading" className="flex items-center justify-center py-20" initial={{ opacity: 0 }} animate={{ opacity: 1 }} exit={{ opacity: 0 }}>
                  <motion.div
                    className="w-12 h-12 rounded-full"
                    style={{ border: '2px solid transparent', borderTopColor: '#00F5FF', borderRightColor: '#8B5CF6' }}
                    animate={{ rotate: 360 }}
                    transition={{ duration: 1, repeat: Infinity, ease: 'linear' }}
                  />
                </motion.div>
              ) : filteredReports.length === 0 ? (
                <motion.div key="empty" className="text-center py-20" initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} exit={{ opacity: 0 }}>
                  <motion.div
                    className="w-20 h-20 mx-auto mb-6 rounded-2xl flex items-center justify-center"
                    style={{ background: 'rgba(255,255,255,0.03)' }}
                    animate={{ y: [0, -8, 0] }}
                    transition={{ duration: 3, repeat: Infinity }}
                  >
                    <svg className="w-10 h-10 text-white/20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.5">
                      <path d="M9 12h6M9 16h6M17 21H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
                    </svg>
                  </motion.div>
                  <p className="text-white/50 mb-2">{hasActiveFilters ? '没有匹配的文档' : '暂无文档'}</p>
                  <p className="text-sm text-white/25">{hasActiveFilters ? '尝试调整筛选条件' : '在智能对话中创建您的第一份文档'}</p>
                </motion.div>
              ) : (
                <motion.div key="documents" className="grid grid-cols-1 md:grid-cols-2 xl:grid-cols-3 gap-5" initial={{ opacity: 0 }} animate={{ opacity: 1 }} exit={{ opacity: 0 }}>
                  {filteredReports.map((report, index) => (
                    <DocumentCard key={report.id} report={report} index={index} onView={handleViewReport} onDelete={handleDeleteReport} />
                  ))}
                </motion.div>
              )
            ) : templatesLoading ? (
              <motion.div key="templates-loading" className="flex items-center justify-center py-20" initial={{ opacity: 0 }} animate={{ opacity: 1 }} exit={{ opacity: 0 }}>
                <motion.div
                  className="w-12 h-12 rounded-full"
                  style={{ border: '2px solid transparent', borderTopColor: '#8B5CF6', borderRightColor: '#00F5FF' }}
                  animate={{ rotate: 360 }}
                  transition={{ duration: 1, repeat: Infinity, ease: 'linear' }}
                />
              </motion.div>
            ) : filteredTemplates.length === 0 ? (
              <motion.div key="templates-empty" className="text-center py-20" initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} exit={{ opacity: 0 }}>
                <motion.div
                  className="w-20 h-20 mx-auto mb-6 rounded-2xl flex items-center justify-center"
                  style={{ background: 'rgba(139, 92, 246, 0.05)' }}
                  animate={{ y: [0, -8, 0] }}
                  transition={{ duration: 3, repeat: Infinity }}
                >
                  <svg className="w-10 h-10 text-[#8B5CF6]/30" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.5">
                    <path d="M9 12h6M9 16h6M17 21H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
                  </svg>
                </motion.div>
                <p className="text-white/50 mb-2">{searchQuery || selectedTemplateCategory !== 'all' ? '没有匹配的模板' : '暂无模板'}</p>
                <p className="text-sm text-white/25">{searchQuery || selectedTemplateCategory !== 'all' ? '尝试调整筛选条件' : '点击"上传模板"按钮上传您的第一个模板'}</p>
              </motion.div>
            ) : (
              <motion.div key="templates" className="grid grid-cols-1 md:grid-cols-2 xl:grid-cols-3 gap-5" initial={{ opacity: 0 }} animate={{ opacity: 1 }} exit={{ opacity: 0 }}>
                {filteredTemplates.map((template, index) => (
                  <TemplateCard key={template.id} template={template} index={index} onViewDetail={handleViewTemplateDetail} onDelete={handleDeleteTemplate} />
                ))}
              </motion.div>
            )}
          </AnimatePresence>
        </div>
      </motion.main>
    </div>
  )
}
