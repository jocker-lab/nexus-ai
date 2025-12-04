# -*- coding: utf-8 -*-
"""
@File    :   documents.py
@Time    :   2025/12/03
@Author  :   Claude Code
@Version :   2.0
@Desc    :   文档CRUD操作（从 reports.py 重命名）- 支持版本管理和交互式生成
"""
import uuid
import time
from typing import Optional, List
from datetime import datetime
from sqlalchemy import desc, and_
from sqlalchemy.orm import Session

from app.models.documents import Document, DocumentVersion, DocumentStatus, ChangeType
from app.database.db import get_db_context
from loguru import logger


class DocumentTable:
    """文档表CRUD操作"""

    # ==================== 创建（Create） ====================

    def create_document(
        self,
        user_id: str,
        title: str,
        content: str = "",
        description: Optional[str] = None,
        chat_id: Optional[str] = None,
        outline: Optional[dict] = None,
        category: Optional[str] = None,
        tags: Optional[str] = None,
        status: DocumentStatus = DocumentStatus.DRAFT
    ) -> Optional[Document]:
        """
        创建新文档

        Args:
            user_id: 用户ID
            title: 文档标题
            content: Markdown内容（默认为空）
            description: 文档描述
            chat_id: 关联的会话ID
            outline: 章节大纲JSON
            category: 分类
            tags: 标签（逗号分隔）
            status: 文档状态

        Returns:
            创建的Document对象，失败返回None
        """
        try:
            with get_db_context() as db:
                document_id = str(uuid.uuid4())
                document = Document(
                    id=document_id,
                    user_id=user_id,
                    title=title,
                    content=content if content else "",
                    description=description,
                    chat_id=chat_id,
                    outline=outline,
                    category=category,
                    tags=tags,
                    status=status,
                    current_version=1,
                    is_manually_edited=False,
                    word_count=len(content) if content else 0,
                    estimated_reading_time=self._calculate_reading_time(content) if content else 0
                )
                db.add(document)
                db.commit()
                db.refresh(document)

                # 创建初始版本
                self._create_version(
                    db=db,
                    document=document,
                    change_type=ChangeType.AI_GENERATED,
                    changed_by="ai",
                    change_summary="初始版本"
                )

                logger.info(f"Created document: {document_id} for user: {user_id}")
                return document
        except Exception as e:
            logger.error(f"Failed to create document: {e}")
            return None

    # ==================== 读取（Read） ====================

    def get_document_by_id(self, document_id: str) -> Optional[Document]:
        """根据ID获取文档"""
        try:
            with get_db_context() as db:
                return db.query(Document).filter(Document.id == document_id).first()
        except Exception as e:
            logger.error(f"Failed to get document {document_id}: {e}")
            return None

    def get_document_by_id_and_user_id(self, document_id: str, user_id: str) -> Optional[Document]:
        """根据文档ID和用户ID获取文档（权限验证）"""
        try:
            with get_db_context() as db:
                return db.query(Document).filter(
                    and_(Document.id == document_id, Document.user_id == user_id)
                ).first()
        except Exception as e:
            logger.error(f"Failed to get document {document_id} for user {user_id}: {e}")
            return None

    def get_documents_by_user_id(
        self,
        user_id: str,
        status: Optional[DocumentStatus] = None,
        limit: int = 50,
        offset: int = 0
    ) -> List[Document]:
        """
        获取用户的所有文档列表

        Args:
            user_id: 用户ID
            status: 筛选状态（可选）
            limit: 返回数量限制
            offset: 偏移量

        Returns:
            文档列表
        """
        try:
            with get_db_context() as db:
                query = db.query(Document).filter(Document.user_id == user_id)

                if status:
                    query = query.filter(Document.status == status)

                return query.order_by(desc(Document.updated_at)).limit(limit).offset(offset).all()
        except Exception as e:
            logger.error(f"Failed to get documents for user {user_id}: {e}")
            return []

    def get_document_by_chat_id(self, chat_id: str) -> Optional[Document]:
        """根据会话ID获取关联的文档"""
        try:
            with get_db_context() as db:
                return db.query(Document).filter(Document.chat_id == chat_id).first()
        except Exception as e:
            logger.error(f"Failed to get document by chat_id {chat_id}: {e}")
            return None

    # ==================== 更新（Update） ====================

    def update_document(
        self,
        document_id: str,
        user_id: str,
        title: Optional[str] = None,
        content: Optional[str] = None,
        description: Optional[str] = None,
        outline: Optional[dict] = None,
        status: Optional[DocumentStatus] = None,
        category: Optional[str] = None,
        tags: Optional[str] = None,
        change_summary: Optional[str] = None,
        changed_by: str = "user"
    ) -> Optional[Document]:
        """
        更新文档（会创建新版本）

        Args:
            document_id: 文档ID
            user_id: 用户ID（权限验证）
            title/content/description/outline/status/category/tags: 更新字段
            change_summary: 变更摘要
            changed_by: 变更来源 ("ai" or "user")

        Returns:
            更新后的Document对象
        """
        try:
            with get_db_context() as db:
                document = db.query(Document).filter(
                    and_(Document.id == document_id, Document.user_id == user_id)
                ).first()

                if not document:
                    logger.warning(f"Document {document_id} not found or access denied")
                    return None

                # 更新字段
                if title is not None:
                    document.title = title
                if content is not None:
                    document.content = content
                    document.word_count = len(content)
                    document.estimated_reading_time = self._calculate_reading_time(content)
                if description is not None:
                    document.description = description
                if outline is not None:
                    document.outline = outline
                if status is not None:
                    document.status = status
                if category is not None:
                    document.category = category
                if tags is not None:
                    document.tags = tags

                # 版本管理
                if changed_by == "user":
                    document.is_manually_edited = True

                document.current_version += 1

                db.commit()
                db.refresh(document)

                # 创建版本快照
                change_type = ChangeType.MANUAL_EDIT if changed_by == "user" else ChangeType.AI_GENERATED
                self._create_version(
                    db=db,
                    document=document,
                    change_type=change_type,
                    changed_by=changed_by,
                    user_id=user_id if changed_by == "user" else None,
                    change_summary=change_summary
                )

                logger.info(f"Updated document {document_id} to version {document.current_version}")
                return document
        except Exception as e:
            logger.error(f"Failed to update document {document_id}: {e}")
            return None

    def update_outline(self, document_id: str, outline: dict) -> Optional[Document]:
        """仅更新章节大纲（不创建版本）"""
        try:
            with get_db_context() as db:
                document = db.query(Document).filter(Document.id == document_id).first()
                if document:
                    document.outline = outline
                    db.commit()
                    db.refresh(document)
                    logger.info(f"Updated outline for document {document_id}")
                return document
        except Exception as e:
            logger.error(f"Failed to update outline for {document_id}: {e}")
            return None

    def publish_document(self, document_id: str, user_id: str) -> Optional[Document]:
        """发布文档（状态变更为PUBLISHED）"""
        try:
            with get_db_context() as db:
                document = db.query(Document).filter(
                    and_(Document.id == document_id, Document.user_id == user_id)
                ).first()

                if not document:
                    return None

                document.status = DocumentStatus.PUBLISHED
                document.published_at = datetime.now()
                document.current_version += 1

                db.commit()
                db.refresh(document)

                # 创建发布版本
                self._create_version(
                    db=db,
                    document=document,
                    change_type=ChangeType.STATUS_CHANGED,
                    changed_by="user",
                    user_id=user_id,
                    change_summary="文档已发布"
                )

                logger.info(f"Published document {document_id}")
                return document
        except Exception as e:
            logger.error(f"Failed to publish document {document_id}: {e}")
            return None

    # ==================== 删除（Delete） ====================

    def delete_document(self, document_id: str, user_id: str) -> bool:
        """
        删除文档（同时删除所有版本历史）

        Args:
            document_id: 文档ID
            user_id: 用户ID（权限验证）

        Returns:
            是否删除成功
        """
        try:
            with get_db_context() as db:
                # 删除版本历史
                db.query(DocumentVersion).filter(DocumentVersion.document_id == document_id).delete()

                # 删除文档
                deleted = db.query(Document).filter(
                    and_(Document.id == document_id, Document.user_id == user_id)
                ).delete()

                db.commit()
                logger.info(f"Deleted document {document_id} and its versions")
                return deleted > 0
        except Exception as e:
            logger.error(f"Failed to delete document {document_id}: {e}")
            return False

    # ==================== 私有辅助方法 ====================

    def _create_version(
        self,
        db: Session,
        document: Document,
        change_type: ChangeType,
        changed_by: str,
        user_id: Optional[str] = None,
        change_summary: Optional[str] = None
    ) -> Optional[DocumentVersion]:
        """创建版本快照（内部方法）"""
        try:
            version = DocumentVersion(
                id=str(uuid.uuid4()),
                document_id=document.id,
                version_number=document.current_version,
                title=document.title,
                content=document.content,
                outline=document.outline,
                change_type=change_type,
                change_summary=change_summary,
                changed_by=changed_by,
                user_id=user_id
            )
            db.add(version)
            db.commit()
            return version
        except Exception as e:
            logger.error(f"Failed to create version: {e}")
            return None

    def _calculate_reading_time(self, content: str) -> int:
        """计算阅读时间（假设200字/分钟）"""
        if not content:
            return 0
        word_count = len(content)
        return max(1, word_count // 200)


class DocumentVersionTable:
    """文档版本历史CRUD操作"""

    def get_versions_by_document_id(
        self,
        document_id: str,
        limit: int = 50
    ) -> List[DocumentVersion]:
        """获取文档的所有版本历史"""
        try:
            with get_db_context() as db:
                return db.query(DocumentVersion)\
                    .filter(DocumentVersion.document_id == document_id)\
                    .order_by(desc(DocumentVersion.version_number))\
                    .limit(limit)\
                    .all()
        except Exception as e:
            logger.error(f"Failed to get versions for document {document_id}: {e}")
            return []

    def get_version_by_number(
        self,
        document_id: str,
        version_number: int
    ) -> Optional[DocumentVersion]:
        """获取指定版本"""
        try:
            with get_db_context() as db:
                return db.query(DocumentVersion)\
                    .filter(
                        and_(
                            DocumentVersion.document_id == document_id,
                            DocumentVersion.version_number == version_number
                        )
                    ).first()
        except Exception as e:
            logger.error(f"Failed to get version {version_number} for document {document_id}: {e}")
            return None

    def rollback_to_version(
        self,
        document_id: str,
        user_id: str,
        version_number: int
    ) -> Optional[Document]:
        """
        回滚到指定版本

        实现方式：从历史版本复制内容，创建新版本
        """
        try:
            # 获取目标版本
            target_version = self.get_version_by_number(document_id, version_number)
            if not target_version:
                logger.warning(f"Version {version_number} not found for document {document_id}")
                return None

            # 使用DocumentTable更新文档
            document_table = DocumentTable()
            return document_table.update_document(
                document_id=document_id,
                user_id=user_id,
                title=target_version.title,
                content=target_version.content,
                outline=target_version.outline,
                change_summary=f"回滚到版本 {version_number}",
                changed_by="user"
            )
        except Exception as e:
            logger.error(f"Failed to rollback document {document_id} to version {version_number}: {e}")
            return None


# 单例导出
Documents = DocumentTable()
DocumentVersions = DocumentVersionTable()

# ==================== 兼容性别名（过渡期使用，后续可移除） ====================
ReportTable = DocumentTable
ReportVersionTable = DocumentVersionTable
Reports = Documents
ReportVersions = DocumentVersions
