'use client'

/**
 * useModelProviders Hook
 * 管理模型供应商配置的 API 调用
 */

import { useState, useEffect, useCallback } from 'react'
import { API_ENDPOINTS } from '@/lib/config'
import { useAuthStore } from '@/lib/stores/auth'
import { createAuthHeaders } from '@/lib/api'
import type {
  ModelProviderResponse,
  ModelProviderCreateForm,
  ModelProviderUpdateForm,
  OllamaCreateForm,
  OllamaUpdateForm,
  AvailableModelsResponse,
  ConnectionTestRequest,
  ConnectionTestResponse,
  OllamaDetectResponse,
} from '@/types/model-providers'

interface UseModelProvidersReturn {
  // 状态
  providers: ModelProviderResponse[]
  isLoading: boolean
  error: string | null

  // 加载
  loadProviders: () => Promise<void>

  // CRUD 操作
  createProvider: (data: ModelProviderCreateForm) => Promise<ModelProviderResponse | null>
  createOllamaProvider: (data: OllamaCreateForm) => Promise<ModelProviderResponse | null>
  updateProvider: (id: string, data: ModelProviderUpdateForm) => Promise<ModelProviderResponse | null>
  updateOllamaProvider: (id: string, data: OllamaUpdateForm) => Promise<ModelProviderResponse | null>
  deleteProvider: (id: string) => Promise<boolean>

  // 状态操作
  toggleProvider: (id: string) => Promise<ModelProviderResponse | null>
  setDefaultProvider: (id: string) => Promise<ModelProviderResponse | null>

  // 测试连接
  testConnection: (data: ConnectionTestRequest) => Promise<ConnectionTestResponse>
  testSavedProvider: (id: string) => Promise<ConnectionTestResponse>

  // 获取可用模型
  getAvailableModels: (providerId: string) => Promise<AvailableModelsResponse>

  // Ollama 专用
  detectOllamaModels: (baseUrl?: string) => Promise<OllamaDetectResponse>
}

export function useModelProviders(): UseModelProvidersReturn {
  const [providers, setProviders] = useState<ModelProviderResponse[]>([])
  const [isLoading, setIsLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)

  // 从认证 store 获取用户 ID
  const { user } = useAuthStore()
  const userId = user?.id || ''

  // ============================================
  // 加载供应商列表
  // ============================================
  const loadProviders = useCallback(async () => {
    if (!userId) return

    setIsLoading(true)
    setError(null)

    try {
      const response = await fetch(
        `${API_ENDPOINTS.modelProviders}?user_id=${userId}`,
        { headers: createAuthHeaders() }
      )

      if (!response.ok) {
        throw new Error(`HTTP ${response.status}`)
      }

      const data = await response.json()
      setProviders(data)
    } catch (err) {
      const message = err instanceof Error ? err.message : '加载供应商列表失败'
      setError(message)
      console.error('Failed to load providers:', err)
    } finally {
      setIsLoading(false)
    }
  }, [userId])

  // 初始加载
  useEffect(() => {
    loadProviders()
  }, [loadProviders])

  // ============================================
  // 创建供应商
  // ============================================
  const createProvider = useCallback(async (
    data: ModelProviderCreateForm
  ): Promise<ModelProviderResponse | null> => {
    try {
      const response = await fetch(
        `${API_ENDPOINTS.modelProviders}?user_id=${userId}`,
        {
          method: 'POST',
          headers: createAuthHeaders(),
          body: JSON.stringify(data),
        }
      )

      if (!response.ok) {
        throw new Error(`HTTP ${response.status}`)
      }

      const newProvider = await response.json()
      setProviders(prev => [...prev, newProvider])
      return newProvider
    } catch (err) {
      console.error('Failed to create provider:', err)
      return null
    }
  }, [userId])

  // ============================================
  // 创建 Ollama 供应商
  // ============================================
  const createOllamaProvider = useCallback(async (
    data: OllamaCreateForm
  ): Promise<ModelProviderResponse | null> => {
    try {
      const response = await fetch(
        `${API_ENDPOINTS.modelProviders}/ollama?user_id=${userId}`,
        {
          method: 'POST',
          headers: createAuthHeaders(),
          body: JSON.stringify(data),
        }
      )

      if (!response.ok) {
        throw new Error(`HTTP ${response.status}`)
      }

      const newProvider = await response.json()
      setProviders(prev => [...prev, newProvider])
      return newProvider
    } catch (err) {
      console.error('Failed to create Ollama provider:', err)
      return null
    }
  }, [userId])

  // ============================================
  // 更新供应商
  // ============================================
  const updateProvider = useCallback(async (
    id: string,
    data: ModelProviderUpdateForm
  ): Promise<ModelProviderResponse | null> => {
    try {
      const response = await fetch(
        `${API_ENDPOINTS.modelProviders}/${id}?user_id=${userId}`,
        {
          method: 'PUT',
          headers: createAuthHeaders(),
          body: JSON.stringify(data),
        }
      )

      if (!response.ok) {
        throw new Error(`HTTP ${response.status}`)
      }

      const updatedProvider = await response.json()
      setProviders(prev =>
        prev.map(p => (p.id === id ? updatedProvider : p))
      )
      return updatedProvider
    } catch (err) {
      console.error('Failed to update provider:', err)
      return null
    }
  }, [userId])

  // ============================================
  // 更新 Ollama 供应商
  // ============================================
  const updateOllamaProvider = useCallback(async (
    id: string,
    data: OllamaUpdateForm
  ): Promise<ModelProviderResponse | null> => {
    try {
      const response = await fetch(
        `${API_ENDPOINTS.modelProviders}/ollama/${id}?user_id=${userId}`,
        {
          method: 'PUT',
          headers: createAuthHeaders(),
          body: JSON.stringify(data),
        }
      )

      if (!response.ok) {
        throw new Error(`HTTP ${response.status}`)
      }

      const updatedProvider = await response.json()
      setProviders(prev =>
        prev.map(p => (p.id === id ? updatedProvider : p))
      )
      return updatedProvider
    } catch (err) {
      console.error('Failed to update Ollama provider:', err)
      return null
    }
  }, [userId])

  // ============================================
  // 删除供应商
  // ============================================
  const deleteProvider = useCallback(async (id: string): Promise<boolean> => {
    try {
      const response = await fetch(
        `${API_ENDPOINTS.modelProviders}/${id}?user_id=${userId}`,
        { method: 'DELETE', headers: createAuthHeaders() }
      )

      if (!response.ok) {
        throw new Error(`HTTP ${response.status}`)
      }

      setProviders(prev => prev.filter(p => p.id !== id))
      return true
    } catch (err) {
      console.error('Failed to delete provider:', err)
      return false
    }
  }, [userId])

  // ============================================
  // 切换供应商状态
  // ============================================
  const toggleProvider = useCallback(async (
    id: string
  ): Promise<ModelProviderResponse | null> => {
    try {
      const response = await fetch(
        `${API_ENDPOINTS.modelProviders}/${id}/toggle?user_id=${userId}`,
        { method: 'POST', headers: createAuthHeaders() }
      )

      if (!response.ok) {
        throw new Error(`HTTP ${response.status}`)
      }

      const updatedProvider = await response.json()
      setProviders(prev =>
        prev.map(p => (p.id === id ? updatedProvider : p))
      )
      return updatedProvider
    } catch (err) {
      console.error('Failed to toggle provider:', err)
      return null
    }
  }, [userId])

  // ============================================
  // 设置默认供应商
  // ============================================
  const setDefaultProvider = useCallback(async (
    id: string
  ): Promise<ModelProviderResponse | null> => {
    try {
      const response = await fetch(
        `${API_ENDPOINTS.modelProviders}/${id}/default?user_id=${userId}`,
        { method: 'POST', headers: createAuthHeaders() }
      )

      if (!response.ok) {
        throw new Error(`HTTP ${response.status}`)
      }

      const updatedProvider = await response.json()
      // 刷新整个列表以更新其他供应商的 is_default 状态
      await loadProviders()
      return updatedProvider
    } catch (err) {
      console.error('Failed to set default provider:', err)
      return null
    }
  }, [loadProviders])

  // ============================================
  // 测试连接（未保存的配置）
  // ============================================
  const testConnection = useCallback(async (
    data: ConnectionTestRequest
  ): Promise<ConnectionTestResponse> => {
    try {
      const response = await fetch(
        `${API_ENDPOINTS.modelProviders}/test-connection`,
        {
          method: 'POST',
          headers: createAuthHeaders(),
          body: JSON.stringify(data),
        }
      )

      if (!response.ok) {
        throw new Error(`HTTP ${response.status}`)
      }

      return await response.json()
    } catch (err) {
      return {
        success: false,
        message: err instanceof Error ? err.message : '连接测试失败',
      }
    }
  }, [])

  // ============================================
  // 测试已保存的供应商连接
  // ============================================
  const testSavedProvider = useCallback(async (
    id: string
  ): Promise<ConnectionTestResponse> => {
    try {
      const response = await fetch(
        `${API_ENDPOINTS.modelProviders}/${id}/test?user_id=${userId}`,
        { method: 'POST', headers: createAuthHeaders() }
      )

      if (!response.ok) {
        throw new Error(`HTTP ${response.status}`)
      }

      const result = await response.json()

      // 更新本地状态中的连接状态
      if (result.success) {
        setProviders(prev =>
          prev.map(p =>
            p.id === id ? { ...p, connection_status: 'connected' as const } : p
          )
        )
      }

      return result
    } catch (err) {
      return {
        success: false,
        message: err instanceof Error ? err.message : '连接测试失败',
      }
    }
  }, [userId])

  // ============================================
  // 获取可用模型列表
  // ============================================
  const getAvailableModels = useCallback(async (
    providerId: string
  ): Promise<AvailableModelsResponse> => {
    try {
      const response = await fetch(
        `${API_ENDPOINTS.modelProviders}/${providerId}/models?user_id=${userId}`
      )

      if (!response.ok) {
        throw new Error(`HTTP ${response.status}`)
      }

      return await response.json()
    } catch (err) {
      return {
        success: false,
        message: err instanceof Error ? err.message : '获取模型列表失败',
        models: [],
      }
    }
  }, [userId])

  // ============================================
  // 检测 Ollama 本地模型
  // ============================================
  const detectOllamaModels = useCallback(async (
    baseUrl: string = 'http://localhost:11434'
  ): Promise<OllamaDetectResponse> => {
    try {
      const response = await fetch(
        `${API_ENDPOINTS.modelProviders}/ollama/detect-models?base_url=${encodeURIComponent(baseUrl)}`
      )

      if (!response.ok) {
        throw new Error(`HTTP ${response.status}`)
      }

      return await response.json()
    } catch (err) {
      return {
        success: false,
        message: err instanceof Error ? err.message : '检测 Ollama 模型失败',
        models: [],
      }
    }
  }, [])

  return {
    providers,
    isLoading,
    error,
    loadProviders,
    createProvider,
    createOllamaProvider,
    updateProvider,
    updateOllamaProvider,
    deleteProvider,
    toggleProvider,
    setDefaultProvider,
    testConnection,
    testSavedProvider,
    getAvailableModels,
    detectOllamaModels,
  }
}
