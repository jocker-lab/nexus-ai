import { useState, useCallback, useRef, useEffect } from 'react'
import { API_ENDPOINTS, buildUrl } from '@/lib/config'
import { useAuthStore } from '@/lib/stores/auth'
import { getAccessToken, getCurrentUserId, createAuthHeaders } from '@/lib/api'

export interface Message {
  id: string
  type: 'user' | 'ai'
  content: string
  loading?: boolean
  timestamp: number
  // 推理模型思考过程
  thinking?: string
  thinkingDuration?: number // 思考耗时（秒）
  isThinking?: boolean // 是否正在思考中
}

export interface ChatSession {
  id: string
  title: string
  updated_at: number
  created_at: number
}

export interface UseChatOptions {
  chatId?: string
  apiUrl?: string
  onError?: (error: Error) => void
  onSessionCreated?: (chatId: string) => void
}

export function useChat(options: UseChatOptions = {}) {
  const {
    chatId: initialChatId,
    apiUrl = API_ENDPOINTS.chatStream,
    onError,
    onSessionCreated
  } = options

  // 从认证 store 获取用户 ID
  const { user } = useAuthStore()
  const userId = user?.id || ''

  const [messages, setMessages] = useState<Message[]>([])
  const [isLoading, setIsLoading] = useState(false)
  const [chatId, setChatId] = useState<string>(initialChatId || '')
  const [currentTitle, setCurrentTitle] = useState<string>('新对话')
  const abortControllerRef = useRef<AbortController | null>(null)
  const isNewChatRef = useRef<boolean>(false) // 标记是否是新创建的会话

  // 同步外部 chatId 变化
  useEffect(() => {
    if (initialChatId !== undefined) {
      setChatId(initialChatId)
      // 外部切换会话时，不是新会话
      isNewChatRef.current = false
    }
  }, [initialChatId])

  // 生成会话ID
  function generateChatId() {
    return `chat_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`
  }

  // 加载历史消息
  const loadMessages = useCallback(async (chatId: string) => {
    try {
      const url = buildUrl(`${API_ENDPOINTS.chats}/${chatId}/messages`, { user_id: userId })
      const response = await fetch(url, {
        headers: createAuthHeaders(),
      })
      if (response.ok) {
        const data = await response.json()
        const loadedMessages: Message[] = data.messages.map((msg: any) => ({
          id: msg.id,
          type: msg.type,
          content: msg.content,
          timestamp: msg.timestamp,
          loading: false
        }))
        setMessages(loadedMessages)
      }
    } catch (error) {
      console.error('Failed to load messages:', error)
    }
  }, [userId])

  // 当chatId改变时加载消息
  useEffect(() => {
    if (chatId && !isNewChatRef.current) {
      // 只在非新会话时加载历史消息
      loadMessages(chatId)
    }
    // 重置标记
    if (isNewChatRef.current) {
      isNewChatRef.current = false
    }
  }, [chatId, loadMessages])

  // 发送消息
  interface SendMessageOptions {
    providerId?: string
    modelName?: string
  }

  const sendMessage = useCallback(async (content: string, options?: SendMessageOptions) => {
    if (!content.trim() || isLoading) return

    const userMessage: Message = {
      id: `msg_${Date.now()}_user`,
      type: 'user',
      content: content.trim(),
      timestamp: Date.now()
    }

    const aiMessage: Message = {
      id: `msg_${Date.now()}_ai`,
      type: 'ai',
      content: '',
      loading: true,
      timestamp: Date.now(),
      thinking: '',
      isThinking: false
    }

    setMessages(prev => [...prev, userMessage, aiMessage])
    setIsLoading(true)

    // 记录思考开始时间
    let thinkingStartTime: number | null = null

    // 创建AbortController用于取消请求
    abortControllerRef.current = new AbortController()

    try {
      const response = await fetch(apiUrl, {
        method: 'POST',
        headers: createAuthHeaders(),
        body: JSON.stringify({
          message: content.trim(),
          chat_id: chatId || undefined, // 如果没有chatId，后端会自动创建
          user_id: userId,
          stream: true,
          provider_id: options?.providerId,
          model_name: options?.modelName
        }),
        signal: abortControllerRef.current.signal
      })

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`)
      }

      const reader = response.body?.getReader()
      const decoder = new TextDecoder()

      if (!reader) {
        throw new Error('Response body is null')
      }

      let accumulatedContent = ''
      let accumulatedThinking = ''
      let receivedChatId = false

      while (true) {
        const { done, value } = await reader.read()

        if (done) break

        const chunk = decoder.decode(value, { stream: true })
        const lines = chunk.split('\n')

        for (const line of lines) {
          if (line.startsWith('data: ')) {
            const data = line.slice(6).trim()

            if (data === '[DONE]') {
              setMessages(prev => {
                const newMessages = [...prev]
                const lastMsg = newMessages[newMessages.length - 1]
                if (lastMsg && lastMsg.type === 'ai') {
                  lastMsg.loading = false
                  lastMsg.isThinking = false
                  // 计算思考时长
                  if (thinkingStartTime && lastMsg.thinking) {
                    lastMsg.thinkingDuration = Math.round((Date.now() - thinkingStartTime) / 1000)
                  }
                }
                return newMessages
              })
              continue
            }

            try {
              const parsed = JSON.parse(data)

              // 处理后端返回的chat_id
              if (parsed.chat_id && !receivedChatId) {
                isNewChatRef.current = true // 标记为新创建的会话
                setChatId(parsed.chat_id)
                receivedChatId = true
                console.log('Received chat_id:', parsed.chat_id)
                // 通知父组件会话已创建
                onSessionCreated?.(parsed.chat_id)
              }

              // 处理标题更新
              if (parsed.title) {
                setCurrentTitle(parsed.title)
                console.log('Received title:', parsed.title)
                // 通知父组件标题已更新，触发会话列表刷新
                onSessionCreated?.(chatId)
              }

              // 处理推理模型的思考过程 (reasoning_content)
              if (parsed.reasoning_content) {
                // 首次收到思考内容时记录开始时间
                if (!thinkingStartTime) {
                  thinkingStartTime = Date.now()
                }
                accumulatedThinking += parsed.reasoning_content

                setMessages(prev => {
                  const newMessages = [...prev]
                  const lastMsg = newMessages[newMessages.length - 1]
                  if (lastMsg && lastMsg.type === 'ai') {
                    lastMsg.thinking = accumulatedThinking
                    lastMsg.isThinking = true
                  }
                  return newMessages
                })
              }

              // 处理内容 - 收到正式内容时，思考阶段结束
              if (parsed.content) {
                // 当开始收到正式内容时，结束思考状态
                if (thinkingStartTime && accumulatedThinking) {
                  setMessages(prev => {
                    const newMessages = [...prev]
                    const lastMsg = newMessages[newMessages.length - 1]
                    if (lastMsg && lastMsg.type === 'ai') {
                      lastMsg.isThinking = false
                      lastMsg.thinkingDuration = Math.round((Date.now() - thinkingStartTime!) / 1000)
                    }
                    return newMessages
                  })
                }

                accumulatedContent += parsed.content

                setMessages(prev => {
                  const newMessages = [...prev]
                  const lastMsg = newMessages[newMessages.length - 1]
                  if (lastMsg && lastMsg.type === 'ai') {
                    lastMsg.content = accumulatedContent
                  }
                  return newMessages
                })
              }
            } catch (e) {
              console.error('Error parsing SSE data:', e)
            }
          }
        }
      }
    } catch (error) {
      if (error instanceof Error) {
        if (error.name === 'AbortError') {
          console.log('Request aborted')
        } else {
          console.error('Chat error:', error)
          onError?.(error)

          // 更新AI消息为错误状态
          setMessages(prev => {
            const newMessages = [...prev]
            const lastMsg = newMessages[newMessages.length - 1]
            if (lastMsg && lastMsg.type === 'ai') {
              lastMsg.content = '抱歉，发生了错误。请稍后重试。'
              lastMsg.loading = false
            }
            return newMessages
          })
        }
      }
    } finally {
      setIsLoading(false)
      abortControllerRef.current = null
    }
  }, [chatId, userId, apiUrl, isLoading, onError])

  // 停止生成
  const stopGeneration = useCallback(() => {
    if (abortControllerRef.current) {
      abortControllerRef.current.abort()
      setIsLoading(false)

      setMessages(prev => {
        const newMessages = [...prev]
        const lastMsg = newMessages[newMessages.length - 1]
        if (lastMsg && lastMsg.type === 'ai' && lastMsg.loading) {
          lastMsg.loading = false
        }
        return newMessages
      })
    }
  }, [])

  // 清空对话
  const clearMessages = useCallback(() => {
    setMessages([])
    setChatId('') // 清空chatId，下次发送消息时会创建新的chat
    isNewChatRef.current = false // 重置新会话标记
  }, [])

  // 重新生成最后一条消息
  const regenerateLastMessage = useCallback(() => {
    if (messages.length < 2) return

    const lastUserMessage = [...messages].reverse().find(m => m.type === 'user')
    if (lastUserMessage) {
      // 移除最后一条AI消息
      setMessages(prev => prev.slice(0, -1))
      sendMessage(lastUserMessage.content)
    }
  }, [messages, sendMessage])

  // 切换会话
  const switchChat = useCallback((newChatId: string) => {
    setMessages([]) // 先清空旧消息
    isNewChatRef.current = false // 切换到已存在的会话
    setChatId(newChatId) // 然后设置新 chatId，触发 loadMessages
  }, [])

  return {
    messages,
    isLoading,
    chatId,
    currentTitle,
    userId,
    sendMessage,
    stopGeneration,
    clearMessages,
    regenerateLastMessage,
    switchChat,
    loadMessages
  }
}
