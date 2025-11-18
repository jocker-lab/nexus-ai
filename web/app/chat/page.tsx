'use client';

import { useRef, useEffect, useState } from 'react';
import { useChat } from './hooks/useChat';
import { useChatSessions } from './hooks/useChatSessions';
import { SessionContextMenu, ContextMenuItem } from './components/SessionContextMenu';
import { RenameDialog } from './components/RenameDialog';
import { InputEnhancementsMenu, InputEnhancement } from './components/InputEnhancementsMenu';

export default function ChatPage() {
  const userId = 'default_user'; // TODO: 从认证系统获取真实用户ID
  const [selectedChatId, setSelectedChatId] = useState<string>('');

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
    userId,
    apiUrl: 'http://localhost:8000/api/v1/chats/stream',
    onError: (error) => {
      console.error('Chat error:', error);
      alert('发生错误，请检查后端服务是否正常运行');
    },
    onSessionCreated: (newChatId) => {
      // 新会话创建后刷新列表
      loadSessions();
    }
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
    userId,
    onError: (error) => {
      console.error('Sessions error:', error);
    }
  });

  const chatAreaRef = useRef<HTMLDivElement>(null);
  const textareaRef = useRef<HTMLTextAreaElement>(null);
  const [inputValue, setInputValue] = useState('');

  // 右键菜单状态
  const [contextMenu, setContextMenu] = useState<{
    x: number;
    y: number;
    sessionId: string;
  } | null>(null);

  // 重命名对话框状态
  const [renameDialog, setRenameDialog] = useState<{
    sessionId: string;
    currentTitle: string;
  } | null>(null);

  // 输入增强菜单状态
  const [showEnhancementsMenu, setShowEnhancementsMenu] = useState(false);
  const [enhancementsMenuPosition, setEnhancementsMenuPosition] = useState({ x: 0, y: 0 });

  // 输入增强选项
  const [webSearchEnabled, setWebSearchEnabled] = useState(false);
  const [codeInterpreterEnabled, setCodeInterpreterEnabled] = useState(false);

  // 语音录制状态
  const [isRecording, setIsRecording] = useState(false);
  const mediaRecorderRef = useRef<MediaRecorder | null>(null);
  const audioChunksRef = useRef<Blob[]>([]);

  // Auto scroll to bottom
  useEffect(() => {
    if (chatAreaRef.current) {
      chatAreaRef.current.scrollTop = chatAreaRef.current.scrollHeight;
    }
  }, [messages]);

  // Auto resize textarea
  const handleInputChange = (e: React.ChangeEvent<HTMLTextAreaElement>) => {
    setInputValue(e.target.value);
    e.target.style.height = 'auto';
    e.target.style.height = Math.min(e.target.scrollHeight, 200) + 'px';
  };

  const handleSendMessage = () => {
    const message = inputValue.trim();
    if (!message || isLoading) return;

    sendMessage(message);
    setInputValue('');

    // Reset textarea height
    if (textareaRef.current) {
      textareaRef.current.style.height = 'auto';
    }
  };

  const handleKeyDown = (e: React.KeyboardEvent<HTMLTextAreaElement>) => {
    // Enter 发送，Shift+Enter 换行
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSendMessage();
    }
    // 支持 ↑ 箭头发送（可选）
    // if (e.key === 'ArrowUp' && !inputValue.trim()) {
    //   e.preventDefault();
    //   // 可以在这里添加重新编辑上一条消息的逻辑
    // }
  };

  // 处理增强菜单按钮点击
  const handleEnhancementsClick = (e: React.MouseEvent<HTMLButtonElement>) => {
    const rect = e.currentTarget.getBoundingClientRect();
    setEnhancementsMenuPosition({
      x: rect.left,
      y: rect.top
    });
    setShowEnhancementsMenu(!showEnhancementsMenu);
  };

  // 获取增强选项配置
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

  // 语音录制功能
  const startRecording = async () => {
    try {
      const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
      const mediaRecorder = new MediaRecorder(stream);
      mediaRecorderRef.current = mediaRecorder;
      audioChunksRef.current = [];

      mediaRecorder.ondataavailable = (event) => {
        if (event.data.size > 0) {
          audioChunksRef.current.push(event.data);
        }
      };

      mediaRecorder.onstop = () => {
        const audioBlob = new Blob(audioChunksRef.current, { type: 'audio/webm' });
        // 这里可以添加发送音频到后端的逻辑
        console.log('录音完成，音频大小:', audioBlob.size);
        // TODO: 发送到后端进行语音转文字

        // 停止所有音频轨道
        stream.getTracks().forEach(track => track.stop());
      };

      mediaRecorder.start();
      setIsRecording(true);
    } catch (error) {
      console.error('无法访问麦克风:', error);
      alert('无法访问麦克风，请检查权限设置');
    }
  };

  const stopRecording = () => {
    if (mediaRecorderRef.current && mediaRecorderRef.current.state !== 'inactive') {
      mediaRecorderRef.current.stop();
      setIsRecording(false);
    }
  };

  const toggleRecording = () => {
    if (isRecording) {
      stopRecording();
    } else {
      startRecording();
    }
  };

  // 新建对话
  const handleNewChat = () => {
    setSelectedChatId('');
    clearMessages();
  };

  // 切换会话
  const handleSelectChat = (sessionId: string) => {
    setSelectedChatId(sessionId);
    // 不需要调用 switchChat，useChat 会通过 prop 变化自动加载消息
  };

  // 删除会话
  const handleDeleteChat = async (sessionId: string) => {
    if (confirm('确定要删除这个对话吗？')) {
      await deleteSession(sessionId);
      if (selectedChatId === sessionId) {
        handleNewChat();
      }
    }
  };

  // 处理右键菜单
  const handleContextMenu = (e: React.MouseEvent, sessionId: string) => {
    e.preventDefault();
    setContextMenu({
      x: e.clientX,
      y: e.clientY,
      sessionId
    });
  };

  // 获取右键菜单项
  const getContextMenuItems = (sessionId: string): ContextMenuItem[] => {
    const session = sessions.find(s => s.id === sessionId);
    if (!session) return [];

    return [
      {
        icon: (
          <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
            <path d="M11 4H4a2 2 0 0 0-2 2v14a2 2 0 0 0 2 2h14a2 2 0 0 0 2-2v-7"/>
            <path d="M18.5 2.5a2.121 2.121 0 0 1 3 3L12 15l-4 1 1-4 9.5-9.5z"/>
          </svg>
        ),
        label: '重命名',
        onClick: () => {
          setRenameDialog({
            sessionId,
            currentTitle: session.title || '新对话'
          });
        }
      },
      {
        icon: (
          <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
            <path d="M21 15a2 2 0 0 1-2 2H7l-4 4V5a2 2 0 0 1 2-2h14a2 2 0 0 1 2 2z"/>
            <path d="M8 10h.01M12 10h.01M16 10h.01"/>
          </svg>
        ),
        label: '分享',
        onClick: () => {
          alert('分享功能即将推出');
        }
      },
      {
        icon: (
          <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
            <path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4"/>
            <polyline points="7 10 12 15 17 10"/>
            <line x1="12" y1="15" x2="12" y2="3"/>
          </svg>
        ),
        label: '下载',
        onClick: () => downloadSession(sessionId)
      },
      {
        icon: (
          <svg viewBox="0 0 24 24" fill="currentColor">
            <path d="M19 3h-4.18C14.4 1.84 13.3 1 12 1c-1.3 0-2.4.84-2.82 2H5c-1.1 0-2 .9-2 2v14c0 1.1.9 2 2 2h14c1.1 0 2-.9 2-2V5c0-1.1-.9-2-2-2zm-7 0c.55 0 1 .45 1 1s-.45 1-1 1-1-.45-1-1 .45-1 1-1zm7 15H5V5h2v3h10V5h2v13z"/>
          </svg>
        ),
        label: '复制',
        onClick: () => cloneSession(sessionId)
      },
      {
        icon: (
          <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
            <path d="M5 12h14M12 5l7 7-7 7"/>
          </svg>
        ),
        label: '移动',
        onClick: () => {
          alert('移动到文件夹功能即将推出');
        },
        divider: true
      },
      {
        icon: (
          <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
            <path d="M19 21l-7-5-7 5V5a2 2 0 0 1 2-2h10a2 2 0 0 1 2 2z"/>
          </svg>
        ),
        label: session.pinned ? '取消置顶' : '置顶',
        onClick: () => pinSession(sessionId)
      },
      {
        icon: (
          <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
            <path d="M21 8v13H3V8M1 3h22v5H1zM10 12h4"/>
          </svg>
        ),
        label: '归档',
        onClick: () => archiveSession(sessionId)
      },
      {
        icon: (
          <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
            <path d="M3 6h18M19 6v14a2 2 0 0 1-2 2H7a2 2 0 0 1-2-2V6m3 0V4a2 2 0 0 1 2-2h4a2 2 0 0 1 2 2v2"/>
          </svg>
        ),
        label: '删除',
        onClick: () => handleDeleteChat(sessionId),
        danger: true,
        divider: true
      }
    ];
  };

  // 按时间分组会话
  const groupSessionsByMonth = () => {
    const grouped: { [key: string]: typeof sessions } = {};
    const now = new Date();
    const today = new Date(now.getFullYear(), now.getMonth(), now.getDate());

    sessions.forEach(session => {
      const sessionDate = new Date(session.updated_at * 1000);
      const sessionDay = new Date(sessionDate.getFullYear(), sessionDate.getMonth(), sessionDate.getDate());

      // 计算时间差
      const diffDays = Math.floor((today.getTime() - sessionDay.getTime()) / (1000 * 60 * 60 * 24));
      const diffMonths = (now.getFullYear() - sessionDate.getFullYear()) * 12 +
                         (now.getMonth() - sessionDate.getMonth());
      const diffYears = now.getFullYear() - sessionDate.getFullYear();

      let key: string;

      // 今天
      if (diffDays === 0) {
        key = '今天';
      }
      // 昨天
      else if (diffDays === 1) {
        key = '昨天';
      }
      // 本周（7天内）
      else if (diffDays < 7) {
        key = '本周';
      }
      // 本月
      else if (diffMonths === 0) {
        key = '本月';
      }
      // 上个月
      else if (diffMonths === 1) {
        key = '上个月';
      }
      // 今年的其他月份
      else if (diffYears === 0) {
        const monthNames = ['一月', '二月', '三月', '四月', '五月', '六月',
                           '七月', '八月', '九月', '十月', '十一月', '十二月'];
        key = monthNames[sessionDate.getMonth()];
      }
      // 去年
      else if (diffYears === 1) {
        key = '去年';
      }
      // 更早的年份
      else {
        key = `${sessionDate.getFullYear()}年`;
      }

      if (!grouped[key]) {
        grouped[key] = [];
      }
      grouped[key].push(session);
    });

    return grouped;
  };

  const groupedSessions = groupSessionsByMonth();

  return (
    <div className="flex h-screen bg-[#212121]" suppressHydrationWarning>
      {/* Sidebar */}
      <div className="w-[260px] bg-[#171717] flex flex-col">
        <div className="p-3">
          <div className="flex items-center gap-2.5 mb-3">
            <div className="w-8 h-8 rounded-full bg-white flex items-center justify-center flex-shrink-0">
              <svg className="w-5 h-5" viewBox="0 0 24 24" fill="none">
                <circle cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="2"/>
                <circle cx="12" cy="12" r="3" fill="currentColor"/>
              </svg>
            </div>
            <div className="text-[15px] font-semibold text-[#e0e0e0] flex-1">Nexus AI</div>
            <div className="flex gap-1">
              <button
                onClick={handleNewChat}
                className="p-1.5 rounded-md hover:bg-[#2a2a2a] text-[#9ca3af] transition-colors"
                title="新对话"
              >
                <svg className="w-[18px] h-[18px]" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                  <path d="M11 4H4a2 2 0 0 0-2 2v14a2 2 0 0 0 2 2h14a2 2 0 0 0 2-2v-7"/>
                  <path d="M18.5 2.5a2.121 2.121 0 0 1 3 3L12 15l-4 1 1-4 9.5-9.5z"/>
                </svg>
              </button>
              <button
                onClick={loadSessions}
                className="p-1.5 rounded-md hover:bg-[#2a2a2a] text-[#9ca3af] transition-colors"
                title="刷新"
              >
                <svg className="w-[18px] h-[18px]" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                  <path d="M21.5 2v6h-6M2.5 22v-6h6M2 11.5a10 10 0 0 1 18.8-4.3M22 12.5a10 10 0 0 1-18.8 4.2"/>
                </svg>
              </button>
            </div>
          </div>
        </div>

        <div className="px-4 flex-1 overflow-y-auto">
          {/* 历史对话列表 */}
          {sessionsLoading ? (
            <div className="text-center text-[#6b7280] text-sm py-4">加载中...</div>
          ) : sessions.length === 0 ? (
            <div className="text-center text-[#6b7280] text-sm py-4">暂无对话</div>
          ) : (
            <div className="space-y-4">
              {Object.entries(groupedSessions).map(([monthKey, monthSessions]) => (
                <div key={monthKey}>
                  <div className="text-[#6b7280] text-[11px] font-semibold px-3 py-2">
                    {monthKey}
                  </div>
                  <div className="space-y-1">
                    {monthSessions.map((session) => (
                      <div
                        key={session.id}
                        onClick={() => handleSelectChat(session.id)}
                        onContextMenu={(e) => handleContextMenu(e, session.id)}
                        className={`group flex items-center gap-2 px-3 py-2.5 rounded-lg cursor-pointer text-sm transition-colors ${
                          chatId === session.id || selectedChatId === session.id
                            ? 'bg-[#2a2a2a] text-[#e0e0e0]'
                            : 'hover:bg-[#2a2a2a] text-[#9ca3af]'
                        }`}
                      >
                        {session.pinned && (
                          <svg className="w-3 h-3 text-[#3b82f6] flex-shrink-0" viewBox="0 0 24 24" fill="currentColor">
                            <path d="M19 21l-7-5-7 5V5a2 2 0 0 1 2-2h10a2 2 0 0 1 2 2z"/>
                          </svg>
                        )}
                        <span className="truncate flex-1">
                          {session.title || '新对话'}
                        </span>
                        <button
                          onClick={(e) => {
                            e.stopPropagation();
                            handleContextMenu(e, session.id);
                          }}
                          className="w-7 h-7 p-1 rounded-md hover:bg-[#3a3a3a] text-[#9ca3af] opacity-0 group-hover:opacity-100 transition-opacity"
                          title="更多操作"
                        >
                          <svg className="w-4 h-4" viewBox="0 0 24 24" fill="currentColor">
                            <circle cx="12" cy="12" r="1.5"/>
                            <circle cx="19" cy="12" r="1.5"/>
                            <circle cx="5" cy="12" r="1.5"/>
                          </svg>
                        </button>
                      </div>
                    ))}
                  </div>
                </div>
              ))}
            </div>
          )}
        </div>

        <div className="p-3 border-t border-[#2a2a2a]">
          <div className="flex items-center gap-2.5">
            <div className="w-8 h-8 rounded-full bg-[#3b82f6] flex items-center justify-center font-semibold text-[13px] text-white flex-shrink-0">
              AI
            </div>
            <div className="text-sm font-medium text-[#e0e0e0]">AI Assistant</div>
          </div>
        </div>
      </div>

      {/* Main Content */}
      <div className="flex-1 flex flex-col bg-[#212121]">
        {/* Top Bar */}
        <div className="flex items-center justify-between px-5 py-3 bg-[#212121] border-b border-[#2a2a2a]">
          <button className="flex items-center gap-1.5 px-3 py-1.5 text-sm font-medium text-[#e0e0e0] hover:opacity-80 transition-opacity">
            Nexus AI
            <svg className="w-4 h-4" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
              <polyline points="6 9 12 15 18 9"/>
            </svg>
          </button>
          <div className="flex items-center gap-2">
            <button className="p-1.5 rounded-md hover:bg-[#2a2a2a] text-[#9ca3af] transition-colors">
              <svg className="w-[18px] h-[18px]" viewBox="0 0 24 24" fill="currentColor">
                <circle cx="12" cy="12" r="1.5"/>
                <circle cx="19" cy="12" r="1.5"/>
                <circle cx="5" cy="12" r="1.5"/>
              </svg>
            </button>
            <div className="w-8 h-8 rounded-full bg-[#3b82f6] flex items-center justify-center font-semibold text-[13px] text-white">
              AI
            </div>
          </div>
        </div>

        {/* Chat Area */}
        <div ref={chatAreaRef} className="flex-1 overflow-y-auto px-5 py-10">
          {messages.length === 0 ? (
            <div className="flex flex-col items-center justify-center h-full text-center">
              <div className="w-16 h-16 rounded-full bg-gradient-to-br from-[#3b82f6] to-[#60a5fa] flex items-center justify-center mb-6">
                <svg className="w-8 h-8 text-white" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                  <path d="M21 15a2 2 0 0 1-2 2H7l-4 4V5a2 2 0 0 1 2-2h14a2 2 0 0 1 2 2z"/>
                </svg>
              </div>
              <h2 className="text-2xl font-semibold text-[#e0e0e0] mb-2">
                开始新对话
              </h2>
              <p className="text-[#9ca3af] max-w-md">
                这是一个基于LangChain的AI助手，支持多轮对话和上下文记忆
              </p>
            </div>
          ) : (
            <div className="flex flex-col gap-8">
              {messages.map((message) => (
                <div key={message.id}>
                  {message.type === 'user' ? (
                    <div className="flex justify-end max-w-[1100px] w-full mx-auto">
                      <div className="bg-[#2f2f2f] px-4 py-2.5 rounded-[18px] text-[#e0e0e0] text-sm max-w-[70%] whitespace-pre-wrap">
                        {message.content}
                      </div>
                    </div>
                  ) : (
                    <div className="flex gap-3 max-w-[1100px] w-full mx-auto">
                      <div className="w-8 h-8 rounded-full bg-gradient-to-br from-[#3b82f6] to-[#60a5fa] flex items-center justify-center flex-shrink-0 text-white">
                        <svg className="w-[18px] h-[18px]" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5">
                          <path d="M21 12a9 9 0 1 1-9-9c2.52 0 4.93 1 6.74 2.74L21 8"/>
                        </svg>
                      </div>
                      <div className="flex-1">
                        <div className="flex items-center gap-2 mb-2">
                          <span className="font-semibold text-sm text-[#e0e0e0]">Nexus AI</span>
                        </div>
                        {message.loading ? (
                          <>
                            <div className="flex items-center gap-2 text-[#9ca3af] text-[13px] mb-4">
                              <div className="w-3.5 h-3.5 border-2 border-[#3a3a3a] border-t-[#666] rounded-full animate-spin"></div>
                              <span>正在思考中...</span>
                            </div>
                            {message.content ? (
                              <div className="text-[#b8b8b8] leading-relaxed text-sm whitespace-pre-wrap">
                                {message.content}
                              </div>
                            ) : (
                              <div className="flex flex-col gap-2.5">
                                <div className="flex gap-2">
                                  <div className="flex-1 max-w-[920px] h-3.5 bg-[#2a2a2a] rounded-md"></div>
                                  <div className="flex-1 max-w-[260px] h-3.5 bg-[#2a2a2a] rounded-md"></div>
                                </div>
                                <div className="flex gap-2">
                                  <div className="flex-1 max-w-[680px] h-3.5 bg-[#2a2a2a] rounded-md"></div>
                                  <div className="flex-1 max-w-[920px] h-3.5 bg-[#2a2a2a] rounded-md"></div>
                                </div>
                              </div>
                            )}
                          </>
                        ) : (
                          <div className="text-[#b8b8b8] leading-relaxed text-sm whitespace-pre-wrap">
                            {message.content}
                          </div>
                        )}
                      </div>
                    </div>
                  )}
                </div>
              ))}
            </div>
          )}
        </div>

        {/* Input Area */}
        <div className="px-5 py-5 bg-[#212121] relative">
          <div className="max-w-[1100px] mx-auto">
            {/* 输入框容器 - 垂直布局 */}
            <div className="bg-[#2a2a2a] rounded-3xl px-5 py-3 transition-colors focus-within:bg-[#2f2f2f] min-h-[90px] flex flex-col">
              {/* 输入框 - 占据中间空间 */}
              <textarea
                ref={textareaRef}
                value={inputValue}
                onChange={handleInputChange}
                onKeyDown={handleKeyDown}
                placeholder="输入消息"
                rows={2}
                disabled={isLoading}
                className="flex-1 bg-transparent border-none text-[#e0e0e0] text-[15px] outline-none resize-none max-h-[200px] leading-relaxed mb-2 placeholder:text-[#6b7280] disabled:opacity-50"
              />

              {/* 底部按钮栏 */}
              <div className="flex items-center justify-between">
                {/* 左侧按钮组 */}
                <div className="flex items-center gap-1">
                  {/* 增强功能按钮 */}
                  <button
                    onClick={handleEnhancementsClick}
                    className="p-2 text-[#9ca3af] hover:text-[#e0e0e0] transition-colors relative"
                    title="输入增强功能"
                  >
                    <svg className="w-5 h-5" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                      <line x1="12" y1="5" x2="12" y2="19"/>
                      <line x1="5" y1="12" x2="19" y2="12"/>
                    </svg>
                    {(webSearchEnabled || codeInterpreterEnabled) && (
                      <span className="absolute top-1 right-1 w-2 h-2 bg-[#3b82f6] rounded-full"></span>
                    )}
                  </button>

                  {/* 附件按钮 */}
                  <button
                    className="p-2 text-[#9ca3af] hover:text-[#e0e0e0] transition-colors opacity-50 cursor-not-allowed"
                    title="附件功能即将推出"
                    disabled
                  >
                    <svg className="w-5 h-5" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                      <path d="M21.44 11.05l-9.19 9.19a6 6 0 01-8.49-8.49l9.19-9.19a4 4 0 015.66 5.66l-9.2 9.19a2 2 0 01-2.83-2.83l8.49-8.48"/>
                    </svg>
                  </button>
                </div>

                {/* 右侧按钮组 */}
                <div className="flex items-center gap-2">
                  {/* 语音按钮 */}
                  <button
                    onClick={toggleRecording}
                    className={`p-2 transition-all ${
                      isRecording
                        ? 'text-[#ef4444] animate-pulse'
                        : 'text-[#9ca3af] hover:text-[#e0e0e0]'
                    }`}
                    title={isRecording ? '停止录音' : '语音输入'}
                  >
                    <svg className="w-5 h-5" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                      <path d="M12 1a3 3 0 0 0-3 3v8a3 3 0 0 0 6 0V4a3 3 0 0 0-3-3z"/>
                      <path d="M19 10v2a7 7 0 0 1-14 0v-2"/>
                      <line x1="12" y1="19" x2="12" y2="23"/>
                      <line x1="8" y1="23" x2="16" y2="23"/>
                    </svg>
                  </button>

                  {/* 发送/停止按钮 */}
                  {isLoading ? (
                    <button
                      onClick={stopGeneration}
                      className="w-9 h-9 rounded-full bg-[#ef4444] flex items-center justify-center text-white hover:bg-[#dc2626] transition-colors flex-shrink-0"
                      title="停止生成"
                    >
                      <svg className="w-4 h-4" viewBox="0 0 24 24" fill="currentColor">
                        <rect x="6" y="6" width="12" height="12" rx="1"/>
                      </svg>
                    </button>
                  ) : (
                    <button
                      onClick={handleSendMessage}
                      disabled={isLoading || !inputValue.trim()}
                      className="w-9 h-9 rounded-full bg-black flex items-center justify-center text-white hover:bg-[#1a1a1a] transition-colors flex-shrink-0 disabled:opacity-30 disabled:cursor-not-allowed"
                      title="发送消息（Enter）"
                    >
                      <svg className="w-[18px] h-[18px]" viewBox="0 0 24 24" fill="currentColor">
                        <circle cx="12" cy="12" r="10"/>
                        <path d="M8 12h8M12 8v8" stroke="currentColor" strokeWidth="2" strokeLinecap="round"/>
                      </svg>
                    </button>
                  )}
                </div>
              </div>
            </div>

            {/* 状态提示 */}
            <div className="flex items-center justify-center gap-4 text-[#6b7280] text-[11px] mt-3">
              {(webSearchEnabled || codeInterpreterEnabled) && (
                <div className="flex items-center gap-2">
                  {webSearchEnabled && (
                    <span className="px-2 py-0.5 bg-[#2a2a2a] rounded text-[#3b82f6]">🌐 联网搜索</span>
                  )}
                  {codeInterpreterEnabled && (
                    <span className="px-2 py-0.5 bg-[#2a2a2a] rounded text-[#3b82f6]">💻 代码解释器</span>
                  )}
                </div>
              )}
              <span>AI可能会犯错误。请验证重要信息。</span>
            </div>
          </div>
        </div>
      </div>

      {/* 右键菜单 */}
      {contextMenu && (
        <SessionContextMenu
          x={contextMenu.x}
          y={contextMenu.y}
          items={getContextMenuItems(contextMenu.sessionId)}
          onClose={() => setContextMenu(null)}
        />
      )}

      {/* 重命名对话框 */}
      {renameDialog && (
        <RenameDialog
          initialTitle={renameDialog.currentTitle}
          onConfirm={(newTitle) => {
            renameSession(renameDialog.sessionId, newTitle);
            setRenameDialog(null);
          }}
          onCancel={() => setRenameDialog(null)}
        />
      )}

      {/* 输入增强菜单 */}
      {showEnhancementsMenu && (
        <InputEnhancementsMenu
          x={enhancementsMenuPosition.x}
          y={enhancementsMenuPosition.y}
          enhancements={getEnhancements()}
          onClose={() => setShowEnhancementsMenu(false)}
        />
      )}
    </div>
  );
}
