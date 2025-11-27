# -*- coding: utf-8 -*-
"""
@File    :   milvus_client.py
@Time    :   2025/11/27
@Desc    :   Milvus 向量数据库客户端 - 用于存储和检索文档向量
"""

import os
import traceback
from typing import Optional, List, Dict, Any
from loguru import logger
from pymilvus import connections, Collection, FieldSchema, CollectionSchema, DataType, utility

# Milvus 配置（从环境变量读取，提供默认值）
MILVUS_HOST = os.getenv("MILVUS_HOST", "localhost")
MILVUS_PORT = os.getenv("MILVUS_PORT", "19530")
MILVUS_COLLECTION = os.getenv("MILVUS_COLLECTION", "document_vectors")

# 向量维度（与 embedding 服务一致）
VECTOR_DIM = 1536


class MilvusClient:
    """Milvus 客户端 - 文档向量存储与检索"""

    def __init__(
        self,
        host: str = MILVUS_HOST,
        port: str = MILVUS_PORT,
        collection_name: str = MILVUS_COLLECTION,
        vector_field: str = "embedding",
        metric_type: str = "COSINE",
    ):
        """
        初始化 Milvus 客户端

        Args:
            host: Milvus 服务器主机地址
            port: Milvus 服务器端口
            collection_name: 集合名称
            vector_field: 向量字段名称
            metric_type: 相似度度量类型
        """
        self.host = host
        self.port = port
        self.collection_name = collection_name
        self.vector_field = vector_field
        self.metric_type = metric_type
        self.client: Optional[Collection] = None
        self._connected = False

        logger.debug(
            f"初始化 MilvusClient: host={host}, port={port}, "
            f"collection={collection_name}, metric_type={metric_type}"
        )

    def connect(self):
        """建立与 Milvus 服务器的连接"""
        if self._connected:
            return

        logger.info(f"尝试连接到 Milvus 服务器: {self.host}:{self.port}")
        try:
            connections.connect(alias="default", host=self.host, port=self.port)
            self._connected = True
            logger.info(f"成功连接到 Milvus 服务器: {self.host}:{self.port}")
        except Exception as e:
            logger.error(f"连接 Milvus 服务器失败: {str(e)}\n{traceback.format_exc()}")
            raise

    def create_collection(self, dim: int = VECTOR_DIM, index_type: str = "IVF_FLAT", index_params: dict = None):
        """
        创建集合并建立索引

        Args:
            dim: 向量维度
            index_type: 索引类型
            index_params: 索引参数
        """
        if not self._connected:
            self.connect()

        logger.info(f"创建集合: {self.collection_name}, 维度={dim}, 索引类型={index_type}")

        try:
            # 检查集合是否存在
            if utility.has_collection(self.collection_name):
                logger.info(f"集合 {self.collection_name} 已存在，加载现有集合")
                self.client = Collection(self.collection_name)
                self.client.load()
                return

            # 定义 schema：只有 uuid 和 embedding
            fields = [
                FieldSchema(name="uuid", dtype=DataType.VARCHAR, is_primary=True, max_length=64),
                FieldSchema(name="embedding", dtype=DataType.FLOAT_VECTOR, dim=dim),
            ]
            schema = CollectionSchema(fields=fields, description="Document vectors for semantic retrieval")

            # 创建集合
            self.client = Collection(self.collection_name, schema)
            logger.info(f"成功创建集合: {self.collection_name}")

            # 设置默认索引参数
            if index_params is None:
                if index_type == "HNSW":
                    index_params = {"M": 16, "efConstruction": 200}
                elif index_type == "IVF_FLAT":
                    index_params = {"nlist": 128}
                else:
                    index_params = {"nlist": 128}

            # 创建索引
            index = {
                "index_type": index_type,
                "metric_type": self.metric_type,
                "params": index_params,
            }
            self.client.create_index(field_name=self.vector_field, index_params=index)
            logger.info(f"成功为字段 {self.vector_field} 创建 {index_type} 索引")

            # 加载集合到内存
            self.client.load()

        except Exception as e:
            logger.error(f"创建集合失败: {str(e)}\n{traceback.format_exc()}")
            raise

    def insert(self, uuid: str, embedding: List[float]) -> bool:
        """
        插入单条数据

        Args:
            uuid: 文档唯一标识，关联 SQL 数据库
            embedding: 向量

        Returns:
            是否成功
        """
        if not self._connected:
            self.connect()

        if self.client is None:
            self.create_collection()

        logger.info(f"插入向量: uuid={uuid}, 维度={len(embedding)}")

        try:
            entities = [
                [uuid],
                [embedding],
            ]
            self.client.insert(entities)
            self.client.flush()
            logger.info(f"成功插入向量: {uuid}")
            return True

        except Exception as e:
            logger.error(f"插入向量失败: {str(e)}\n{traceback.format_exc()}")
            return False

    def search(
        self,
        query_vector: List[float],
        top_k: int = 5,
        threshold: Optional[float] = None,
    ) -> List[Dict[str, Any]]:
        """
        向量检索

        Args:
            query_vector: 查询向量
            top_k: 返回前 k 个结果
            threshold: 相似度阈值（0-1），低于此值的结果会被过滤

        Returns:
            检索结果列表，每项包含 uuid 和 score
        """
        if not self._connected:
            self.connect()

        if self.client is None:
            self.create_collection()

        logger.info(f"搜索向量: top_k={top_k}, threshold={threshold}")

        try:
            # 确保集合已加载
            self.client.load()

            search_params = {
                "metric_type": self.metric_type,
                "params": {"nprobe": 10},
            }

            results = self.client.search(
                data=[query_vector],
                anns_field=self.vector_field,
                param=search_params,
                limit=top_k,
                output_fields=["uuid"],
            )

            # 转换结果格式并应用阈值过滤
            output = []
            for hits in results:
                for hit in hits:
                    score = hit.score
                    if threshold is not None and score < threshold:
                        continue
                    output.append({
                        "uuid": hit.entity.get("uuid"),
                        "score": score,
                    })

            logger.info(f"搜索完成，返回 {len(output)} 个结果")
            return output

        except Exception as e:
            logger.error(f"搜索失败: {str(e)}\n{traceback.format_exc()}")
            return []

    def delete(self, uuid: str) -> bool:
        """
        删除单条数据

        Args:
            uuid: 文档唯一标识

        Returns:
            是否成功
        """
        if not self._connected:
            self.connect()

        try:
            self.client.delete(expr=f'uuid == "{uuid}"')
            logger.info(f"成功删除向量: {uuid}")
            return True

        except Exception as e:
            logger.error(f"删除失败: {str(e)}\n{traceback.format_exc()}")
            return False

    def exists(self, uuid: str) -> bool:
        """
        检查 uuid 是否存在

        Args:
            uuid: 文档唯一标识

        Returns:
            是否存在
        """
        if not self._connected:
            self.connect()

        try:
            results = self.client.query(
                expr=f'uuid == "{uuid}"',
                output_fields=["uuid"],
            )
            return len(results) > 0

        except Exception as e:
            logger.error(f"检查存在性失败: {str(e)}\n{traceback.format_exc()}")
            return False

    def close(self):
        """关闭连接"""
        if self._connected:
            connections.disconnect("default")
            self._connected = False
            logger.debug("已断开 Milvus 连接")


# 全局单例
_milvus_client: Optional[MilvusClient] = None


def get_milvus_client() -> MilvusClient:
    """获取 Milvus 客户端单例"""
    global _milvus_client
    if _milvus_client is None:
        _milvus_client = MilvusClient()
    return _milvus_client
