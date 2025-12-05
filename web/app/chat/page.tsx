'use client';

import { useRef, useEffect, useState, useCallback } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { useChat } from './hooks/useChat';
import { useChatSessions } from './hooks/useChatSessions';
import { useModelProviders } from './hooks/useModelProviders';
import { SessionContextMenu, ContextMenuItem } from './components/SessionContextMenu';
import { RenameDialog } from './components/RenameDialog';
import { InputEnhancementsMenu, InputEnhancement } from './components/InputEnhancementsMenu';
import ChatMarkdown from './components/ChatMarkdown';
import Link from 'next/link';
import { API_ENDPOINTS } from '@/lib/config';
import { logout } from '@/lib/auth/api';
import { useRouter } from 'next/navigation';
import { useAuthStore } from '@/lib/stores/auth';
import type { ProviderType, AvailableModel, ModelProviderResponse } from '@/types/model-providers';

// ============================================
// ICON COMPONENTS
// ============================================

const NexusLogo = ({ size = 32 }: { size?: number }) => (
  <div
    className="rounded-xl bg-gradient-neural flex items-center justify-center shadow-glow-sm"
    style={{ width: size, height: size }}
  >
    <svg
      className="text-white"
      style={{ width: size * 0.6, height: size * 0.6 }}
      viewBox="0 0 24 24"
      fill="none"
      stroke="currentColor"
      strokeWidth="1.5"
    >
      <circle cx="12" cy="12" r="3" />
      <path d="M12 2v4m0 12v4M2 12h4m12 0h4" />
    </svg>
  </div>
);

const TypingIndicator = () => (
  <div className="flex items-center gap-1.5">
    {[0, 1, 2].map((i) => (
      <motion.div
        key={i}
        className="w-2 h-2 rounded-full bg-[var(--nexus-cyan)]"
        animate={{ scale: [1, 1.2, 1], opacity: [0.5, 1, 0.5] }}
        transition={{ duration: 1, repeat: Infinity, delay: i * 0.2 }}
      />
    ))}
  </div>
);

// ============================================
// THINKING BLOCK - 推理模型思考过程展示
// ============================================

interface ThinkingBlockProps {
  thinking: string;
  duration?: number;
  isThinking?: boolean;
}

const ThinkingBlock = ({ thinking, duration, isThinking }: ThinkingBlockProps) => {
  const [isExpanded, setIsExpanded] = useState(false);

  if (!thinking) return null;

  // 将思考内容按段落分割，支持 markdown 列表格式
  const formatThinkingContent = (content: string) => {
    // 处理换行和列表
    const lines = content.split('\n').filter(line => line.trim());
    return lines.map((line, index) => {
      // 检测列表项
      const isBullet = line.trim().startsWith('•') || line.trim().startsWith('-') || line.trim().startsWith('*');
      return (
        <div key={index} className={`${isBullet ? 'pl-2' : ''} mb-1.5 last:mb-0`}>
          {line}
        </div>
      );
    });
  };

  return (
    <div className="mb-3">
      {/* 思考状态标签/折叠按钮 */}
      <motion.button
        onClick={() => setIsExpanded(!isExpanded)}
        className="flex items-center gap-2 px-3 py-1.5 rounded-lg bg-[var(--nexus-violet)]/10 border border-[var(--nexus-violet)]/20 hover:bg-[var(--nexus-violet)]/15 transition-all duration-200 group"
        whileHover={{ scale: 1.01 }}
        whileTap={{ scale: 0.99 }}
      >
        {/* 思考图标 - 神经网络风格 */}
        <div className="relative">
          <svg
            className={`w-4 h-4 text-[var(--nexus-violet)] ${isThinking ? 'animate-pulse' : ''}`}
            viewBox="0 0 24 24"
            fill="none"
            stroke="currentColor"
            strokeWidth="1.5"
          >
            {/* 大脑/神经网络图标 */}
            <path d="M12 2C6.48 2 2 6.48 2 12s4.48 10 10 10 10-4.48 10-10S17.52 2 12 2z" strokeOpacity="0.3" />
            <circle cx="12" cy="8" r="1.5" fill="currentColor" />
            <circle cx="8" cy="12" r="1.5" fill="currentColor" />
            <circle cx="16" cy="12" r="1.5" fill="currentColor" />
            <circle cx="12" cy="16" r="1.5" fill="currentColor" />
            <path d="M12 8v2.5M8 12h2.5M16 12h-2.5M12 16v-2.5" strokeWidth="1" />
            <path d="M9.5 9.5l1.5 1.5M14.5 9.5l-1.5 1.5M9.5 14.5l1.5-1.5M14.5 14.5l-1.5-1.5" strokeWidth="0.75" strokeOpacity="0.6" />
          </svg>
          {/* 思考中的脉冲效果 */}
          {isThinking && (
            <motion.div
              className="absolute inset-0 rounded-full bg-[var(--nexus-violet)]"
              animate={{ scale: [1, 1.8, 1], opacity: [0.4, 0, 0.4] }}
              transition={{ duration: 1.5, repeat: Infinity }}
            />
          )}
        </div>

        {/* 状态文本 */}
        <span className="text-xs font-medium text-[var(--nexus-violet)]" style={{ fontFamily: 'Exo 2, sans-serif' }}>
          {isThinking ? '思考中...' : `已思考（用时 ${duration || 0} 秒）`}
        </span>

        {/* 展开/收起箭头 */}
        <motion.svg
          className="w-3.5 h-3.5 text-[var(--nexus-violet)]/60 group-hover:text-[var(--nexus-violet)]"
          viewBox="0 0 24 24"
          fill="none"
          stroke="currentColor"
          strokeWidth="2"
          animate={{ rotate: isExpanded ? 180 : 0 }}
          transition={{ duration: 0.2 }}
        >
          <polyline points="6 9 12 15 18 9" />
        </motion.svg>
      </motion.button>

      {/* 思考内容 - 可折叠 */}
      <AnimatePresence>
        {isExpanded && (
          <motion.div
            initial={{ opacity: 0, height: 0 }}
            animate={{ opacity: 1, height: 'auto' }}
            exit={{ opacity: 0, height: 0 }}
            transition={{ duration: 0.3, ease: 'easeInOut' }}
            className="overflow-hidden"
          >
            <div className="mt-2 pl-3 border-l-2 border-[var(--nexus-violet)]/30">
              <div className="p-3 rounded-lg bg-[var(--nexus-abyss)]/50 backdrop-blur-sm">
                <div className="text-xs text-[var(--text-tertiary)] leading-relaxed max-h-64 overflow-y-auto custom-scrollbar">
                  {formatThinkingContent(thinking)}
                </div>
              </div>
            </div>
          </motion.div>
        )}
      </AnimatePresence>
    </div>
  );
};

// ============================================
// MESSAGE ACTION TOOLBAR
// ============================================

interface MessageAction {
  icon: React.ReactNode;
  label: string;
  onClick: () => void;
}

const MessageActionBar = ({ actions }: { actions: MessageAction[] }) => (
  <div className="flex items-center gap-0.5 opacity-0 group-hover:opacity-100 transition-opacity duration-200">
    {actions.map((action, i) => (
      <motion.button
        key={i}
        onClick={action.onClick}
        className="p-1.5 rounded-md text-[var(--text-tertiary)] hover:text-[var(--text-primary)] hover:bg-[var(--nexus-surface)]/60 transition-colors"
        whileHover={{ scale: 1.1 }}
        whileTap={{ scale: 0.95 }}
        title={action.label}
      >
        <div className="w-4 h-4">{action.icon}</div>
      </motion.button>
    ))}
  </div>
);

// ============================================
// SIDEBAR SECTION COMPONENTS
// ============================================

interface SidebarSectionProps {
  title: string;
  icon?: React.ReactNode;
  children: React.ReactNode;
  defaultOpen?: boolean;
  collapsed?: boolean;
}

const SidebarSection = ({ title, icon, children, defaultOpen = true, collapsed }: SidebarSectionProps) => {
  const [isOpen, setIsOpen] = useState(defaultOpen);

  if (collapsed) return null;

  return (
    <div className="mb-1">
      <button
        onClick={() => setIsOpen(!isOpen)}
        className="w-full flex items-center gap-2 px-3 py-2 text-[11px] font-semibold text-[var(--text-tertiary)] uppercase tracking-wider hover:text-[var(--text-secondary)] transition-colors"
      >
        <motion.svg
          className="w-3 h-3"
          viewBox="0 0 24 24"
          fill="none"
          stroke="currentColor"
          strokeWidth="2"
          animate={{ rotate: isOpen ? 90 : 0 }}
          transition={{ duration: 0.2 }}
        >
          <path d="M9 18l6-6-6-6" />
        </motion.svg>
        {icon && <span className="w-4 h-4">{icon}</span>}
        <span className="flex-1 text-left">{title}</span>
      </button>
      <AnimatePresence initial={false}>
        {isOpen && (
          <motion.div
            initial={{ height: 0, opacity: 0 }}
            animate={{ height: 'auto', opacity: 1 }}
            exit={{ height: 0, opacity: 0 }}
            transition={{ duration: 0.2 }}
            className="overflow-hidden"
          >
            {children}
          </motion.div>
        )}
      </AnimatePresence>
    </div>
  );
};

// ============================================
// USER MENU COMPONENT
// ============================================

interface UserMenuProps {
  onClose: () => void;
  onOpenSettings: () => void;
  onLogout: () => void;
}

const UserMenu = ({ onClose, onOpenSettings, onLogout }: UserMenuProps) => {
  const menuItems = [
    {
      icon: (
        <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.5" className="w-5 h-5">
          <path d="M12.22 2h-.44a2 2 0 0 0-2 2v.18a2 2 0 0 1-1 1.73l-.43.25a2 2 0 0 1-2 0l-.15-.08a2 2 0 0 0-2.73.73l-.22.38a2 2 0 0 0 .73 2.73l.15.1a2 2 0 0 1 1 1.72v.51a2 2 0 0 1-1 1.74l-.15.09a2 2 0 0 0-.73 2.73l.22.38a2 2 0 0 0 2.73.73l.15-.08a2 2 0 0 1 2 0l.43.25a2 2 0 0 1 1 1.73V20a2 2 0 0 0 2 2h.44a2 2 0 0 0 2-2v-.18a2 2 0 0 1 1-1.73l.43-.25a2 2 0 0 1 2 0l.15.08a2 2 0 0 0 2.73-.73l.22-.39a2 2 0 0 0-.73-2.73l-.15-.08a2 2 0 0 1-1-1.74v-.5a2 2 0 0 1 1-1.74l.15-.09a2 2 0 0 0 .73-2.73l-.22-.38a2 2 0 0 0-2.73-.73l-.15.08a2 2 0 0 1-2 0l-.43-.25a2 2 0 0 1-1-1.73V4a2 2 0 0 0-2-2z"/>
          <circle cx="12" cy="12" r="3"/>
        </svg>
      ),
      label: '设置',
      onClick: () => { onOpenSettings(); onClose(); }
    },
    {
      icon: (
        <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.5" className="w-5 h-5">
          <path d="M19 21H5a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h11l5 5v11a2 2 0 0 1-2 2z"/>
          <polyline points="17 21 17 13 7 13 7 21"/>
          <polyline points="7 3 7 8 15 8"/>
        </svg>
      ),
      label: '已归档对话',
      onClick: () => { console.log('Archive'); onClose(); }
    },
    {
      icon: (
        <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.5" className="w-5 h-5">
          <path d="M16 18l2-2v-3"/>
          <path d="M8 18l-2-2v-3"/>
          <path d="M12 18V8"/>
          <path d="M7 8h10"/>
          <path d="M17 8V6a2 2 0 0 0-2-2H9a2 2 0 0 0-2 2v2"/>
        </svg>
      ),
      label: 'AI 对话探索区',
      onClick: () => { console.log('Playground'); onClose(); }
    },
    {
      icon: (
        <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.5" className="w-5 h-5">
          <path d="M16 21v-2a4 4 0 0 0-4-4H6a4 4 0 0 0-4 4v2"/>
          <circle cx="9" cy="7" r="4"/>
          <path d="M22 21v-2a4 4 0 0 0-3-3.87"/>
          <path d="M16 3.13a4 4 0 0 1 0 7.75"/>
        </svg>
      ),
      label: '管理员面板',
      onClick: () => { console.log('Admin'); onClose(); }
    },
  ];

  return (
    <motion.div
      initial={{ opacity: 0, y: 10, scale: 0.95 }}
      animate={{ opacity: 1, y: 0, scale: 1 }}
      exit={{ opacity: 0, y: 10, scale: 0.95 }}
      transition={{ duration: 0.15 }}
      className="absolute bottom-full left-0 mb-2 w-56 rounded-xl overflow-hidden"
      style={{
        background: 'linear-gradient(145deg, rgba(31, 41, 55, 0.98) 0%, rgba(17, 24, 39, 0.98) 100%)',
        border: '1px solid rgba(255, 255, 255, 0.08)',
        boxShadow: '0 25px 50px -12px rgba(0, 0, 0, 0.8), 0 0 30px rgba(6, 182, 212, 0.1)',
        backdropFilter: 'blur(20px)',
      }}
    >
      <div className="p-1.5">
        {menuItems.map((item, index) => (
          <motion.button
            key={index}
            onClick={item.onClick}
            className="w-full flex items-center gap-3 px-3 py-2.5 rounded-lg text-[var(--text-secondary)] hover:text-[var(--text-primary)] hover:bg-[var(--nexus-surface)]/60 transition-all duration-200 group"
            whileHover={{ x: 2 }}
            whileTap={{ scale: 0.98 }}
          >
            <span className="text-[var(--text-tertiary)] group-hover:text-[var(--nexus-cyan)] transition-colors">
              {item.icon}
            </span>
            <span className="text-sm font-medium">{item.label}</span>
          </motion.button>
        ))}
      </div>

      <div className="h-px bg-gradient-to-r from-transparent via-[var(--border-default)] to-transparent mx-3" />

      <div className="p-1.5">
        <motion.button
          onClick={() => { onLogout(); onClose(); }}
          className="w-full flex items-center gap-3 px-3 py-2.5 rounded-lg text-[var(--nexus-error)]/80 hover:text-[var(--nexus-error)] hover:bg-[var(--nexus-error)]/10 transition-all duration-200 group"
          whileHover={{ x: 2 }}
          whileTap={{ scale: 0.98 }}
        >
          <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.5" className="w-5 h-5">
            <path d="M9 21H5a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h4"/>
            <polyline points="16 17 21 12 16 7"/>
            <line x1="21" y1="12" x2="9" y2="12"/>
          </svg>
          <span className="text-sm font-medium">登出</span>
        </motion.button>
      </div>

      <div className="px-3 py-2 flex items-center gap-2 text-xs text-[var(--text-tertiary)]">
        <span className="w-2 h-2 rounded-full bg-[var(--nexus-success)] animate-pulse" />
        <span>当前在线用户: <span className="text-[var(--text-secondary)]">1</span></span>
      </div>
    </motion.div>
  );
};

// ============================================
// MODEL PROVIDER STATIC METADATA
// ============================================

/**
 * 前端静态元数据（图标、描述等）
 * 配置状态从后端 API 动态获取
 */
interface ProviderMetadata {
  id: ProviderType;
  name: string;
  description: string;
  icon: React.ReactNode;
  tags: string[];
  downloads?: number;
}

/**
 * 合并后端配置与静态元数据的富化数据
 */
interface EnrichedProvider extends ProviderMetadata {
  configured: boolean;
  hasApiKey: boolean;
  connectionStatus: 'connected' | 'failed' | 'unknown';
  configId: string | null;
  configName: string | null;
  enabledModels: AvailableModel[];
}

const PROVIDER_METADATA: ProviderMetadata[] = [
  {
    id: 'openai',
    name: 'OpenAI',
    description: 'GPT-4o, GPT-4, GPT-3.5-Turbo 等先进模型',
    icon: <svg viewBox="0 0 24 24" className="w-full h-full"><path fill="currentColor" d="M22.282 9.821a5.985 5.985 0 0 0-.516-4.91 6.046 6.046 0 0 0-6.51-2.9A6.065 6.065 0 0 0 4.981 4.18a5.985 5.985 0 0 0-3.998 2.9 6.046 6.046 0 0 0 .743 7.097 5.98 5.98 0 0 0 .51 4.911 6.051 6.051 0 0 0 6.515 2.9A5.985 5.985 0 0 0 13.26 24a6.056 6.056 0 0 0 5.772-4.206 5.99 5.99 0 0 0 3.997-2.9 6.056 6.056 0 0 0-.747-7.073zM13.26 22.43a4.476 4.476 0 0 1-2.876-1.04l.141-.081 4.779-2.758a.795.795 0 0 0 .392-.681v-6.737l2.02 1.168a.071.071 0 0 1 .038.052v5.583a4.504 4.504 0 0 1-4.494 4.494zM3.6 18.304a4.47 4.47 0 0 1-.535-3.014l.142.085 4.783 2.759a.771.771 0 0 0 .78 0l5.843-3.369v2.332a.08.08 0 0 1-.033.062L9.74 19.95a4.5 4.5 0 0 1-6.14-1.646zM2.34 7.896a4.485 4.485 0 0 1 2.366-1.973V11.6a.766.766 0 0 0 .388.676l5.815 3.355-2.02 1.168a.076.076 0 0 1-.071 0l-4.83-2.786A4.504 4.504 0 0 1 2.34 7.872zm16.597 3.855l-5.833-3.387L15.119 7.2a.076.076 0 0 1 .071 0l4.83 2.791a4.494 4.494 0 0 1-.676 8.105v-5.678a.79.79 0 0 0-.407-.667zm2.01-3.023l-.141-.085-4.774-2.782a.776.776 0 0 0-.785 0L9.409 9.23V6.897a.066.066 0 0 1 .028-.061l4.83-2.787a4.5 4.5 0 0 1 6.68 4.66zm-12.64 4.135l-2.02-1.164a.08.08 0 0 1-.038-.057V6.075a4.5 4.5 0 0 1 7.375-3.453l-.142.08L8.704 5.46a.795.795 0 0 0-.393.681zm1.097-2.365l2.602-1.5 2.607 1.5v2.999l-2.597 1.5-2.607-1.5z"/></svg>,
    tags: ['LLM', 'Embedding', 'Vision'],
    downloads: 336451,
  },
  {
    id: 'anthropic',
    name: 'Anthropic',
    description: 'Claude 3.5 Sonnet, Claude 3 Opus 等',
    icon: <svg viewBox="0 0 24 24" className="w-full h-full"><path fill="currentColor" d="M17.304 3.541h-3.672l6.696 16.918h3.672L17.304 3.541zm-10.608 0L0 20.459h3.744l1.344-3.541h6.816l1.344 3.541h3.744L10.296 3.541H6.696zm.576 10.836l2.352-6.199 2.352 6.199H7.272z"/></svg>,
    tags: ['LLM'],
    downloads: 67536,
  },
  {
    id: 'deepseek',
    name: '深度求索',
    description: 'DeepSeek-V3, DeepSeek-R1 推理模型',
    icon: <svg viewBox="0 0 24 24" className="w-full h-full"><circle cx="12" cy="12" r="10" fill="none" stroke="currentColor" strokeWidth="2"/><path fill="currentColor" d="M8 12l3 3 5-6"/></svg>,
    tags: ['LLM'],
    downloads: 244154,
  },
  {
    id: 'ollama',
    name: 'Ollama',
    description: '本地运行开源大模型',
    icon: <svg viewBox="0 0 24 24" className="w-full h-full"><ellipse cx="12" cy="12" rx="8" ry="5" fill="none" stroke="currentColor" strokeWidth="2"/><ellipse cx="12" cy="8" rx="5" ry="3" fill="none" stroke="currentColor" strokeWidth="2"/></svg>,
    tags: ['LLM', 'Embedding', 'Rerank'],
  },
  {
    id: 'gemini',
    name: 'Gemini',
    description: '谷歌 Gemini Pro, Gemini Ultra',
    icon: <svg viewBox="0 0 24 24" className="w-full h-full"><path fill="#4285F4" d="M12 2L2 7l10 5 10-5-10-5z"/><path fill="#34A853" d="M2 17l10 5 10-5M2 12l10 5 10-5"/></svg>,
    tags: ['LLM', 'Vision'],
    downloads: 139432,
  },
  {
    id: 'azure_openai',
    name: 'Azure OpenAI',
    description: 'Azure 云上的 OpenAI 服务',
    icon: <svg viewBox="0 0 24 24" className="w-full h-full"><path fill="#0078D4" d="M13.05 4.24L6.56 18.05a.5.5 0 00.46.7h5.42l-3.38 3.39a.5.5 0 00.35.86h9.09a.5.5 0 00.43-.75l-6.44-11.3 4.58-7.36a.5.5 0 00-.86-.5l-3.16 5.06V4.74a.5.5 0 00-.5-.5z"/></svg>,
    tags: ['LLM', 'Embedding'],
    downloads: 55555,
  },
  {
    id: 'amazon_bedrock',
    name: 'Amazon Bedrock',
    description: 'AWS 托管的基础模型服务',
    icon: <svg viewBox="0 0 24 24" className="w-full h-full"><path fill="#FF9900" d="M12 2L2 7v10l10 5 10-5V7L12 2zm0 2.18L19.09 7 12 9.82 4.91 7 12 4.18zM4 8.27l7 3.5v7.96l-7-3.5V8.27zm9 11.46v-7.96l7-3.5v7.96l-7 3.5z"/></svg>,
    tags: ['LLM'],
    downloads: 30598,
  },
  {
    id: 'hugging_face',
    name: 'Hugging Face',
    description: 'Hugging Face Hub 开源模型',
    icon: <svg viewBox="0 0 24 24" className="w-full h-full"><path fill="#FFD21E" d="M12 2C6.48 2 2 6.48 2 12s4.48 10 10 10 10-4.48 10-10S17.52 2 12 2zm-2 15l-1.5-1.5L10 14l-1.5-1.5L10 11l-1.5-1.5 1.5-1.5 4 4-4 4zm4 0l-4-4 4-4 1.5 1.5L14 12l1.5 1.5L14 15l1.5 1.5L14 18l-1.5-1z"/></svg>,
    tags: ['LLM', 'Embedding'],
    downloads: 27594,
  },
];

// ============================================
// API KEY MODAL COMPONENT
// ============================================

interface ApiKeyModalProps {
  isOpen: boolean;
  provider: ProviderMetadata | null;
  existingConfig?: {
    configId: string;
    configName: string | null;
    hasApiKey: boolean;
    baseUrl: string | null;
  } | null;
  onClose: () => void;
  onSave: (providerId: ProviderType, config: { name: string; apiKey: string; endpoint?: string }, configId?: string) => void;
}

const ApiKeyModal = ({ isOpen, provider, existingConfig, onClose, onSave }: ApiKeyModalProps) => {
  const [configName, setConfigName] = useState('');
  const [apiKey, setApiKey] = useState('');
  const [endpoint, setEndpoint] = useState('');

  // 编辑模式时预填充已有配置
  useEffect(() => {
    if (isOpen && existingConfig) {
      setConfigName(existingConfig.configName || '');
      setEndpoint(existingConfig.baseUrl || '');
      setApiKey(''); // API Key 不回显，保持安全
    } else if (isOpen) {
      setConfigName('');
      setApiKey('');
      setEndpoint('');
    }
  }, [isOpen, existingConfig]);

  if (!isOpen || !provider) return null;

  const isEditMode = !!existingConfig;

  const handleSave = () => {
    // 新建时必须填 API Key，编辑时可选（不填则保持原值）
    if (!isEditMode && !apiKey.trim()) return;

    onSave(
      provider.id,
      { name: configName, apiKey, endpoint },
      existingConfig?.configId
    );
    setConfigName('');
    setApiKey('');
    setEndpoint('');
    onClose();
  };

  return (
    <motion.div
      initial={{ opacity: 0 }}
      animate={{ opacity: 1 }}
      exit={{ opacity: 0 }}
      className="fixed inset-0 z-[60] flex items-center justify-center"
      onClick={onClose}
    >
      <div className="absolute inset-0 bg-black/70 backdrop-blur-sm" />

      <motion.div
        initial={{ opacity: 0, scale: 0.95, y: 20 }}
        animate={{ opacity: 1, scale: 1, y: 0 }}
        exit={{ opacity: 0, scale: 0.95, y: 20 }}
        className="relative w-full max-w-lg mx-4 rounded-2xl overflow-hidden"
        style={{
          background: 'linear-gradient(145deg, rgba(17, 24, 39, 0.99) 0%, rgba(3, 7, 18, 0.99) 100%)',
          border: '1px solid rgba(255, 255, 255, 0.1)',
          boxShadow: '0 25px 100px -20px rgba(0, 0, 0, 0.9), 0 0 80px rgba(6, 182, 212, 0.2)',
        }}
        onClick={(e) => e.stopPropagation()}
      >
        {/* Header */}
        <div className="px-6 py-5 border-b border-[var(--border-subtle)]">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-3">
              <div className="w-10 h-10 rounded-xl bg-[var(--nexus-surface)] p-2 text-[var(--nexus-cyan)]">
                {provider.icon}
              </div>
              <div>
                <h3 className="text-base font-semibold text-[var(--text-primary)]" style={{ fontFamily: 'Orbitron, sans-serif' }}>
                  {isEditMode ? '编辑模型配置' : 'API 密钥配置'}
                </h3>
                <p className="text-xs text-[var(--text-tertiary)] mt-0.5">{provider.name}</p>
              </div>
            </div>
            <motion.button
              onClick={onClose}
              className="p-2 rounded-lg text-[var(--text-tertiary)] hover:text-[var(--text-primary)] hover:bg-[var(--nexus-surface)] transition-colors"
              whileHover={{ scale: 1.05 }}
              whileTap={{ scale: 0.95 }}
            >
              <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" className="w-5 h-5">
                <path d="M18 6L6 18M6 6l12 12"/>
              </svg>
            </motion.button>
          </div>
          <p className="text-sm text-[var(--text-secondary)] mt-3">
            {isEditMode
              ? '修改现有的模型配置。如不需要更新 API Key，可留空。'
              : '配置凭据后，工作空间中的所有成员都可以在编排应用时使用此模型。'}
          </p>
        </div>

        {/* Content */}
        <div className="p-6 space-y-5">
          {/* Config Name */}
          <div>
            <label className="block text-sm font-medium text-[var(--text-primary)] mb-2">
              模型配置名称
            </label>
            <input
              type="text"
              value={configName}
              onChange={(e) => setConfigName(e.target.value)}
              placeholder="请输入配置名称，如：我的 DeepSeek 配置"
              className="w-full px-4 py-3 text-sm bg-[var(--nexus-surface)]/50 border border-[var(--border-subtle)] rounded-xl text-[var(--text-primary)] placeholder-[var(--text-tertiary)] focus:outline-none focus:border-[var(--nexus-cyan)]/50 transition-colors"
            />
          </div>

          {/* API Key */}
          <div>
            <label className="block text-sm font-medium text-[var(--text-primary)] mb-2">
              API Key {!isEditMode && <span className="text-[var(--nexus-error)]">*</span>}
              {isEditMode && <span className="text-[var(--text-tertiary)] text-xs ml-2">(留空则保持原值)</span>}
            </label>
            <div className="relative">
              <input
                type="password"
                value={apiKey}
                onChange={(e) => setApiKey(e.target.value)}
                placeholder={isEditMode ? '输入新的 API Key 或留空保持不变' : '在此输入您的 API Key'}
                className="w-full px-4 py-3 text-sm bg-[var(--nexus-surface)]/50 border border-[var(--border-subtle)] rounded-xl text-[var(--text-primary)] placeholder-[var(--text-tertiary)] focus:outline-none focus:border-[var(--nexus-cyan)]/50 transition-colors pr-12"
              />
              <button className="absolute right-3 top-1/2 -translate-y-1/2 p-1.5 rounded-md text-[var(--text-tertiary)] hover:text-[var(--text-primary)] transition-colors">
                <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" className="w-4 h-4">
                  <path d="M1 12s4-8 11-8 11 8 11 8-4 8-11 8-11-8-11-8z"/>
                  <circle cx="12" cy="12" r="3"/>
                </svg>
              </button>
            </div>
          </div>

          {/* Custom Endpoint */}
          <div>
            <label className="block text-sm font-medium text-[var(--text-primary)] mb-2">
              自定义 API endpoint 地址
            </label>
            <input
              type="text"
              value={endpoint}
              onChange={(e) => setEndpoint(e.target.value)}
              placeholder={`Base URL, e.g. https://api.${provider.id}.com/v1`}
              className="w-full px-4 py-3 text-sm bg-[var(--nexus-surface)]/50 border border-[var(--border-subtle)] rounded-xl text-[var(--text-primary)] placeholder-[var(--text-tertiary)] focus:outline-none focus:border-[var(--nexus-cyan)]/50 transition-colors"
            />
          </div>

          {/* Help Link */}
          <a
            href="#"
            className="inline-flex items-center gap-1.5 text-sm text-[var(--nexus-cyan)] hover:underline"
          >
            从 {provider.name} 获取 API Key
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" className="w-3.5 h-3.5">
              <path d="M18 13v6a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2V8a2 2 0 0 1 2-2h6"/>
              <polyline points="15 3 21 3 21 9"/>
              <line x1="10" y1="14" x2="21" y2="3"/>
            </svg>
          </a>
        </div>

        {/* Footer */}
        <div className="px-6 py-4 border-t border-[var(--border-subtle)] flex items-center justify-between">
          <div className="flex items-center gap-2 text-xs text-[var(--text-tertiary)]">
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" className="w-4 h-4">
              <rect x="3" y="11" width="18" height="11" rx="2" ry="2"/>
              <path d="M7 11V7a5 5 0 0 1 10 0v4"/>
            </svg>
            <span>您的密钥将使用 <span className="text-[var(--nexus-cyan)]">AES-256</span> 加密存储</span>
          </div>
          <div className="flex items-center gap-3">
            <motion.button
              onClick={onClose}
              className="px-5 py-2 text-sm font-medium rounded-xl text-[var(--text-secondary)] border border-[var(--border-subtle)] hover:bg-[var(--nexus-surface)] transition-colors"
              whileTap={{ scale: 0.98 }}
            >
              取消
            </motion.button>
            <motion.button
              onClick={handleSave}
              disabled={!isEditMode && !apiKey.trim()}
              className="px-5 py-2 text-sm font-medium rounded-xl text-white disabled:opacity-50 disabled:cursor-not-allowed"
              style={{
                background: 'linear-gradient(135deg, var(--nexus-cyan) 0%, var(--nexus-blue) 100%)',
                boxShadow: '0 4px 20px rgba(6, 182, 212, 0.3)',
              }}
              whileHover={{ scale: (isEditMode || apiKey.trim()) ? 1.02 : 1 }}
              whileTap={{ scale: (isEditMode || apiKey.trim()) ? 0.98 : 1 }}
            >
              {isEditMode ? '更新' : '保存'}
            </motion.button>
          </div>
        </div>
      </motion.div>
    </motion.div>
  );
};

// ============================================
// OLLAMA CONFIGURATION MODAL
// ============================================

interface OllamaModel {
  name: string;
  model: string;
  modified_at: string;
  size: number;
  digest: string;
  details?: {
    parameter_size?: string;
    quantization_level?: string;
  };
}

interface OllamaExistingConfig {
  configId: string;
  configName: string | null;
  baseUrl: string | null;
  modelName: string | null;
  modelType: string | null;
  contextLength: number | null;
}

interface OllamaConfigModalProps {
  isOpen: boolean;
  existingConfig?: OllamaExistingConfig | null;
  onClose: () => void;
  onSave: (config: {
    modelName: string;
    modelType: string;
    credentialName: string;
    baseUrl: string;
    contextLength: number;
  }, configId?: string) => void;
}

const OllamaConfigModal = ({ isOpen, existingConfig, onClose, onSave }: OllamaConfigModalProps) => {
  const [modelName, setModelName] = useState('');
  const [modelType, setModelType] = useState('');
  const [credentialName, setCredentialName] = useState('');
  const [baseUrl, setBaseUrl] = useState('http://localhost:11434');
  const [contextLength, setContextLength] = useState(4096);

  const isEditMode = !!existingConfig;
  const [localModels, setLocalModels] = useState<OllamaModel[]>([]);
  const [isLoading, setIsLoading] = useState(false);
  const [connectionStatus, setConnectionStatus] = useState<'idle' | 'connecting' | 'connected' | 'error'>('idle');
  const [errorMessage, setErrorMessage] = useState('');
  const [isDropdownOpen, setIsDropdownOpen] = useState(false);
  const [isTypeDropdownOpen, setIsTypeDropdownOpen] = useState(false);
  const dropdownRef = useRef<HTMLDivElement>(null);
  const typeDropdownRef = useRef<HTMLDivElement>(null);

  // Model type options
  const modelTypes = [
    { value: 'llm', label: 'LLM', description: '大语言模型' },
    { value: 'embedding', label: 'Text Embedding', description: '文本嵌入模型' },
    { value: 'reranker', label: 'Rerank', description: '重排序模型' },
    { value: 'speech2text', label: 'Speech to Text', description: '语音转文字' },
    { value: 'tts', label: 'TTS', description: '文字转语音' },
    { value: 'moderation', label: 'Moderation', description: '内容审核' },
  ];

  // Test connection and fetch models
  const testConnection = async () => {
    setIsLoading(true);
    setConnectionStatus('connecting');
    setErrorMessage('');

    try {
      // First test if Ollama is running
      const response = await fetch(`${baseUrl}/api/tags`, {
        method: 'GET',
        headers: { 'Content-Type': 'application/json' },
      });

      if (!response.ok) {
        throw new Error('无法连接到 Ollama 服务');
      }

      const data = await response.json();
      setLocalModels(data.models || []);
      setConnectionStatus('connected');
    } catch (error: any) {
      setConnectionStatus('error');
      setErrorMessage(error.message || '连接失败，请确保 Ollama 正在运行');
      setLocalModels([]);
    } finally {
      setIsLoading(false);
    }
  };

  // 编辑模式时预填充已有配置
  useEffect(() => {
    if (isOpen && existingConfig) {
      setModelName(existingConfig.modelName || '');
      setModelType(existingConfig.modelType || '');
      setCredentialName(existingConfig.configName || '');
      setBaseUrl(existingConfig.baseUrl || 'http://localhost:11434');
      setContextLength(existingConfig.contextLength || 4096);
    } else if (isOpen) {
      // 新建模式时重置表单
      setModelName('');
      setModelType('');
      setCredentialName('');
      setBaseUrl('http://localhost:11434');
      setContextLength(4096);
    }
  }, [isOpen, existingConfig]);

  // Auto test connection when modal opens
  useEffect(() => {
    if (isOpen) {
      testConnection();
    }
  }, [isOpen, baseUrl]);

  // Click outside handlers
  useEffect(() => {
    const handleClickOutside = (event: MouseEvent) => {
      if (dropdownRef.current && !dropdownRef.current.contains(event.target as Node)) {
        setIsDropdownOpen(false);
      }
      if (typeDropdownRef.current && !typeDropdownRef.current.contains(event.target as Node)) {
        setIsTypeDropdownOpen(false);
      }
    };
    document.addEventListener('mousedown', handleClickOutside);
    return () => document.removeEventListener('mousedown', handleClickOutside);
  }, []);

  const handleSave = () => {
    if (modelName && modelType) {
      onSave(
        { modelName, modelType, credentialName, baseUrl, contextLength },
        existingConfig?.configId
      );
      // Reset form
      setModelName('');
      setModelType('');
      setCredentialName('');
      setBaseUrl('http://localhost:11434');
      setContextLength(4096);
      onClose();
    }
  };

  const formatSize = (bytes: number) => {
    const gb = bytes / (1024 * 1024 * 1024);
    return gb >= 1 ? `${gb.toFixed(1)} GB` : `${(bytes / (1024 * 1024)).toFixed(0)} MB`;
  };

  const selectedModel = localModels.find(m => m.name === modelName);
  const selectedType = modelTypes.find(t => t.value === modelType);

  if (!isOpen) return null;

  return (
    <motion.div
      initial={{ opacity: 0 }}
      animate={{ opacity: 1 }}
      exit={{ opacity: 0 }}
      className="fixed inset-0 z-[60] flex items-center justify-center"
      onClick={onClose}
    >
      <div className="absolute inset-0 bg-black/70 backdrop-blur-sm" />

      <motion.div
        initial={{ opacity: 0, scale: 0.95, y: 20 }}
        animate={{ opacity: 1, scale: 1, y: 0 }}
        exit={{ opacity: 0, scale: 0.95, y: 20 }}
        className="relative w-full max-w-xl mx-4 rounded-2xl overflow-hidden"
        style={{
          background: 'linear-gradient(145deg, rgba(17, 24, 39, 0.99) 0%, rgba(3, 7, 18, 0.99) 100%)',
          border: '1px solid rgba(255, 255, 255, 0.1)',
          boxShadow: '0 25px 100px -20px rgba(0, 0, 0, 0.9), 0 0 80px rgba(251, 146, 60, 0.15)',
        }}
        onClick={(e) => e.stopPropagation()}
      >
        {/* Header */}
        <div className="px-6 py-5 border-b border-[var(--border-subtle)]">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-3">
              {/* Ollama Icon */}
              <div className="relative">
                <div className="w-11 h-11 rounded-xl bg-gradient-to-br from-gray-800 to-gray-900 p-2.5 flex items-center justify-center shadow-lg">
                  <svg viewBox="0 0 32 32" className="w-6 h-6">
                    <circle cx="16" cy="12" r="8" fill="white" />
                    <ellipse cx="16" cy="24" rx="12" ry="6" fill="white" />
                    <circle cx="13" cy="10" r="1.5" fill="#1a1a1a" />
                    <circle cx="19" cy="10" r="1.5" fill="#1a1a1a" />
                    <ellipse cx="16" cy="14" rx="2" ry="1" fill="#1a1a1a" />
                  </svg>
                </div>
                {/* Connection Status Indicator */}
                <motion.div
                  className={`absolute -bottom-0.5 -right-0.5 w-3.5 h-3.5 rounded-full border-2 border-[var(--nexus-deep)]`}
                  style={{
                    backgroundColor: connectionStatus === 'connected' ? '#22c55e' :
                                    connectionStatus === 'connecting' ? '#f59e0b' :
                                    connectionStatus === 'error' ? '#ef4444' : '#6b7280',
                  }}
                  animate={connectionStatus === 'connecting' ? { scale: [1, 1.2, 1] } : {}}
                  transition={{ duration: 1, repeat: connectionStatus === 'connecting' ? Infinity : 0 }}
                />
              </div>
              <div>
                <h3 className="text-base font-semibold text-[var(--text-primary)]" style={{ fontFamily: 'Orbitron, sans-serif' }}>
                  {isEditMode ? '编辑模型配置' : '添加模型'}
                </h3>
                <div className="flex items-center gap-2 mt-0.5">
                  <span className="text-xs text-[var(--text-tertiary)]">Ollama</span>
                  <span className={`text-[10px] px-1.5 py-0.5 rounded-full ${
                    connectionStatus === 'connected' ? 'bg-green-500/20 text-green-400' :
                    connectionStatus === 'connecting' ? 'bg-amber-500/20 text-amber-400' :
                    connectionStatus === 'error' ? 'bg-red-500/20 text-red-400' :
                    'bg-gray-500/20 text-gray-400'
                  }`}>
                    {connectionStatus === 'connected' ? '已连接' :
                     connectionStatus === 'connecting' ? '连接中...' :
                     connectionStatus === 'error' ? '连接失败' : '未连接'}
                  </span>
                </div>
              </div>
            </div>
            <motion.button
              onClick={onClose}
              className="p-2 rounded-lg text-[var(--text-tertiary)] hover:text-[var(--text-primary)] hover:bg-[var(--nexus-surface)] transition-colors"
              whileHover={{ scale: 1.05 }}
              whileTap={{ scale: 0.95 }}
            >
              <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" className="w-5 h-5">
                <path d="M18 6L6 18M6 6l12 12"/>
              </svg>
            </motion.button>
          </div>
        </div>

        {/* Content */}
        <div className="p-6 space-y-5 max-h-[60vh] overflow-y-auto custom-scrollbar">
          {/* Model Name - Dropdown with local models */}
          <div>
            <label className="block text-sm font-medium text-[var(--text-primary)] mb-2">
              模型名称 <span className="text-orange-400">*</span>
            </label>
            <div className="relative" ref={dropdownRef}>
              <motion.button
                type="button"
                onClick={() => connectionStatus === 'connected' && setIsDropdownOpen(!isDropdownOpen)}
                className={`w-full px-4 py-3 text-sm text-left rounded-xl transition-all flex items-center justify-between ${
                  connectionStatus !== 'connected'
                    ? 'bg-[var(--nexus-surface)]/30 border border-[var(--border-subtle)] text-[var(--text-tertiary)] cursor-not-allowed'
                    : 'bg-[var(--nexus-surface)]/50 border border-[var(--border-subtle)] text-[var(--text-primary)] hover:border-orange-500/50 cursor-pointer'
                }`}
                whileTap={connectionStatus === 'connected' ? { scale: 0.995 } : {}}
              >
                <span className={selectedModel ? 'text-[var(--text-primary)]' : 'text-[var(--text-tertiary)]'}>
                  {selectedModel ? selectedModel.name : (connectionStatus === 'connected' ? '选择本地模型' : '请先连接到 Ollama')}
                </span>
                <div className="flex items-center gap-2">
                  {selectedModel && (
                    <span className="text-[10px] px-2 py-0.5 rounded-full bg-orange-500/20 text-orange-400">
                      {formatSize(selectedModel.size)}
                    </span>
                  )}
                  <svg className={`w-4 h-4 text-[var(--text-tertiary)] transition-transform ${isDropdownOpen ? 'rotate-180' : ''}`} viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                    <path d="M6 9l6 6 6-6"/>
                  </svg>
                </div>
              </motion.button>

              <AnimatePresence>
                {isDropdownOpen && localModels.length > 0 && (
                  <motion.div
                    initial={{ opacity: 0, y: -10, scale: 0.95 }}
                    animate={{ opacity: 1, y: 0, scale: 1 }}
                    exit={{ opacity: 0, y: -10, scale: 0.95 }}
                    transition={{ duration: 0.15 }}
                    className="absolute z-50 w-full mt-2 rounded-xl overflow-hidden"
                    style={{
                      background: 'linear-gradient(145deg, rgba(31, 41, 55, 0.98) 0%, rgba(17, 24, 39, 0.98) 100%)',
                      border: '1px solid rgba(255, 255, 255, 0.1)',
                      boxShadow: '0 20px 40px rgba(0, 0, 0, 0.5)',
                    }}
                  >
                    <div className="max-h-64 overflow-y-auto custom-scrollbar py-1">
                      {localModels.map((model, idx) => (
                        <motion.button
                          key={model.name}
                          onClick={() => {
                            setModelName(model.name);
                            setIsDropdownOpen(false);
                          }}
                          className={`w-full px-4 py-3 text-left hover:bg-orange-500/10 transition-colors ${
                            modelName === model.name ? 'bg-orange-500/15' : ''
                          }`}
                          initial={{ opacity: 0, x: -10 }}
                          animate={{ opacity: 1, x: 0 }}
                          transition={{ delay: idx * 0.03 }}
                        >
                          <div className="flex items-center justify-between">
                            <div className="flex items-center gap-3">
                              <div className="w-8 h-8 rounded-lg bg-gradient-to-br from-orange-500/20 to-amber-500/20 flex items-center justify-center">
                                <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.5" className="w-4 h-4 text-orange-400">
                                  <path d="M21 16V8a2 2 0 0 0-1-1.73l-7-4a2 2 0 0 0-2 0l-7 4A2 2 0 0 0 3 8v8a2 2 0 0 0 1 1.73l7 4a2 2 0 0 0 2 0l7-4A2 2 0 0 0 21 16z"/>
                                  <polyline points="3.27 6.96 12 12.01 20.73 6.96"/>
                                  <line x1="12" y1="22.08" x2="12" y2="12"/>
                                </svg>
                              </div>
                              <div>
                                <p className="text-sm font-medium text-[var(--text-primary)]">{model.name}</p>
                                <p className="text-[10px] text-[var(--text-tertiary)]">
                                  {model.details?.parameter_size || 'Unknown'} · {model.details?.quantization_level || 'Default'}
                                </p>
                              </div>
                            </div>
                            <div className="flex items-center gap-2">
                              <span className="text-[10px] text-[var(--text-tertiary)]">{formatSize(model.size)}</span>
                              {modelName === model.name && (
                                <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" className="w-4 h-4 text-orange-400">
                                  <polyline points="20 6 9 17 4 12"/>
                                </svg>
                              )}
                            </div>
                          </div>
                        </motion.button>
                      ))}
                    </div>
                  </motion.div>
                )}
              </AnimatePresence>

              {/* Empty state or error */}
              {connectionStatus === 'connected' && localModels.length === 0 && (
                <p className="mt-2 text-xs text-amber-400">
                  未检测到本地模型。请先运行 <code className="px-1.5 py-0.5 rounded bg-[var(--nexus-surface)] text-orange-400">ollama pull &lt;model&gt;</code> 下载模型
                </p>
              )}
              {connectionStatus === 'error' && (
                <p className="mt-2 text-xs text-red-400">{errorMessage}</p>
              )}
            </div>
          </div>

          {/* Model Type Dropdown */}
          <div>
            <label className="block text-sm font-medium text-[var(--text-primary)] mb-2">
              模型类型 <span className="text-orange-400">*</span>
            </label>
            <div className="relative" ref={typeDropdownRef}>
              <motion.button
                type="button"
                onClick={() => setIsTypeDropdownOpen(!isTypeDropdownOpen)}
                className="w-full px-4 py-3 text-sm text-left rounded-xl bg-[var(--nexus-surface)]/50 border border-[var(--border-subtle)] text-[var(--text-primary)] hover:border-orange-500/50 cursor-pointer transition-all flex items-center justify-between"
                whileTap={{ scale: 0.995 }}
              >
                <span className={selectedType ? 'text-[var(--text-primary)]' : 'text-[var(--text-tertiary)]'}>
                  {selectedType ? selectedType.label : '请输入'}
                </span>
                <svg className={`w-4 h-4 text-[var(--text-tertiary)] transition-transform ${isTypeDropdownOpen ? 'rotate-180' : ''}`} viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                  <path d="M6 9l6 6 6-6"/>
                </svg>
              </motion.button>

              <AnimatePresence>
                {isTypeDropdownOpen && (
                  <motion.div
                    initial={{ opacity: 0, y: -10, scale: 0.95 }}
                    animate={{ opacity: 1, y: 0, scale: 1 }}
                    exit={{ opacity: 0, y: -10, scale: 0.95 }}
                    transition={{ duration: 0.15 }}
                    className="absolute z-50 w-full mt-2 rounded-xl overflow-hidden"
                    style={{
                      background: 'linear-gradient(145deg, rgba(31, 41, 55, 0.98) 0%, rgba(17, 24, 39, 0.98) 100%)',
                      border: '1px solid rgba(255, 255, 255, 0.1)',
                      boxShadow: '0 20px 40px rgba(0, 0, 0, 0.5)',
                    }}
                  >
                    <div className="py-1">
                      {modelTypes.map((type, idx) => (
                        <motion.button
                          key={type.value}
                          onClick={() => {
                            setModelType(type.value);
                            setIsTypeDropdownOpen(false);
                          }}
                          className={`w-full px-4 py-2.5 text-left hover:bg-orange-500/10 transition-colors ${
                            modelType === type.value ? 'bg-orange-500/15' : ''
                          }`}
                          initial={{ opacity: 0, x: -10 }}
                          animate={{ opacity: 1, x: 0 }}
                          transition={{ delay: idx * 0.03 }}
                        >
                          <div className="flex items-center justify-between">
                            <div>
                              <p className="text-sm font-medium text-[var(--text-primary)]">{type.label}</p>
                              <p className="text-[10px] text-[var(--text-tertiary)]">{type.description}</p>
                            </div>
                            {modelType === type.value && (
                              <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" className="w-4 h-4 text-orange-400">
                                <polyline points="20 6 9 17 4 12"/>
                              </svg>
                            )}
                          </div>
                        </motion.button>
                      ))}
                    </div>
                  </motion.div>
                )}
              </AnimatePresence>
            </div>
          </div>

          {/* Fieldset: Model Credentials */}
          <fieldset className="border border-[var(--border-subtle)] rounded-xl p-4">
            <legend className="px-2 text-xs font-medium text-[var(--text-tertiary)]">模型凭据</legend>

            {/* Credential Name */}
            <div className="mb-4">
              <label className="block text-sm font-medium text-[var(--text-primary)] mb-2">
                凭据名称
              </label>
              <input
                type="text"
                value={credentialName}
                onChange={(e) => setCredentialName(e.target.value)}
                placeholder="请输入"
                className="w-full px-4 py-3 text-sm bg-[var(--nexus-surface)]/50 border border-[var(--border-subtle)] rounded-xl text-[var(--text-primary)] placeholder-[var(--text-tertiary)] focus:outline-none focus:border-orange-500/50 transition-colors"
              />
            </div>

            {/* Base URL */}
            <div>
              <label className="block text-sm font-medium text-[var(--text-primary)] mb-2">
                基础 URL <span className="text-orange-400">*</span>
              </label>
              <div className="flex gap-2">
                <input
                  type="text"
                  value={baseUrl}
                  onChange={(e) => setBaseUrl(e.target.value)}
                  placeholder="Ollama server 的基础 URL，例如 http://192.168.1.100:11434"
                  className="flex-1 px-4 py-3 text-sm bg-[var(--nexus-surface)]/50 border border-[var(--border-subtle)] rounded-xl text-[var(--text-primary)] placeholder-[var(--text-tertiary)] focus:outline-none focus:border-orange-500/50 transition-colors"
                />
                <motion.button
                  onClick={testConnection}
                  disabled={isLoading}
                  className="px-4 py-3 text-sm font-medium rounded-xl border border-orange-500/50 text-orange-400 hover:bg-orange-500/10 transition-colors disabled:opacity-50"
                  whileHover={{ scale: 1.02 }}
                  whileTap={{ scale: 0.98 }}
                >
                  {isLoading ? (
                    <motion.svg className="w-4 h-4 animate-spin" viewBox="0 0 24 24" fill="none">
                      <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"/>
                      <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"/>
                    </motion.svg>
                  ) : '测试'}
                </motion.button>
              </div>
            </div>
          </fieldset>

          {/* Context Length */}
          <div>
            <label className="block text-sm font-medium text-[var(--text-primary)] mb-2">
              模型上下文长度 <span className="text-orange-400">*</span>
            </label>
            <input
              type="number"
              value={contextLength}
              onChange={(e) => setContextLength(parseInt(e.target.value) || 4096)}
              className="w-full px-4 py-3 text-sm bg-[var(--nexus-surface)]/50 border border-[var(--border-subtle)] rounded-xl text-[var(--text-primary)] placeholder-[var(--text-tertiary)] focus:outline-none focus:border-orange-500/50 transition-colors"
            />
            <p className="mt-1.5 text-[10px] text-[var(--text-tertiary)]">
              模型的最大上下文长度，通常为 4096 或 8192
            </p>
          </div>

          {/* Help Link */}
          <a
            href="https://ollama.com/library"
            target="_blank"
            rel="noopener noreferrer"
            className="inline-flex items-center gap-1.5 text-sm text-orange-400 hover:underline"
          >
            如何集成 Ollama
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" className="w-3.5 h-3.5">
              <path d="M18 13v6a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2V8a2 2 0 0 1 2-2h6"/>
              <polyline points="15 3 21 3 21 9"/>
              <line x1="10" y1="14" x2="21" y2="3"/>
            </svg>
          </a>
        </div>

        {/* Footer */}
        <div className="px-6 py-4 border-t border-[var(--border-subtle)] flex items-center justify-between">
          <div className="flex items-center gap-2 text-xs text-[var(--text-tertiary)]">
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" className="w-4 h-4">
              <rect x="3" y="11" width="18" height="11" rx="2" ry="2"/>
              <path d="M7 11V7a5 5 0 0 1 10 0v4"/>
            </svg>
            <span>您的密钥将使用 <span className="text-orange-400">PKCS1_OAEP</span> 技术进行加密和存储</span>
          </div>
          <div className="flex items-center gap-3">
            <motion.button
              onClick={onClose}
              className="px-5 py-2 text-sm font-medium rounded-xl text-[var(--text-secondary)] border border-[var(--border-subtle)] hover:bg-[var(--nexus-surface)] transition-colors"
              whileTap={{ scale: 0.98 }}
            >
              取消
            </motion.button>
            <motion.button
              onClick={handleSave}
              disabled={!modelName || !modelType}
              className="px-5 py-2 text-sm font-medium rounded-xl text-white disabled:opacity-50 disabled:cursor-not-allowed"
              style={{
                background: 'linear-gradient(135deg, #f97316 0%, #ea580c 100%)',
                boxShadow: modelName && modelType ? '0 4px 20px rgba(249, 115, 22, 0.3)' : 'none',
              }}
              whileHover={{ scale: modelName && modelType ? 1.02 : 1 }}
              whileTap={{ scale: modelName && modelType ? 0.98 : 1 }}
            >
              {isEditMode ? '更新' : '添加'}
            </motion.button>
          </div>
        </div>
      </motion.div>
    </motion.div>
  );
};

// ============================================
// MODEL PROVIDER CARD COMPONENT
// ============================================

interface ProviderCardProps {
  provider: ProviderMetadata;
  onConfigure: (provider: ProviderMetadata) => void;
  isConfigured?: boolean;
}

const ProviderCard = ({ provider, onConfigure, isConfigured }: ProviderCardProps) => {
  return (
    <motion.div
      className="group relative rounded-xl overflow-hidden cursor-pointer"
      style={{
        background: 'linear-gradient(145deg, rgba(31, 41, 55, 0.6) 0%, rgba(17, 24, 39, 0.6) 100%)',
        border: '1px solid rgba(255, 255, 255, 0.06)',
      }}
      whileHover={{
        borderColor: 'rgba(6, 182, 212, 0.3)',
        boxShadow: '0 8px 30px rgba(6, 182, 212, 0.15)',
      }}
      onClick={() => onConfigure(provider)}
    >
      {/* Glow effect on hover */}
      <div className="absolute inset-0 opacity-0 group-hover:opacity-100 transition-opacity duration-300 pointer-events-none">
        <div className="absolute inset-0 bg-gradient-to-br from-[var(--nexus-cyan)]/5 to-transparent" />
      </div>

      <div className="relative p-4">
        <div className="flex items-start gap-4">
          {/* Icon */}
          <div className="w-12 h-12 rounded-xl bg-[var(--nexus-surface)] p-2.5 text-[var(--text-secondary)] group-hover:text-[var(--nexus-cyan)] transition-colors flex-shrink-0">
            {provider.icon}
          </div>

          {/* Content */}
          <div className="flex-1 min-w-0">
            <div className="flex items-center gap-2 mb-1">
              <h4 className="text-sm font-semibold text-[var(--text-primary)]">{provider.name}</h4>
              {isConfigured && (
                <span className="px-1.5 py-0.5 text-[10px] rounded bg-[var(--nexus-success)]/20 text-[var(--nexus-success)] border border-[var(--nexus-success)]/30">
                  已配置
                </span>
              )}
            </div>
            <p className="text-xs text-[var(--text-tertiary)] line-clamp-2 mb-2">{provider.description}</p>

            {/* Tags */}
            <div className="flex flex-wrap gap-1.5">
              {provider.tags.map((tag) => (
                <span
                  key={tag}
                  className="px-2 py-0.5 text-[10px] rounded-md bg-[var(--nexus-surface)]/80 text-[var(--text-tertiary)] border border-[var(--border-subtle)]"
                >
                  {tag}
                </span>
              ))}
            </div>
          </div>

          {/* Action */}
          <motion.button
            className="flex-shrink-0 p-2 rounded-lg text-[var(--text-tertiary)] hover:text-[var(--nexus-cyan)] hover:bg-[var(--nexus-surface)] transition-colors opacity-0 group-hover:opacity-100"
            whileHover={{ scale: 1.1 }}
            whileTap={{ scale: 0.95 }}
            onClick={(e) => { e.stopPropagation(); onConfigure(provider); }}
          >
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" className="w-4 h-4">
              <path d="M12.22 2h-.44a2 2 0 0 0-2 2v.18a2 2 0 0 1-1 1.73l-.43.25a2 2 0 0 1-2 0l-.15-.08a2 2 0 0 0-2.73.73l-.22.38a2 2 0 0 0 .73 2.73l.15.1a2 2 0 0 1 1 1.72v.51a2 2 0 0 1-1 1.74l-.15.09a2 2 0 0 0-.73 2.73l.22.38a2 2 0 0 0 2.73.73l.15-.08a2 2 0 0 1 2 0l.43.25a2 2 0 0 1 1 1.73V20a2 2 0 0 0 2 2h.44a2 2 0 0 0 2-2v-.18a2 2 0 0 1 1-1.73l.43-.25a2 2 0 0 1 2 0l.15.08a2 2 0 0 0 2.73-.73l.22-.39a2 2 0 0 0-.73-2.73l-.15-.08a2 2 0 0 1-1-1.74v-.5a2 2 0 0 1 1-1.74l.15-.09a2 2 0 0 0 .73-2.73l-.22-.38a2 2 0 0 0-2.73-.73l-.15.08a2 2 0 0 1-2 0l-.43-.25a2 2 0 0 1-1-1.73V4a2 2 0 0 0-2-2z"/>
              <circle cx="12" cy="12" r="3"/>
            </svg>
          </motion.button>
        </div>

        {/* Downloads */}
        {provider.downloads && (
          <div className="flex items-center gap-1.5 mt-3 text-[10px] text-[var(--text-tertiary)]">
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" className="w-3 h-3">
              <path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4"/>
              <polyline points="7 10 12 15 17 10"/>
              <line x1="12" y1="15" x2="12" y2="3"/>
            </svg>
            <span>{provider.downloads.toLocaleString()}</span>
          </div>
        )}
      </div>
    </motion.div>
  );
};

// ============================================
// CONFIGURED PROVIDER CARD (显示已配置供应商及模型列表)
// ============================================

interface ConfiguredProviderCardProps {
  provider: EnrichedProvider;
  onEdit: (provider: EnrichedProvider) => void;  // 编辑已配置的供应商
  onTestConnection: (configId: string) => void;
}

const ConfiguredProviderCard = ({ provider, onEdit, onTestConnection }: ConfiguredProviderCardProps) => {
  const [isExpanded, setIsExpanded] = useState(false);

  const metadata = PROVIDER_METADATA.find(p => p.id === provider.id);
  if (!metadata) return null;

  // 判断是否已完成配置：有 API Key 或者是 Ollama 类型（不需要 API Key）
  const isFullyConfigured = provider.hasApiKey || provider.id === 'ollama';

  return (
    <motion.div
      className="rounded-xl overflow-hidden"
      style={{
        background: 'linear-gradient(145deg, rgba(31, 41, 55, 0.5) 0%, rgba(17, 24, 39, 0.5) 100%)',
        border: '1px solid rgba(255, 255, 255, 0.06)',
      }}
    >
      <div className="p-4">
        <div className="flex items-center justify-between mb-3">
          <div className="flex items-center gap-3">
            <div className="w-10 h-10 rounded-xl bg-[var(--nexus-surface)] p-2 text-[var(--text-secondary)]">
              {metadata.icon}
            </div>
            <div>
              <h5 className="text-sm font-semibold text-[var(--text-primary)]">{provider.configName || metadata.name}</h5>
              <div className="flex gap-1.5 mt-1">
                {metadata.tags.map((tag) => (
                  <span
                    key={tag}
                    className="px-2 py-0.5 text-[10px] rounded-md bg-[var(--nexus-surface)]/80 text-[var(--text-tertiary)] border border-[var(--border-subtle)]"
                  >
                    {tag}
                  </span>
                ))}
              </div>
            </div>
          </div>
          <div className="flex items-center gap-3">
            {/* 配置状态 */}
            <div className="flex items-center gap-2">
              {isFullyConfigured ? (
                <>
                  <span className="text-xs text-[var(--text-secondary)]">
                    {provider.configName || '已配置'}
                  </span>
                  <span className={`w-2 h-2 rounded-full ${
                    provider.connectionStatus === 'connected' ? 'bg-[var(--nexus-success)]' :
                    provider.connectionStatus === 'failed' ? 'bg-[var(--nexus-error)]' :
                    'bg-[var(--nexus-warning)]'
                  }`} />
                </>
              ) : (
                <>
                  <span className="text-xs text-[var(--text-tertiary)]">待配置</span>
                  <span className="w-2 h-2 rounded-full bg-[var(--nexus-warning)]" />
                </>
              )}
            </div>
            <motion.button
              onClick={() => onEdit(provider)}
              className="flex items-center gap-1.5 px-3 py-1.5 text-xs font-medium rounded-lg border border-[var(--border-subtle)] text-[var(--text-secondary)] hover:text-[var(--nexus-cyan)] hover:border-[var(--nexus-cyan)]/30 transition-colors"
              whileHover={{ scale: 1.02 }}
              whileTap={{ scale: 0.98 }}
            >
              <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" className="w-3.5 h-3.5">
                <path d="M12.22 2h-.44a2 2 0 0 0-2 2v.18a2 2 0 0 1-1 1.73l-.43.25a2 2 0 0 1-2 0l-.15-.08a2 2 0 0 0-2.73.73l-.22.38a2 2 0 0 0 .73 2.73l.15.1a2 2 0 0 1 1 1.72v.51a2 2 0 0 1-1 1.74l-.15.09a2 2 0 0 0-.73 2.73l.22.38a2 2 0 0 0 2.73.73l.15-.08a2 2 0 0 1 2 0l.43.25a2 2 0 0 1 1 1.73V20a2 2 0 0 0 2 2h.44"/>
                <circle cx="12" cy="12" r="3"/>
              </svg>
              {isFullyConfigured ? '编辑' : '配置'}
            </motion.button>
            {/* 展开/收起按钮 */}
            {provider.enabledModels.length > 0 && (
              <motion.button
                onClick={() => setIsExpanded(!isExpanded)}
                className="p-1.5 rounded-lg text-[var(--text-tertiary)] hover:text-[var(--text-primary)] hover:bg-[var(--nexus-surface)] transition-colors"
                whileTap={{ scale: 0.95 }}
              >
                <motion.svg
                  viewBox="0 0 24 24"
                  fill="none"
                  stroke="currentColor"
                  strokeWidth="2"
                  className="w-4 h-4"
                  animate={{ rotate: isExpanded ? 180 : 0 }}
                  transition={{ duration: 0.2 }}
                >
                  <path d="M6 9l6 6 6-6"/>
                </motion.svg>
              </motion.button>
            )}
          </div>
        </div>

        {/* 模型列表（可展开） */}
        <AnimatePresence>
          {isExpanded && provider.enabledModels.length > 0 && (
            <motion.div
              initial={{ height: 0, opacity: 0 }}
              animate={{ height: 'auto', opacity: 1 }}
              exit={{ height: 0, opacity: 0 }}
              transition={{ duration: 0.2 }}
              className="overflow-hidden"
            >
              <div className="pt-3 mt-3 border-t border-[var(--border-subtle)]">
                <div className="flex items-center gap-2 mb-2 text-xs text-[var(--text-tertiary)]">
                  <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" className="w-3.5 h-3.5">
                    <path d="M21 16V8a2 2 0 0 0-1-1.73l-7-4a2 2 0 0 0-2 0l-7 4A2 2 0 0 0 3 8v8a2 2 0 0 0 1 1.73l7 4a2 2 0 0 0 2 0l7-4A2 2 0 0 0 21 16z"/>
                  </svg>
                  <span>已启用模型 ({provider.enabledModels.length})</span>
                </div>
                <div className="space-y-1.5">
                  {provider.enabledModels.map((model) => (
                    <div
                      key={model.id}
                      className="flex items-center justify-between px-3 py-2 rounded-lg bg-[var(--nexus-surface)]/50"
                    >
                      <span className="text-xs text-[var(--text-primary)]">{model.name}</span>
                      <span className="text-[10px] text-[var(--text-tertiary)]">{model.model_type}</span>
                    </div>
                  ))}
                </div>
              </div>
            </motion.div>
          )}
        </AnimatePresence>

        {/* 未配置提示 */}
        {!isFullyConfigured && (
          <div className="flex items-center gap-2 text-xs text-[var(--nexus-info)]">
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" className="w-4 h-4">
              <circle cx="12" cy="12" r="10"/>
              <line x1="12" y1="16" x2="12" y2="12"/>
              <line x1="12" y1="8" x2="12.01" y2="8"/>
            </svg>
            <span>请配置 API 密钥，添加模型。</span>
          </div>
        )}
      </div>
    </motion.div>
  );
};

// ============================================
// MODEL PROVIDERS TAB CONTENT
// ============================================

interface ModelProvidersTabProps {
  onConfigureProvider: (provider: ProviderMetadata) => void;  // 新建配置
  onEditProvider: (provider: EnrichedProvider) => void;       // 编辑已有配置
  providers: ModelProviderResponse[];
  isLoading: boolean;
  onTestConnection: (configId: string) => void;
  getAvailableModels: (configId: string) => Promise<{ success: boolean; models: AvailableModel[] }>;
}

const ModelProvidersTab = ({
  onConfigureProvider,
  onEditProvider,
  providers,
  isLoading,
  onTestConnection,
  getAvailableModels
}: ModelProvidersTabProps) => {
  const [searchQuery, setSearchQuery] = useState('');
  const [showInstalled, setShowInstalled] = useState(true);
  const [enrichedProviders, setEnrichedProviders] = useState<EnrichedProvider[]>([]);
  const [loadingModels, setLoadingModels] = useState<Set<string>>(new Set());

  // 合并后端配置与静态元数据
  useEffect(() => {
    const enrichProviders = async () => {
      const enriched: EnrichedProvider[] = PROVIDER_METADATA.map((metadata) => {
        const config = providers.find(p => p.provider_type === metadata.id);
        return {
          ...metadata,
          configured: !!config,
          hasApiKey: config?.has_api_key ?? false,
          connectionStatus: config?.connection_status ?? 'unknown',
          configId: config?.id ?? null,
          configName: config?.name ?? null,
          enabledModels: [],
        };
      });

      // 为已配置的供应商异步加载模型列表
      for (const provider of enriched) {
        if (provider.configId && provider.hasApiKey) {
          setLoadingModels(prev => new Set(prev).add(provider.configId!));
          try {
            const result = await getAvailableModels(provider.configId);
            if (result.success) {
              provider.enabledModels = result.models.filter(m => m.is_enabled);
            }
          } catch (error) {
            console.error(`Failed to load models for ${provider.id}:`, error);
          } finally {
            setLoadingModels(prev => {
              const next = new Set(prev);
              next.delete(provider.configId!);
              return next;
            });
          }
        }
      }

      setEnrichedProviders(enriched);
    };

    enrichProviders();
  }, [providers, getAvailableModels]);

  // 分类：已配置 vs 未配置
  const configuredProviders = enrichedProviders.filter(p => p.configured);
  const availableProviders = enrichedProviders.filter(p => !p.configured);
  const filteredProviders = availableProviders.filter(p =>
    p.name.toLowerCase().includes(searchQuery.toLowerCase()) ||
    p.description.toLowerCase().includes(searchQuery.toLowerCase())
  );

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <h3 className="text-base font-semibold text-[var(--text-primary)]" style={{ fontFamily: 'Orbitron, sans-serif' }}>
          模型供应商
        </h3>
        <div className="relative w-64">
          <svg className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-[var(--text-tertiary)]" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
            <circle cx="11" cy="11" r="8"/>
            <path d="m21 21-4.35-4.35"/>
          </svg>
          <input
            type="text"
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            placeholder="搜索供应商..."
            className="w-full pl-9 pr-3 py-2 text-sm bg-[var(--nexus-surface)]/50 border border-[var(--border-subtle)] rounded-lg text-[var(--text-primary)] placeholder-[var(--text-tertiary)] focus:outline-none focus:border-[var(--nexus-cyan)]/50 transition-colors"
          />
        </div>
      </div>

      {/* Loading State */}
      {isLoading && (
        <div className="flex items-center justify-center py-8">
          <div className="flex items-center gap-3 text-[var(--text-tertiary)]">
            <motion.svg
              className="w-5 h-5"
              viewBox="0 0 24 24"
              fill="none"
              animate={{ rotate: 360 }}
              transition={{ duration: 1, repeat: Infinity, ease: 'linear' }}
            >
              <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"/>
              <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"/>
            </motion.svg>
            <span className="text-sm">加载供应商配置...</span>
          </div>
        </div>
      )}

      {/* Warning Banner */}
      {!isLoading && configuredProviders.some(p => !p.hasApiKey) && (
        <motion.div
          initial={{ opacity: 0, y: -10 }}
          animate={{ opacity: 1, y: 0 }}
          className="flex items-center gap-3 px-4 py-3 rounded-xl bg-[var(--nexus-warning)]/10 border border-[var(--nexus-warning)]/30"
        >
          <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" className="w-5 h-5 text-[var(--nexus-warning)]">
            <path d="M10.29 3.86L1.82 18a2 2 0 0 0 1.71 3h16.94a2 2 0 0 0 1.71-3L13.71 3.86a2 2 0 0 0-3.42 0z"/>
            <line x1="12" y1="9" x2="12" y2="13"/>
            <line x1="12" y1="17" x2="12.01" y2="17"/>
          </svg>
          <span className="text-sm text-[var(--nexus-warning)]">系统模型尚未完全配置</span>
          <motion.button
            className="ml-auto px-3 py-1.5 text-xs font-medium rounded-lg bg-[var(--nexus-cyan)] text-white"
            whileHover={{ scale: 1.02 }}
            whileTap={{ scale: 0.98 }}
          >
            系统模型设置
          </motion.button>
        </motion.div>
      )}

      {/* Configured Providers */}
      {!isLoading && configuredProviders.length > 0 && (
        <div className="space-y-4">
          <h4 className="text-sm font-medium text-[var(--text-secondary)]">已配置</h4>
          <div className="space-y-3">
            {configuredProviders.map((provider) => (
              <ConfiguredProviderCard
                key={provider.id}
                provider={provider}
                onEdit={onEditProvider}
                onTestConnection={onTestConnection}
              />
            ))}
          </div>
        </div>
      )}

      {/* Available Providers */}
      <div className="space-y-4">
        <div className="flex items-center justify-between">
          <button
            onClick={() => setShowInstalled(!showInstalled)}
            className="flex items-center gap-2 text-sm font-medium text-[var(--text-secondary)] hover:text-[var(--text-primary)] transition-colors"
          >
            <motion.svg
              viewBox="0 0 24 24"
              fill="none"
              stroke="currentColor"
              strokeWidth="2"
              className="w-4 h-4"
              animate={{ rotate: showInstalled ? 90 : 0 }}
              transition={{ duration: 0.2 }}
            >
              <path d="M9 18l6-6-6-6"/>
            </motion.svg>
            安装模型供应商
          </button>
          <a href="#" className="text-sm text-[var(--nexus-cyan)] hover:underline flex items-center gap-1">
            发现更多
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" className="w-3.5 h-3.5">
              <path d="M18 13v6a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2V8a2 2 0 0 1 2-2h6"/>
              <polyline points="15 3 21 3 21 9"/>
              <line x1="10" y1="14" x2="21" y2="3"/>
            </svg>
          </a>
        </div>

        <AnimatePresence>
          {showInstalled && (
            <motion.div
              initial={{ height: 0, opacity: 0 }}
              animate={{ height: 'auto', opacity: 1 }}
              exit={{ height: 0, opacity: 0 }}
              transition={{ duration: 0.3 }}
              className="overflow-hidden"
            >
              <div className="grid grid-cols-2 gap-3">
                {filteredProviders.map((provider) => (
                  <ProviderCard
                    key={provider.id}
                    provider={provider}
                    onConfigure={onConfigureProvider}
                  />
                ))}
              </div>
            </motion.div>
          )}
        </AnimatePresence>
      </div>
    </div>
  );
};

// ============================================
// SETTINGS MODAL COMPONENT
// ============================================

interface SettingsModalProps {
  isOpen: boolean;
  onClose: () => void;
  activeTab: string;
  onTabChange: (tab: string) => void;
}

const SettingsModal = ({ isOpen, onClose, activeTab, onTabChange }: SettingsModalProps) => {
  const [theme, setTheme] = useState('dark');
  const [language, setLanguage] = useState('zh-CN');
  const [notifications, setNotifications] = useState(false);
  const [systemPrompt, setSystemPrompt] = useState('');
  const [apiKeyModal, setApiKeyModal] = useState<{
    isOpen: boolean;
    provider: ProviderMetadata | null;
    existingConfig?: {
      configId: string;
      configName: string | null;
      hasApiKey: boolean;
      baseUrl: string | null;
    } | null;
  }>({
    isOpen: false,
    provider: null,
    existingConfig: null,
  });
  const [ollamaConfigModal, setOllamaConfigModal] = useState<{
    isOpen: boolean;
    existingConfig?: OllamaExistingConfig | null;
  }>({
    isOpen: false,
    existingConfig: null,
  });

  // 使用 useModelProviders hook 获取后端数据
  const {
    providers,
    isLoading: providersLoading,
    createProvider,
    updateProvider,
    createOllamaProvider,
    updateOllamaProvider,
    testSavedProvider,
    getAvailableModels,
    loadProviders,
  } = useModelProviders();

  const tabs = [
    { id: 'general', label: '通用', icon: <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.5" className="w-4 h-4"><path d="M12.22 2h-.44a2 2 0 0 0-2 2v.18a2 2 0 0 1-1 1.73l-.43.25a2 2 0 0 1-2 0l-.15-.08a2 2 0 0 0-2.73.73l-.22.38a2 2 0 0 0 .73 2.73l.15.1a2 2 0 0 1 1 1.72v.51a2 2 0 0 1-1 1.74l-.15.09a2 2 0 0 0-.73 2.73l.22.38a2 2 0 0 0 2.73.73l.15-.08a2 2 0 0 1 2 0l.43.25a2 2 0 0 1 1 1.73V20a2 2 0 0 0 2 2h.44a2 2 0 0 0 2-2v-.18a2 2 0 0 1 1-1.73l.43-.25a2 2 0 0 1 2 0l.15.08a2 2 0 0 0 2.73-.73l.22-.39a2 2 0 0 0-.73-2.73l-.15-.08a2 2 0 0 1-1-1.74v-.5a2 2 0 0 1 1-1.74l.15-.09a2 2 0 0 0 .73-2.73l-.22-.38a2 2 0 0 0-2.73-.73l-.15.08a2 2 0 0 1-2 0l-.43-.25a2 2 0 0 1-1-1.73V4a2 2 0 0 0-2-2z"/><circle cx="12" cy="12" r="3"/></svg> },
    { id: 'models', label: '模型供应商', icon: <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.5" className="w-4 h-4"><path d="M21 16V8a2 2 0 0 0-1-1.73l-7-4a2 2 0 0 0-2 0l-7 4A2 2 0 0 0 3 8v8a2 2 0 0 0 1 1.73l7 4a2 2 0 0 0 2 0l7-4A2 2 0 0 0 21 16z"/><polyline points="3.27 6.96 12 12.01 20.73 6.96"/><line x1="12" y1="22.08" x2="12" y2="12"/></svg> },
    { id: 'interface', label: '界面', icon: <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.5" className="w-4 h-4"><rect x="3" y="3" width="18" height="18" rx="2"/><path d="M3 9h18"/><path d="M9 21V9"/></svg> },
    { id: 'tools', label: '外部工具', icon: <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.5" className="w-4 h-4"><path d="M14.7 6.3a1 1 0 0 0 0 1.4l1.6 1.6a1 1 0 0 0 1.4 0l3.77-3.77a6 6 0 0 1-7.94 7.94l-6.91 6.91a2.12 2.12 0 0 1-3-3l6.91-6.91a6 6 0 0 1 7.94-7.94l-3.76 3.76z"/></svg> },
    { id: 'voice', label: '语音', icon: <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.5" className="w-4 h-4"><polygon points="11 5 6 9 2 9 2 15 6 15 11 19 11 5"/><path d="M15.54 8.46a5 5 0 0 1 0 7.07"/></svg> },
    { id: 'data', label: '数据', icon: <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.5" className="w-4 h-4"><path d="M12 2v4M12 18v4M4.93 4.93l2.83 2.83M16.24 16.24l2.83 2.83M2 12h4M18 12h4"/></svg> },
    { id: 'account', label: '账号', icon: <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.5" className="w-4 h-4"><path d="M19 21v-2a4 4 0 0 0-4-4H9a4 4 0 0 0-4 4v2"/><circle cx="12" cy="7" r="4"/></svg> },
    { id: 'about', label: '关于', icon: <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.5" className="w-4 h-4"><circle cx="12" cy="12" r="10"/><path d="M12 16v-4"/><path d="M12 8h.01"/></svg> },
  ];

  const handleConfigureProvider = (provider: ProviderMetadata) => {
    // Use specialized modal for Ollama
    if (provider.id === 'ollama') {
      setOllamaConfigModal({ isOpen: true, existingConfig: null });
    } else {
      setApiKeyModal({ isOpen: true, provider, existingConfig: null });
    }
  };

  const handleSaveApiKey = async (
    providerId: ProviderType,
    config: { name: string; apiKey: string; endpoint?: string },
    configId?: string
  ) => {
    console.log('Saving API key for:', providerId, config, 'configId:', configId);

    let result;
    if (configId) {
      // 更新已有配置
      result = await updateProvider(configId, {
        name: config.name || undefined,
        api_key: config.apiKey || undefined, // 空字符串不更新
        base_url: config.endpoint || undefined,
      });
      if (result) {
        console.log('Provider updated successfully:', result);
      } else {
        console.error('Failed to update provider');
      }
    } else {
      // 创建新配置
      result = await createProvider({
        provider_type: providerId,
        name: config.name || `${providerId}-default`,
        api_key: config.apiKey,
        base_url: config.endpoint,
        is_active: true,
      });
      if (result) {
        console.log('Provider created successfully:', result);
      } else {
        console.error('Failed to create provider');
      }
    }

    // 重新加载供应商列表
    if (result) {
      loadProviders();
    }
  };

  const handleSaveOllamaConfig = async (
    config: {
      modelName: string;
      modelType: string;
      credentialName: string;
      baseUrl: string;
      contextLength: number;
    },
    configId?: string
  ) => {
    console.log('Saving Ollama config:', config, 'configId:', configId);

    let result;
    if (configId) {
      // 更新已有配置
      result = await updateOllamaProvider(configId, {
        name: config.credentialName || undefined,
        base_url: config.baseUrl || undefined,
        model_name: config.modelName || undefined,
        model_type: config.modelType as any || undefined,
        context_length: config.contextLength || undefined,
      });
      if (result) {
        console.log('Ollama provider updated successfully:', result);
      } else {
        console.error('Failed to update Ollama provider');
      }
    } else {
      // 创建新配置
      result = await createOllamaProvider({
        name: config.credentialName || 'Ollama',
        base_url: config.baseUrl,
        model_name: config.modelName,
        model_type: config.modelType as any,
        context_length: config.contextLength,
        is_active: true,
      });
      if (result) {
        console.log('Ollama provider created successfully:', result);
      } else {
        console.error('Failed to create Ollama provider');
      }
    }

    // 重新加载供应商列表
    if (result) {
      loadProviders();
    }
  };

  // 测试已保存供应商连接
  const handleTestConnection = async (configId: string) => {
    const result = await testSavedProvider(configId);
    console.log('Connection test result:', result);
  };

  // 编辑已配置的供应商
  const handleEditProvider = (provider: EnrichedProvider) => {
    // 根据供应商类型打开对应的编辑弹窗
    const metadata = PROVIDER_METADATA.find(p => p.id === provider.id);
    if (!metadata) return;

    // 从 providers 中找到对应的后端配置信息
    const backendConfig = providers.find(p => p.id === provider.configId);

    if (provider.id === 'ollama') {
      // Ollama 使用专门的配置弹窗，并传入已有配置
      const providerConfig = backendConfig?.provider_config as Record<string, unknown> | null;
      setOllamaConfigModal({
        isOpen: true,
        existingConfig: provider.configId ? {
          configId: provider.configId,
          configName: provider.configName,
          baseUrl: backendConfig?.base_url || null,
          modelName: (providerConfig?.model_name as string) || null,
          modelType: (providerConfig?.model_type as string) || null,
          contextLength: (providerConfig?.context_length as number) || null,
        } : null,
      });
    } else {
      // 其他供应商使用 API Key 弹窗，并传入已有配置
      setApiKeyModal({
        isOpen: true,
        provider: metadata,
        existingConfig: provider.configId ? {
          configId: provider.configId,
          configName: provider.configName,
          hasApiKey: provider.hasApiKey,
          baseUrl: backendConfig?.base_url || null,
        } : null,
      });
    }
  };

  if (!isOpen) return null;

  return (
    <>
      <AnimatePresence>
        {isOpen && (
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
            className="fixed inset-0 z-50 flex items-center justify-center"
            onClick={onClose}
          >
            {/* Backdrop */}
            <div className="absolute inset-0 bg-black/60 backdrop-blur-sm" />

            {/* Modal */}
            <motion.div
              initial={{ opacity: 0, scale: 0.95, y: 20 }}
              animate={{ opacity: 1, scale: 1, y: 0 }}
              exit={{ opacity: 0, scale: 0.95, y: 20 }}
              transition={{ duration: 0.2, ease: [0.4, 0, 0.2, 1] }}
              className="relative w-full max-w-5xl h-[700px] mx-4 rounded-2xl overflow-hidden flex"
              style={{
                background: 'linear-gradient(145deg, rgba(17, 24, 39, 0.98) 0%, rgba(3, 7, 18, 0.98) 100%)',
                border: '1px solid rgba(255, 255, 255, 0.08)',
                boxShadow: '0 25px 100px -20px rgba(0, 0, 0, 0.9), 0 0 60px rgba(6, 182, 212, 0.15)',
              }}
              onClick={(e) => e.stopPropagation()}
            >
              {/* Sidebar */}
              <div className="w-56 flex flex-col border-r border-[var(--border-subtle)] bg-[var(--nexus-abyss)]/50">
                {/* Header */}
                <div className="p-5">
                  <h2 className="text-lg font-semibold text-[var(--text-primary)]" style={{ fontFamily: 'Orbitron, sans-serif' }}>
                    设置
                  </h2>
                </div>

                {/* Search */}
                <div className="px-4 pb-4">
                  <div className="relative">
                    <svg className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-[var(--text-tertiary)]" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                      <circle cx="11" cy="11" r="8"/>
                      <path d="m21 21-4.35-4.35"/>
                    </svg>
                    <input
                      type="text"
                      placeholder="搜索"
                      className="w-full pl-9 pr-3 py-2 text-sm bg-[var(--nexus-surface)]/50 border border-[var(--border-subtle)] rounded-lg text-[var(--text-primary)] placeholder-[var(--text-tertiary)] focus:outline-none focus:border-[var(--nexus-cyan)]/50 transition-colors"
                    />
                  </div>
                </div>

                {/* Tabs */}
                <nav className="flex-1 px-2 space-y-0.5 overflow-y-auto">
                  {tabs.map((tab) => (
                    <motion.button
                      key={tab.id}
                      onClick={() => onTabChange(tab.id)}
                      className={`w-full flex items-center gap-3 px-3 py-2.5 rounded-lg text-sm transition-all duration-200 ${
                        activeTab === tab.id
                          ? 'bg-[var(--nexus-surface)] text-[var(--text-primary)]'
                          : 'text-[var(--text-tertiary)] hover:text-[var(--text-secondary)] hover:bg-[var(--nexus-surface)]/30'
                      }`}
                      whileHover={{ x: 2 }}
                      whileTap={{ scale: 0.98 }}
                    >
                      <span className={activeTab === tab.id ? 'text-[var(--nexus-cyan)]' : ''}>
                        {tab.icon}
                      </span>
                      <span className="font-medium">{tab.label}</span>
                    </motion.button>
                  ))}
                </nav>

                {/* Admin Settings */}
                <div className="p-3">
                  <button className="w-full flex items-center gap-3 px-3 py-2.5 rounded-lg text-sm text-[var(--text-tertiary)] hover:text-[var(--text-secondary)] hover:bg-[var(--nexus-surface)]/30 transition-all">
                    <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.5" className="w-4 h-4">
                      <path d="M16 21v-2a4 4 0 0 0-4-4H6a4 4 0 0 0-4 4v2"/>
                      <circle cx="9" cy="7" r="4"/>
                      <path d="M22 21v-2a4 4 0 0 0-3-3.87"/>
                      <path d="M16 3.13a4 4 0 0 1 0 7.75"/>
                    </svg>
                    <span className="font-medium">管理员设置</span>
                  </button>
                </div>
              </div>

              {/* Content */}
              <div className="flex-1 flex flex-col">
                {/* Close Button */}
                <div className="absolute top-4 right-4">
                  <motion.button
                    onClick={onClose}
                    className="p-2 rounded-lg text-[var(--text-tertiary)] hover:text-[var(--text-primary)] hover:bg-[var(--nexus-surface)] transition-colors"
                    whileHover={{ scale: 1.05 }}
                    whileTap={{ scale: 0.95 }}
                  >
                    <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" className="w-5 h-5">
                      <path d="M18 6L6 18M6 6l12 12"/>
                    </svg>
                  </motion.button>
                </div>

                {/* Settings Content */}
                <div className="flex-1 p-8 overflow-y-auto">
                  {activeTab === 'general' && (
                    <div className="space-y-8">
                      <div>
                        <h3 className="text-base font-semibold text-[var(--text-primary)] mb-6" style={{ fontFamily: 'Orbitron, sans-serif' }}>
                          Nexus AI 设置
                        </h3>

                        <div className="space-y-5">
                          {/* Theme */}
                          <div className="flex items-center justify-between">
                            <span className="text-sm text-[var(--text-secondary)]">主题</span>
                            <select
                              value={theme}
                              onChange={(e) => setTheme(e.target.value)}
                              className="px-4 py-2 text-sm bg-[var(--nexus-surface)] border border-[var(--border-subtle)] rounded-lg text-[var(--text-primary)] focus:outline-none focus:border-[var(--nexus-cyan)]/50 transition-colors cursor-pointer"
                            >
                              <option value="dark">深色</option>
                              <option value="light">浅色</option>
                              <option value="system">跟随系统</option>
                            </select>
                          </div>

                          {/* Language */}
                          <div className="flex items-center justify-between">
                            <span className="text-sm text-[var(--text-secondary)]">语言</span>
                            <select
                              value={language}
                              onChange={(e) => setLanguage(e.target.value)}
                              className="px-4 py-2 text-sm bg-[var(--nexus-surface)] border border-[var(--border-subtle)] rounded-lg text-[var(--text-primary)] focus:outline-none focus:border-[var(--nexus-cyan)]/50 transition-colors cursor-pointer"
                            >
                              <option value="zh-CN">Chinese (简体中文)</option>
                              <option value="en">English</option>
                              <option value="ja">日本語</option>
                            </select>
                          </div>

                          {/* Desktop Notifications */}
                          <div className="flex items-center justify-between">
                            <span className="text-sm text-[var(--text-secondary)]">桌面通知</span>
                            <motion.button
                              onClick={() => setNotifications(!notifications)}
                              className={`px-4 py-1.5 text-sm rounded-lg border transition-all ${
                                notifications
                                  ? 'bg-[var(--nexus-cyan)]/20 border-[var(--nexus-cyan)]/30 text-[var(--nexus-cyan)]'
                                  : 'bg-[var(--nexus-surface)] border-[var(--border-subtle)] text-[var(--text-secondary)]'
                              }`}
                              whileTap={{ scale: 0.98 }}
                            >
                              {notifications ? '开启' : '关闭'}
                            </motion.button>
                          </div>
                        </div>
                      </div>

                      <div className="h-px bg-gradient-to-r from-transparent via-[var(--border-default)] to-transparent" />

                      {/* System Prompt */}
                      <div>
                        <h4 className="text-sm font-medium text-[var(--text-primary)] mb-3">系统提示词</h4>
                        <div className="relative">
                          <textarea
                            value={systemPrompt}
                            onChange={(e) => setSystemPrompt(e.target.value)}
                            placeholder="在这里输入系统提示词"
                            className="w-full h-24 px-4 py-3 text-sm bg-[var(--nexus-surface)]/50 border border-[var(--border-subtle)] rounded-xl text-[var(--text-primary)] placeholder-[var(--text-tertiary)] focus:outline-none focus:border-[var(--nexus-cyan)]/50 transition-colors resize-none"
                          />
                          <motion.button
                            className="absolute bottom-3 right-3 p-1.5 rounded-md text-[var(--text-tertiary)] hover:text-[var(--text-primary)] hover:bg-[var(--nexus-elevated)] transition-colors"
                            whileHover={{ scale: 1.1 }}
                            whileTap={{ scale: 0.95 }}
                          >
                            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" className="w-4 h-4">
                              <path d="M17 3a2.828 2.828 0 1 1 4 4L7.5 20.5 2 22l1.5-5.5L17 3z"/>
                            </svg>
                          </motion.button>
                        </div>
                      </div>

                      <div className="h-px bg-gradient-to-r from-transparent via-[var(--border-default)] to-transparent" />

                      {/* Advanced */}
                      <div>
                        <button className="flex items-center justify-between w-full text-left">
                          <span className="text-sm font-medium text-[var(--text-primary)]">高级参数</span>
                          <span className="text-sm text-[var(--nexus-cyan)] hover:underline cursor-pointer">显示</span>
                        </button>
                      </div>
                    </div>
                  )}

                  {activeTab === 'models' && (
                    <ModelProvidersTab
                      onConfigureProvider={handleConfigureProvider}
                      onEditProvider={handleEditProvider}
                      providers={providers}
                      isLoading={providersLoading}
                      onTestConnection={handleTestConnection}
                      getAvailableModels={getAvailableModels}
                    />
                  )}

                  {activeTab !== 'general' && activeTab !== 'models' && (
                    <div className="flex items-center justify-center h-full">
                      <div className="text-center">
                        <div className="w-16 h-16 mx-auto mb-4 rounded-full bg-[var(--nexus-surface)] flex items-center justify-center">
                          <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.5" className="w-8 h-8 text-[var(--text-tertiary)]">
                            <path d="M12 2v4M12 18v4M4.93 4.93l2.83 2.83M16.24 16.24l2.83 2.83M2 12h4M18 12h4"/>
                          </svg>
                        </div>
                        <p className="text-sm text-[var(--text-tertiary)]">
                          {tabs.find(t => t.id === activeTab)?.label} 设置即将推出
                        </p>
                      </div>
                    </div>
                  )}
                </div>

                {/* Footer */}
                <div className="px-8 py-4 flex justify-end">
                  <motion.button
                    onClick={onClose}
                    className="px-6 py-2.5 text-sm font-medium rounded-xl text-white"
                    style={{
                      background: 'linear-gradient(135deg, var(--nexus-cyan) 0%, var(--nexus-blue) 100%)',
                      boxShadow: '0 4px 20px rgba(6, 182, 212, 0.3)',
                    }}
                    whileHover={{ scale: 1.02, boxShadow: '0 6px 30px rgba(6, 182, 212, 0.4)' }}
                    whileTap={{ scale: 0.98 }}
                  >
                    保存
                  </motion.button>
                </div>
              </div>
            </motion.div>
          </motion.div>
        )}
      </AnimatePresence>

      {/* API Key Modal */}
      <AnimatePresence>
        {apiKeyModal.isOpen && (
          <ApiKeyModal
            isOpen={apiKeyModal.isOpen}
            provider={apiKeyModal.provider}
            existingConfig={apiKeyModal.existingConfig}
            onClose={() => setApiKeyModal({ isOpen: false, provider: null, existingConfig: null })}
            onSave={handleSaveApiKey}
          />
        )}
      </AnimatePresence>

      {/* Ollama Config Modal */}
      <AnimatePresence>
        {ollamaConfigModal.isOpen && (
          <OllamaConfigModal
            isOpen={ollamaConfigModal.isOpen}
            existingConfig={ollamaConfigModal.existingConfig}
            onClose={() => setOllamaConfigModal({ isOpen: false, existingConfig: null })}
            onSave={handleSaveOllamaConfig}
          />
        )}
      </AnimatePresence>
    </>
  );
};

// ============================================
// AGENT MODE DEFINITIONS
// ============================================

type AgentMode = 'chat' | 'research' | 'analysis' | 'report' | 'creative';

interface AgentModeConfig {
  id: AgentMode;
  label: string;
  description: string;
  icon: React.ReactNode;
  color: string;
}

// 功能模式配置（不包含默认的对话模式）
const agentModes: AgentModeConfig[] = [
  {
    id: 'research',
    label: '深度研究',
    description: '联网搜索，深度调研分析',
    icon: (
      <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.5" className="w-4 h-4">
        <circle cx="11" cy="11" r="7"/>
        <path d="m21 21-4.35-4.35"/>
        <path d="M11 8v6M8 11h6"/>
      </svg>
    ),
    color: 'var(--nexus-cyan)',
  },
  {
    id: 'analysis',
    label: '数据分析',
    description: '数据处理与可视化分析',
    icon: (
      <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.5" className="w-4 h-4">
        <path d="M3 3v18h18"/>
        <path d="M18 17V9"/>
        <path d="M13 17V5"/>
        <path d="M8 17v-3"/>
      </svg>
    ),
    color: 'var(--nexus-blue)',
  },
  {
    id: 'report',
    label: '报告生成',
    description: '专业报告与文档生成',
    icon: (
      <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.5" className="w-4 h-4">
        <path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"/>
        <polyline points="14 2 14 8 20 8"/>
        <line x1="16" y1="13" x2="8" y2="13"/>
        <line x1="16" y1="17" x2="8" y2="17"/>
      </svg>
    ),
    color: 'var(--nexus-violet)',
  },
  {
    id: 'creative',
    label: '创意激发',
    description: '头脑风暴，创意生成',
    icon: (
      <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.5" className="w-4 h-4">
        <path d="M12 2v4M12 18v4M4.93 4.93l2.83 2.83M16.24 16.24l2.83 2.83M2 12h4M18 12h4M4.93 19.07l2.83-2.83M16.24 7.76l2.83-2.83"/>
      </svg>
    ),
    color: 'var(--nexus-magenta)',
  },
];

// ============================================
// AGENT MODE SELECTOR COMPONENT
// ============================================

interface AgentModeSelectorProps {
  selectedMode: AgentMode;
  onModeChange: (mode: AgentMode) => void;
  disabled?: boolean;
}

const AgentModeSelector: React.FC<AgentModeSelectorProps> = ({ selectedMode, onModeChange, disabled }) => {
  const handleModeClick = (modeId: AgentMode) => {
    if (disabled) return;
    // 点击已选中的模式则取消选择（回到默认对话模式）
    if (selectedMode === modeId) {
      onModeChange('chat');
    } else {
      onModeChange(modeId);
    }
  };

  return (
    <div className="flex items-center justify-center gap-2 mb-3">
      {agentModes.map((mode) => {
        const isSelected = selectedMode === mode.id;
        return (
          <motion.button
            key={mode.id}
            onClick={() => handleModeClick(mode.id)}
            disabled={disabled}
            className={`
              relative flex items-center gap-1.5 px-3 py-1.5 rounded-xl text-xs font-medium
              transition-all duration-200 group
              ${isSelected
                ? 'text-white'
                : 'text-[var(--text-secondary)] hover:text-[var(--text-primary)] bg-[var(--nexus-surface)]/40 hover:bg-[var(--nexus-surface)]/70 border border-[var(--border-subtle)] hover:border-[var(--border-default)]'
              }
              ${disabled ? 'opacity-50 cursor-not-allowed' : 'cursor-pointer'}
            `}
            style={{
              background: isSelected ? `linear-gradient(135deg, ${mode.color}, ${mode.color}cc)` : undefined,
              boxShadow: isSelected ? `0 4px 16px ${mode.color}50` : undefined,
              borderColor: isSelected ? 'transparent' : undefined,
            }}
            whileHover={!disabled ? { scale: 1.03, y: -1 } : {}}
            whileTap={!disabled ? { scale: 0.97 } : {}}
            title={mode.description}
          >
            <span style={{ color: isSelected ? 'white' : mode.color }}>
              {mode.icon}
            </span>
            <span>{mode.label}</span>
          </motion.button>
        );
      })}
    </div>
  );
};

// ============================================
// MAIN CHAT PAGE COMPONENT
// ============================================

export default function ChatPage() {
  const router = useRouter();
  const user = useAuthStore((state) => state.user);
  const userId = user?.id || 'default_user';
  const [selectedChatId, setSelectedChatId] = useState<string>('');
  const [sidebarCollapsed, setSidebarCollapsed] = useState(false);

  // 登出处理
  const handleLogout = async () => {
    await logout();
    router.push('/login');
  };

  const {
    messages,
    isLoading,
    chatId,
    sendMessage,
    stopGeneration,
    clearMessages,
    switchChat
  } = useChat({
    chatId: selectedChatId,
    apiUrl: API_ENDPOINTS.chatStream,
    onError: (error) => console.error('Chat error:', error),
    onSessionCreated: () => loadSessions()
  });

  const {
    sessions,
    isLoading: sessionsLoading,
    loadSessions,
    deleteSession,
    renameSession,
    pinSession,
    archiveSession,
    cloneSession,
    downloadSession
  } = useChatSessions({
    onError: (error) => console.error('Sessions error:', error)
  });

  const chatAreaRef = useRef<HTMLDivElement>(null);
  const textareaRef = useRef<HTMLTextAreaElement>(null);
  const [inputValue, setInputValue] = useState('');
  const [contextMenu, setContextMenu] = useState<{ x: number; y: number; sessionId: string } | null>(null);
  const [renameDialog, setRenameDialog] = useState<{ sessionId: string; currentTitle: string } | null>(null);
  const [showEnhancementsMenu, setShowEnhancementsMenu] = useState(false);
  const [enhancementsMenuPosition, setEnhancementsMenuPosition] = useState({ x: 0, y: 0 });
  const [webSearchEnabled, setWebSearchEnabled] = useState(false);
  const [codeInterpreterEnabled, setCodeInterpreterEnabled] = useState(false);
  const [isRecording, setIsRecording] = useState(false);
  const mediaRecorderRef = useRef<MediaRecorder | null>(null);
  const audioChunksRef = useRef<Blob[]>([]);

  // User menu & settings state
  const [showUserMenu, setShowUserMenu] = useState(false);
  const [showSettings, setShowSettings] = useState(false);
  const [settingsTab, setSettingsTab] = useState('general');
  const userMenuRef = useRef<HTMLDivElement>(null);

  // Model selector state
  const [showModelSelector, setShowModelSelector] = useState(false);
  const [selectedModel, setSelectedModel] = useState<{ id: string; name: string; provider: string } | null>(null);
  const [availableModels, setAvailableModels] = useState<Array<{ id: string; name: string; provider: string; providerName: string; size?: string }>>([]);
  const modelSelectorRef = useRef<HTMLDivElement>(null);

  // Agent mode state
  const [agentMode, setAgentMode] = useState<AgentMode>('chat');

  // 获取已配置的模型供应商
  const { providers: configuredProviders, getAvailableModels: fetchProviderModels } = useModelProviders();

  // Auto-scroll to bottom
  useEffect(() => {
    if (chatAreaRef.current) {
      chatAreaRef.current.scrollTop = chatAreaRef.current.scrollHeight;
    }
  }, [messages]);

  // Close user menu when clicking outside
  useEffect(() => {
    const handleClickOutside = (e: MouseEvent) => {
      if (userMenuRef.current && !userMenuRef.current.contains(e.target as Node)) {
        setShowUserMenu(false);
      }
    };
    if (showUserMenu) {
      document.addEventListener('mousedown', handleClickOutside);
      return () => document.removeEventListener('mousedown', handleClickOutside);
    }
  }, [showUserMenu]);

  // Close model selector when clicking outside
  useEffect(() => {
    const handleClickOutside = (e: MouseEvent) => {
      if (modelSelectorRef.current && !modelSelectorRef.current.contains(e.target as Node)) {
        setShowModelSelector(false);
      }
    };
    if (showModelSelector) {
      document.addEventListener('mousedown', handleClickOutside);
      return () => document.removeEventListener('mousedown', handleClickOutside);
    }
  }, [showModelSelector]);

  // 加载已配置供应商的可用模型列表
  useEffect(() => {
    const loadAvailableModels = async () => {
      const models: Array<{ id: string; name: string; provider: string; providerName: string; size?: string }> = [];

      for (const provider of configuredProviders) {
        if (!provider.is_active) continue;

        // 对于 Ollama，从 provider_config 中获取模型信息
        if (provider.provider_type === 'ollama') {
          const config = provider.provider_config as Record<string, unknown> | null;
          if (config?.model_name) {
            models.push({
              id: `${provider.id}:${config.model_name}`,
              name: config.model_name as string,
              provider: provider.id,
              providerName: provider.name,
              size: undefined,
            });
          }
        } else {
          // 对于其他供应商，尝试获取模型列表
          try {
            const result = await fetchProviderModels(provider.id);
            if (result.success && result.models) {
              for (const model of result.models) {
                if (model.is_enabled) {
                  models.push({
                    id: `${provider.id}:${model.id}`,
                    name: model.name,
                    provider: provider.id,
                    providerName: provider.name,
                  });
                }
              }
            }
          } catch (error) {
            console.error(`Failed to load models for ${provider.name}:`, error);
          }
        }
      }

      setAvailableModels(models);

      // 如果没有选中的模型，选择第一个
      if (!selectedModel && models.length > 0) {
        setSelectedModel({
          id: models[0].id,
          name: models[0].name,
          provider: models[0].provider,
        });
      }
    };

    if (configuredProviders.length > 0) {
      loadAvailableModels();
    }
  }, [configuredProviders, fetchProviderModels]);

  // Input handlers
  const handleInputChange = (e: React.ChangeEvent<HTMLTextAreaElement>) => {
    setInputValue(e.target.value);
    e.target.style.height = 'auto';
    e.target.style.height = Math.min(e.target.scrollHeight, 200) + 'px';
  };

  const handleSendMessage = () => {
    const message = inputValue.trim();
    if (!message || isLoading) return;

    // 传递选中的模型配置
    sendMessage(message, {
      providerId: selectedModel?.provider,
      modelName: selectedModel?.name
    });

    setInputValue('');
    if (textareaRef.current) textareaRef.current.style.height = 'auto';
  };

  const handleKeyDown = (e: React.KeyboardEvent<HTMLTextAreaElement>) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSendMessage();
    }
  };

  // Enhancement handlers
  const handleEnhancementsClick = (e: React.MouseEvent<HTMLButtonElement>) => {
    const rect = e.currentTarget.getBoundingClientRect();
    setEnhancementsMenuPosition({ x: rect.left, y: rect.top });
    setShowEnhancementsMenu(!showEnhancementsMenu);
  };

  const getEnhancements = (): InputEnhancement[] => [
    {
      id: 'web-search',
      icon: (
        <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
          <circle cx="12" cy="12" r="10"/>
          <line x1="2" y1="12" x2="22" y2="12"/>
          <path d="M12 2a15.3 15.3 0 0 1 4 10 15.3 15.3 0 0 1-4 10 15.3 15.3 0 0 1-4-10 15.3 15.3 0 0 1 4-10z"/>
        </svg>
      ),
      label: '联网搜索',
      enabled: webSearchEnabled,
      onChange: setWebSearchEnabled
    },
    {
      id: 'code-interpreter',
      icon: (
        <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
          <rect x="3" y="3" width="18" height="18" rx="2"/>
          <path d="M9 9l-3 3 3 3M15 9l3 3-3 3"/>
        </svg>
      ),
      label: '代码解释器',
      enabled: codeInterpreterEnabled,
      onChange: setCodeInterpreterEnabled
    }
  ];

  // Recording handlers
  const startRecording = async () => {
    try {
      const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
      const mediaRecorder = new MediaRecorder(stream);
      mediaRecorderRef.current = mediaRecorder;
      audioChunksRef.current = [];
      mediaRecorder.ondataavailable = (e) => e.data.size > 0 && audioChunksRef.current.push(e.data);
      mediaRecorder.onstop = () => stream.getTracks().forEach(track => track.stop());
      mediaRecorder.start();
      setIsRecording(true);
    } catch (error) {
      console.error('无法访问麦克风:', error);
    }
  };

  const stopRecording = () => {
    if (mediaRecorderRef.current?.state !== 'inactive') {
      mediaRecorderRef.current?.stop();
      setIsRecording(false);
    }
  };

  // Chat handlers
  const handleNewChat = () => {
    setSelectedChatId('');
    clearMessages();
  };

  const handleSelectChat = (sessionId: string) => setSelectedChatId(sessionId);

  const handleDeleteChat = async (sessionId: string) => {
    if (confirm('确定要删除这个对话吗？')) {
      await deleteSession(sessionId);
      if (selectedChatId === sessionId) handleNewChat();
    }
  };

  const handleContextMenu = (e: React.MouseEvent, sessionId: string) => {
    e.preventDefault();
    setContextMenu({ x: e.clientX, y: e.clientY, sessionId });
  };

  // Message actions
  const getMessageActions = (message: any): MessageAction[] => [
    {
      icon: <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2"><path d="M11 4H4a2 2 0 0 0-2 2v14a2 2 0 0 0 2 2h14a2 2 0 0 0 2-2v-7"/><path d="M18.5 2.5a2.121 2.121 0 0 1 3 3L12 15l-4 1 1-4 9.5-9.5z"/></svg>,
      label: '编辑',
      onClick: () => console.log('Edit:', message.id)
    },
    {
      icon: <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2"><rect x="9" y="9" width="13" height="13" rx="2" ry="2"/><path d="M5 15H4a2 2 0 0 1-2-2V4a2 2 0 0 1 2-2h9a2 2 0 0 1 2 2v1"/></svg>,
      label: '复制',
      onClick: () => navigator.clipboard.writeText(message.content)
    },
    {
      icon: <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2"><polygon points="11 5 6 9 2 9 2 15 6 15 11 19 11 5"/><path d="M15.54 8.46a5 5 0 0 1 0 7.07"/><path d="M19.07 4.93a10 10 0 0 1 0 14.14"/></svg>,
      label: '朗读',
      onClick: () => {
        const utterance = new SpeechSynthesisUtterance(message.content);
        utterance.lang = 'zh-CN';
        speechSynthesis.speak(utterance);
      }
    },
    {
      icon: <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2"><path d="M14 9V5a3 3 0 0 0-3-3l-4 9v11h11.28a2 2 0 0 0 2-1.7l1.38-9a2 2 0 0 0-2-2.3zM7 22H4a2 2 0 0 1-2-2v-7a2 2 0 0 1 2-2h3"/></svg>,
      label: '有帮助',
      onClick: () => console.log('Helpful:', message.id)
    },
    {
      icon: <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2"><path d="M10 15v4a3 3 0 0 0 3 3l4-9V2H5.72a2 2 0 0 0-2 1.7l-1.38 9a2 2 0 0 0 2 2.3zm7-13h2.67A2.31 2.31 0 0 1 22 4v7a2.31 2.31 0 0 1-2.33 2H17"/></svg>,
      label: '无帮助',
      onClick: () => console.log('Not helpful:', message.id)
    },
    {
      icon: <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2"><path d="M21.5 2v6h-6M2.5 22v-6h6M2 11.5a10 10 0 0 1 18.8-4.3M22 12.5a10 10 0 0 1-18.8 4.2"/></svg>,
      label: '重新生成',
      onClick: () => console.log('Regenerate:', message.id)
    }
  ];

  // Context menu items
  const getContextMenuItems = (sessionId: string): ContextMenuItem[] => {
    const session = sessions.find(s => s.id === sessionId);
    if (!session) return [];
    return [
      { icon: <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2"><path d="M11 4H4a2 2 0 0 0-2 2v14a2 2 0 0 0 2 2h14a2 2 0 0 0 2-2v-7"/><path d="M18.5 2.5a2.121 2.121 0 0 1 3 3L12 15l-4 1 1-4 9.5-9.5z"/></svg>, label: '重命名', onClick: () => setRenameDialog({ sessionId, currentTitle: session.title || '新对话' }) },
      { icon: <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2"><path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4"/><polyline points="7 10 12 15 17 10"/><line x1="12" y1="15" x2="12" y2="3"/></svg>, label: '下载', onClick: () => downloadSession(sessionId) },
      { icon: <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2"><rect x="9" y="9" width="13" height="13" rx="2" ry="2"/><path d="M5 15H4a2 2 0 0 1-2-2V4a2 2 0 0 1 2-2h9a2 2 0 0 1 2 2v1"/></svg>, label: '复制', onClick: () => cloneSession(sessionId) },
      { icon: <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2"><path d="M19 21l-7-5-7 5V5a2 2 0 0 1 2-2h10a2 2 0 0 1 2 2z"/></svg>, label: session.pinned ? '取消置顶' : '置顶', onClick: () => pinSession(sessionId), divider: true },
      { icon: <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2"><path d="M21 8v13H3V8M1 3h22v5H1zM10 12h4"/></svg>, label: '归档', onClick: () => archiveSession(sessionId) },
      { icon: <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2"><path d="M3 6h18M19 6v14a2 2 0 0 1-2 2H7a2 2 0 0 1-2-2V6m3 0V4a2 2 0 0 1 2-2h4a2 2 0 0 1 2 2v2"/></svg>, label: '删除', onClick: () => handleDeleteChat(sessionId), danger: true, divider: true }
    ];
  };

  // Group sessions
  const groupSessionsByTime = () => {
    const grouped: { [key: string]: typeof sessions } = {};
    const pinned = sessions.filter(s => s.pinned);
    const unpinned = sessions.filter(s => !s.pinned);

    if (pinned.length > 0) grouped['已置顶'] = pinned;

    const now = new Date();
    const today = new Date(now.getFullYear(), now.getMonth(), now.getDate());

    unpinned.forEach(session => {
      const sessionDate = new Date(session.updated_at * 1000);
      const sessionDay = new Date(sessionDate.getFullYear(), sessionDate.getMonth(), sessionDate.getDate());
      const diffDays = Math.floor((today.getTime() - sessionDay.getTime()) / (1000 * 60 * 60 * 24));

      let key: string;
      if (diffDays === 0) key = '今天';
      else if (diffDays === 1) key = '昨天';
      else if (diffDays < 7) key = '过去 7 天';
      else if (diffDays < 30) key = '过去 30 天';
      else {
        const monthNames = ['一月', '二月', '三月', '四月', '五月', '六月', '七月', '八月', '九月', '十月', '十一月', '十二月'];
        key = monthNames[sessionDate.getMonth()];
      }

      if (!grouped[key]) grouped[key] = [];
      grouped[key].push(session);
    });

    return grouped;
  };

  const groupedSessions = groupSessionsByTime();

  return (
    <div className="flex h-screen overflow-hidden" suppressHydrationWarning>
      {/* ============================================ */}
      {/* SIDEBAR */}
      {/* ============================================ */}
      <motion.aside
        className="nexus-sidebar flex flex-col h-full relative"
        initial={false}
        animate={{ width: sidebarCollapsed ? 68 : 260 }}
        transition={{ duration: 0.3, ease: [0.4, 0, 0.2, 1] }}
      >
        {/* Sidebar Header */}
        <div className="px-4 py-4">
          <div className="flex items-center gap-3">
            <motion.div
              className="relative cursor-pointer flex-shrink-0"
              onClick={() => sidebarCollapsed && setSidebarCollapsed(false)}
              whileHover={{ scale: 1.05 }}
              whileTap={{ scale: 0.95 }}
            >
              <NexusLogo size={sidebarCollapsed ? 36 : 32} />
            </motion.div>
            {!sidebarCollapsed && (
              <div className="flex items-baseline gap-1.5 min-w-0">
                <span
                  className="text-lg font-bold tracking-tight"
                  style={{
                    fontFamily: 'Orbitron, sans-serif',
                    background: 'linear-gradient(135deg, var(--nexus-cyan) 0%, var(--nexus-violet) 100%)',
                    WebkitBackgroundClip: 'text',
                    WebkitTextFillColor: 'transparent',
                  }}
                >
                  NEXUS
                </span>
                <span
                  className="text-lg font-light text-[var(--text-secondary)] tracking-tight"
                  style={{ fontFamily: 'Orbitron, sans-serif' }}
                >
                  AI
                </span>
              </div>
            )}
          </div>
        </div>

        {/* Collapse Handle */}
        <motion.div
          className="absolute right-0 top-1/2 -translate-y-1/2 z-50 group"
          onClick={() => setSidebarCollapsed(!sidebarCollapsed)}
        >
          <div className="py-8 px-1 cursor-pointer">
            <motion.div className="relative flex items-center justify-center" whileHover={{ scale: 1.1 }} whileTap={{ scale: 0.95 }}>
              <motion.div className="w-1 h-10 rounded-full bg-[var(--border-subtle)] group-hover:bg-gradient-to-b group-hover:from-[var(--nexus-cyan)] group-hover:to-[var(--nexus-violet)] transition-all duration-300" />
            </motion.div>
          </div>
        </motion.div>

        {/* New Chat Button */}
        <div className="p-3">
          <motion.button
            onClick={handleNewChat}
            className={`w-full ${sidebarCollapsed ? 'nexus-btn-icon justify-center px-0' : 'nexus-btn nexus-btn-secondary'}`}
            whileHover={{ scale: 1.02 }}
            whileTap={{ scale: 0.98 }}
          >
            <svg className="w-5 h-5" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
              <path d="M12 20h9M16.5 3.5a2.121 2.121 0 0 1 3 3L7 19l-4 1 1-4L16.5 3.5z"/>
            </svg>
            {!sidebarCollapsed && <span>新对话</span>}
          </motion.button>
        </div>

        {/* Sessions List */}
        <div className={`flex-1 overflow-y-auto ${sidebarCollapsed ? 'px-2' : 'px-2'}`}>
          <AnimatePresence mode="wait">
            {sidebarCollapsed ? (
              <motion.div
                key="collapsed"
                initial={{ opacity: 0 }}
                animate={{ opacity: 1 }}
                exit={{ opacity: 0 }}
                className="flex flex-col items-center py-4 gap-4"
              >
                {/* Sessions Icon */}
                <div className="flex flex-col items-center gap-1">
                  <div className="w-10 h-10 rounded-xl bg-[var(--nexus-surface)] flex items-center justify-center" title={`${sessions.length} 个对话`}>
                    <svg className="w-5 h-5 text-[var(--text-tertiary)]" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                      <path d="M21 15a2 2 0 0 1-2 2H7l-4 4V5a2 2 0 0 1 2-2h14a2 2 0 0 1 2 2z" />
                    </svg>
                  </div>
                  <span className="text-[10px] text-[var(--text-tertiary)]">{sessions.length}</span>
                </div>

                {/* Report Center - Nexus Hexagon Button */}
                <Link href="/center">
                  <motion.div
                    className="group relative cursor-pointer"
                    whileHover={{ scale: 1.08 }}
                    whileTap={{ scale: 0.95 }}
                    title="报告中心"
                  >
                    {/* Outer Glow Ring - Breathing Animation */}
                    <motion.div
                      className="absolute inset-[-3px] rounded-xl opacity-40"
                      style={{
                        background: 'linear-gradient(135deg, var(--nexus-cyan), var(--nexus-violet))',
                        filter: 'blur(6px)',
                      }}
                      animate={{
                        opacity: [0.3, 0.5, 0.3],
                        scale: [1, 1.05, 1],
                      }}
                      transition={{
                        duration: 3,
                        repeat: Infinity,
                        ease: 'easeInOut',
                      }}
                    />
                    {/* Main Button - Hexagon-inspired shape */}
                    <div className="relative w-10 h-10 rounded-xl overflow-hidden">
                      {/* Animated Border */}
                      <div
                        className="absolute inset-0 rounded-xl p-[1px]"
                        style={{
                          background: 'linear-gradient(135deg, var(--nexus-cyan), var(--nexus-violet), var(--nexus-cyan))',
                          backgroundSize: '200% 200%',
                        }}
                      >
                        <div className="w-full h-full rounded-[10px] bg-[var(--nexus-abyss)] group-hover:bg-[var(--nexus-surface)] transition-colors duration-300 flex items-center justify-center">
                          {/* Icon with Data Flow Effect */}
                          <motion.svg
                            className="w-5 h-5 relative z-10"
                            viewBox="0 0 24 24"
                            fill="none"
                            style={{ color: 'var(--nexus-cyan)' }}
                          >
                            {/* Stacked Documents Icon */}
                            <motion.path
                              d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8l-6-6z"
                              stroke="currentColor"
                              strokeWidth="1.5"
                              strokeLinecap="round"
                              strokeLinejoin="round"
                              fill="none"
                            />
                            <motion.path
                              d="M14 2v6h6"
                              stroke="currentColor"
                              strokeWidth="1.5"
                              strokeLinecap="round"
                              strokeLinejoin="round"
                            />
                            {/* Data Lines */}
                            <motion.path
                              d="M8 13h8M8 17h5"
                              stroke="currentColor"
                              strokeWidth="1.5"
                              strokeLinecap="round"
                              initial={{ pathLength: 0, opacity: 0 }}
                              animate={{ pathLength: 1, opacity: 1 }}
                              transition={{ duration: 0.5, delay: 0.2 }}
                            />
                            {/* Spark/Generate indicator */}
                            <motion.circle
                              cx="18"
                              cy="6"
                              r="2"
                              fill="var(--nexus-violet)"
                              initial={{ scale: 0 }}
                              animate={{ scale: [0, 1.2, 1] }}
                              transition={{ duration: 0.4, delay: 0.5 }}
                            />
                          </motion.svg>
                        </div>
                      </div>
                    </div>
                  </motion.div>
                </Link>
              </motion.div>
            ) : sessionsLoading ? (
              <motion.div key="loading" className="flex items-center justify-center py-8">
                <div className="nexus-spinner w-6 h-6" />
              </motion.div>
            ) : sessions.length === 0 ? (
              <motion.div key="empty" className="text-center py-8 px-4">
                <div className="w-12 h-12 mx-auto mb-3 rounded-xl bg-[var(--nexus-surface)] flex items-center justify-center">
                  <svg className="w-6 h-6 text-[var(--text-tertiary)]" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                    <path d="M21 15a2 2 0 0 1-2 2H7l-4 4V5a2 2 0 0 1 2-2h14a2 2 0 0 1 2 2z" />
                  </svg>
                </div>
                <p className="text-sm text-[var(--text-tertiary)]">暂无对话</p>
              </motion.div>
            ) : (
              <motion.div key="sessions" initial={{ opacity: 0 }} animate={{ opacity: 1 }} exit={{ opacity: 0 }}>
                {Object.entries(groupedSessions).map(([groupKey, groupSessions]) => (
                  <SidebarSection key={groupKey} title={groupKey} defaultOpen={groupKey === '今天' || groupKey === '已置顶'}>
                    <div className="space-y-0.5 pb-2">
                      {groupSessions.map((session, idx) => (
                        <motion.div
                          key={session.id}
                          initial={{ opacity: 0, x: -10 }}
                          animate={{ opacity: 1, x: 0 }}
                          transition={{ delay: idx * 0.02 }}
                          onClick={() => handleSelectChat(session.id)}
                          onContextMenu={(e) => handleContextMenu(e, session.id)}
                          className={`group flex items-center gap-2 px-3 py-2 rounded-lg cursor-pointer transition-all duration-200 ${
                            chatId === session.id || selectedChatId === session.id
                              ? 'bg-[var(--nexus-surface)] border-l-2 border-l-[var(--nexus-cyan)]'
                              : 'hover:bg-[var(--nexus-surface)]/40 border-l-2 border-l-transparent'
                          }`}
                        >
                          {session.pinned && (
                            <svg className="w-3 h-3 text-[var(--nexus-cyan)] flex-shrink-0" viewBox="0 0 24 24" fill="currentColor">
                              <path d="M19 21l-7-5-7 5V5a2 2 0 0 1 2-2h10a2 2 0 0 1 2 2z"/>
                            </svg>
                          )}
                          <span className="flex-1 truncate text-sm text-[var(--text-secondary)] group-hover:text-[var(--text-primary)]">
                            {session.title || '新对话'}
                          </span>
                          <button
                            onClick={(e) => { e.stopPropagation(); handleContextMenu(e, session.id); }}
                            className="w-6 h-6 rounded flex items-center justify-center text-[var(--text-tertiary)] opacity-0 group-hover:opacity-100 hover:bg-[var(--nexus-elevated)] hover:text-[var(--text-primary)] transition-all"
                          >
                            <svg className="w-4 h-4" viewBox="0 0 24 24" fill="currentColor">
                              <circle cx="12" cy="12" r="1.5"/><circle cx="19" cy="12" r="1.5"/><circle cx="5" cy="12" r="1.5"/>
                            </svg>
                          </button>
                        </motion.div>
                      ))}
                    </div>
                  </SidebarSection>
                ))}
              </motion.div>
            )}
          </AnimatePresence>
        </div>

        {/* Sidebar Footer - User Info */}
        <div className="p-3 relative" ref={userMenuRef}>
          <AnimatePresence>
            {showUserMenu && (
              <UserMenu
                onClose={() => setShowUserMenu(false)}
                onOpenSettings={() => setShowSettings(true)}
                onLogout={handleLogout}
              />
            )}
          </AnimatePresence>

          <motion.button
            onClick={() => setShowUserMenu(!showUserMenu)}
            className={`w-full flex items-center gap-3 p-2 rounded-xl transition-all duration-200 ${
              showUserMenu
                ? 'bg-[var(--nexus-surface)]'
                : 'hover:bg-[var(--nexus-surface)]/50'
            } ${sidebarCollapsed ? 'justify-center' : ''}`}
            whileHover={{ scale: 1.01 }}
            whileTap={{ scale: 0.99 }}
          >
            <div className="relative flex-shrink-0">
              <div className="w-9 h-9 rounded-full bg-gradient-to-br from-[var(--nexus-cyan)] to-[var(--nexus-violet)] flex items-center justify-center text-white text-xs font-bold">
                {user?.name?.charAt(0).toUpperCase() || 'U'}
              </div>
              <span className="absolute bottom-0 right-0 w-2.5 h-2.5 rounded-full bg-[var(--nexus-success)] border-2 border-[var(--nexus-abyss)]" />
            </div>
            {!sidebarCollapsed && (
              <>
                <div className="flex-1 min-w-0 text-left">
                  <div className="text-sm font-medium text-[var(--text-primary)]">{user?.name || 'User'}</div>
                  <div className="text-xs text-[var(--nexus-success)] flex items-center gap-1">
                    在线
                  </div>
                </div>
                <motion.div
                  animate={{ rotate: showUserMenu ? 180 : 0 }}
                  transition={{ duration: 0.2 }}
                >
                  <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" className="w-4 h-4 text-[var(--text-tertiary)]">
                    <path d="m18 15-6-6-6 6"/>
                  </svg>
                </motion.div>
              </>
            )}
          </motion.button>
        </div>
      </motion.aside>

      {/* ============================================ */}
      {/* MAIN CONTENT */}
      {/* ============================================ */}
      <div className="flex-1 flex flex-col min-w-0 relative bg-[var(--nexus-void)]">
        {/* Top Bar */}
        <header className="flex items-center justify-between px-6 py-3 bg-[var(--nexus-void)]/90 backdrop-blur-sm">
          {/* Model Selector Dropdown */}
          <div className="flex items-center gap-3 relative" ref={modelSelectorRef}>
            <button
              onClick={() => setShowModelSelector(!showModelSelector)}
              className="flex items-center gap-2 px-3 py-1.5 rounded-lg hover:bg-[var(--nexus-surface)] transition-colors"
            >
              <span className="text-sm font-medium text-[var(--text-primary)]" style={{ fontFamily: 'Orbitron, sans-serif' }}>
                {selectedModel ? selectedModel.name : 'Select Model'}
              </span>
              <svg
                className={`w-4 h-4 text-[var(--text-tertiary)] transition-transform ${showModelSelector ? 'rotate-180' : ''}`}
                viewBox="0 0 24 24"
                fill="none"
                stroke="currentColor"
                strokeWidth="2"
              >
                <polyline points="6 9 12 15 18 9"/>
              </svg>
            </button>

            {/* Dropdown Menu */}
            {showModelSelector && (
              <div className="absolute top-full left-0 mt-2 w-72 bg-[var(--nexus-surface)] border border-[var(--border-subtle)] rounded-xl shadow-xl z-50 overflow-hidden">
                <div className="p-2 border-b border-[var(--border-subtle)]">
                  <span className="text-xs text-[var(--text-tertiary)] px-2">选择模型</span>
                </div>
                <div className="max-h-64 overflow-y-auto">
                  {availableModels.length === 0 ? (
                    <div className="p-4 text-center text-sm text-[var(--text-tertiary)]">
                      暂无可用模型，请先配置模型供应商
                    </div>
                  ) : (
                    availableModels.map((model) => (
                      <button
                        key={model.id}
                        onClick={() => {
                          setSelectedModel({ id: model.id, name: model.name, provider: model.provider });
                          setShowModelSelector(false);
                        }}
                        className={`w-full flex items-center gap-3 px-3 py-2.5 hover:bg-[var(--nexus-void)] transition-colors text-left ${
                          selectedModel?.id === model.id ? 'bg-[var(--nexus-void)]' : ''
                        }`}
                      >
                        <div className="flex-1 min-w-0">
                          <div className="text-sm font-medium text-[var(--text-primary)] truncate">
                            {model.name}
                          </div>
                          <div className="text-xs text-[var(--text-tertiary)] truncate">
                            {model.providerName}{model.size ? ` · ${model.size}` : ''}
                          </div>
                        </div>
                        {selectedModel?.id === model.id && (
                          <svg className="w-4 h-4 text-[var(--nexus-accent-primary)]" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                            <polyline points="20 6 9 17 4 12"/>
                          </svg>
                        )}
                      </button>
                    ))
                  )}
                </div>
              </div>
            )}
          </div>
          <div className="flex items-center gap-2">
            <button onClick={loadSessions} className="nexus-btn-icon" title="刷新">
              <svg className="w-4 h-4" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                <path d="M21.5 2v6h-6M2.5 22v-6h6M2 11.5a10 10 0 0 1 18.8-4.3M22 12.5a10 10 0 0 1-18.8 4.2"/>
              </svg>
            </button>
            <button className="nexus-btn-icon">
              <svg className="w-4 h-4" viewBox="0 0 24 24" fill="currentColor">
                <circle cx="12" cy="12" r="1.5"/><circle cx="19" cy="12" r="1.5"/><circle cx="5" cy="12" r="1.5"/>
              </svg>
            </button>
          </div>
        </header>

        {/* Chat Area */}
        <div ref={chatAreaRef} className="flex-1 overflow-y-auto">
          {messages.length === 0 ? (
            /* Empty State - 简化版，主要引导用户选择下方的模式 */
            <div className="flex flex-col items-center justify-center h-full px-6">
              {(() => {
                const currentMode = agentModes.find(m => m.id === agentMode);
                const isDefaultChat = agentMode === 'chat';
                const displayColor = currentMode?.color || 'var(--nexus-cyan)';
                const displayLabel = currentMode?.label || '智能对话';
                const displayDesc = currentMode?.description || '多智能体AI助手，支持深度研究、数据分析与智能报告生成';
                const displayIcon = currentMode?.icon || (
                  <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.5" className="w-4 h-4">
                    <path d="M21 15a2 2 0 0 1-2 2H7l-4 4V5a2 2 0 0 1 2-2h14a2 2 0 0 1 2 2z"/>
                  </svg>
                );

                return (
                  <>
                    <motion.div
                      key={agentMode}
                      initial={{ scale: 0.8, opacity: 0 }}
                      animate={{ scale: 1, opacity: 1 }}
                      transition={{ type: 'spring', duration: 0.5 }}
                      className="mb-6"
                    >
                      <div
                        className="w-16 h-16 rounded-2xl flex items-center justify-center transition-all duration-300"
                        style={{
                          background: `linear-gradient(135deg, ${displayColor}, ${displayColor}99)`,
                          boxShadow: `0 8px 32px ${displayColor}40`
                        }}
                      >
                        <span className="text-white scale-[2]">
                          {displayIcon}
                        </span>
                      </div>
                    </motion.div>

                    <motion.h2
                      key={`title-${agentMode}`}
                      className="text-2xl font-bold mb-2"
                      style={{ fontFamily: 'Orbitron, sans-serif' }}
                      initial={{ opacity: 0, y: 10 }}
                      animate={{ opacity: 1, y: 0 }}
                      transition={{ delay: 0.1 }}
                    >
                      开启 <span className="text-gradient-neural">{displayLabel}</span>
                    </motion.h2>

                    <motion.p
                      key={`desc-${agentMode}`}
                      className="text-[var(--text-secondary)] text-center max-w-md mb-4 text-sm"
                      initial={{ opacity: 0, y: 10 }}
                      animate={{ opacity: 1, y: 0 }}
                      transition={{ delay: 0.2 }}
                    >
                      {displayDesc}
                    </motion.p>

                    <motion.p
                      className="text-[var(--text-tertiary)] text-center text-xs"
                      initial={{ opacity: 0 }}
                      animate={{ opacity: 1 }}
                      transition={{ delay: 0.4 }}
                    >
                      {isDefaultChat ? '选择下方功能模式，或直接开始对话' : '点击已选模式可取消，回到普通对话'}
                    </motion.p>
                  </>
                );
              })()}
            </div>
          ) : (
            /* Messages */
            <div className="max-w-3xl mx-auto px-6 py-6 space-y-6">
              <AnimatePresence>
                {messages.map((message) => (
                  <motion.div
                    key={message.id}
                    initial={{ opacity: 0, y: 20 }}
                    animate={{ opacity: 1, y: 0 }}
                    exit={{ opacity: 0, y: -20 }}
                    transition={{ duration: 0.3 }}
                    className="group"
                  >
                    {message.type === 'user' ? (
                      /* User Message */
                      <div className="flex justify-end">
                        <div className="max-w-[85%] px-4 py-3 rounded-2xl rounded-br-sm bg-gradient-neural text-white">
                          <p className="text-sm whitespace-pre-wrap leading-relaxed">{message.content}</p>
                        </div>
                      </div>
                    ) : (
                      /* AI Message */
                      <div className="flex gap-3">
                        <div className="flex-shrink-0 mt-1">
                          <NexusLogo size={28} />
                        </div>
                        <div className="flex-1 min-w-0">
                          <div className="flex items-center gap-2 mb-1.5">
                            <span className="text-xs font-semibold text-[var(--text-tertiary)]" style={{ fontFamily: 'Orbitron, sans-serif' }}>
                              nexus-ai
                            </span>
                            {message.loading && !message.isThinking && !message.thinking && (
                              <span className="text-[10px] text-[var(--nexus-cyan)] animate-pulse">生成中...</span>
                            )}
                          </div>

                          {/* 思考过程展示 */}
                          {message.thinking && (
                            <ThinkingBlock
                              thinking={message.thinking}
                              duration={message.thinkingDuration}
                              isThinking={message.isThinking}
                            />
                          )}

                          {message.loading && !message.content && !message.thinking ? (
                            <div className="space-y-3">
                              <TypingIndicator />
                            </div>
                          ) : (
                            <>
                              {message.content && (
                                <ChatMarkdown
                                  content={message.content}
                                  isStreaming={message.loading}
                                />
                              )}
                              {/* Action Bar - 只在非加载状态显示 */}
                              {!message.loading && message.content && (
                                <div className="mt-3">
                                  <MessageActionBar actions={getMessageActions(message)} />
                                </div>
                              )}
                            </>
                          )}
                        </div>
                      </div>
                    )}
                  </motion.div>
                ))}
              </AnimatePresence>
            </div>
          )}
        </div>

        {/* Input Area */}
        <div className="px-6 py-4 bg-gradient-to-t from-[var(--nexus-void)] via-[var(--nexus-void)]/95 to-transparent">
          <div className="max-w-3xl mx-auto">
            {/* Agent Mode Selector - 放在输入框上方 */}
            <AgentModeSelector
              selectedMode={agentMode}
              onModeChange={setAgentMode}
              disabled={isLoading}
            />

            <div className="nexus-card p-3 rounded-2xl shadow-lg">
              <textarea
                ref={textareaRef}
                value={inputValue}
                onChange={handleInputChange}
                onKeyDown={handleKeyDown}
                placeholder={agentMode === 'chat' ? '输入消息...' : `输入${agentModes.find(m => m.id === agentMode)?.label}任务...`}
                rows={1}
                disabled={isLoading}
                className="w-full bg-transparent text-[var(--text-primary)] text-sm outline-none resize-none max-h-[200px] leading-relaxed placeholder:text-[var(--text-tertiary)] disabled:opacity-50 mb-2 border-none focus:ring-0"
              />

              <div className="flex items-center justify-between">
                <div className="flex items-center gap-1">
                  <button onClick={handleEnhancementsClick} className="nexus-btn-icon relative w-7 h-7 !p-0" title="增强功能">
                    <svg className="w-[18px] h-[18px]" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                      <line x1="12" y1="5" x2="12" y2="19"/><line x1="5" y1="12" x2="19" y2="12"/>
                    </svg>
                    {(webSearchEnabled || codeInterpreterEnabled) && (
                      <span className="absolute -top-0.5 -right-0.5 w-1.5 h-1.5 bg-[var(--nexus-cyan)] rounded-full" />
                    )}
                  </button>
                  <button className="nexus-btn-icon w-7 h-7 !p-0 opacity-50 cursor-not-allowed" title="附件" disabled>
                    <svg className="w-[18px] h-[18px]" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                      <path d="M21.44 11.05l-9.19 9.19a6 6 0 01-8.49-8.49l9.19-9.19a4 4 0 015.66 5.66l-9.2 9.19a2 2 0 01-2.83-2.83l8.49-8.48"/>
                    </svg>
                  </button>
                </div>

                <div className="flex items-center gap-1.5">
                  {(webSearchEnabled || codeInterpreterEnabled) && (
                    <div className="flex items-center gap-1.5 mr-1">
                      {webSearchEnabled && (
                        <span className="px-2 py-0.5 text-[10px] rounded-md bg-[var(--nexus-cyan)]/10 text-[var(--nexus-cyan)] border border-[var(--nexus-cyan)]/20">
                          联网
                        </span>
                      )}
                      {codeInterpreterEnabled && (
                        <span className="px-2 py-0.5 text-[10px] rounded-md bg-[var(--nexus-violet)]/10 text-[var(--nexus-violet)] border border-[var(--nexus-violet)]/20">
                          代码
                        </span>
                      )}
                    </div>
                  )}

                  <button
                    onClick={isRecording ? stopRecording : startRecording}
                    className={`nexus-btn-icon w-7 h-7 !p-0 ${isRecording ? 'text-[var(--nexus-error)] animate-pulse bg-[var(--nexus-error)]/10' : ''}`}
                    title={isRecording ? '停止录音' : '语音输入'}
                  >
                    <svg className="w-[18px] h-[18px]" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                      <path d="M12 1a3 3 0 0 0-3 3v8a3 3 0 0 0 6 0V4a3 3 0 0 0-3-3z"/>
                      <path d="M19 10v2a7 7 0 0 1-14 0v-2"/><line x1="12" y1="19" x2="12" y2="23"/><line x1="8" y1="23" x2="16" y2="23"/>
                    </svg>
                  </button>

                  {isLoading ? (
                    <motion.button
                      onClick={stopGeneration}
                      className="w-7 h-7 rounded-lg bg-[var(--nexus-error)] text-white flex items-center justify-center"
                      whileHover={{ scale: 1.05 }}
                      whileTap={{ scale: 0.95 }}
                    >
                      <svg className="w-3.5 h-3.5" viewBox="0 0 24 24" fill="currentColor">
                        <rect x="6" y="6" width="12" height="12" rx="2"/>
                      </svg>
                    </motion.button>
                  ) : (
                    <motion.button
                      onClick={handleSendMessage}
                      disabled={!inputValue.trim()}
                      className={`w-7 h-7 rounded-lg flex items-center justify-center transition-all ${
                        inputValue.trim()
                          ? 'bg-gradient-neural text-white shadow-lg shadow-[var(--nexus-cyan)]/20'
                          : 'bg-[var(--nexus-surface)] text-[var(--text-tertiary)] cursor-not-allowed'
                      }`}
                      whileHover={{ scale: inputValue.trim() ? 1.05 : 1 }}
                      whileTap={{ scale: inputValue.trim() ? 0.95 : 1 }}
                    >
                      <svg className="w-[18px] h-[18px]" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                        <path d="M22 2L11 13"/><path d="M22 2L15 22L11 13L2 9L22 2Z"/>
                      </svg>
                    </motion.button>
                  )}
                </div>
              </div>
            </div>

            <p className="text-center text-[10px] text-[var(--text-tertiary)] mt-2">
              AI 生成内容仅供参考，请验证重要信息
            </p>
          </div>
        </div>
      </div>

      {/* ============================================ */}
      {/* MODALS & MENUS */}
      {/* ============================================ */}
      {contextMenu && (
        <SessionContextMenu
          x={contextMenu.x}
          y={contextMenu.y}
          items={getContextMenuItems(contextMenu.sessionId)}
          onClose={() => setContextMenu(null)}
        />
      )}

      {renameDialog && (
        <RenameDialog
          initialTitle={renameDialog.currentTitle}
          onConfirm={(newTitle) => { renameSession(renameDialog.sessionId, newTitle); setRenameDialog(null); }}
          onCancel={() => setRenameDialog(null)}
        />
      )}

      {showEnhancementsMenu && (
        <InputEnhancementsMenu
          x={enhancementsMenuPosition.x}
          y={enhancementsMenuPosition.y}
          enhancements={getEnhancements()}
          onClose={() => setShowEnhancementsMenu(false)}
        />
      )}

      {/* Settings Modal */}
      <SettingsModal
        isOpen={showSettings}
        onClose={() => setShowSettings(false)}
        activeTab={settingsTab}
        onTabChange={setSettingsTab}
      />
    </div>
  );
}
