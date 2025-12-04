# -*- coding: utf-8 -*-
"""
@File    :   milvus_db.py
@Desc    :   Milvus 向量数据库客户端封装
"""

from typing import Optional, List, Dict, Any
from loguru import logger

from pymilvus import (
    connections,
    Collection,
    FieldSchema,
    CollectionSchema,
    DataType,
    utility,
)

from app.config import (
    MILVUS_HOST,
    MILVUS_PORT,
    MILVUS_COLLECTION,
    EMBEDDING_DIMENSION,
)


class MilvusClient:
    """Milvus 客户端封装类"""

    def __init__(self, collection_name: Optional[str] = None):
        """
        初始化 Milvus 客户端

        Args:
            collection_name: 集合名称，默认使用配置中的 MILVUS_COLLECTION
        """
        self.collection_name = collection_name or MILVUS_COLLECTION
        self.collection: Optional[Collection] = None
        self._initialized = False

    def initialize(self):
        """延迟初始化 Milvus 连接"""
        if self._initialized:
            return

        try:
            # 连接 Milvus
            logger.debug(f"Connecting to Milvus: {MILVUS_HOST}:{MILVUS_PORT}")
            connections.connect(
                alias="default",
                host=MILVUS_HOST,
                port=MILVUS_PORT,
            )

            # 确保集合存在
            self._ensure_collection_exists()

            self._initialized = True
            logger.info(f"Milvus client initialized: {self.collection_name}")

        except Exception as e:
            logger.error(f"Failed to initialize Milvus client: {e}")
            raise

    def _ensure_collection_exists(self):
        """确保集合存在，不存在则创建"""
        try:
            if utility.has_collection(self.collection_name):
                self.collection = Collection(self.collection_name)
                self.collection.load()
                logger.debug(f"Milvus collection loaded: {self.collection_name}")
            else:
                # 创建集合 schema
                fields = [
                    FieldSchema(
                        name="uuid",
                        dtype=DataType.VARCHAR,
                        max_length=64,
                        is_primary=True,
                    ),
                    FieldSchema(
                        name="embedding",
                        dtype=DataType.FLOAT_VECTOR,
                        dim=EMBEDDING_DIMENSION,
                    ),
                ]

                schema = CollectionSchema(
                    fields=fields,
                    description=f"Vector collection for {self.collection_name}",
                )

                self.collection = Collection(
                    name=self.collection_name,
                    schema=schema,
                )

                # 创建索引
                index_params = {
                    "metric_type": "COSINE",
                    "index_type": "IVF_FLAT",
                    "params": {"nlist": 128},
                }
                self.collection.create_index(
                    field_name="embedding",
                    index_params=index_params,
                )

                self.collection.load()
                logger.info(f"Created Milvus collection: {self.collection_name}")

        except Exception as e:
            logger.error(f"Error ensuring collection exists: {e}")
            raise

    def insert(self, uuid: str, embedding: List[float]) -> bool:
        """
        插入向量数据

        Args:
            uuid: 唯一标识符
            embedding: 向量数据

        Returns:
            是否成功
        """
        if not self._initialized:
            self.initialize()

        try:
            data = [
                [uuid],      # uuid 字段
                [embedding], # embedding 字段
            ]

            self.collection.insert(data)
            self.collection.flush()

            logger.debug(f"Inserted vector: {uuid}")
            return True

        except Exception as e:
            logger.error(f"Failed to insert vector: {e}")
            return False

    def search(
        self,
        query_vector: List[float],
        top_k: int = 5,
        threshold: Optional[float] = None,
    ) -> List[Dict[str, Any]]:
        """
        搜索相似向量

        Args:
            query_vector: 查询向量
            top_k: 返回前 k 个结果
            threshold: 相似度阈值（可选）

        Returns:
            搜索结果列表 [{"uuid": "...", "score": 0.9}, ...]
        """
        if not self._initialized:
            self.initialize()

        try:
            search_params = {
                "metric_type": "COSINE",
                "params": {"nprobe": 10},
            }

            results = self.collection.search(
                data=[query_vector],
                anns_field="embedding",
                param=search_params,
                limit=top_k,
                output_fields=["uuid"],
            )

            # 处理结果
            output = []
            for hits in results:
                for hit in hits:
                    score = hit.score
                    # 如果设置了阈值，过滤低于阈值的结果
                    if threshold is not None and score < threshold:
                        continue

                    output.append({
                        "uuid": hit.entity.get("uuid"),
                        "score": score,
                    })

            return output

        except Exception as e:
            logger.error(f"Failed to search vectors: {e}")
            return []

    def delete(self, uuid: str) -> bool:
        """
        删除向量

        Args:
            uuid: 要删除的向量 UUID

        Returns:
            是否成功
        """
        if not self._initialized:
            self.initialize()

        try:
            expr = f'uuid == "{uuid}"'
            self.collection.delete(expr)
            logger.debug(f"Deleted vector: {uuid}")
            return True

        except Exception as e:
            logger.error(f"Failed to delete vector: {e}")
            return False

    def close(self):
        """关闭连接"""
        try:
            connections.disconnect("default")
            self._initialized = False
            logger.debug("Milvus connection closed")
        except Exception as e:
            logger.error(f"Error closing Milvus connection: {e}")


# 全局单例（默认集合）
_milvus_client: Optional[MilvusClient] = None


def get_milvus_client(collection_name: Optional[str] = None) -> MilvusClient:
    """
    获取 Milvus 客户端

    Args:
        collection_name: 集合名称，如果为 None 则返回默认单例

    Returns:
        MilvusClient 实例
    """
    global _milvus_client

    # 如果指定了 collection_name，返回新实例
    if collection_name is not None:
        return MilvusClient(collection_name=collection_name)

    # 否则返回默认单例
    if _milvus_client is None:
        _milvus_client = MilvusClient()

    return _milvus_client
