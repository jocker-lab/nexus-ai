# -*- coding: utf-8 -*-
"""
@File    :   minio_db.py
@Time    :   2025/10/23 09:17
@Author  :   pygao
@Version :   1.0
@Contact :   pygao.1@outlook.com
@License :   (C)Copyright 2025, GienTech Technology Co.,Ltd. All rights reserved.
@Desc    :   MinIO对象存储客户端封装
"""

import io
from typing import Optional
from datetime import timedelta
from minio import Minio
from minio.error import S3Error
from loguru import logger

from app.config import (
    MINIO_ENDPOINT,
    MINIO_ACCESS_KEY,
    MINIO_SECRET_KEY,
    MINIO_BUCKET,
    MINIO_SECURE,
)


class MinIOClient:
    """MinIO客户端封装类"""

    def __init__(self):
        """初始化MinIO客户端"""
        self.client: Optional[Minio] = None
        self.bucket_name: str = MINIO_BUCKET
        self._initialized = False

    def initialize(self):
        """延迟初始化MinIO连接"""
        if self._initialized:
            return

        try:
            # 从统一配置系统获取配置
            logger.debug(f"Initializing MinIO client with endpoint: {MINIO_ENDPOINT}")

            # 创建MinIO客户端
            self.client = Minio(
                endpoint=MINIO_ENDPOINT,
                access_key=MINIO_ACCESS_KEY,
                secret_key=MINIO_SECRET_KEY,
                secure=MINIO_SECURE
            )

            # 确保bucket存在
            self._ensure_bucket_exists()

            self._initialized = True
            logger.info(f"MinIO client initialized successfully: {MINIO_ENDPOINT}/{self.bucket_name}")

        except Exception as e:
            logger.error(f"Failed to initialize MinIO client: {e}")
            raise

    def _ensure_bucket_exists(self):
        """确保bucket存在，不存在则创建"""
        try:
            if not self.client.bucket_exists(self.bucket_name):
                self.client.make_bucket(self.bucket_name)
                logger.info(f"Created MinIO bucket: {self.bucket_name}")
            else:
                logger.debug(f"MinIO bucket already exists: {self.bucket_name}")
        except S3Error as e:
            logger.error(f"Error checking/creating bucket: {e}")
            raise

    def upload_chart(
        self,
        file_data: bytes,
        report_id: str,
        filename: str,
        content_type: str = "image/png"
    ) -> str:
        """
        上传图表文件到MinIO

        Args:
            file_data: 图片的二进制数据
            report_id: 报告ID，用于组织文件路径
            filename: 文件名
            content_type: MIME类型

        Returns:
            str: MinIO中的对象URL
        """
        if not self._initialized:
            self.initialize()

        try:
            # 构造对象路径: reports/{report_id}/charts/{filename}
            object_name = f"reports/{report_id}/charts/{filename}"

            # 创建字节流
            file_stream = io.BytesIO(file_data)
            file_size = len(file_data)

            # 上传文件
            self.client.put_object(
                bucket_name=self.bucket_name,
                object_name=object_name,
                data=file_stream,
                length=file_size,
                content_type=content_type
            )

            # 生成访问URL
            url = self._get_object_url(object_name)
            logger.info(f"Uploaded chart to MinIO: {url}")
            return url

        except S3Error as e:
            logger.error(f"Failed to upload chart to MinIO: {e}")
            raise

    def _get_object_url(self, object_name: str) -> str:
        """
        获取对象的访问URL

        Args:
            object_name: MinIO中的对象名称

        Returns:
            str: 访问URL
        """
        # 对于公开访问的bucket，直接返回HTTP URL
        endpoint = self.client._base_url._url.netloc
        scheme = "https" if self.client._base_url._url.scheme == "https" else "http"
        return f"{scheme}://{endpoint}/{self.bucket_name}/{object_name}"

    def get_presigned_url(self, object_name: str, expires: int = 3600) -> str:
        """
        获取对象的预签名URL（临时访问链接）

        Args:
            object_name: MinIO中的对象名称
            expires: 过期时间（秒），默认1小时

        Returns:
            str: 预签名URL
        """
        if not self._initialized:
            self.initialize()

        try:
            url = self.client.presigned_get_object(
                bucket_name=self.bucket_name,
                object_name=object_name,
                expires=timedelta(seconds=expires)
            )
            return url
        except S3Error as e:
            logger.error(f"Failed to generate presigned URL: {e}")
            raise

    def delete_chart(self, object_name: str) -> bool:
        """
        删除MinIO中的图表文件

        Args:
            object_name: 对象名称或完整URL

        Returns:
            bool: 删除是否成功
        """
        if not self._initialized:
            self.initialize()

        try:
            # 如果传入的是完整URL，提取object_name
            if object_name.startswith('http'):
                # 格式: http://endpoint/bucket/object_name
                parts = object_name.split(f"/{self.bucket_name}/", 1)
                if len(parts) == 2:
                    object_name = parts[1]
                else:
                    logger.error(f"Invalid MinIO URL format: {object_name}")
                    return False

            self.client.remove_object(
                bucket_name=self.bucket_name,
                object_name=object_name
            )
            logger.info(f"Deleted chart from MinIO: {object_name}")
            return True

        except S3Error as e:
            logger.error(f"Failed to delete chart from MinIO: {e}")
            return False

    def delete_report_charts(self, report_id: str) -> int:
        """
        删除某个报告的所有图表

        Args:
            report_id: 报告ID

        Returns:
            int: 删除的文件数量
        """
        if not self._initialized:
            self.initialize()

        try:
            prefix = f"reports/{report_id}/charts/"
            objects = self.client.list_objects(
                bucket_name=self.bucket_name,
                prefix=prefix,
                recursive=True
            )

            count = 0
            for obj in objects:
                self.client.remove_object(
                    bucket_name=self.bucket_name,
                    object_name=obj.object_name
                )
                count += 1

            logger.info(f"Deleted {count} charts for report {report_id}")
            return count

        except S3Error as e:
            logger.error(f"Failed to delete report charts: {e}")
            return 0


# 全局单例
_minio_client = None


def get_minio_client() -> MinIOClient:
    """获取MinIO客户端单例"""
    global _minio_client
    if _minio_client is None:
        _minio_client = MinIOClient()
    return _minio_client


# 便捷函数
def upload_chart(file_data: bytes, report_id: str, filename: str, content_type: str = "image/png") -> str:
    """上传图表到MinIO的便捷函数"""
    client = get_minio_client()
    return client.upload_chart(file_data, report_id, filename, content_type)


def delete_chart(object_name: str) -> bool:
    """删除图表的便捷函数"""
    client = get_minio_client()
    return client.delete_chart(object_name)


def delete_report_charts(report_id: str) -> int:
    """删除报告所有图表的便捷函数"""
    client = get_minio_client()
    return client.delete_report_charts(report_id)
