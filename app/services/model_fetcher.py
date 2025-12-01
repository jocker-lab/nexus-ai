"""
Model Fetcher Service
从各个模型供应商 API 动态获取可用模型列表
"""

from typing import List, Optional, Dict, Any, Callable
import httpx
from loguru import logger

from app.schemas.model_providers import AvailableModel, AvailableModelsResponse


# ============================================
# 硬编码的模型列表（用于无公开 API 的供应商）
# ============================================

ANTHROPIC_MODELS = [
    {"id": "claude-3-opus-20240229", "name": "Claude 3 Opus", "model_type": "llm", "context_length": 200000},
    {"id": "claude-3-sonnet-20240229", "name": "Claude 3 Sonnet", "model_type": "llm", "context_length": 200000},
    {"id": "claude-3-haiku-20240307", "name": "Claude 3 Haiku", "model_type": "llm", "context_length": 200000},
    {"id": "claude-3-5-sonnet-20241022", "name": "Claude 3.5 Sonnet", "model_type": "llm", "context_length": 200000},
    {"id": "claude-3-5-haiku-20241022", "name": "Claude 3.5 Haiku", "model_type": "llm", "context_length": 200000},
]


class ModelFetcher:
    """
    统一的模型获取服务
    支持从 8 个供应商动态获取模型列表
    """

    def __init__(self):
        self._fetchers: Dict[str, Callable] = {
            "openai": self._fetch_openai_models,
            "anthropic": self._fetch_anthropic_models,
            "deepseek": self._fetch_deepseek_models,
            "ollama": self._fetch_ollama_models,
            "gemini": self._fetch_gemini_models,
            "azure_openai": self._fetch_azure_openai_models,
            "amazon_bedrock": self._fetch_bedrock_models,
            "hugging_face": self._fetch_huggingface_models,
        }

    async def fetch_models(
        self,
        provider_type: str,
        api_key: Optional[str] = None,
        base_url: Optional[str] = None,
        provider_config: Optional[Dict[str, Any]] = None
    ) -> AvailableModelsResponse:
        """
        获取指定供应商的可用模型列表

        Args:
            provider_type: 供应商类型 (openai, anthropic, deepseek, etc.)
            api_key: API 密钥
            base_url: 自定义端点 URL
            provider_config: 供应商特定配置

        Returns:
            AvailableModelsResponse 包含模型列表
        """
        fetcher = self._fetchers.get(provider_type)

        if not fetcher:
            return AvailableModelsResponse(
                success=False,
                message=f"不支持的供应商类型: {provider_type}",
                models=[]
            )

        try:
            return await fetcher(api_key, base_url, provider_config)
        except Exception as e:
            logger.exception(f"获取 {provider_type} 模型列表失败: {e}")
            return AvailableModelsResponse(
                success=False,
                message=str(e),
                models=[]
            )

    # ============================================
    # OpenAI
    # ============================================
    async def _fetch_openai_models(
        self,
        api_key: Optional[str],
        base_url: Optional[str],
        config: Optional[Dict]
    ) -> AvailableModelsResponse:
        """获取 OpenAI 模型列表"""
        if not api_key:
            return AvailableModelsResponse(
                success=False,
                message="缺少 API Key",
                models=[]
            )

        url = base_url or "https://api.openai.com/v1"
        headers = {"Authorization": f"Bearer {api_key}"}

        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.get(f"{url}/models", headers=headers)

            if response.status_code != 200:
                return AvailableModelsResponse(
                    success=False,
                    message=f"API 请求失败: HTTP {response.status_code}",
                    models=[]
                )

            data = response.json()
            models_data = data.get("data", [])

            # 过滤并格式化模型
            models = []
            for m in models_data:
                model_id = m.get("id", "")
                # 只保留常用模型
                if any(prefix in model_id for prefix in ["gpt-4", "gpt-3.5", "o1", "chatgpt"]):
                    models.append(AvailableModel(
                        id=model_id,
                        name=model_id,
                        model_type="llm",
                        context_length=self._get_openai_context_length(model_id),
                        is_enabled=True
                    ))

            # 按名称排序
            models.sort(key=lambda x: x.name)

            return AvailableModelsResponse(
                success=True,
                message=f"找到 {len(models)} 个可用模型",
                models=models
            )

    def _get_openai_context_length(self, model_id: str) -> int:
        """获取 OpenAI 模型的上下文长度"""
        if "gpt-4o" in model_id or "gpt-4-turbo" in model_id:
            return 128000
        elif "gpt-4-32k" in model_id:
            return 32768
        elif "gpt-4" in model_id:
            return 8192
        elif "gpt-3.5-turbo-16k" in model_id:
            return 16384
        elif "gpt-3.5" in model_id:
            return 4096
        elif "o1" in model_id:
            return 128000
        return 4096

    # ============================================
    # Anthropic (硬编码)
    # ============================================
    async def _fetch_anthropic_models(
        self,
        api_key: Optional[str],
        base_url: Optional[str],
        config: Optional[Dict]
    ) -> AvailableModelsResponse:
        """获取 Anthropic 模型列表（硬编码）"""
        # Anthropic 没有公开的模型列表 API，使用硬编码
        models = [
            AvailableModel(
                id=m["id"],
                name=m["name"],
                model_type=m["model_type"],
                context_length=m["context_length"],
                is_enabled=True
            )
            for m in ANTHROPIC_MODELS
        ]

        return AvailableModelsResponse(
            success=True,
            message=f"找到 {len(models)} 个可用模型",
            models=models
        )

    # ============================================
    # DeepSeek
    # ============================================
    async def _fetch_deepseek_models(
        self,
        api_key: Optional[str],
        base_url: Optional[str],
        config: Optional[Dict]
    ) -> AvailableModelsResponse:
        """获取 DeepSeek 模型列表"""
        if not api_key:
            return AvailableModelsResponse(
                success=False,
                message="缺少 API Key",
                models=[]
            )

        url = base_url or "https://api.deepseek.com"
        headers = {"Authorization": f"Bearer {api_key}"}

        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.get(f"{url}/models", headers=headers)

            if response.status_code != 200:
                return AvailableModelsResponse(
                    success=False,
                    message=f"API 请求失败: HTTP {response.status_code}",
                    models=[]
                )

            data = response.json()
            models_data = data.get("data", [])

            models = []
            for m in models_data:
                model_id = m.get("id", "")
                models.append(AvailableModel(
                    id=model_id,
                    name=model_id,
                    model_type="llm",
                    context_length=128000,  # DeepSeek 默认 128K
                    is_enabled=True
                ))

            return AvailableModelsResponse(
                success=True,
                message=f"找到 {len(models)} 个可用模型",
                models=models
            )

    # ============================================
    # Ollama
    # ============================================
    async def _fetch_ollama_models(
        self,
        api_key: Optional[str],
        base_url: Optional[str],
        config: Optional[Dict]
    ) -> AvailableModelsResponse:
        """获取 Ollama 本地模型列表"""
        url = base_url or "http://localhost:11434"

        try:
            async with httpx.AsyncClient(timeout=10.0) as client:
                response = await client.get(f"{url}/api/tags")

                if response.status_code != 200:
                    return AvailableModelsResponse(
                        success=False,
                        message=f"Ollama 服务返回错误: HTTP {response.status_code}",
                        models=[]
                    )

                data = response.json()
                models_data = data.get("models", [])

                models = []
                for m in models_data:
                    model_name = m.get("name", "")
                    details = m.get("details", {})
                    models.append(AvailableModel(
                        id=model_name,
                        name=model_name.split(":")[0],  # 去掉标签部分
                        model_type="llm",
                        context_length=None,  # Ollama 不提供此信息
                        is_enabled=True
                    ))

                return AvailableModelsResponse(
                    success=True,
                    message=f"找到 {len(models)} 个本地模型",
                    models=models
                )

        except httpx.ConnectError:
            return AvailableModelsResponse(
                success=False,
                message="无法连接到 Ollama 服务，请确保 Ollama 正在运行",
                models=[]
            )
        except httpx.TimeoutException:
            return AvailableModelsResponse(
                success=False,
                message="连接 Ollama 服务超时",
                models=[]
            )

    # ============================================
    # Gemini
    # ============================================
    async def _fetch_gemini_models(
        self,
        api_key: Optional[str],
        base_url: Optional[str],
        config: Optional[Dict]
    ) -> AvailableModelsResponse:
        """获取 Google Gemini 模型列表"""
        if not api_key:
            return AvailableModelsResponse(
                success=False,
                message="缺少 API Key",
                models=[]
            )

        url = "https://generativelanguage.googleapis.com/v1beta/models"

        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.get(f"{url}?key={api_key}")

            if response.status_code != 200:
                return AvailableModelsResponse(
                    success=False,
                    message=f"API 请求失败: HTTP {response.status_code}",
                    models=[]
                )

            data = response.json()
            models_data = data.get("models", [])

            models = []
            for m in models_data:
                model_name = m.get("name", "")
                display_name = m.get("displayName", model_name)
                # 只保留 gemini 模型
                if "gemini" in model_name.lower():
                    # 从 models/gemini-pro 提取 gemini-pro
                    model_id = model_name.replace("models/", "")
                    input_limit = m.get("inputTokenLimit", 0)
                    models.append(AvailableModel(
                        id=model_id,
                        name=display_name,
                        model_type="llm",
                        context_length=input_limit,
                        is_enabled=True
                    ))

            return AvailableModelsResponse(
                success=True,
                message=f"找到 {len(models)} 个可用模型",
                models=models
            )

    # ============================================
    # Azure OpenAI
    # ============================================
    async def _fetch_azure_openai_models(
        self,
        api_key: Optional[str],
        base_url: Optional[str],
        config: Optional[Dict]
    ) -> AvailableModelsResponse:
        """获取 Azure OpenAI deployments 列表"""
        if not api_key or not base_url:
            return AvailableModelsResponse(
                success=False,
                message="缺少 API Key 或 Azure 资源 URL",
                models=[]
            )

        # base_url 格式: https://{resource-name}.openai.azure.com
        api_version = config.get("api_version", "2023-05-15") if config else "2023-05-15"
        headers = {"api-key": api_key}

        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.get(
                f"{base_url}/openai/deployments?api-version={api_version}",
                headers=headers
            )

            if response.status_code != 200:
                return AvailableModelsResponse(
                    success=False,
                    message=f"API 请求失败: HTTP {response.status_code}",
                    models=[]
                )

            data = response.json()
            deployments = data.get("data", [])

            models = []
            for d in deployments:
                deployment_id = d.get("id", "")
                model_name = d.get("model", deployment_id)
                models.append(AvailableModel(
                    id=deployment_id,
                    name=model_name,
                    model_type="llm",
                    context_length=self._get_openai_context_length(model_name),
                    is_enabled=True
                ))

            return AvailableModelsResponse(
                success=True,
                message=f"找到 {len(models)} 个 deployment",
                models=models
            )

    # ============================================
    # Amazon Bedrock
    # ============================================
    async def _fetch_bedrock_models(
        self,
        api_key: Optional[str],
        base_url: Optional[str],
        config: Optional[Dict]
    ) -> AvailableModelsResponse:
        """获取 Amazon Bedrock 可用模型列表"""
        # Bedrock 需要 AWS credentials，这里返回常用模型的硬编码列表
        # 实际生产环境需要使用 boto3 SDK
        bedrock_models = [
            {"id": "anthropic.claude-3-sonnet-20240229-v1:0", "name": "Claude 3 Sonnet (Bedrock)", "context_length": 200000},
            {"id": "anthropic.claude-3-haiku-20240307-v1:0", "name": "Claude 3 Haiku (Bedrock)", "context_length": 200000},
            {"id": "amazon.titan-text-express-v1", "name": "Titan Text Express", "context_length": 8000},
            {"id": "amazon.titan-text-lite-v1", "name": "Titan Text Lite", "context_length": 4000},
            {"id": "meta.llama3-8b-instruct-v1:0", "name": "Llama 3 8B Instruct", "context_length": 8000},
            {"id": "meta.llama3-70b-instruct-v1:0", "name": "Llama 3 70B Instruct", "context_length": 8000},
            {"id": "mistral.mistral-7b-instruct-v0:2", "name": "Mistral 7B Instruct", "context_length": 32000},
            {"id": "mistral.mixtral-8x7b-instruct-v0:1", "name": "Mixtral 8x7B Instruct", "context_length": 32000},
        ]

        models = [
            AvailableModel(
                id=m["id"],
                name=m["name"],
                model_type="llm",
                context_length=m["context_length"],
                is_enabled=True
            )
            for m in bedrock_models
        ]

        return AvailableModelsResponse(
            success=True,
            message=f"找到 {len(models)} 个可用模型（预设列表）",
            models=models
        )

    # ============================================
    # Hugging Face
    # ============================================
    async def _fetch_huggingface_models(
        self,
        api_key: Optional[str],
        base_url: Optional[str],
        config: Optional[Dict]
    ) -> AvailableModelsResponse:
        """获取 Hugging Face 可推理模型列表"""
        if not api_key:
            return AvailableModelsResponse(
                success=False,
                message="缺少 API Token",
                models=[]
            )

        headers = {"Authorization": f"Bearer {api_key}"}

        async with httpx.AsyncClient(timeout=30.0) as client:
            # 获取热门的文本生成模型
            response = await client.get(
                "https://huggingface.co/api/models",
                params={
                    "pipeline_tag": "text-generation",
                    "sort": "downloads",
                    "direction": "-1",
                    "limit": 20,
                },
                headers=headers
            )

            if response.status_code != 200:
                return AvailableModelsResponse(
                    success=False,
                    message=f"API 请求失败: HTTP {response.status_code}",
                    models=[]
                )

            models_data = response.json()

            models = []
            for m in models_data:
                model_id = m.get("modelId", "")
                # 过滤一些太大的模型
                models.append(AvailableModel(
                    id=model_id,
                    name=model_id.split("/")[-1],  # 只取模型名称部分
                    model_type="llm",
                    context_length=None,
                    is_enabled=True
                ))

            return AvailableModelsResponse(
                success=True,
                message=f"找到 {len(models)} 个可用模型",
                models=models
            )


# 单例导出
model_fetcher = ModelFetcher()
