'use client'

import { useState } from 'react'
import { Highlight, themes } from 'prism-react-renderer'

interface CodeBlockProps {
  code: string
  language: string
  filename?: string
}

export default function CodeBlock({ code, language, filename }: CodeBlockProps) {
  const [copied, setCopied] = useState(false)

  const handleCopy = async () => {
    await navigator.clipboard.writeText(code)
    setCopied(true)
    setTimeout(() => setCopied(false), 2000)
  }

  return (
    <div className="group relative my-6 rounded-lg overflow-hidden glass-code">
      {/* 头部 - 语言标签和复制按钮 */}
      <div className="flex items-center justify-between px-4 py-2 bg-slate-800/50 border-b border-purple-500/20">
        <div className="flex items-center gap-2">
          {filename && (
            <span className="text-sm text-slate-300 font-mono">{filename}</span>
          )}
          {!filename && language && (
            <span className="text-xs px-2 py-1 rounded bg-purple-500/20 text-purple-300 font-mono">
              {language}
            </span>
          )}
        </div>

        {/* 复制按钮 */}
        <button
          onClick={handleCopy}
          className="flex items-center gap-1.5 px-3 py-1.5 rounded text-xs font-medium
            bg-white/5 hover:bg-white/10 text-slate-300 hover:text-white
            border border-white/10 hover:border-purple-400/50
            transition-all duration-200"
        >
          {copied ? (
            <>
              <svg className="w-3.5 h-3.5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
              </svg>
              <span>已复制</span>
            </>
          ) : (
            <>
              <svg className="w-3.5 h-3.5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2}
                  d="M8 16H6a2 2 0 01-2-2V6a2 2 0 012-2h8a2 2 0 012 2v2m-6 12h8a2 2 0 002-2v-8a2 2 0 00-2-2h-8a2 2 0 00-2 2v8a2 2 0 002 2z" />
              </svg>
              <span>复制</span>
            </>
          )}
        </button>
      </div>

      {/* 代码内容 */}
      <Highlight theme={themes.nightOwl} code={code.trim()} language={language || 'text'}>
        {({ className, style, tokens, getLineProps, getTokenProps }) => (
          <pre
            className={`${className} p-4 overflow-x-auto text-sm leading-relaxed`}
            style={{
              ...style,
              background: 'transparent',
              margin: 0,
            }}
          >
            {tokens.map((line, i) => (
              <div key={i} {...getLineProps({ line })} className="table-row">
                {/* 行号 */}
                <span className="table-cell pr-4 text-right text-slate-600 select-none w-8">
                  {i + 1}
                </span>
                {/* 代码 */}
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
}
