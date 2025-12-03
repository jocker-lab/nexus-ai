# -*- coding: utf-8 -*-
"""
@File    :   sentiment_embedding_client.py
@Time    :   2025/5/29 10:33
@Author  :   pygao
@Version :   1.0
@Contact :   pygao.1@outlook.com
@License :   (C)Copyright 2025, GienTech Technology Co.,Ltd. All rights reserved.
@Desc    :   文件描述
"""

import aiohttp
import asyncio
from loguru import logger
from typing import List, Dict, Optional, Tuple


class SentimentEmbeddingClient:
    """舆情向量嵌入客户端，用于向 FastAPI 服务请求文本嵌入向量。"""

    def __init__(self, base_url: str = "http://117.83.83.32:8090", timeout: int = 90, retries: int = 4):
        """
        初始化舆情向量嵌入客户端。

        Args:
            base_url (str): FastAPI 服务的基础 URL，默认 "http://117.83.83.32:8090"
            timeout (int): 请求超时时间（秒），默认 30
            retries (int): 重试次数，默认 3
        """
        self.base_url = base_url.rstrip('/')
        self.endpoint = f"{self.base_url}/compute-sentiment-vector"
        self.timeout = timeout
        self.retries = retries
        logger.debug(f"初始化 SentimentEmbeddingClient: base_url={self.base_url}, timeout={timeout}秒, retries={retries}")

    async def get_embedding(self, id: str, text: str, session: Optional[aiohttp.ClientSession] = None) -> Optional[Dict[str, any]]:
        """
        获取单个文本的嵌入向量。

        Args:
            id (str): 文本的唯一标识符
            text (str): 要嵌入的文本
            session (Optional[aiohttp.ClientSession]): HTTP 会话，如果为 None 则创建新会话

        Returns:
            Optional[Dict[str, any]]: 包含 ID 和嵌入向量的字典，失败时返回 None

        Raises:
            ValueError: 如果输入参数无效
        """
        if not id or not text:
            logger.error("ID 或文本为空")
            raise ValueError("ID 和文本均不能为空")

        # 构造请求体
        payload = {"id": id, "text": text}
        logger.info(f"请求嵌入向量，ID: {id}，文本长度: {len(text)}")

        # 创建或使用会话
        own_session = False
        if session is None:
            session = aiohttp.ClientSession(timeout=aiohttp.ClientTimeout(total=self.timeout))
            own_session = True

        try:
            for attempt in range(self.retries):
                try:
                    logger.debug(f"发送请求，尝试 {attempt + 1}/{self.retries}，URL: {self.endpoint}，负载: {payload}")
                    async with session.post(self.endpoint, json=payload) as response:
                        response.raise_for_status()
                        data = await response.json()
                        logger.info(f"成功获取嵌入向量，ID: {id}，向量维度: {len(data['embedding'])}")
                        return data
                except (aiohttp.ClientConnectionError, asyncio.TimeoutError) as e:
                    logger.warning(f"尝试 {attempt + 1}/{self.retries} 失败，ID: {id}，错误: {str(e)}")
                    if attempt == self.retries - 1:
                        logger.error(f"获取嵌入向量失败，ID: {id}，错误: {str(e)}")
                        return None
                    await asyncio.sleep(2 ** attempt)  # Exponential backoff
                except aiohttp.ClientResponseError as e:
                    logger.error(f"获取嵌入向量失败，ID: {id}，HTTP 错误: 状态码 {e.status} - {e.message}")
                    return None
                except Exception as e:
                    logger.error(f"获取嵌入向量失败，ID: {id}，未知错误: {type(e).__name__} - {str(e)}")
                    return None

        finally:
            if own_session:
                await session.close()
                logger.debug("关闭自创建的 HTTP 会话")

    async def get_batch_embeddings(self, texts: List[Tuple[str, str]]) -> List[Optional[Dict[str, any]]]:
        """
        批量获取多个文本的嵌入向量。

        Args:
            texts (List[Tuple[str, str]]): 包含 (id, text) 元组的列表

        Returns:
            List[Optional[Dict[str, any]]]: 每个文本的嵌入向量结果列表，失败的项为 None
        """
        if not texts:
            logger.error("文本列表为空")
            raise ValueError("文本列表不能为空")

        logger.info(f"开始批量请求嵌入向量，文本数量: {len(texts)}")
        async with aiohttp.ClientSession(timeout=aiohttp.ClientTimeout(total=self.timeout)) as session:
            tasks = [
                self.get_embedding(id, text, session)
                for id, text in texts
            ]
            results = await asyncio.gather(*tasks, return_exceptions=True)
            logger.info(
                f"批量请求完成，成功: {sum(1 for r in results if r is not None)}，失败: {sum(1 for r in results if r is None)}")
            return results
