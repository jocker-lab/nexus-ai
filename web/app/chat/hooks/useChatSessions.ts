import { useState, useCallback, useEffect } from 'react'

export interface ChatSession {
  id: string
  title: string
  updated_at: number
  created_at: number
  pinned?: boolean
}

export interface UseChatSessionsOptions {
  userId: string
  onError?: (error: Error) => void
}

export function useChatSessions(options: UseChatSessionsOptions) {
  const { userId, onError } = options

  const [sessions, setSessions] = useState<ChatSession[]>([])
  const [isLoading, setIsLoading] = useState(false)

  // 加载会话列表
  const loadSessions = useCallback(async () => {
    try {
      setIsLoading(true)
      const response = await fetch(`http://localhost:8000/api/v1/chats/?user_id=${userId}`)

      if (!response.ok) {
        throw new Error('Failed to load sessions')
      }

      const data = await response.json()
      setSessions(data)
    } catch (error) {
      console.error('Failed to load sessions:', error)
      onError?.(error as Error)
    } finally {
      setIsLoading(false)
    }
  }, [userId, onError])

  // 删除会话
  const deleteSession = useCallback(async (sessionId: string) => {
    try {
      const response = await fetch(`http://localhost:8000/api/v1/chats/${sessionId}?user_id=${userId}`, {
        method: 'DELETE'
      })

      if (!response.ok) {
        throw new Error('Failed to delete session')
      }

      // 从列表中移除
      setSessions(prev => prev.filter(s => s.id !== sessionId))
    } catch (error) {
      console.error('Failed to delete session:', error)
      onError?.(error as Error)
    }
  }, [userId, onError])

  // 重命名会话
  const renameSession = useCallback(async (sessionId: string, newTitle: string) => {
    try {
      const response = await fetch(`http://localhost:8000/api/v1/chats/${sessionId}/title?user_id=${userId}`, {
        method: 'PATCH',
        headers: {
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({ title: newTitle })
      })

      if (!response.ok) {
        throw new Error('Failed to rename session')
      }

      // 更新本地列表
      setSessions(prev => prev.map(s =>
        s.id === sessionId ? { ...s, title: newTitle } : s
      ))
    } catch (error) {
      console.error('Failed to rename session:', error)
      onError?.(error as Error)
    }
  }, [userId, onError])

  // 置顶会话
  const pinSession = useCallback(async (sessionId: string) => {
    try {
      const response = await fetch(`http://localhost:8000/api/v1/chats/${sessionId}/pin?user_id=${userId}`, {
        method: 'POST'
      })

      if (!response.ok) {
        throw new Error('Failed to pin session')
      }

      // 重新加载列表以获取最新状态
      await loadSessions()
    } catch (error) {
      console.error('Failed to pin session:', error)
      onError?.(error as Error)
    }
  }, [userId, onError, loadSessions])

  // 归档会话
  const archiveSession = useCallback(async (sessionId: string) => {
    try {
      const response = await fetch(`http://localhost:8000/api/v1/chats/${sessionId}/archive?user_id=${userId}`, {
        method: 'POST'
      })

      if (!response.ok) {
        throw new Error('Failed to archive session')
      }

      // 从列表中移除已归档的会话
      setSessions(prev => prev.filter(s => s.id !== sessionId))
    } catch (error) {
      console.error('Failed to archive session:', error)
      onError?.(error as Error)
    }
  }, [userId, onError])

  // 复制会话
  const cloneSession = useCallback(async (sessionId: string) => {
    try {
      const response = await fetch(`http://localhost:8000/api/v1/chats/${sessionId}/clone?user_id=${userId}`, {
        method: 'POST'
      })

      if (!response.ok) {
        throw new Error('Failed to clone session')
      }

      // 重新加载列表
      await loadSessions()
    } catch (error) {
      console.error('Failed to clone session:', error)
      onError?.(error as Error)
    }
  }, [userId, onError, loadSessions])

  // 下载会话
  const downloadSession = useCallback(async (sessionId: string) => {
    try {
      const response = await fetch(`http://localhost:8000/api/v1/chats/${sessionId}/export?user_id=${userId}`)

      if (!response.ok) {
        throw new Error('Failed to download session')
      }

      // 获取文件内容并触发下载
      const blob = await response.blob()
      const url = window.URL.createObjectURL(blob)
      const a = document.createElement('a')
      a.href = url
      a.download = `chat_${sessionId}.json`
      document.body.appendChild(a)
      a.click()
      document.body.removeChild(a)
      window.URL.revokeObjectURL(url)
    } catch (error) {
      console.error('Failed to download session:', error)
      onError?.(error as Error)
    }
  }, [userId, onError])

  // 初始加载（仅执行一次）
  useEffect(() => {
    loadSessions()
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [])

  return {
    sessions,
    isLoading,
    loadSessions,
    deleteSession,
    renameSession,
    pinSession,
    archiveSession,
    cloneSession,
    downloadSession
  }
}
