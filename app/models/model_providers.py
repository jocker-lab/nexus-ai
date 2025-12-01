"""
Model Provider Configuration Table
存储用户配置的模型供应商信息（API Key、端点等）
"""

from app.database.db import Base
from sqlalchemy import BigInteger, Boolean, Column, String, Text, Index
from sqlalchemy.dialects.mysql import JSON
import enum


class ProviderType(str, enum.Enum):
    """供应商类型枚举"""
    OPENAI = "openai"
    ANTHROPIC = "anthropic"
    DEEPSEEK = "deepseek"
    OLLAMA = "ollama"
    GEMINI = "gemini"
    AZURE_OPENAI = "azure_openai"
    AMAZON_BEDROCK = "amazon_bedrock"
    HUGGING_FACE = "hugging_face"


class ModelType(str, enum.Enum):
    """模型能力类型枚举"""
    LLM = "llm"
    EMBEDDING = "embedding"
    RERANKER = "reranker"
    TTS = "tts"
    STT = "stt"
    IMAGE = "image"


class ModelProvider(Base):
    """
    模型供应商配置表

    存储用户配置的模型供应商凭据和设置。
    每个用户可以配置多个供应商，每个供应商可以有多个配置（如多个 API Key）。

    Ollama 特殊配置示例:
    provider_config = {
        "context_length": 4096,
        "model_name": "llama3:8b",
        "model_type": "llm"
    }
    """
    __tablename__ = "model_provider"

    # 主键
    id = Column(String(36), primary_key=True)

    # 用户关联
    user_id = Column(String(36), nullable=False, index=True)

    # 供应商标识
    provider_type = Column(String(50), nullable=False, index=True)
    name = Column(String(100), nullable=False)  # 凭据名称/显示名称

    # 通用凭据
    api_key = Column(Text, nullable=True)       # API Key (Ollama 可为空)
    base_url = Column(Text, nullable=True)      # 自定义端点 URL

    # 供应商特定配置 (JSON)
    # 通用: {"model_name": "gpt-4", "max_tokens": 4096}
    # Ollama: {"context_length": 4096, "model_name": "llama3:8b", "model_type": "llm"}
    provider_config = Column(JSON, nullable=True)

    # 支持的模型类型 (JSON 数组)
    # 例: ["llm", "embedding"]
    supported_model_types = Column(JSON, nullable=True)

    # 状态
    is_active = Column(Boolean, default=True, nullable=False)
    is_default = Column(Boolean, default=False, nullable=False)

    # 连接状态
    connection_status = Column(String(20), default="unknown", nullable=False)  # connected, failed, unknown
    last_tested_at = Column(BigInteger, nullable=True)

    # 时间戳 (Unix timestamp)
    created_at = Column(BigInteger, nullable=False)
    updated_at = Column(BigInteger, nullable=False)

    # 索引
    __table_args__ = (
        Index('idx_model_provider_user_type', 'user_id', 'provider_type'),
    )
