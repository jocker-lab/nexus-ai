# -*- coding: utf-8 -*-
"""
@File    :   embedding_db.py
@Desc    :   Embedding 服务客户端封装
"""

from typing import Optional, Dict, Any, List
import httpx
from loguru import logger

from app.config import (
    EMBEDDING_API_URL,
    EMBEDDING_DIMENSION,
)


class EmbeddingClient:
    """Embedding 服务客户端封装类"""

    def __init__(self, api_url: Optional[str] = None):
        """
        初始化 Embedding 客户端

        Args:
            api_url: API 地址，默认使用配置中的 EMBEDDING_API_URL
        """
        self.api_url = api_url or EMBEDDING_API_URL
        self._client: Optional[httpx.AsyncClient] = None

    async def _get_client(self) -> httpx.AsyncClient:
        """获取 HTTP 客户端（懒加载）"""
        if self._client is None:
            self._client = httpx.AsyncClient(timeout=60.0)
        return self._client

    async def get_embedding(
        self,
        id: str,
        text: str,
    ) -> Optional[Dict[str, Any]]:
        """
        获取文本的 Embedding 向量

        Args:
            id: 文本标识符
            text: 要向量化的文本

        Returns:
            {"id": "...", "embedding": [...]} 或 None
        """
        if not text:
            logger.warning("[EmbeddingClient] 文本为空，跳过向量化")
            return None

        try:
            client = await self._get_client()

            payload = {
                "id": id,
                "text": text,
            }

            response = await client.post(
                self.api_url,
                json=payload,
            )

            if response.status_code != 200:
                logger.error(f"[EmbeddingClient] API 错误: {response.status_code}")
                return None

            result = response.json()

            # 验证返回的向量维度
            embedding = result.get("embedding", [])
            if len(embedding) != EMBEDDING_DIMENSION:
                logger.warning(
                    f"[EmbeddingClient] 向量维度不匹配: "
                    f"期望 {EMBEDDING_DIMENSION}, 实际 {len(embedding)}"
                )

            return result

        except httpx.TimeoutException:
            logger.error("[EmbeddingClient] 请求超时")
            return None
        except Exception as e:
            logger.error(f"[EmbeddingClient] 请求失败: {e}")
            return None

    async def get_embeddings_batch(
        self,
        texts: List[Dict[str, str]],
    ) -> List[Dict[str, Any]]:
        """
        批量获取 Embedding 向量

        Args:
            texts: 文本列表 [{"id": "...", "text": "..."}, ...]

        Returns:
            结果列表 [{"id": "...", "embedding": [...]}, ...]
        """
        results = []
        for item in texts:
            result = await self.get_embedding(
                id=item.get("id", ""),
                text=item.get("text", ""),
            )
            if result:
                results.append(result)

        return results

    async def close(self):
        """关闭 HTTP 客户端"""
        if self._client:
            await self._client.aclose()
            self._client = None
            logger.debug("[EmbeddingClient] HTTP 客户端已关闭")


# 兼容旧名称
SentimentEmbeddingClient = EmbeddingClient


# 全局单例
_embedding_client: Optional[EmbeddingClient] = None


def get_embedding_client(api_url: Optional[str] = None) -> EmbeddingClient:
    """
    获取 Embedding 客户端

    Args:
        api_url: API 地址，如果为 None 则返回默认单例

    Returns:
        EmbeddingClient 实例
    """
    global _embedding_client

    # 如果指定了 api_url，返回新实例
    if api_url is not None:
        return EmbeddingClient(api_url=api_url)

    # 否则返回默认单例
    if _embedding_client is None:
        _embedding_client = EmbeddingClient()

    return _embedding_client
