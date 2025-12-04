# -*- coding: utf-8 -*-
"""
统一的配置管理系统
使用 Pydantic Settings 实现类型安全的配置管理
- .env 文件管理敏感信息（API keys, 数据库连接等）
- config.yaml 管理应用配置（连接池参数、模型参数等）
"""
import os
import yaml
from typing import Optional, Dict, Any
from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """应用配置类"""

    # ==================== API Keys（从 .env 读取）====================
    TAVILY_API_KEY: str = Field(
        ...,
        description="Tavily 搜索 API Key"
    )

    OPENWEATHER_API_KEY: str = Field(
        ...,
        description="OpenWeather API Key"
    )

    DEEPSEEK_API_KEY: str = Field(
        ...,
        description="DeepSeek API Key"
    )

    OPENAI_API_KEY: str = Field(
        ...,
        description="OpenAI API Key"
    )

    NEWSAPI_API_KEY: Optional[str] = Field(
        None,
        description="NewsAPI Key（可选）"
    )

    LANGSMITH_API_KEY: Optional[str] = Field(
        None,
        description="LangSmith API Key（可选）"
    )

    # ==================== 数据库配置（从 .env 读取）====================
    DATABASE_URL: str = Field(
        ...,
        description="数据库连接 URL"
    )

    DATABASE_SCHEMA: Optional[str] = Field(
        None,
        description="数据库 Schema"
    )

    # ==================== MinIO 配置（从 .env 读取）====================
    MINIO_ENDPOINT: str = Field(
        "localhost:9000",
        description="MinIO 服务端点"
    )

    MINIO_ACCESS_KEY: str = Field(
        "minioadmin",
        description="MinIO Access Key"
    )

    MINIO_SECRET_KEY: str = Field(
        "minioadmin",
        description="MinIO Secret Key"
    )

    MINIO_BUCKET: str = Field(
        "nexus-reports",
        description="MinIO 存储桶名称"
    )

    MINIO_PENDING_BUCKET: str = Field(
        "pending-uploads",
        description="MinIO 待处理文件存储桶名称"
    )

    MINIO_SECURE: bool = Field(
        False,
        description="是否使用 HTTPS 连接 MinIO"
    )

    # ==================== Milvus 向量数据库配置（从 .env 读取）====================
    MILVUS_HOST: str = Field(
        "localhost",
        description="Milvus 服务主机"
    )

    MILVUS_PORT: int = Field(
        19530,
        description="Milvus 服务端口"
    )

    MILVUS_COLLECTION: str = Field(
        "document_vectors",
        description="Milvus 默认集合名称"
    )

    # ==================== Embedding 服务配置（从 .env 读取）====================
    EMBEDDING_API_URL: str = Field(
        "http://localhost:8080/embedding",
        description="Embedding 服务 API 地址"
    )

    EMBEDDING_DIMENSION: int = Field(
        1024,
        description="Embedding 向量维度"
    )

    # ==================== Redis 配置（从 .env 读取）====================
    REDIS_HOST: str = Field(
        "localhost",
        description="Redis 服务主机"
    )

    REDIS_PORT: int = Field(
        6379,
        description="Redis 服务端口"
    )

    REDIS_DB_BROKER: int = Field(
        0,
        description="Celery Broker 使用的 Redis 数据库"
    )

    REDIS_DB_BACKEND: int = Field(
        1,
        description="Celery Backend 使用的 Redis 数据库"
    )

    # ==================== 其他配置（从 .env 读取）====================
    LANGSMITH_PROJECT: str = Field(
        "nexus-ai",
        description="LangSmith 项目名称"
    )

    ENABLE_PYTHON_REPL: bool = Field(
        True,
        description="是否启用 Python REPL"
    )

    EXECUTE_QUERY_MAX_CHARS: int = Field(
        4000,
        description="查询执行结果最大字符数"
    )

    # ==================== 从 config.yaml 加载的配置 ====================
    _yaml_config: Optional[Dict[str, Any]] = None

    model_config = SettingsConfigDict(
        # 查找项目根目录的 .env 文件，支持从任意子目录运行
        env_file=os.path.join(
            os.path.dirname(os.path.dirname(os.path.dirname(__file__))),
            ".env"
        ),
        env_file_encoding="utf-8",
        case_sensitive=True,
        extra="ignore"
    )

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        # 加载 config.yaml
        self._load_yaml_config()

    def _load_yaml_config(self):
        """从 config.yaml 加载应用配置"""
        config_path = os.path.join(
            os.path.dirname(__file__),
            'config.yaml'
        )

        if os.path.exists(config_path):
            with open(config_path, 'r', encoding='utf-8') as f:
                self._yaml_config = yaml.safe_load(f)
        else:
            self._yaml_config = {}

    # ==================== 数据库连接池配置（从 yaml）====================
    @property
    def DATABASE_POOL_SIZE(self) -> int:
        """数据库连接池大小"""
        return self._yaml_config.get('database', {}).get('pool', {}).get('pool_size', 5)

    @property
    def DATABASE_POOL_MAX_OVERFLOW(self) -> int:
        """数据库连接池最大溢出"""
        return self._yaml_config.get('database', {}).get('pool', {}).get('max_overflow', 10)

    @property
    def DATABASE_POOL_TIMEOUT(self) -> int:
        """数据库连接池超时时间（秒）"""
        return self._yaml_config.get('database', {}).get('pool', {}).get('pool_timeout', 30)

    @property
    def DATABASE_POOL_RECYCLE(self) -> int:
        """数据库连接回收时间（秒）"""
        return self._yaml_config.get('database', {}).get('pool', {}).get('pool_recycle', 3600)

    # ==================== 模型参数配置（从 yaml）====================
    @property
    def model_params(self) -> Dict[str, Any]:
        """
        大模型参数配置
        注意：openai_api_key 从环境变量获取，不从 yaml 读取
        """
        params = self._yaml_config.get('model_params', {}).copy()

        # 从环境变量覆盖 API key（安全考虑）
        if 'openai_api_key' in params:
            params['openai_api_key'] = self.OPENAI_API_KEY

        return params

    # ==================== Milvus 配置（从 yaml）====================
    @property
    def MILVUS_INDEX_CONFIG(self) -> Dict[str, Any]:
        """Milvus 索引配置"""
        return self._yaml_config.get('milvus', {}).get('index', {
            'metric_type': 'COSINE',
            'index_type': 'IVF_FLAT',
            'nlist': 128
        })

    @property
    def MILVUS_SEARCH_CONFIG(self) -> Dict[str, Any]:
        """Milvus 搜索配置"""
        return self._yaml_config.get('milvus', {}).get('search', {
            'nprobe': 10
        })

    # ==================== Embedding 配置（从 yaml）====================
    @property
    def EMBEDDING_TIMEOUT(self) -> int:
        """Embedding 请求超时时间"""
        return self._yaml_config.get('embedding', {}).get('timeout', 60)

    @property
    def EMBEDDING_BATCH_SIZE(self) -> int:
        """Embedding 批量处理大小"""
        return self._yaml_config.get('embedding', {}).get('batch_size', 32)

    # ==================== Celery 配置（从 yaml）====================
    @property
    def CELERY_CONFIG(self) -> Dict[str, Any]:
        """Celery 配置"""
        return self._yaml_config.get('celery', {})

    @property
    def CELERY_TASK_TIME_LIMIT(self) -> int:
        """Celery 任务超时时间"""
        return self._yaml_config.get('celery', {}).get('task_time_limit', 600)

    # ==================== Docling 配置（从 yaml）====================
    @property
    def DOCLING_TIMEOUT(self) -> int:
        """文档解析超时时间"""
        return self._yaml_config.get('docling', {}).get('timeout', 120)

    @property
    def DOCLING_MAX_WORKERS(self) -> int:
        """文档解析线程池大小"""
        return self._yaml_config.get('docling', {}).get('max_workers', 5)

    # ==================== Template 配置（从 yaml）====================
    @property
    def TEMPLATE_COLLECTION_NAME(self) -> str:
        """模版向量集合名称"""
        return self._yaml_config.get('template', {}).get('collection_name', 'template_vectors')

    @property
    def TEMPLATE_DUPLICATE_THRESHOLD(self) -> float:
        """模版重复检测阈值"""
        return self._yaml_config.get('template', {}).get('duplicate_threshold', 0.95)

    # ==================== Redis URL 生成 ====================
    @property
    def CELERY_BROKER_URL(self) -> str:
        """Celery Broker URL"""
        return f"redis://{self.REDIS_HOST}:{self.REDIS_PORT}/{self.REDIS_DB_BROKER}"

    @property
    def CELERY_RESULT_BACKEND(self) -> str:
        """Celery Result Backend URL"""
        return f"redis://{self.REDIS_HOST}:{self.REDIS_PORT}/{self.REDIS_DB_BACKEND}"

    # ==================== 向后兼容属性 ====================
    @property
    def MYSQL_DATABASE_URL(self) -> str:
        """MySQL 数据库 URL（向后兼容）"""
        return self.DATABASE_URL


# 创建全局配置实例
settings = Settings()


# ==================== 导出常用配置（向后兼容）====================
MYSQL_DATABASE_URL = settings.MYSQL_DATABASE_URL
LOCAL_BIG_MODEL_PARAMS = settings.model_params
DATABASE_SCHEMA = settings.DATABASE_SCHEMA
DATABASE_POOL_SIZE = settings.DATABASE_POOL_SIZE
DATABASE_POOL_MAX_OVERFLOW = settings.DATABASE_POOL_MAX_OVERFLOW
DATABASE_POOL_TIMEOUT = settings.DATABASE_POOL_TIMEOUT
DATABASE_POOL_RECYCLE = settings.DATABASE_POOL_RECYCLE
