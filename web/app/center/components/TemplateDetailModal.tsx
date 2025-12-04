'use client'

import { motion, AnimatePresence } from 'framer-motion'
import { WritingTemplate } from '../../chat/hooks/useTemplates'

// ============================================
// TEMPLATE DETAIL MODAL
// 模版详情预览弹窗 - 深空科技风格
// ============================================

interface TemplateDetailModalProps {
  isOpen: boolean
  template: WritingTemplate | null
  onClose: () => void
  onUseTemplate: (id: string) => void
}

// 写作风格映射
const WRITING_STYLE_MAP: Record<string, { label: string; color: string }> = {
  academic: { label: '学术研究', color: '#00F5FF' },
  business: { label: '商务报告', color: '#8B5CF6' },
  technical: { label: '技术文档', color: '#10B981' },
  creative: { label: '创意写作', color: '#F59E0B' },
  journalistic: { label: '新闻报道', color: '#EC4899' },
}

// 写作语气映射
const WRITING_TONE_MAP: Record<string, { label: string; icon: string }> = {
  formal: { label: '正式', icon: '◆' },
  neutral: { label: '中性', icon: '◇' },
  casual: { label: '轻松', icon: '○' },
  professional: { label: '专业', icon: '◈' },
  persuasive: { label: '说服性', icon: '◉' },
}

// 章节卡片组件
const SectionCard = ({
  section,
  index,
  total
}: {
  section: { title: string; description?: string; key_points?: string[]; estimated_percentage?: number }
  index: number
  total: number
}) => {
  const progress = section.estimated_percentage || Math.round(100 / total)

  return (
    <motion.div
      initial={{ opacity: 0, x: -20 }}
      animate={{ opacity: 1, x: 0 }}
      transition={{ delay: 0.1 + index * 0.05, duration: 0.4 }}
      className="group relative"
    >
      {/* 连接线 */}
      {index < total - 1 && (
        <div
          className="absolute left-[18px] top-[44px] w-[2px] h-[calc(100%-20px)]"
          style={{
            background: 'linear-gradient(180deg, rgba(139, 92, 246, 0.4) 0%, rgba(139, 92, 246, 0.1) 100%)'
          }}
        />
      )}

      <div className="flex gap-4">
        {/* 序号节点 */}
        <div className="flex-shrink-0 relative">
          <motion.div
            className="w-9 h-9 rounded-xl flex items-center justify-center text-sm font-bold relative z-10"
            style={{
              background: 'linear-gradient(135deg, rgba(139, 92, 246, 0.2) 0%, rgba(0, 245, 255, 0.1) 100%)',
              border: '1px solid rgba(139, 92, 246, 0.3)',
              color: '#A78BFA',
            }}
            whileHover={{
              scale: 1.1,
              boxShadow: '0 0 20px rgba(139, 92, 246, 0.4)'
            }}
          >
            {String(index + 1).padStart(2, '0')}
          </motion.div>
        </div>

        {/* 内容区 */}
        <div className="flex-1 pb-6">
          <div className="flex items-start justify-between gap-4 mb-2">
            <h4
              className="text-base font-semibold text-white/90 group-hover:text-[#A78BFA] transition-colors"
            >
              {section.title}
            </h4>
            <div
              className="flex-shrink-0 px-2 py-0.5 rounded text-[10px] font-medium"
              style={{
                background: 'rgba(0, 245, 255, 0.1)',
                color: '#00F5FF',
              }}
            >
              {progress}%
            </div>
          </div>

          {section.description && (
            <p className="text-sm text-white/50 mb-3 leading-relaxed">
              {section.description}
            </p>
          )}

          {section.key_points && section.key_points.length > 0 && (
            <div className="space-y-1.5">
              {section.key_points.map((point, i) => (
                <div
                  key={i}
                  className="flex items-start gap-2 text-[13px] text-white/40"
                >
                  <span
                    className="w-1 h-1 rounded-full mt-2 flex-shrink-0"
                    style={{ background: 'linear-gradient(135deg, #00F5FF, #8B5CF6)' }}
                  />
                  <span>{point}</span>
                </div>
              ))}
            </div>
          )}
        </div>
      </div>
    </motion.div>
  )
}

// 信息标签组件
const InfoTag = ({
  label,
  value,
  color = '#00F5FF',
  icon
}: {
  label: string
  value: string
  color?: string
  icon?: string
}) => (
  <div
    className="px-4 py-3 rounded-xl"
    style={{
      background: 'rgba(255, 255, 255, 0.02)',
      border: '1px solid rgba(255, 255, 255, 0.05)',
    }}
  >
    <div className="text-[10px] text-white/30 uppercase tracking-wider mb-1">
      {label}
    </div>
    <div className="flex items-center gap-2">
      {icon && <span style={{ color }}>{icon}</span>}
      <span className="text-sm font-medium" style={{ color }}>
        {value}
      </span>
    </div>
  </div>
)

// 统计数字组件
const StatNumber = ({
  value,
  label,
  suffix = ''
}: {
  value: number | string
  label: string
  suffix?: string
}) => (
  <div className="text-center">
    <div
      className="text-2xl font-bold mb-1"
      style={{
        background: 'linear-gradient(135deg, #00F5FF 0%, #8B5CF6 100%)',
        WebkitBackgroundClip: 'text',
        WebkitTextFillColor: 'transparent',
      }}
    >
      {value}{suffix}
    </div>
    <div className="text-[11px] text-white/30 uppercase tracking-wider">
      {label}
    </div>
  </div>
)

export default function TemplateDetailModal({
  isOpen,
  template,
  onClose,
  onUseTemplate
}: TemplateDetailModalProps) {
  if (!isOpen || !template) return null

  const styleInfo = WRITING_STYLE_MAP[template.writing_style] || { label: template.writing_style, color: '#8B5CF6' }
  const toneInfo = WRITING_TONE_MAP[template.writing_tone] || { label: template.writing_tone, icon: '◇' }
  const sections = template.sections || []
  const contentLength = template.markdown_content?.length || 0
  const estimatedWords = Math.round(contentLength / 2)

  return (
    <AnimatePresence>
      <div className="fixed inset-0 z-50 flex items-center justify-center p-4">
        {/* Backdrop with blur */}
        <motion.div
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          exit={{ opacity: 0 }}
          className="absolute inset-0 bg-black/85 backdrop-blur-xl"
          onClick={onClose}
        />

        {/* Modal Container */}
        <motion.div
          initial={{ opacity: 0, scale: 0.92, y: 30 }}
          animate={{ opacity: 1, scale: 1, y: 0 }}
          exit={{ opacity: 0, scale: 0.92, y: 30 }}
          transition={{ type: 'spring', damping: 28, stiffness: 350 }}
          className="relative w-full max-w-5xl max-h-[90vh] overflow-hidden rounded-3xl flex"
          style={{
            background: 'linear-gradient(180deg, rgba(15, 15, 25, 0.98) 0%, rgba(8, 8, 16, 0.99) 100%)',
            border: '1px solid rgba(255, 255, 255, 0.06)',
            boxShadow: `
              0 50px 100px -20px rgba(0, 0, 0, 0.9),
              0 0 0 1px rgba(255, 255, 255, 0.03),
              inset 0 1px 0 rgba(255, 255, 255, 0.04),
              0 0 120px rgba(139, 92, 246, 0.1),
              0 0 80px rgba(0, 245, 255, 0.05)
            `,
          }}
        >
          {/* 背景装饰 */}
          <div className="absolute inset-0 pointer-events-none overflow-hidden">
            {/* 网格背景 */}
            <div
              className="absolute inset-0 opacity-[0.015]"
              style={{
                backgroundImage: `
                  linear-gradient(rgba(139, 92, 246, 0.5) 1px, transparent 1px),
                  linear-gradient(90deg, rgba(139, 92, 246, 0.5) 1px, transparent 1px)
                `,
                backgroundSize: '40px 40px',
              }}
            />
            {/* 光晕效果 */}
            <div
              className="absolute -top-40 -right-40 w-[500px] h-[500px] rounded-full"
              style={{
                background: 'radial-gradient(circle, rgba(139, 92, 246, 0.08) 0%, transparent 70%)',
              }}
            />
            <div
              className="absolute -bottom-40 -left-40 w-[400px] h-[400px] rounded-full"
              style={{
                background: 'radial-gradient(circle, rgba(0, 245, 255, 0.06) 0%, transparent 70%)',
              }}
            />
          </div>

          {/* 左侧面板 - 基础信息 */}
          <div
            className="w-[380px] flex-shrink-0 flex flex-col border-r border-white/5 relative"
          >
            {/* Header */}
            <div className="p-6 pb-4">
              {/* 关闭按钮 */}
              <motion.button
                onClick={onClose}
                className="absolute top-4 left-4 w-8 h-8 rounded-lg flex items-center justify-center text-white/30 hover:text-white hover:bg-white/5 transition-all z-10"
                whileHover={{ scale: 1.1 }}
                whileTap={{ scale: 0.9 }}
              >
                <svg className="w-5 h-5" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                  <path d="M18 6L6 18M6 6l12 12" />
                </svg>
              </motion.button>

              {/* 分类标签 */}
              <div className="flex items-center gap-2 mb-4 mt-8">
                <motion.div
                  className="px-3 py-1.5 rounded-full text-xs font-medium"
                  style={{
                    background: `${styleInfo.color}15`,
                    color: styleInfo.color,
                    border: `1px solid ${styleInfo.color}30`,
                  }}
                  initial={{ opacity: 0, x: -10 }}
                  animate={{ opacity: 1, x: 0 }}
                  transition={{ delay: 0.1 }}
                >
                  {template.category || '未分类'}
                </motion.div>
                <motion.div
                  className="px-3 py-1.5 rounded-full text-xs font-medium"
                  style={{
                    background: 'rgba(139, 92, 246, 0.1)',
                    color: '#A78BFA',
                    border: '1px solid rgba(139, 92, 246, 0.2)',
                  }}
                  initial={{ opacity: 0, x: -10 }}
                  animate={{ opacity: 1, x: 0 }}
                  transition={{ delay: 0.15 }}
                >
                  模板
                </motion.div>
              </div>

              {/* 标题 */}
              <motion.h2
                className="text-2xl font-bold text-white mb-3 leading-tight"
                initial={{ opacity: 0, y: 10 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ delay: 0.2 }}
              >
                {template.title}
              </motion.h2>

              {/* 摘要 */}
              <motion.p
                className="text-sm text-white/50 leading-relaxed"
                initial={{ opacity: 0, y: 10 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ delay: 0.25 }}
              >
                {template.summary}
              </motion.p>
            </div>

            {/* 统计数据 */}
            <motion.div
              className="px-6 py-5 mx-4 rounded-2xl mb-4"
              style={{
                background: 'linear-gradient(135deg, rgba(139, 92, 246, 0.05) 0%, rgba(0, 245, 255, 0.03) 100%)',
                border: '1px solid rgba(139, 92, 246, 0.1)',
              }}
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: 0.3 }}
            >
              <div className="grid grid-cols-3 gap-4">
                <StatNumber value={sections.length} label="章节数" />
                <StatNumber
                  value={estimatedWords > 1000 ? `${(estimatedWords / 1000).toFixed(1)}k` : estimatedWords}
                  label="参考字数"
                />
                <StatNumber value={template.usage_count || 0} label="使用次数" />
              </div>
            </motion.div>

            {/* 写作参数 */}
            <div className="px-6 flex-1 overflow-y-auto custom-scrollbar">
              <motion.div
                className="text-[11px] text-white/30 uppercase tracking-wider mb-3"
                initial={{ opacity: 0 }}
                animate={{ opacity: 1 }}
                transition={{ delay: 0.35 }}
              >
                写作参数
              </motion.div>

              <div className="grid grid-cols-2 gap-3 pb-4">
                <motion.div
                  initial={{ opacity: 0, y: 10 }}
                  animate={{ opacity: 1, y: 0 }}
                  transition={{ delay: 0.4 }}
                >
                  <InfoTag
                    label="写作风格"
                    value={styleInfo.label}
                    color={styleInfo.color}
                  />
                </motion.div>
                <motion.div
                  initial={{ opacity: 0, y: 10 }}
                  animate={{ opacity: 1, y: 0 }}
                  transition={{ delay: 0.45 }}
                >
                  <InfoTag
                    label="写作语气"
                    value={toneInfo.label}
                    icon={toneInfo.icon}
                    color="#A78BFA"
                  />
                </motion.div>
              </div>

              {template.target_audience && (
                <motion.div
                  className="mb-4"
                  initial={{ opacity: 0, y: 10 }}
                  animate={{ opacity: 1, y: 0 }}
                  transition={{ delay: 0.5 }}
                >
                  <InfoTag
                    label="目标受众"
                    value={template.target_audience}
                    color="#00F5FF"
                  />
                </motion.div>
              )}

              {/* 元信息 */}
              <motion.div
                className="pt-4 border-t border-white/5 space-y-2"
                initial={{ opacity: 0 }}
                animate={{ opacity: 1 }}
                transition={{ delay: 0.55 }}
              >
                <div className="flex items-center justify-between text-xs">
                  <span className="text-white/30">原始文件</span>
                  <span className="text-white/50 truncate max-w-[180px]">
                    {template.original_filename || '-'}
                  </span>
                </div>
                <div className="flex items-center justify-between text-xs">
                  <span className="text-white/30">创建时间</span>
                  <span className="text-white/50">
                    {new Date(template.created_at).toLocaleDateString('zh-CN', {
                      year: 'numeric',
                      month: 'long',
                      day: 'numeric',
                    })}
                  </span>
                </div>
                <div className="flex items-center justify-between text-xs">
                  <span className="text-white/30">更新时间</span>
                  <span className="text-white/50">
                    {new Date(template.updated_at).toLocaleDateString('zh-CN', {
                      year: 'numeric',
                      month: 'long',
                      day: 'numeric',
                    })}
                  </span>
                </div>
              </motion.div>
            </div>

            {/* 底部操作 */}
            <div className="p-6 pt-4 border-t border-white/5">
              <motion.button
                onClick={() => onUseTemplate(template.id)}
                className="w-full py-3.5 rounded-xl text-sm font-semibold transition-all relative overflow-hidden group"
                style={{
                  background: 'linear-gradient(135deg, #8B5CF6 0%, #00F5FF 100%)',
                  color: '#0a0a0f',
                  boxShadow: '0 8px 30px rgba(139, 92, 246, 0.3)',
                }}
                whileHover={{
                  scale: 1.02,
                  boxShadow: '0 12px 40px rgba(139, 92, 246, 0.4)'
                }}
                whileTap={{ scale: 0.98 }}
              >
                <span className="relative z-10 flex items-center justify-center gap-2">
                  <svg className="w-4 h-4" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5">
                    <path d="M12 5v14M5 12h14" />
                  </svg>
                  使用此模板
                </span>
                <motion.div
                  className="absolute inset-0"
                  style={{
                    background: 'linear-gradient(135deg, #00F5FF 0%, #8B5CF6 100%)',
                  }}
                  initial={{ x: '100%' }}
                  whileHover={{ x: 0 }}
                  transition={{ duration: 0.3 }}
                />
              </motion.button>
            </div>
          </div>

          {/* 右侧面板 - 章节结构 */}
          <div className="flex-1 flex flex-col min-w-0">
            {/* 章节标题栏 */}
            <div className="px-8 py-5 border-b border-white/5 flex items-center justify-between">
              <motion.div
                className="flex items-center gap-3"
                initial={{ opacity: 0, x: -10 }}
                animate={{ opacity: 1, x: 0 }}
                transition={{ delay: 0.3 }}
              >
                <div
                  className="w-1 h-5 rounded-full"
                  style={{ background: 'linear-gradient(180deg, #8B5CF6 0%, #00F5FF 100%)' }}
                />
                <h3 className="text-base font-semibold text-white">章节结构</h3>
                <span className="text-xs text-white/30">
                  共 {sections.length} 个章节
                </span>
              </motion.div>

              {/* 进度指示器 */}
              <motion.div
                className="flex items-center gap-2"
                initial={{ opacity: 0, x: 10 }}
                animate={{ opacity: 1, x: 0 }}
                transition={{ delay: 0.35 }}
              >
                <div className="w-32 h-1.5 rounded-full bg-white/5 overflow-hidden">
                  <motion.div
                    className="h-full rounded-full"
                    style={{
                      background: 'linear-gradient(90deg, #8B5CF6 0%, #00F5FF 100%)',
                    }}
                    initial={{ width: 0 }}
                    animate={{ width: '100%' }}
                    transition={{ delay: 0.5, duration: 1, ease: 'easeOut' }}
                  />
                </div>
                <span className="text-[11px] text-white/40">100%</span>
              </motion.div>
            </div>

            {/* 章节列表 */}
            <div className="flex-1 overflow-y-auto px-8 py-6 custom-scrollbar">
              {sections.length === 0 ? (
                <motion.div
                  className="h-full flex flex-col items-center justify-center text-center"
                  initial={{ opacity: 0 }}
                  animate={{ opacity: 1 }}
                  transition={{ delay: 0.3 }}
                >
                  <div
                    className="w-16 h-16 rounded-2xl flex items-center justify-center mb-4"
                    style={{ background: 'rgba(139, 92, 246, 0.1)' }}
                  >
                    <svg className="w-8 h-8 text-[#8B5CF6]/50" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.5">
                      <path d="M9 12h6M9 16h6M17 21H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
                    </svg>
                  </div>
                  <p className="text-white/40 mb-1">暂无章节结构</p>
                  <p className="text-sm text-white/25">该模板未定义章节结构</p>
                </motion.div>
              ) : (
                <div className="space-y-0">
                  {sections.map((section, index) => (
                    <SectionCard
                      key={index}
                      section={section}
                      index={index}
                      total={sections.length}
                    />
                  ))}
                </div>
              )}
            </div>

            {/* 底部提示 */}
            <motion.div
              className="px-8 py-4 border-t border-white/5"
              style={{ background: 'rgba(0, 0, 0, 0.2)' }}
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              transition={{ delay: 0.6 }}
            >
              <div className="flex items-center gap-3 text-xs text-white/30">
                <div
                  className="w-5 h-5 rounded-lg flex items-center justify-center"
                  style={{ background: 'rgba(0, 245, 255, 0.1)' }}
                >
                  <svg className="w-3 h-3 text-[#00F5FF]" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                    <circle cx="12" cy="12" r="10" />
                    <path d="M12 16v-4M12 8h.01" />
                  </svg>
                </div>
                <span>
                  使用此模板后，AI 将根据上述章节结构生成符合风格的完整文档
                </span>
              </div>
            </motion.div>
          </div>
        </motion.div>

        {/* Custom Scrollbar Styles */}
        <style jsx global>{`
          .custom-scrollbar::-webkit-scrollbar {
            width: 5px;
          }
          .custom-scrollbar::-webkit-scrollbar-track {
            background: transparent;
          }
          .custom-scrollbar::-webkit-scrollbar-thumb {
            background: rgba(139, 92, 246, 0.2);
            border-radius: 3px;
          }
          .custom-scrollbar::-webkit-scrollbar-thumb:hover {
            background: rgba(139, 92, 246, 0.3);
          }
        `}</style>
      </div>
    </AnimatePresence>
  )
}
