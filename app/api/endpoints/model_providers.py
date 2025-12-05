
"""
Model Provider API Endpoints
模型供应商配置管理 API
"""

from typing import List, Optional
from fastapi import APIRouter, HTTPException, status
from loguru import logger
import httpx

from app.curd.model_providers import ModelProviders
from app.schemas.model_providers import (
    ModelProviderResponse,
    ModelProviderCreateForm,
    ModelProviderUpdateForm,
    OllamaCreateForm,
    OllamaUpdateForm,
    ConnectionTestRequest,
    ConnectionTestResponse,
    OllamaDetectResponse,
    OllamaLocalModel,
    ProviderType,
    ModelType,
    AvailableModelsResponse,
)

router = APIRouter()


# ===================== List/Get Endpoints =====================

@router.get("", response_model=List[ModelProviderResponse])
@router.get("/", response_model=List[ModelProviderResponse])
async def get_user_providers(
    user_id: str = "user-123",
    provider_type: Optional[str] = None,
    active_only: bool = False
):
    """
    获取用户的所有模型供应商配置

    Args:
        user_id: 用户 ID
        provider_type: 可选，按供应商类型筛选
        active_only: 是否只返回启用的供应商
    """
    try:
        if provider_type:
            providers = ModelProviders.get_providers_by_user_and_type(
                user_id, provider_type, active_only
            )
        else:
            providers = ModelProviders.get_providers_by_user_id(user_id, active_only)

        return [ModelProviderResponse.from_model(p) for p in providers]

    except Exception as e:
        logger.exception(f"Failed to get providers: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )


@router.get("/{provider_id}", response_model=ModelProviderResponse)
async def get_provider(provider_id: str, user_id: str = "user-123"):
    """获取指定的供应商配置"""
    provider = ModelProviders.get_provider_by_id_and_user_id(provider_id, user_id)

    if not provider:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Provider not found"
        )

    return ModelProviderResponse.from_model(provider)


@router.get("/default/{provider_type}", response_model=Optional[ModelProviderResponse])
async def get_default_provider(provider_type: str, user_id: str = "user-123"):
    """获取指定类型的默认供应商"""
    provider = ModelProviders.get_default_provider_by_type(user_id, provider_type)

    if provider:
        return ModelProviderResponse.from_model(provider)
    return None


# ===================== Create Endpoints =====================

@router.post("", response_model=ModelProviderResponse, status_code=status.HTTP_201_CREATED)
@router.post("/", response_model=ModelProviderResponse, status_code=status.HTTP_201_CREATED)
async def create_provider(form_data: ModelProviderCreateForm, user_id: str = "user-123"):
    """
    创建新的模型供应商配置

    Args:
        form_data: 供应商配置表单
        user_id: 用户 ID
    """
    provider = ModelProviders.create_provider(user_id, form_data)

    if not provider:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Failed to create provider"
        )

    return ModelProviderResponse.from_model(provider)


@router.post("/ollama", response_model=ModelProviderResponse, status_code=status.HTTP_201_CREATED)
async def create_ollama_provider(form_data: OllamaCreateForm, user_id: str = "user-123"):
    """
    创建 Ollama 专用供应商配置

    Args:
        form_data: Ollama 配置表单
        user_id: 用户 ID
    """
    provider = ModelProviders.create_ollama_provider(user_id, form_data)

    if not provider:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Failed to create Ollama provider"
        )

    return ModelProviderResponse.from_model(provider)


# ===================== Update Endpoints =====================

@router.put("/{provider_id}", response_model=ModelProviderResponse)
async def update_provider(
    provider_id: str,
    form_data: ModelProviderUpdateForm,
    user_id: str = "user-123"
):
    """更新供应商配置"""
    provider = ModelProviders.update_provider(provider_id, user_id, form_data)

    if not provider:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Provider not found"
        )

    return ModelProviderResponse.from_model(provider)


@router.put("/ollama/{provider_id}", response_model=ModelProviderResponse)
async def update_ollama_provider(
    provider_id: str,
    form_data: OllamaUpdateForm,
    user_id: str = "user-123"
):
    """更新 Ollama 供应商配置"""
    provider = ModelProviders.update_ollama_provider(provider_id, user_id, form_data)

    if not provider:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Ollama provider not found"
        )

    return ModelProviderResponse.from_model(provider)


@router.post("/{provider_id}/toggle", response_model=ModelProviderResponse)
async def toggle_provider(provider_id: str, user_id: str = "user-123"):
    """切换供应商启用状态"""
    provider = ModelProviders.toggle_provider_active(provider_id, user_id)

    if not provider:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Provider not found"
        )

    return ModelProviderResponse.from_model(provider)


@router.post("/{provider_id}/default", response_model=ModelProviderResponse)
async def set_default(provider_id: str, user_id: str = "user-123"):
    """设置供应商为默认"""
    provider = ModelProviders.set_default_provider(provider_id, user_id)

    if not provider:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Provider not found"
        )

    return ModelProviderResponse.from_model(provider)


# ===================== Delete Endpoints =====================

@router.delete("/{provider_id}", response_model=bool)
async def delete_provider(provider_id: str, user_id: str = "user-123"):
    """删除供应商配置"""
    success = ModelProviders.delete_provider(provider_id, user_id)

    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Provider not found"
        )

    return True


# ===================== Connection Test Endpoints =====================

@router.post("/test-connection", response_model=ConnectionTestResponse)
async def test_connection(request: ConnectionTestRequest):
    """
    测试供应商连接（未保存的配置）

    对于 Ollama，会返回本地模型列表
    """
    try:
        if request.provider_type == ProviderType.OLLAMA:
            return await _test_ollama_connection(request.base_url or "http://localhost:11434")

        # 其他供应商的测试逻辑
        # TODO: 实现其他供应商的连接测试
        return ConnectionTestResponse(
            success=True,
            message="Connection test not implemented for this provider yet"
        )

    except Exception as e:
        logger.exception(f"Connection test failed: {e}")
        return ConnectionTestResponse(
            success=False,
            message=str(e)
        )


@router.post("/{provider_id}/test", response_model=ConnectionTestResponse)
async def test_saved_provider(provider_id: str, user_id: str = "user-123"):
    """测试已保存的供应商连接"""
    provider = ModelProviders.get_provider_by_id_and_user_id(provider_id, user_id)

    if not provider:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Provider not found"
        )

    try:
        if provider.provider_type == ProviderType.OLLAMA.value:
            result = await _test_ollama_connection(
                provider.base_url or "http://localhost:11434"
            )
        else:
            # TODO: 实现其他供应商的连接测试
            result = ConnectionTestResponse(
                success=True,
                message="Connection test not implemented for this provider yet"
            )

        # 更新连接状态
        status_value = "connected" if result.success else "failed"
        ModelProviders.update_connection_status(provider_id, status_value)

        return result

    except Exception as e:
        logger.exception(f"Connection test failed: {e}")
        ModelProviders.update_connection_status(provider_id, "failed")
        return ConnectionTestResponse(
            success=False,
            message=str(e)
        )


# ===================== Available Models Endpoints =====================

@router.get("/{provider_id}/models", response_model=AvailableModelsResponse)
async def get_available_models(provider_id: str, user_id: str = "user-123"):
    """
    获取指定供应商的可用模型列表

    从供应商 API 动态获取可用模型：
    - OpenAI: GET https://api.openai.com/v1/models
    - DeepSeek: GET https://api.deepseek.com/models
    - Anthropic: 硬编码列表
    - Ollama: GET {base_url}/api/tags
    - 等...
    """
    from app.services.model_fetcher import model_fetcher

    # 获取供应商配置
    provider = ModelProviders.get_provider_by_id_and_user_id(provider_id, user_id)

    if not provider:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Provider not found"
        )

    # 调用模型获取服务
    result = await model_fetcher.fetch_models(
        provider_type=provider.provider_type,
        api_key=provider.api_key,
        base_url=provider.base_url,
        provider_config=provider.provider_config
    )

    return result


# ===================== Ollama-specific Endpoints =====================

@router.get("/ollama/detect-models", response_model=OllamaDetectResponse)
async def detect_ollama_models(base_url: str = "http://localhost:11434"):
    """
    检测 Ollama 本地已安装的模型

    Args:
        base_url: Ollama 服务地址
    """
    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            response = await client.get(f"{base_url}/api/tags")

            if response.status_code != 200:
                return OllamaDetectResponse(
                    success=False,
                    message=f"Failed to connect to Ollama: HTTP {response.status_code}",
                    models=[]
                )

            data = response.json()
            models_data = data.get("models", [])

            models = []
            for m in models_data:
                details = m.get("details", {})
                model = OllamaLocalModel(
                    id=m.get("name", ""),
                    name=m.get("name", "").split(":")[0],  # 去掉标签部分作为显示名
                    model_type=ModelType.LLM,  # 默认为 LLM
                    context_length=None,
                    size=_format_size(m.get("size", 0)),
                    parameter_size=details.get("parameter_size"),
                    quantization_level=details.get("quantization_level"),
                )
                models.append(model)

            return OllamaDetectResponse(
                success=True,
                message=f"Found {len(models)} local models",
                models=models
            )

    except httpx.ConnectError:
        return OllamaDetectResponse(
            success=False,
            message="无法连接到 Ollama 服务，请确保 Ollama 正在运行",
            models=[]
        )
    except httpx.TimeoutException:
        return OllamaDetectResponse(
            success=False,
            message="连接 Ollama 服务超时",
            models=[]
        )
    except Exception as e:
        logger.exception(f"Failed to detect Ollama models: {e}")
        return OllamaDetectResponse(
            success=False,
            message=str(e),
            models=[]
        )


# ===================== Helper Functions =====================

async def _test_ollama_connection(base_url: str) -> ConnectionTestResponse:
    """测试 Ollama 连接并返回模型列表"""
    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            response = await client.get(f"{base_url}/api/tags")

            if response.status_code != 200:
                return ConnectionTestResponse(
                    success=False,
                    message=f"HTTP {response.status_code}"
                )

            data = response.json()
            models = data.get("models", [])

            return ConnectionTestResponse(
                success=True,
                message=f"Connected. Found {len(models)} models.",
                models=[{
                    "name": m.get("name"),
                    "size": _format_size(m.get("size", 0)),
                    "modified_at": m.get("modified_at")
                } for m in models]
            )

    except httpx.ConnectError:
        return ConnectionTestResponse(
            success=False,
            message="无法连接到 Ollama 服务"
        )
    except httpx.TimeoutException:
        return ConnectionTestResponse(
            success=False,
            message="连接超时"
        )
    except Exception as e:
        return ConnectionTestResponse(
            success=False,
            message=str(e)
        )


def _format_size(bytes_size: int) -> str:
    """格式化文件大小"""
    if bytes_size == 0:
        return "0 B"

    gb = bytes_size / (1024 * 1024 * 1024)
    if gb >= 1:
        return f"{gb:.1f} GB"

    mb = bytes_size / (1024 * 1024)
    return f"{mb:.0f} MB"
