'use client'

import ReactMarkdown from 'react-markdown'
import remarkGfm from 'remark-gfm'
import remarkMath from 'remark-math'
import { motion } from 'framer-motion'
import CodeBlock from './CodeBlock'
import MermaidBlock from './MermaidBlock'
import MathBlock from './MathBlock'
import '../styles/markdown.css'
import '../styles/glassmorphism.css'
import '../styles/animations.css'

interface MarkdownRendererProps {
  content: string
  className?: string
}

export default function MarkdownRenderer({ content, className = '' }: MarkdownRendererProps) {
  // 预处理内容：确保markdown语法正确
  const processedContent = content
    .replace(/\\\*\\\*/g, '**') // 处理转义的星号
    .replace(/\\\_\\\_/g, '__')  // 处理转义的下划线
    .replace(/\\\*/g, '*')       // 处理单个转义星号

  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.6 }}
      className={`markdown-body ${className}`}
    >
      <ReactMarkdown
        remarkPlugins={[remarkGfm, remarkMath]}
        components={{
          // 代码块处理
          code({ className, children, ...props }: any) {
            const match = /language-(\w+)/.exec(className || '')
            const code = String(children).replace(/\n$/, '')
            const language = match ? match[1] : ''
            const inline = !className

            // Mermaid图表
            if (language === 'mermaid') {
              return <MermaidBlock chart={code} />
            }

            // 数学公式（如果在$$ $$块中）
            if (language === 'math') {
              return <MathBlock math={code} inline={false} />
            }

            // 普通代码块
            if (!inline && match) {
              return <CodeBlock code={code} language={language} />
            }

            // 行内代码
            return (
              <code className={className} {...props}>
                {children}
              </code>
            )
          },

          // 标题 - 添加动画和ID（用于目录导航）
          h1({ children, ...props }: any) {
            const id = String(children).toLowerCase().replace(/\s+/g, '-')
            return (
              <motion.h1
                id={id}
                initial={{ opacity: 0, x: -20 }}
                whileInView={{ opacity: 1, x: 0 }}
                viewport={{ once: true }}
                transition={{ duration: 0.5 }}
              >
                {children}
              </motion.h1>
            )
          },

          h2({ children, ...props }: any) {
            const id = String(children).toLowerCase().replace(/\s+/g, '-')
            return (
              <motion.h2
                id={id}
                initial={{ opacity: 0, x: -20 }}
                whileInView={{ opacity: 1, x: 0 }}
                viewport={{ once: true }}
                transition={{ duration: 0.5, delay: 0.1 }}
              >
                {children}
              </motion.h2>
            )
          },

          h3({ children, ...props }: any) {
            const id = String(children).toLowerCase().replace(/\s+/g, '-')
            return (
              <motion.h3
                id={id}
                initial={{ opacity: 0, x: -20 }}
                whileInView={{ opacity: 1, x: 0 }}
                viewport={{ once: true }}
                transition={{ duration: 0.5, delay: 0.15 }}
              >
                {children}
              </motion.h3>
            )
          },

          h4({ children, ...props }: any) {
            const id = String(children).toLowerCase().replace(/\s+/g, '-')
            return <h4 id={id}>{children}</h4>
          },

          // 段落 - 渐入动画
          p({ children, ...props }: any) {
            return (
              <motion.p
                initial={{ opacity: 0 }}
                whileInView={{ opacity: 1 }}
                viewport={{ once: true }}
                transition={{ duration: 0.4 }}
              >
                {children}
              </motion.p>
            )
          },

          // 图片 - 懒加载 + 动画
          img({ src, alt, ...props }: any) {
            return (
              <motion.img
                src={src}
                alt={alt}
                initial={{ opacity: 0, scale: 0.95 }}
                whileInView={{ opacity: 1, scale: 1 }}
                viewport={{ once: true }}
                transition={{ duration: 0.5 }}
                loading="lazy"
              />
            )
          },

          // 引用块 - 玻璃态效果
          blockquote({ children, ...props }: any) {
            return (
              <motion.blockquote
                initial={{ opacity: 0, x: -10 }}
                whileInView={{ opacity: 1, x: 0 }}
                viewport={{ once: true }}
                transition={{ duration: 0.5 }}
              >
                {children}
              </motion.blockquote>
            )
          },

          // 表格 - 响应式封装
          table({ children, ...props }: any) {
            return (
              <div className="overflow-x-auto my-6">
                <motion.table
                  initial={{ opacity: 0 }}
                  whileInView={{ opacity: 1 }}
                  viewport={{ once: true }}
                  transition={{ duration: 0.5 }}
                >
                  {children}
                </motion.table>
              </div>
            )
          },

          // 链接 - 悬浮效果
          a({ href, children, ...props }: any) {
            const isExternal = href?.startsWith('http')
            return (
              <a
                href={href}
                target={isExternal ? '_blank' : undefined}
                rel={isExternal ? 'noopener noreferrer' : undefined}
              >
                {children}
                {isExternal && (
                  <svg
                    className="inline-block w-3 h-3 ml-1 mb-1"
                    fill="none"
                    stroke="currentColor"
                    viewBox="0 0 24 24"
                  >
                    <path
                      strokeLinecap="round"
                      strokeLinejoin="round"
                      strokeWidth={2}
                      d="M10 6H6a2 2 0 00-2 2v10a2 2 0 002 2h10a2 2 0 002-2v-4M14 4h6m0 0v6m0-6L10 14"
                    />
                  </svg>
                )}
              </a>
            )
          },

          // 列表 - 渐入动画
          ul({ children, ...props }: any) {
            return (
              <motion.ul
                initial={{ opacity: 0 }}
                whileInView={{ opacity: 1 }}
                viewport={{ once: true }}
                transition={{ duration: 0.4 }}
              >
                {children}
              </motion.ul>
            )
          },

          ol({ children, ...props }: any) {
            return (
              <motion.ol
                initial={{ opacity: 0 }}
                whileInView={{ opacity: 1 }}
                viewport={{ once: true }}
                transition={{ duration: 0.4 }}
              >
                {children}
              </motion.ol>
            )
          },

          // 分割线 - 动画
          hr({ ...props }: any) {
            return (
              <motion.hr
                initial={{ scaleX: 0 }}
                whileInView={{ scaleX: 1 }}
                viewport={{ once: true }}
                transition={{ duration: 0.6 }}
              />
            )
          },

          // 粗体 - 确保正确渲染
          strong({ children, ...props }: any) {
            return <strong {...props}>{children}</strong>
          },

          // 斜体 - 确保正确渲染
          em({ children, ...props }: any) {
            return <em {...props}>{children}</em>
          },
        }}
      >
        {processedContent}
      </ReactMarkdown>
    </motion.div>
  )
}
