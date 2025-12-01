'use client'

import { useState, memo, useMemo } from 'react'
import ReactMarkdown from 'react-markdown'
import remarkGfm from 'remark-gfm'
import remarkMath from 'remark-math'
import rehypeKatex from 'rehype-katex'
import { Highlight, themes } from 'prism-react-renderer'
import 'katex/dist/katex.min.css'
import '../styles/chat-markdown.css'

interface ChatMarkdownProps {
  content: string
  isStreaming?: boolean
}

// Code block component - elegant dark glass design
const CodeBlock = memo(({ code, language }: { code: string; language: string }) => {
  const [copied, setCopied] = useState(false)

  const handleCopy = async () => {
    await navigator.clipboard.writeText(code)
    setCopied(true)
    setTimeout(() => setCopied(false), 2000)
  }

  return (
    <div className="chat-code-block group my-4 rounded-xl overflow-hidden border border-white/[0.06] bg-[#0d1117]/80 backdrop-blur-md shadow-lg shadow-black/20">
      {/* Header bar */}
      <div className="flex items-center justify-between px-4 py-2.5 bg-gradient-to-r from-white/[0.03] to-transparent border-b border-white/[0.06]">
        <div className="flex items-center gap-3">
          {/* macOS style buttons */}
          <div className="flex gap-1.5">
            <span className="w-3 h-3 rounded-full bg-[#ff5f57]/80" />
            <span className="w-3 h-3 rounded-full bg-[#febc2e]/80" />
            <span className="w-3 h-3 rounded-full bg-[#28c840]/80" />
          </div>
          {language && (
            <span className="text-[11px] font-medium tracking-wide uppercase text-white/40 font-mono">
              {language}
            </span>
          )}
        </div>

        <button
          onClick={handleCopy}
          className="flex items-center gap-1.5 px-2.5 py-1 rounded-md text-[11px] font-medium
            text-white/40 hover:text-white/80 hover:bg-white/[0.06]
            transition-all duration-200"
        >
          {copied ? (
            <>
              <svg className="w-3.5 h-3.5 text-emerald-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
              </svg>
              <span className="text-emerald-400">Copied</span>
            </>
          ) : (
            <>
              <svg className="w-3.5 h-3.5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5}
                  d="M8 16H6a2 2 0 01-2-2V6a2 2 0 012-2h8a2 2 0 012 2v2m-6 12h8a2 2 0 002-2v-8a2 2 0 00-2-2h-8a2 2 0 00-2 2v8a2 2 0 002 2z" />
              </svg>
              <span>Copy</span>
            </>
          )}
        </button>
      </div>

      {/* Code content */}
      <Highlight theme={themes.nightOwl} code={code.trim()} language={language || 'text'}>
        {({ className, style, tokens, getLineProps, getTokenProps }) => (
          <pre
            className={`${className} px-4 py-4 overflow-x-auto text-[13px] leading-[1.7] font-mono`}
            style={{ ...style, background: 'transparent', margin: 0 }}
          >
            {tokens.map((line, i) => (
              <div key={i} {...getLineProps({ line })} className="table-row">
                <span className="table-cell pr-4 text-right text-white/20 select-none w-8 text-[12px]">
                  {i + 1}
                </span>
                <span className="table-cell">
                  {line.map((token, key) => (
                    <span key={key} {...getTokenProps({ token })} />
                  ))}
                </span>
              </div>
            ))}
          </pre>
        )}
      </Highlight>
    </div>
  )
})

CodeBlock.displayName = 'CodeBlock'

// Inline code
const InlineCode = memo(({ children }: { children: React.ReactNode }) => (
  <code className="px-1.5 py-0.5 mx-0.5 rounded-md bg-white/[0.06] text-[#7dd3fc] text-[0.9em] font-mono border border-white/[0.08]">
    {children}
  </code>
))

InlineCode.displayName = 'InlineCode'

// Main component
function ChatMarkdown({ content, isStreaming = false }: ChatMarkdownProps) {
  // Pre-process content - handle LaTeX format from DeepSeek models
  const processedContent = useMemo(() => {
    let processed = content

    // Convert \( ... \) inline math to $...$
    processed = processed.replace(/\\\(([^)]+)\\\)/g, '$$$1$$')

    // Convert \[ ... \] block math to $$...$$
    processed = processed.replace(/\\\[([^\]]+)\\\]/g, '\n$$$$$1$$$$\n')

    return processed
  }, [content])

  return (
    <div className={`chat-markdown ${isStreaming ? 'streaming' : ''}`}>
      <ReactMarkdown
        remarkPlugins={[remarkGfm, remarkMath]}
        rehypePlugins={[rehypeKatex]}
        components={{
          // Code blocks
          code({ className, children, ...props }: any) {
            const match = /language-(\w+)/.exec(className || '')
            const code = String(children).replace(/\n$/, '')
            const isInline = !className && !code.includes('\n')

            if (isInline) {
              return <InlineCode>{children}</InlineCode>
            }

            return <CodeBlock code={code} language={match ? match[1] : ''} />
          },

          // Paragraphs
          p({ children, ...props }: any) {
            return (
              <p className="my-3 leading-[1.8] text-white/85">
                {children}
              </p>
            )
          },

          // Headings
          h1({ children }: any) {
            return <h1 className="text-2xl font-semibold mt-6 mb-4 text-white/95 tracking-tight">{children}</h1>
          },
          h2({ children }: any) {
            return <h2 className="text-xl font-semibold mt-5 mb-3 text-white/95 tracking-tight">{children}</h2>
          },
          h3({ children }: any) {
            return <h3 className="text-lg font-semibold mt-4 mb-2 text-white/90">{children}</h3>
          },
          h4({ children }: any) {
            return <h4 className="text-base font-semibold mt-3 mb-2 text-white/90">{children}</h4>
          },

          // Lists
          ul({ children }: any) {
            return (
              <ul className="my-3 ml-1 space-y-2">
                {children}
              </ul>
            )
          },
          ol({ children }: any) {
            return (
              <ol className="my-3 ml-1 space-y-2 list-decimal list-inside marker:text-cyan-400/60">
                {children}
              </ol>
            )
          },
          li({ children }: any) {
            return (
              <li className="flex gap-2 text-white/80 leading-[1.7]">
                <span className="text-cyan-400/60 mt-1.5 flex-shrink-0">•</span>
                <span className="flex-1">{children}</span>
              </li>
            )
          },

          // Blockquote
          blockquote({ children }: any) {
            return (
              <blockquote className="my-4 pl-4 border-l-2 border-cyan-500/40 text-white/60 italic">
                {children}
              </blockquote>
            )
          },

          // Links
          a({ href, children }: any) {
            return (
              <a
                href={href}
                target="_blank"
                rel="noopener noreferrer"
                className="text-cyan-400 hover:text-cyan-300 underline underline-offset-2 decoration-cyan-400/30 hover:decoration-cyan-300/50 transition-colors"
              >
                {children}
              </a>
            )
          },

          // Bold
          strong({ children }: any) {
            return <strong className="font-semibold text-white/95">{children}</strong>
          },

          // Italic
          em({ children }: any) {
            return <em className="italic text-white/80">{children}</em>
          },

          // Table
          table({ children }: any) {
            return (
              <div className="my-4 overflow-x-auto rounded-lg border border-white/[0.08]">
                <table className="w-full text-sm">{children}</table>
              </div>
            )
          },
          thead({ children }: any) {
            return <thead className="bg-white/[0.04] border-b border-white/[0.08]">{children}</thead>
          },
          tbody({ children }: any) {
            return <tbody className="divide-y divide-white/[0.06]">{children}</tbody>
          },
          tr({ children }: any) {
            return <tr className="hover:bg-white/[0.02] transition-colors">{children}</tr>
          },
          th({ children }: any) {
            return <th className="px-4 py-3 text-left font-medium text-white/70">{children}</th>
          },
          td({ children }: any) {
            return <td className="px-4 py-3 text-white/60">{children}</td>
          },

          // Horizontal rule
          hr() {
            return <hr className="my-6 border-0 h-px bg-gradient-to-r from-transparent via-white/10 to-transparent" />
          },
        }}
      >
        {processedContent}
      </ReactMarkdown>
    </div>
  )
}

export default memo(ChatMarkdown)
