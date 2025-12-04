'use client'

import { useEffect, useRef } from 'react'
import katex from 'katex'
import 'katex/dist/katex.min.css'

interface MathBlockProps {
  math: string
  inline?: boolean
}

export default function MathBlock({ math, inline = false }: MathBlockProps) {
  const containerRef = useRef<HTMLSpanElement | HTMLDivElement>(null)

  useEffect(() => {
    if (!containerRef.current) return

    try {
      katex.render(math, containerRef.current, {
        displayMode: !inline,
        throwOnError: false,
        errorColor: '#f87171',
        strict: false,
        trust: false,
        macros: {
          '\\f': '#1f(#2)',
        },
      })
    } catch (error) {
      console.error('KaTeX rendering error:', error)
    }
  }, [math, inline])

  if (inline) {
    return <span ref={containerRef as React.RefObject<HTMLSpanElement>} className="inline-math" />
  }

  return (
    <div className="my-6">
      <div className="glass-card p-6 rounded-lg overflow-x-auto">
        <div
          ref={containerRef as React.RefObject<HTMLDivElement>}
          className="math-block text-center"
        />
      </div>
    </div>
  )
}
