'use client';

import { motion } from 'framer-motion';
import Link from 'next/link';
import { useAuthStore } from '@/lib/stores/auth';

// 预计算轨道节点位置（使用固定整数值避免 SSR/CSR hydration 不一致）
// 角度: 0, 60, 120, 180, 240, 300 度，半径 100px
const ORBIT_POSITIONS = [
  { top: 0, left: 100, lineX: 80, lineY: 0 },       // 0°
  { top: 87, left: 50, lineX: 40, lineY: 69 },      // 60°
  { top: 87, left: -50, lineX: -40, lineY: 69 },    // 120°
  { top: 0, left: -100, lineX: -80, lineY: 0 },     // 180°
  { top: -87, left: -50, lineX: -40, lineY: -69 },  // 240°
  { top: -87, left: 50, lineX: 40, lineY: -69 },    // 300°
];

// Neural Network Node Component
const NeuralNode = ({ delay, size, x, y }: { delay: number; size: number; x: string; y: string }) => (
  <motion.div
    className="absolute rounded-full"
    style={{
      width: size,
      height: size,
      left: x,
      top: y,
      background: 'radial-gradient(circle, rgba(6, 182, 212, 0.6) 0%, transparent 70%)',
      boxShadow: '0 0 20px rgba(6, 182, 212, 0.4)',
    }}
    initial={{ scale: 0, opacity: 0 }}
    animate={{
      scale: [1, 1.2, 1],
      opacity: [0.4, 0.8, 0.4],
    }}
    transition={{
      duration: 3,
      delay,
      repeat: Infinity,
      ease: 'easeInOut',
    }}
  />
);

// Neural Connection Line Component
const NeuralLine = ({ from, to, delay }: { from: { x: number; y: number }; to: { x: number; y: number }; delay: number }) => {
  const length = Math.sqrt(Math.pow(to.x - from.x, 2) + Math.pow(to.y - from.y, 2));
  const angle = Math.atan2(to.y - from.y, to.x - from.x) * (180 / Math.PI);

  return (
    <motion.div
      className="absolute h-[1px] origin-left"
      style={{
        left: from.x,
        top: from.y,
        width: length,
        transform: `rotate(${angle}deg)`,
        background: 'linear-gradient(90deg, rgba(6, 182, 212, 0.3), rgba(139, 92, 246, 0.3))',
      }}
      initial={{ scaleX: 0, opacity: 0 }}
      animate={{ scaleX: 1, opacity: 1 }}
      transition={{ duration: 1, delay }}
    />
  );
};

// Feature Card Component
const FeatureCard = ({ icon, title, description, delay }: { icon: React.ReactNode; title: string; description: string; delay: number }) => (
  <motion.div
    className="nexus-card-glow group"
    initial={{ opacity: 0, y: 30 }}
    animate={{ opacity: 1, y: 0 }}
    transition={{ duration: 0.6, delay }}
    whileHover={{ scale: 1.02 }}
  >
    <div className="nexus-card-glow-inner p-6">
      <div className="w-12 h-12 rounded-xl bg-gradient-neural flex items-center justify-center mb-4 group-hover:shadow-glow-md transition-shadow duration-300">
        {icon}
      </div>
      <h3 className="text-lg font-semibold mb-2 text-[var(--text-primary)]" style={{ fontFamily: 'Orbitron, sans-serif' }}>
        {title}
      </h3>
      <p className="text-sm text-[var(--text-secondary)] leading-relaxed">
        {description}
      </p>
    </div>
  </motion.div>
);

// Stats Card Component
const StatCard = ({ value, label, delay }: { value: string; label: string; delay: number }) => (
  <motion.div
    className="text-center"
    initial={{ opacity: 0, scale: 0.8 }}
    animate={{ opacity: 1, scale: 1 }}
    transition={{ duration: 0.5, delay }}
  >
    <div className="text-4xl font-bold text-gradient-neural mb-2" style={{ fontFamily: 'Orbitron, sans-serif' }}>
      {value}
    </div>
    <div className="text-sm text-[var(--text-tertiary)] uppercase tracking-wider">
      {label}
    </div>
  </motion.div>
);

export default function Home() {
  const { isAuthenticated, user } = useAuthStore();

  return (
    <div className="min-h-screen relative overflow-hidden">
      {/* Hero Section */}
      <section className="relative min-h-screen flex items-center justify-center px-6 py-20">
        {/* Neural Network Background Animation */}
        <div className="absolute inset-0 overflow-hidden pointer-events-none">
          <NeuralNode delay={0} size={8} x="10%" y="20%" />
          <NeuralNode delay={0.5} size={6} x="25%" y="35%" />
          <NeuralNode delay={1} size={10} x="40%" y="15%" />
          <NeuralNode delay={1.5} size={7} x="60%" y="25%" />
          <NeuralNode delay={2} size={9} x="75%" y="40%" />
          <NeuralNode delay={2.5} size={6} x="85%" y="20%" />
          <NeuralNode delay={0.3} size={8} x="20%" y="70%" />
          <NeuralNode delay={0.8} size={7} x="50%" y="80%" />
          <NeuralNode delay={1.3} size={9} x="70%" y="65%" />
          <NeuralNode delay={1.8} size={6} x="90%" y="75%" />

          {/* Neural Lines */}
          <svg className="absolute inset-0 w-full h-full" style={{ opacity: 0.15 }}>
            <defs>
              <linearGradient id="lineGradient" x1="0%" y1="0%" x2="100%" y2="0%">
                <stop offset="0%" stopColor="#06b6d4" />
                <stop offset="100%" stopColor="#8b5cf6" />
              </linearGradient>
            </defs>
            <motion.path
              d="M100,200 Q300,100 500,250 T900,200"
              stroke="url(#lineGradient)"
              strokeWidth="1"
              fill="none"
              initial={{ pathLength: 0 }}
              animate={{ pathLength: 1 }}
              transition={{ duration: 2, delay: 0.5 }}
            />
            <motion.path
              d="M50,400 Q250,300 450,400 T850,350"
              stroke="url(#lineGradient)"
              strokeWidth="1"
              fill="none"
              initial={{ pathLength: 0 }}
              animate={{ pathLength: 1 }}
              transition={{ duration: 2, delay: 0.8 }}
            />
            <motion.path
              d="M200,600 Q400,500 600,600 T1000,550"
              stroke="url(#lineGradient)"
              strokeWidth="1"
              fill="none"
              initial={{ pathLength: 0 }}
              animate={{ pathLength: 1 }}
              transition={{ duration: 2, delay: 1.1 }}
            />
          </svg>
        </div>

        {/* Hero Content */}
        <div className="relative z-10 max-w-5xl mx-auto text-center">
          {/* Logo/Icon */}
          <motion.div
            className="mb-8 inline-block"
            initial={{ scale: 0, rotate: -180 }}
            animate={{ scale: 1, rotate: 0 }}
            transition={{ type: 'spring', duration: 1.2, bounce: 0.4 }}
          >
            <div className="relative w-24 h-24 mx-auto">
              <div className="absolute inset-0 rounded-2xl bg-gradient-neural animate-neural-pulse" />
              <div className="absolute inset-[2px] rounded-2xl bg-[var(--nexus-void)] flex items-center justify-center">
                <svg className="w-12 h-12 text-[var(--nexus-cyan)]" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.5">
                  <circle cx="12" cy="12" r="3" />
                  <path d="M12 2v4m0 12v4M2 12h4m12 0h4" />
                  <path d="M4.93 4.93l2.83 2.83m8.48 8.48l2.83 2.83M4.93 19.07l2.83-2.83m8.48-8.48l2.83-2.83" />
                </svg>
              </div>
            </div>
          </motion.div>

          {/* Title */}
          <motion.h1
            className="text-5xl md:text-7xl font-bold mb-6 leading-tight"
            style={{ fontFamily: 'Orbitron, sans-serif' }}
            initial={{ opacity: 0, y: 30 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.8, delay: 0.3 }}
          >
            <span className="text-gradient-neural">NEXUS</span>
            <span className="text-[var(--text-primary)]"> AI</span>
          </motion.h1>

          {/* Subtitle */}
          <motion.p
            className="text-xl md:text-2xl text-[var(--text-secondary)] mb-4 max-w-2xl mx-auto"
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.8, delay: 0.5 }}
          >
            神经智能研究平台
          </motion.p>

          {/* Description */}
          <motion.p
            className="text-base md:text-lg text-[var(--text-tertiary)] mb-10 max-w-3xl mx-auto leading-relaxed"
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.8, delay: 0.7 }}
          >
            基于先进多智能体架构的AI系统，融合深度研究、数据分析与智能报告生成，
            <br className="hidden md:block" />
            为您提供前所未有的研究洞察体验
          </motion.p>

          {/* CTA Buttons */}
          <motion.div
            className="flex flex-col sm:flex-row items-center justify-center gap-4"
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.8, delay: 0.9 }}
          >
            {isAuthenticated ? (
              <>
                <Link href="/chat">
                  <button className="nexus-btn nexus-btn-primary px-8 py-4 text-base">
                    <svg className="w-5 h-5" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                      <path d="M21 15a2 2 0 0 1-2 2H7l-4 4V5a2 2 0 0 1 2-2h14a2 2 0 0 1 2 2z" />
                    </svg>
                    开始对话
                  </button>
                </Link>
                <Link href="/reports">
                  <button className="nexus-btn nexus-btn-secondary px-8 py-4 text-base">
                    <svg className="w-5 h-5" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                      <path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z" />
                      <polyline points="14 2 14 8 20 8" />
                      <line x1="16" y1="13" x2="8" y2="13" />
                      <line x1="16" y1="17" x2="8" y2="17" />
                    </svg>
                    浏览报告
                  </button>
                </Link>
              </>
            ) : (
              <>
                <Link href="/login">
                  <button className="nexus-btn nexus-btn-primary px-8 py-4 text-base">
                    <svg className="w-5 h-5" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                      <path d="M15 3h4a2 2 0 0 1 2 2v14a2 2 0 0 1-2 2h-4" />
                      <polyline points="10 17 15 12 10 7" />
                      <line x1="15" y1="12" x2="3" y2="12" />
                    </svg>
                    登录系统
                  </button>
                </Link>
                <Link href="/register">
                  <button className="nexus-btn nexus-btn-secondary px-8 py-4 text-base">
                    <svg className="w-5 h-5" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                      <path d="M16 21v-2a4 4 0 0 0-4-4H5a4 4 0 0 0-4 4v2" />
                      <circle cx="8.5" cy="7" r="4" />
                      <line x1="20" y1="8" x2="20" y2="14" />
                      <line x1="23" y1="11" x2="17" y2="11" />
                    </svg>
                    注册账号
                  </button>
                </Link>
              </>
            )}
          </motion.div>

          {/* Stats */}
          <motion.div
            className="mt-20 grid grid-cols-2 md:grid-cols-4 gap-8 max-w-3xl mx-auto"
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            transition={{ duration: 1, delay: 1.2 }}
          >
            <StatCard value="5+" delay={1.3} label="智能代理" />
            <StatCard value="∞" delay={1.4} label="研究深度" />
            <StatCard value="24/7" delay={1.5} label="全天候服务" />
            <StatCard value="<1s" delay={1.6} label="响应速度" />
          </motion.div>
        </div>

        {/* Scroll Indicator */}
        <motion.div
          className="absolute bottom-8 left-1/2 -translate-x-1/2"
          initial={{ opacity: 0 }}
          animate={{ opacity: 1, y: [0, 10, 0] }}
          transition={{
            opacity: { delay: 2 },
            y: { duration: 2, repeat: Infinity, ease: 'easeInOut' }
          }}
        >
          <div className="w-6 h-10 rounded-full border-2 border-[var(--border-default)] flex justify-center">
            <div className="w-1.5 h-3 bg-[var(--nexus-cyan)] rounded-full mt-2" />
          </div>
        </motion.div>
      </section>

      {/* Features Section */}
      <section className="relative py-24 px-6">
        <div className="max-w-6xl mx-auto">
          {/* Section Header */}
          <motion.div
            className="text-center mb-16"
            initial={{ opacity: 0, y: 20 }}
            whileInView={{ opacity: 1, y: 0 }}
            viewport={{ once: true }}
            transition={{ duration: 0.6 }}
          >
            <h2 className="text-3xl md:text-4xl font-bold mb-4" style={{ fontFamily: 'Orbitron, sans-serif' }}>
              <span className="text-gradient-neural">核心能力</span>
            </h2>
            <p className="text-[var(--text-secondary)] max-w-2xl mx-auto">
              多智能体协作架构，打造全方位智能研究体验
            </p>
          </motion.div>

          {/* Feature Cards Grid */}
          <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-6">
            <FeatureCard
              delay={0.1}
              icon={
                <svg className="w-6 h-6 text-white" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                  <circle cx="12" cy="12" r="10" />
                  <path d="M12 16v-4M12 8h.01" />
                </svg>
              }
              title="Blueprint Agent"
              description="规划执行再规划工作流，智能协调报告生成流程，确保研究任务高效完成"
            />

            <FeatureCard
              delay={0.2}
              icon={
                <svg className="w-6 h-6 text-white" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                  <path d="M12 19l7-7 3 3-7 7-3-3z" />
                  <path d="M18 13l-1.5-7.5L2 2l3.5 14.5L13 18l5-5z" />
                </svg>
              }
              title="Publisher Agent"
              description="统筹研究、章节撰写和文档组装，输出专业级研究报告"
            />

            <FeatureCard
              delay={0.3}
              icon={
                <svg className="w-6 h-6 text-white" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                  <circle cx="11" cy="11" r="8" />
                  <line x1="21" y1="21" x2="16.65" y2="16.65" />
                </svg>
              }
              title="Research Agent"
              description="深度网络搜索与信息聚合，多源数据采集确保研究全面性"
            />

            <FeatureCard
              delay={0.4}
              icon={
                <svg className="w-6 h-6 text-white" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                  <path d="M21.21 15.89A10 10 0 1 1 8 2.83" />
                  <path d="M22 12A10 10 0 0 0 12 2v10z" />
                </svg>
              }
              title="MetricVision Agent"
              description="数据智能分析引擎，洞察关键指标，可视化呈现研究发现"
            />

            <FeatureCard
              delay={0.5}
              icon={
                <svg className="w-6 h-6 text-white" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                  <path d="M2 3h6a4 4 0 0 1 4 4v14a3 3 0 0 0-3-3H2z" />
                  <path d="M22 3h-6a4 4 0 0 0-4 4v14a3 3 0 0 1 3-3h7z" />
                </svg>
              }
              title="Deep Research Agent"
              description="专注深度研究任务，挖掘复杂问题的本质与关联"
            />

            <FeatureCard
              delay={0.6}
              icon={
                <svg className="w-6 h-6 text-white" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                  <rect x="3" y="3" width="18" height="18" rx="2" ry="2" />
                  <line x1="3" y1="9" x2="21" y2="9" />
                  <line x1="9" y1="21" x2="9" y2="9" />
                </svg>
              }
              title="实时流式响应"
              description="SSE 流式架构实现实时更新，思考过程透明可见，交互体验流畅自然"
            />
          </div>
        </div>
      </section>

      {/* Architecture Section */}
      <section className="relative py-24 px-6">
        <div className="max-w-6xl mx-auto">
          <motion.div
            className="nexus-card p-8 md:p-12"
            initial={{ opacity: 0, y: 30 }}
            whileInView={{ opacity: 1, y: 0 }}
            viewport={{ once: true }}
            transition={{ duration: 0.8 }}
          >
            <div className="grid md:grid-cols-2 gap-12 items-center">
              {/* Architecture Diagram */}
              <div className="relative h-64 md:h-80">
                {/* Center Hub */}
                <motion.div
                  className="absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 w-20 h-20 rounded-2xl bg-gradient-neural flex items-center justify-center"
                  animate={{
                    boxShadow: [
                      '0 0 20px rgba(6, 182, 212, 0.3)',
                      '0 0 40px rgba(6, 182, 212, 0.5)',
                      '0 0 20px rgba(6, 182, 212, 0.3)',
                    ],
                  }}
                  transition={{ duration: 2, repeat: Infinity }}
                >
                  <svg className="w-10 h-10 text-white" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.5">
                    <circle cx="12" cy="12" r="3" />
                    <path d="M12 2v4m0 12v4M2 12h4m12 0h4" />
                  </svg>
                </motion.div>

                {/* Orbiting Nodes */}
                {ORBIT_POSITIONS.map((pos, i) => (
                  <motion.div
                    key={i}
                    className="absolute w-10 h-10 rounded-lg bg-[var(--nexus-surface)] border border-[var(--border-default)] flex items-center justify-center"
                    style={{
                      top: `calc(50% + ${pos.top}px - 20px)`,
                      left: `calc(50% + ${pos.left}px - 20px)`,
                    }}
                    initial={{ scale: 0, opacity: 0 }}
                    whileInView={{ scale: 1, opacity: 1 }}
                    viewport={{ once: true }}
                    transition={{ delay: 0.2 + i * 0.1 }}
                    whileHover={{ scale: 1.2, borderColor: 'var(--nexus-cyan)' }}
                  >
                    <div className="w-3 h-3 rounded-full bg-gradient-neural" />
                  </motion.div>
                ))}

                {/* Connecting Lines */}
                <svg className="absolute inset-0 w-full h-full pointer-events-none">
                  {ORBIT_POSITIONS.map((pos, i) => (
                    <motion.line
                      key={i}
                      x1="50%"
                      y1="50%"
                      x2={`calc(50% + ${pos.lineX}px)`}
                      y2={`calc(50% + ${pos.lineY}px)`}
                      stroke="url(#lineGradient2)"
                      strokeWidth="1"
                      strokeDasharray="4 2"
                      initial={{ opacity: 0 }}
                      whileInView={{ opacity: 0.5 }}
                      viewport={{ once: true }}
                      transition={{ delay: 0.5 + i * 0.1 }}
                    />
                  ))}
                  <defs>
                    <linearGradient id="lineGradient2" x1="0%" y1="0%" x2="100%" y2="0%">
                      <stop offset="0%" stopColor="#06b6d4" />
                      <stop offset="100%" stopColor="#8b5cf6" />
                    </linearGradient>
                  </defs>
                </svg>
              </div>

              {/* Architecture Description */}
              <div>
                <h3 className="text-2xl md:text-3xl font-bold mb-4" style={{ fontFamily: 'Orbitron, sans-serif' }}>
                  <span className="text-gradient-neural">多智能体</span>
                  <span className="text-[var(--text-primary)]"> 协作架构</span>
                </h3>
                <p className="text-[var(--text-secondary)] mb-6 leading-relaxed">
                  基于 LangGraph 构建的模块化多智能体系统，采用子图模式实现复杂任务分解。
                  支持 Plan-Execute-Replan 工作流，配备检查点机制实现工作流中断恢复。
                </p>
                <ul className="space-y-3">
                  {[
                    '智能任务协调与分配',
                    '子图模式支持复杂流程',
                    '人机协作中断恢复',
                    '实时状态追踪与更新',
                  ].map((item, i) => (
                    <motion.li
                      key={i}
                      className="flex items-center gap-3 text-[var(--text-secondary)]"
                      initial={{ opacity: 0, x: -20 }}
                      whileInView={{ opacity: 1, x: 0 }}
                      viewport={{ once: true }}
                      transition={{ delay: 0.3 + i * 0.1 }}
                    >
                      <div className="w-1.5 h-1.5 rounded-full bg-[var(--nexus-cyan)]" />
                      {item}
                    </motion.li>
                  ))}
                </ul>
              </div>
            </div>
          </motion.div>
        </div>
      </section>

      {/* CTA Section */}
      <section className="relative py-24 px-6">
        <motion.div
          className="max-w-4xl mx-auto text-center"
          initial={{ opacity: 0, y: 30 }}
          whileInView={{ opacity: 1, y: 0 }}
          viewport={{ once: true }}
          transition={{ duration: 0.8 }}
        >
          <h2 className="text-3xl md:text-4xl font-bold mb-6" style={{ fontFamily: 'Orbitron, sans-serif' }}>
            <span className="text-[var(--text-primary)]">开启您的</span>
            <span className="text-gradient-neural"> 智能研究</span>
            <span className="text-[var(--text-primary)]"> 之旅</span>
          </h2>
          <p className="text-[var(--text-secondary)] mb-10 max-w-2xl mx-auto">
            立即体验 Nexus AI 的强大功能，让人工智能成为您研究工作的得力助手
          </p>
          <Link href={isAuthenticated ? "/chat" : "/login"}>
            <motion.button
              className="nexus-btn nexus-btn-primary px-10 py-4 text-lg"
              whileHover={{ scale: 1.05 }}
              whileTap={{ scale: 0.95 }}
            >
              <svg className="w-6 h-6" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                <path d="M5 12h14M12 5l7 7-7 7" />
              </svg>
              {isAuthenticated ? '立即开始' : '登录开始'}
            </motion.button>
          </Link>
        </motion.div>
      </section>

      {/* Footer */}
      <footer className="relative py-12 px-6 border-t border-[var(--border-subtle)]">
        <div className="max-w-6xl mx-auto">
          <div className="flex flex-col md:flex-row items-center justify-between gap-6">
            <div className="flex items-center gap-3">
              <div className="w-8 h-8 rounded-lg bg-gradient-neural flex items-center justify-center">
                <svg className="w-4 h-4 text-white" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                  <circle cx="12" cy="12" r="3" />
                </svg>
              </div>
              <span className="text-[var(--text-primary)] font-semibold" style={{ fontFamily: 'Orbitron, sans-serif' }}>
                NEXUS AI
              </span>
            </div>
            <div className="text-sm text-[var(--text-tertiary)]">
              © 2024 Nexus AI. 神经智能研究平台
            </div>
            <div className="flex items-center gap-6">
              <a href="#" className="text-[var(--text-tertiary)] hover:text-[var(--nexus-cyan)] transition-colors">
                文档
              </a>
              <a href="#" className="text-[var(--text-tertiary)] hover:text-[var(--nexus-cyan)] transition-colors">
                API
              </a>
              <a href="#" className="text-[var(--text-tertiary)] hover:text-[var(--nexus-cyan)] transition-colors">
                GitHub
              </a>
            </div>
          </div>
        </div>
      </footer>
    </div>
  );
}
