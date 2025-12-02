'use client'

import { useState } from 'react'
import { motion, AnimatePresence } from 'framer-motion'
import Link from 'next/link'
import { useRouter } from 'next/navigation'
import { register } from '@/lib/auth/api'

export default function RegisterPage() {
  const router = useRouter()
  const [name, setName] = useState('')
  const [email, setEmail] = useState('')
  const [password, setPassword] = useState('')
  const [confirmPassword, setConfirmPassword] = useState('')
  const [error, setError] = useState('')
  const [isLoading, setIsLoading] = useState(false)
  const [showPassword, setShowPassword] = useState(false)

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    setError('')

    // 验证密码匹配
    if (password !== confirmPassword) {
      setError('两次输入的密码不一致')
      return
    }

    // 验证密码长度
    if (password.length < 8) {
      setError('密码长度至少 8 位')
      return
    }

    setIsLoading(true)

    try {
      await register({ name, email, password })
      router.push('/chat')
    } catch (err) {
      setError(err instanceof Error ? err.message : '注册失败')
    } finally {
      setIsLoading(false)
    }
  }

  return (
    <div className="min-h-screen flex items-center justify-center px-4 py-12">
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.6 }}
        className="w-full max-w-md"
      >
        {/* Logo 和标题 */}
        <div className="text-center mb-8">
          <motion.div
            className="inline-block mb-6"
            initial={{ scale: 0, rotate: -180 }}
            animate={{ scale: 1, rotate: 0 }}
            transition={{ type: 'spring', duration: 1, delay: 0.2 }}
          >
            <div
              className="w-20 h-20 rounded-2xl flex items-center justify-center mx-auto relative overflow-hidden"
              style={{
                background: 'var(--gradient-neural)',
                boxShadow: 'var(--shadow-neural)',
              }}
            >
              <div
                className="absolute inset-0 opacity-50"
                style={{
                  background: 'radial-gradient(circle at 30% 30%, rgba(255,255,255,0.3) 0%, transparent 60%)',
                }}
              />
              <svg
                className="w-10 h-10 text-white relative z-10"
                viewBox="0 0 24 24"
                fill="none"
                stroke="currentColor"
                strokeWidth="1.5"
              >
                <circle cx="12" cy="12" r="3" />
                <path d="M12 2v4m0 12v4M2 12h4m12 0h4" />
                <path d="M4.93 4.93l2.83 2.83m8.48 8.48l2.83 2.83M4.93 19.07l2.83-2.83m8.48-8.48l2.83-2.83" />
              </svg>
            </div>
          </motion.div>

          <motion.h1
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            transition={{ delay: 0.4 }}
            className="text-4xl font-bold mb-2"
            style={{
              fontFamily: 'Orbitron, sans-serif',
              background: 'var(--gradient-neural)',
              WebkitBackgroundClip: 'text',
              WebkitTextFillColor: 'transparent',
              backgroundClip: 'text',
            }}
          >
            创建账号
          </motion.h1>
          <motion.p
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            transition={{ delay: 0.5 }}
            className="text-[var(--text-secondary)]"
          >
            加入 Nexus AI 智能平台
          </motion.p>
        </div>

        {/* 注册表单卡片 */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.3 }}
          className="relative"
        >
          {/* 发光边框效果 */}
          <div
            className="absolute -inset-[1px] rounded-2xl opacity-50"
            style={{
              background: 'var(--gradient-neural)',
              filter: 'blur(1px)',
            }}
          />

          {/* 卡片内容 */}
          <div
            className="relative rounded-2xl p-8"
            style={{
              background: 'rgba(17, 24, 39, 0.8)',
              backdropFilter: 'blur(20px) saturate(150%)',
              border: '1px solid var(--border-default)',
            }}
          >
            <form onSubmit={handleSubmit} className="space-y-5">
              {/* 错误提示 */}
              <AnimatePresence>
                {error && (
                  <motion.div
                    initial={{ opacity: 0, height: 0, marginBottom: 0 }}
                    animate={{ opacity: 1, height: 'auto', marginBottom: 16 }}
                    exit={{ opacity: 0, height: 0, marginBottom: 0 }}
                    className="p-4 rounded-xl overflow-hidden"
                    style={{
                      background: 'rgba(239, 68, 68, 0.1)',
                      border: '1px solid rgba(239, 68, 68, 0.3)',
                    }}
                  >
                    <p className="text-[var(--nexus-error)] text-sm flex items-center gap-2">
                      <svg className="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 8v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
                      </svg>
                      {error}
                    </p>
                  </motion.div>
                )}
              </AnimatePresence>

              {/* 用户名输入 */}
              <div>
                <label className="block text-sm font-medium text-[var(--text-secondary)] mb-2">
                  用户名
                </label>
                <div className="relative">
                  <input
                    type="text"
                    value={name}
                    onChange={(e) => setName(e.target.value)}
                    className="w-full px-4 py-3 pl-11 rounded-xl text-[var(--text-primary)] placeholder-[var(--text-tertiary)] transition-all duration-300 focus:outline-none"
                    style={{
                      background: 'var(--nexus-deep)',
                      border: '1px solid var(--border-default)',
                    }}
                    placeholder="输入用户名"
                    required
                    maxLength={50}
                  />
                  <svg
                    className="absolute left-4 top-1/2 -translate-y-1/2 w-4 h-4 text-[var(--text-tertiary)]"
                    fill="none"
                    viewBox="0 0 24 24"
                    stroke="currentColor"
                  >
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M16 7a4 4 0 11-8 0 4 4 0 018 0zM12 14a7 7 0 00-7 7h14a7 7 0 00-7-7z" />
                  </svg>
                </div>
              </div>

              {/* 邮箱输入 */}
              <div>
                <label className="block text-sm font-medium text-[var(--text-secondary)] mb-2">
                  邮箱
                </label>
                <div className="relative">
                  <input
                    type="email"
                    value={email}
                    onChange={(e) => setEmail(e.target.value)}
                    className="w-full px-4 py-3 pl-11 rounded-xl text-[var(--text-primary)] placeholder-[var(--text-tertiary)] transition-all duration-300 focus:outline-none"
                    style={{
                      background: 'var(--nexus-deep)',
                      border: '1px solid var(--border-default)',
                    }}
                    placeholder="your@email.com"
                    required
                    autoComplete="email"
                  />
                  <svg
                    className="absolute left-4 top-1/2 -translate-y-1/2 w-4 h-4 text-[var(--text-tertiary)]"
                    fill="none"
                    viewBox="0 0 24 24"
                    stroke="currentColor"
                  >
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M3 8l7.89 5.26a2 2 0 002.22 0L21 8M5 19h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v10a2 2 0 002 2z" />
                  </svg>
                </div>
              </div>

              {/* 密码输入 */}
              <div>
                <label className="block text-sm font-medium text-[var(--text-secondary)] mb-2">
                  密码
                </label>
                <div className="relative">
                  <input
                    type={showPassword ? 'text' : 'password'}
                    value={password}
                    onChange={(e) => setPassword(e.target.value)}
                    className="w-full px-4 py-3 pl-11 pr-11 rounded-xl text-[var(--text-primary)] placeholder-[var(--text-tertiary)] transition-all duration-300 focus:outline-none"
                    style={{
                      background: 'var(--nexus-deep)',
                      border: '1px solid var(--border-default)',
                    }}
                    placeholder="至少 8 位字符"
                    required
                    minLength={8}
                    autoComplete="new-password"
                  />
                  <svg
                    className="absolute left-4 top-1/2 -translate-y-1/2 w-4 h-4 text-[var(--text-tertiary)]"
                    fill="none"
                    viewBox="0 0 24 24"
                    stroke="currentColor"
                  >
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M12 15v2m-6 4h12a2 2 0 002-2v-6a2 2 0 00-2-2H6a2 2 0 00-2 2v6a2 2 0 002 2zm10-10V7a4 4 0 00-8 0v4h8z" />
                  </svg>
                  <button
                    type="button"
                    onClick={() => setShowPassword(!showPassword)}
                    className="absolute right-4 top-1/2 -translate-y-1/2 text-[var(--text-tertiary)] hover:text-[var(--text-secondary)] transition-colors"
                  >
                    {showPassword ? (
                      <svg className="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M13.875 18.825A10.05 10.05 0 0112 19c-4.478 0-8.268-2.943-9.543-7a9.97 9.97 0 011.563-3.029m5.858.908a3 3 0 114.243 4.243M9.878 9.878l4.242 4.242M9.88 9.88l-3.29-3.29m7.532 7.532l3.29 3.29M3 3l3.59 3.59m0 0A9.953 9.953 0 0112 5c4.478 0 8.268 2.943 9.543 7a10.025 10.025 0 01-4.132 5.411m0 0L21 21" />
                      </svg>
                    ) : (
                      <svg className="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M15 12a3 3 0 11-6 0 3 3 0 016 0z" />
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M2.458 12C3.732 7.943 7.523 5 12 5c4.478 0 8.268 2.943 9.542 7-1.274 4.057-5.064 7-9.542 7-4.477 0-8.268-2.943-9.542-7z" />
                      </svg>
                    )}
                  </button>
                </div>
              </div>

              {/* 确认密码 */}
              <div>
                <label className="block text-sm font-medium text-[var(--text-secondary)] mb-2">
                  确认密码
                </label>
                <div className="relative">
                  <input
                    type={showPassword ? 'text' : 'password'}
                    value={confirmPassword}
                    onChange={(e) => setConfirmPassword(e.target.value)}
                    className="w-full px-4 py-3 pl-11 rounded-xl text-[var(--text-primary)] placeholder-[var(--text-tertiary)] transition-all duration-300 focus:outline-none"
                    style={{
                      background: 'var(--nexus-deep)',
                      border: '1px solid var(--border-default)',
                    }}
                    placeholder="再次输入密码"
                    required
                    autoComplete="new-password"
                  />
                  <svg
                    className="absolute left-4 top-1/2 -translate-y-1/2 w-4 h-4 text-[var(--text-tertiary)]"
                    fill="none"
                    viewBox="0 0 24 24"
                    stroke="currentColor"
                  >
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M9 12l2 2 4-4m5.618-4.016A11.955 11.955 0 0112 2.944a11.955 11.955 0 01-8.618 3.04A12.02 12.02 0 003 9c0 5.591 3.824 10.29 9 11.622 5.176-1.332 9-6.03 9-11.622 0-1.042-.133-2.052-.382-3.016z" />
                  </svg>
                </div>
              </div>

              {/* 注册按钮 */}
              <motion.button
                type="submit"
                disabled={isLoading}
                className="w-full py-3.5 rounded-xl font-medium text-white transition-all duration-300 relative overflow-hidden group mt-2"
                style={{
                  background: 'var(--gradient-neural)',
                  boxShadow: isLoading ? 'none' : 'var(--shadow-glow-sm)',
                }}
                whileHover={{ scale: 1.02 }}
                whileTap={{ scale: 0.98 }}
              >
                <div className="absolute inset-0 opacity-0 group-hover:opacity-100 transition-opacity duration-300" style={{ background: 'rgba(255,255,255,0.1)' }} />

                {isLoading ? (
                  <div className="flex items-center justify-center gap-2">
                    <svg className="animate-spin w-5 h-5" fill="none" viewBox="0 0 24 24">
                      <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" />
                      <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z" />
                    </svg>
                    <span>注册中...</span>
                  </div>
                ) : (
                  <span className="relative z-10">创建账号</span>
                )}
              </motion.button>
            </form>

            {/* 登录链接 */}
            <div className="mt-8 pt-6 border-t border-[var(--border-subtle)]">
              <p className="text-center text-[var(--text-tertiary)]">
                已有账号？{' '}
                <Link
                  href="/login"
                  className="text-[var(--nexus-cyan)] hover:text-[var(--nexus-blue)] transition-colors font-medium"
                >
                  立即登录
                </Link>
              </p>
            </div>
          </div>
        </motion.div>

        {/* 底部版权 */}
        <motion.p
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          transition={{ delay: 0.8 }}
          className="text-center text-[var(--text-tertiary)] text-sm mt-8"
        >
          Nexus AI - Multi-Agent Intelligence Platform
        </motion.p>
      </motion.div>
    </div>
  )
}
