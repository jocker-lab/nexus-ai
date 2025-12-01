"""
Model Provider Schemas
Pydantic models for model provider API requests and responses
"""

from typing import Optional, List
from pydantic import BaseModel, ConfigDict, Field
from enum import Enum


# ============================================
# ENUMS
# ============================================

class ProviderType(str, Enum):
    """供应商类型枚举"""
    OPENAI = "openai"
    ANTHROPIC = "anthropic"
    DEEPSEEK = "deepseek"
    OLLAMA = "ollama"
    GEMINI = "gemini"
    AZURE_OPENAI = "azure_openai"
    AMAZON_BEDROCK = "amazon_bedrock"
    HUGGING_FACE = "hugging_face"


class ModelType(str, Enum):
    """模型能力类型枚举"""
    LLM = "llm"
    EMBEDDING = "embedding"
    RERANKER = "reranker"
    TTS = "tts"
    STT = "stt"
    IMAGE = "image"
    MODERATION = "moderation"


class ConnectionStatus(str, Enum):
    """连接状态枚举"""
    CONNECTED = "connected"
    FAILED = "failed"
    UNKNOWN = "unknown"


# ============================================
# OLLAMA SPECIFIC SCHEMAS
# ============================================

class OllamaLocalModel(BaseModel):
    """Ollama 本地模型信息"""
    id: str                                     # 模型 ID，如 "llama3:8b"
    name: str                                   # 显示名称
    model_type: ModelType = ModelType.LLM       # 模型类型
    context_length: Optional[int] = None        # 上下文长度
    size: Optional[str] = None                  # 模型大小，如 "4.7 GB"
    parameter_size: Optional[str] = None        # 参数量，如 "8B"
    quantization_level: Optional[str] = None    # 量化级别，如 "Q4_0"


class OllamaConfig(BaseModel):
    """Ollama 特定配置"""
    context_length: int = 4096
    model_name: str                             # 选择的模型名称
    model_type: ModelType = ModelType.LLM


# ============================================
# DATABASE MODEL (ORM Mapping)
# ============================================

class ModelProviderModel(BaseModel):
    """完整的模型供应商数据模型（数据库映射）"""
    model_config = ConfigDict(from_attributes=True)

    id: str
    user_id: str
    provider_type: str
    name: str
    api_key: Optional[str] = None
    base_url: Optional[str] = None
    provider_config: Optional[dict] = None
    supported_model_types: Optional[List[str]] = None
    is_active: bool = True
    is_default: bool = False
    connection_status: str = "unknown"
    last_tested_at: Optional[int] = None
    created_at: int
    updated_at: int


# ============================================
# API RESPONSE MODELS
# ============================================

class ModelProviderResponse(BaseModel):
    """API 响应模型（隐藏敏感数据）"""
    id: str
    user_id: str
    provider_type: str
    name: str
    has_api_key: bool                           # 不暴露实际 API Key，只显示是否已设置
    base_url: Optional[str] = None
    provider_config: Optional[dict] = None
    supported_model_types: Optional[List[str]] = None
    is_active: bool
    is_default: bool
    connection_status: str
    last_tested_at: Optional[int] = None
    created_at: int
    updated_at: int

    @classmethod
    def from_model(cls, model: ModelProviderModel) -> "ModelProviderResponse":
        """从数据库模型转换为响应模型"""
        return cls(
            id=model.id,
            user_id=model.user_id,
            provider_type=model.provider_type,
            name=model.name,
            has_api_key=bool(model.api_key),
            base_url=model.base_url,
            provider_config=model.provider_config,
            supported_model_types=model.supported_model_types,
            is_active=model.is_active,
            is_default=model.is_default,
            connection_status=model.connection_status,
            last_tested_at=model.last_tested_at,
            created_at=model.created_at,
            updated_at=model.updated_at,
        )


class ModelProviderListResponse(BaseModel):
    """供应商列表响应"""
    providers: List[ModelProviderResponse]
    total: int


# ============================================
# FORM SCHEMAS (Input)
# ============================================

class ModelProviderCreateForm(BaseModel):
    """创建模型供应商配置表单"""
    provider_type: ProviderType
    name: str = Field(..., min_length=1, max_length=100, description="凭据名称")
    api_key: Optional[str] = Field(None, description="API Key")
    base_url: Optional[str] = Field(None, description="自定义端点 URL")
    provider_config: Optional[dict] = Field(None, description="供应商特定配置")
    supported_model_types: Optional[List[ModelType]] = Field(None, description="支持的模型类型")
    is_active: bool = True
    is_default: bool = False


class ModelProviderUpdateForm(BaseModel):
    """更新模型供应商配置表单"""
    name: Optional[str] = Field(None, min_length=1, max_length=100)
    api_key: Optional[str] = None
    base_url: Optional[str] = None
    provider_config: Optional[dict] = None
    supported_model_types: Optional[List[ModelType]] = None
    is_active: Optional[bool] = None
    is_default: Optional[bool] = None


# ============================================
# OLLAMA SPECIFIC FORMS
# ============================================

class OllamaCreateForm(BaseModel):
    """Ollama 专用创建表单"""
    name: str = Field(..., min_length=1, max_length=100, description="配置名称")
    base_url: str = Field(default="http://localhost:11434", description="Ollama 服务地址")
    model_name: str = Field(..., description="选择的模型名称")
    model_type: ModelType = Field(default=ModelType.LLM, description="模型类型")
    context_length: int = Field(default=4096, ge=512, le=131072, description="上下文长度")
    is_active: bool = True
    is_default: bool = False


class OllamaUpdateForm(BaseModel):
    """Ollama 专用更新表单"""
    name: Optional[str] = Field(None, min_length=1, max_length=100)
    base_url: Optional[str] = None
    model_name: Optional[str] = None
    model_type: Optional[ModelType] = None
    context_length: Optional[int] = Field(None, ge=512, le=131072)
    is_active: Optional[bool] = None
    is_default: Optional[bool] = None


# ============================================
# CONNECTION TEST SCHEMAS
# ============================================

class ConnectionTestRequest(BaseModel):
    """连接测试请求"""
    provider_type: ProviderType
    api_key: Optional[str] = None
    base_url: Optional[str] = None


class ConnectionTestResponse(BaseModel):
    """连接测试响应"""
    success: bool
    message: str
    models: Optional[List[dict]] = None         # Ollama 返回的本地模型列表


class OllamaDetectResponse(BaseModel):
    """Ollama 模型检测响应"""
    success: bool
    message: str
    models: List[OllamaLocalModel] = []


# ============================================
# AVAILABLE MODELS SCHEMAS
# ============================================

class AvailableModel(BaseModel):
    """可用模型信息（从供应商 API 动态获取）"""
    id: str                                     # 模型 ID（如 deepseek-chat, gpt-4o）
    name: str                                   # 显示名称
    model_type: str = "llm"                     # 模型类型（llm, embedding, etc.）
    context_length: Optional[int] = None        # 上下文长度
    is_enabled: bool = True                     # 是否启用


class AvailableModelsResponse(BaseModel):
    """可用模型列表响应"""
    success: bool
    message: str
    models: List[AvailableModel] = []
