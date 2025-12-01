/**
 * Model Provider Types
 * 模型供应商相关的 TypeScript 类型定义
 */

// ============================================
// ENUMS
// ============================================

export type ProviderType =
  | 'openai'
  | 'anthropic'
  | 'deepseek'
  | 'ollama'
  | 'gemini'
  | 'azure_openai'
  | 'amazon_bedrock'
  | 'hugging_face'

export type ModelType =
  | 'llm'
  | 'embedding'
  | 'reranker'
  | 'tts'
  | 'stt'
  | 'image'
  | 'moderation'

export type ConnectionStatus = 'connected' | 'failed' | 'unknown'

// ============================================
// API RESPONSE TYPES
// ============================================

/**
 * 模型供应商配置响应（从后端获取）
 */
export interface ModelProviderResponse {
  id: string
  user_id: string
  provider_type: ProviderType
  name: string
  has_api_key: boolean
  base_url: string | null
  provider_config: Record<string, unknown> | null
  supported_model_types: ModelType[] | null
  is_active: boolean
  is_default: boolean
  connection_status: ConnectionStatus
  last_tested_at: number | null
  created_at: number
  updated_at: number
}

/**
 * 可用模型信息
 */
export interface AvailableModel {
  id: string
  name: string
  model_type: string
  context_length: number | null
  is_enabled: boolean
}

/**
 * 可用模型列表响应
 */
export interface AvailableModelsResponse {
  success: boolean
  message: string
  models: AvailableModel[]
}

/**
 * 连接测试响应
 */
export interface ConnectionTestResponse {
  success: boolean
  message: string
  models?: Record<string, unknown>[]
}

/**
 * Ollama 本地模型信息
 */
export interface OllamaLocalModel {
  id: string
  name: string
  model_type: ModelType
  context_length: number | null
  size: string | null
  parameter_size: string | null
  quantization_level: string | null
}

/**
 * Ollama 模型检测响应
 */
export interface OllamaDetectResponse {
  success: boolean
  message: string
  models: OllamaLocalModel[]
}

// ============================================
// FORM TYPES (Request)
// ============================================

/**
 * 创建模型供应商表单
 */
export interface ModelProviderCreateForm {
  provider_type: ProviderType
  name: string
  api_key?: string
  base_url?: string
  provider_config?: Record<string, unknown>
  supported_model_types?: ModelType[]
  is_active?: boolean
  is_default?: boolean
}

/**
 * 更新模型供应商表单
 */
export interface ModelProviderUpdateForm {
  name?: string
  api_key?: string
  base_url?: string
  provider_config?: Record<string, unknown>
  supported_model_types?: ModelType[]
  is_active?: boolean
  is_default?: boolean
}

/**
 * Ollama 创建表单
 */
export interface OllamaCreateForm {
  name: string
  base_url?: string
  model_name: string
  model_type?: ModelType
  context_length?: number
  is_active?: boolean
  is_default?: boolean
}

/**
 * Ollama 更新表单
 */
export interface OllamaUpdateForm {
  name?: string
  base_url?: string
  model_name?: string
  model_type?: ModelType
  context_length?: number
  is_active?: boolean
  is_default?: boolean
}

/**
 * 连接测试请求
 */
export interface ConnectionTestRequest {
  provider_type: ProviderType
  api_key?: string
  base_url?: string
}

// ============================================
// UI TYPES
// ============================================

/**
 * 前端供应商元数据（静态信息，如图标、描述）
 */
export interface ProviderMetadata {
  id: ProviderType
  name: string
  description: string
  icon: React.ReactNode
  tags: string[]
  downloads?: number
}

/**
 * 富化后的供应商数据（合并静态信息与后端配置）
 */
export interface EnrichedProvider extends ProviderMetadata {
  configured: boolean
  hasApiKey: boolean
  connectionStatus: ConnectionStatus
  configId: string | null // 后端配置 ID
  configName: string | null // 配置名称
}
