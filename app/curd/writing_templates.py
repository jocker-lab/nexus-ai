# -*- coding: utf-8 -*-
"""
@File    :   writing_templates.py
@Time    :   2025/12/03
@Author  :   pygao
@Version :   1.0
@Contact :   pygao.1@outlook.com
@License :   (C)Copyright 2025, GienTech Technology Co.,Ltd. All rights reserved.
@Desc    :   写作模版 CRUD 操作
"""
import uuid
from typing import Optional, List, Tuple
from sqlalchemy import desc, and_, or_
from sqlalchemy.orm import Session

from app.models.writing_templates import (
    WritingTemplate,
    WritingStyle,
    WritingTone,
    TemplateStatus,
    TemplateScope
)
from app.database.db import get_db_context
from loguru import logger


class WritingTemplateTable:
    """写作模版表 CRUD 操作"""

    # ==================== 创建（Create） ====================

    def create_template(
        self,
        user_id: str,
        title: str,
        summary: str,
        category: Optional[str] = None,
        original_filename: Optional[str] = None,
        markdown_content: Optional[str] = None,
        writing_style: WritingStyle = WritingStyle.BUSINESS,
        writing_tone: WritingTone = WritingTone.NEUTRAL,
        target_audience: Optional[str] = None,
        sections: Optional[list] = None,
        scope: TemplateScope = TemplateScope.PRIVATE,
        status: TemplateStatus = TemplateStatus.PENDING
    ) -> Optional[WritingTemplate]:
        """
        创建新写作模版

        Args:
            user_id: 用户ID
            title: 模版标题
            summary: 模版摘要
            category: 分类
            original_filename: 原始文件名
            markdown_content: Markdown 内容
            writing_style: 写作风格
            writing_tone: 写作语气
            target_audience: 目标受众
            sections: 章节结构
            scope: 可见范围
            status: 解析状态

        Returns:
            创建的 WritingTemplate 对象，失败返回 None
        """
        try:
            with get_db_context() as db:
                template_id = str(uuid.uuid4())
                template = WritingTemplate(
                    id=template_id,
                    user_id=user_id,
                    title=title,
                    summary=summary,
                    category=category,
                    original_filename=original_filename,
                    markdown_content=markdown_content,
                    writing_style=writing_style,
                    writing_tone=writing_tone,
                    target_audience=target_audience,
                    sections=sections,
                    scope=scope,
                    status=status,
                    usage_count=0
                )
                db.add(template)
                db.commit()
                db.refresh(template)

                logger.info(f"Created writing template: {template_id} for user: {user_id}")
                return template
        except Exception as e:
            logger.error(f"Failed to create writing template: {e}")
            return None

    # ==================== 读取（Read） ====================

    def get_template_by_id(self, template_id: str) -> Optional[WritingTemplate]:
        """根据ID获取模版"""
        try:
            with get_db_context() as db:
                return db.query(WritingTemplate).filter(
                    WritingTemplate.id == template_id
                ).first()
        except Exception as e:
            logger.error(f"Failed to get template {template_id}: {e}")
            return None

    def get_template_by_id_and_user_id(
        self,
        template_id: str,
        user_id: str
    ) -> Optional[WritingTemplate]:
        """根据模版ID和用户ID获取模版（权限验证）"""
        try:
            with get_db_context() as db:
                return db.query(WritingTemplate).filter(
                    and_(
                        WritingTemplate.id == template_id,
                        WritingTemplate.user_id == user_id
                    )
                ).first()
        except Exception as e:
            logger.error(f"Failed to get template {template_id} for user {user_id}: {e}")
            return None

    def get_templates_by_user_id(
        self,
        user_id: str,
        status: Optional[TemplateStatus] = None,
        category: Optional[str] = None,
        limit: int = 50,
        offset: int = 0
    ) -> Tuple[List[WritingTemplate], int]:
        """
        获取用户的所有模版列表

        Args:
            user_id: 用户ID
            status: 筛选状态（可选）
            category: 筛选分类（可选）
            limit: 返回数量限制
            offset: 偏移量

        Returns:
            (模版列表, 总数)
        """
        try:
            with get_db_context() as db:
                query = db.query(WritingTemplate).filter(
                    WritingTemplate.user_id == user_id
                )

                if status:
                    query = query.filter(WritingTemplate.status == status)
                if category:
                    query = query.filter(WritingTemplate.category == category)

                total = query.count()
                templates = query.order_by(desc(WritingTemplate.updated_at))\
                    .limit(limit).offset(offset).all()

                return templates, total
        except Exception as e:
            logger.error(f"Failed to get templates for user {user_id}: {e}")
            return [], 0

    def get_public_templates(
        self,
        category: Optional[str] = None,
        limit: int = 50,
        offset: int = 0
    ) -> Tuple[List[WritingTemplate], int]:
        """
        获取公开模版列表

        Args:
            category: 筛选分类（可选）
            limit: 返回数量限制
            offset: 偏移量

        Returns:
            (模版列表, 总数)
        """
        try:
            with get_db_context() as db:
                query = db.query(WritingTemplate).filter(
                    and_(
                        WritingTemplate.scope == TemplateScope.PUBLIC,
                        WritingTemplate.status == TemplateStatus.COMPLETED
                    )
                )

                if category:
                    query = query.filter(WritingTemplate.category == category)

                total = query.count()
                templates = query.order_by(desc(WritingTemplate.usage_count))\
                    .limit(limit).offset(offset).all()

                return templates, total
        except Exception as e:
            logger.error(f"Failed to get public templates: {e}")
            return [], 0

    def get_accessible_template(
        self,
        template_id: str,
        user_id: str
    ) -> Optional[WritingTemplate]:
        """
        获取用户可访问的模版（自己的或公开的）

        Args:
            template_id: 模版ID
            user_id: 用户ID

        Returns:
            模版对象，如果无权访问则返回 None
        """
        try:
            with get_db_context() as db:
                return db.query(WritingTemplate).filter(
                    and_(
                        WritingTemplate.id == template_id,
                        or_(
                            WritingTemplate.user_id == user_id,
                            WritingTemplate.scope == TemplateScope.PUBLIC
                        )
                    )
                ).first()
        except Exception as e:
            logger.error(f"Failed to get accessible template {template_id}: {e}")
            return None

    # ==================== 更新（Update） ====================

    def update_template(
        self,
        template_id: str,
        user_id: str,
        title: Optional[str] = None,
        summary: Optional[str] = None,
        category: Optional[str] = None,
        markdown_content: Optional[str] = None,
        writing_style: Optional[WritingStyle] = None,
        writing_tone: Optional[WritingTone] = None,
        target_audience: Optional[str] = None,
        sections: Optional[list] = None,
        status: Optional[TemplateStatus] = None,
        error_message: Optional[str] = None,
        scope: Optional[TemplateScope] = None
    ) -> Optional[WritingTemplate]:
        """
        更新模版

        Args:
            template_id: 模版ID
            user_id: 用户ID（权限验证）
            其他参数: 需要更新的字段

        Returns:
            更新后的模版对象
        """
        try:
            with get_db_context() as db:
                template = db.query(WritingTemplate).filter(
                    and_(
                        WritingTemplate.id == template_id,
                        WritingTemplate.user_id == user_id
                    )
                ).first()

                if not template:
                    logger.warning(f"Template {template_id} not found or access denied")
                    return None

                # 更新字段
                if title is not None:
                    template.title = title
                if summary is not None:
                    template.summary = summary
                if category is not None:
                    template.category = category
                if markdown_content is not None:
                    template.markdown_content = markdown_content
                if writing_style is not None:
                    template.writing_style = writing_style
                if writing_tone is not None:
                    template.writing_tone = writing_tone
                if target_audience is not None:
                    template.target_audience = target_audience
                if sections is not None:
                    template.sections = sections
                if status is not None:
                    template.status = status
                if error_message is not None:
                    template.error_message = error_message
                if scope is not None:
                    template.scope = scope

                db.commit()
                db.refresh(template)

                logger.info(f"Updated writing template {template_id}")
                return template
        except Exception as e:
            logger.error(f"Failed to update template {template_id}: {e}")
            return None

    def update_template_status(
        self,
        template_id: str,
        status: TemplateStatus,
        error_message: Optional[str] = None
    ) -> Optional[WritingTemplate]:
        """
        更新模版解析状态（无需用户权限验证，供后台任务使用）

        Args:
            template_id: 模版ID
            status: 新状态
            error_message: 错误信息（失败时）

        Returns:
            更新后的模版对象
        """
        try:
            with get_db_context() as db:
                template = db.query(WritingTemplate).filter(
                    WritingTemplate.id == template_id
                ).first()

                if not template:
                    logger.warning(f"Template {template_id} not found")
                    return None

                template.status = status
                if error_message is not None:
                    template.error_message = error_message

                db.commit()
                db.refresh(template)

                logger.info(f"Updated template {template_id} status to {status}")
                return template
        except Exception as e:
            logger.error(f"Failed to update template status {template_id}: {e}")
            return None

    def increment_usage_count(self, template_id: str) -> Optional[WritingTemplate]:
        """
        增加模版使用次数

        Args:
            template_id: 模版ID

        Returns:
            更新后的模版对象
        """
        try:
            with get_db_context() as db:
                template = db.query(WritingTemplate).filter(
                    WritingTemplate.id == template_id
                ).first()

                if not template:
                    logger.warning(f"Template {template_id} not found")
                    return None

                template.usage_count += 1
                db.commit()
                db.refresh(template)

                logger.info(f"Incremented usage count for template {template_id}")
                return template
        except Exception as e:
            logger.error(f"Failed to increment usage count for {template_id}: {e}")
            return None

    # ==================== 删除（Delete） ====================

    def delete_template(self, template_id: str, user_id: str) -> bool:
        """
        删除模版

        Args:
            template_id: 模版ID
            user_id: 用户ID（权限验证）

        Returns:
            是否删除成功
        """
        try:
            with get_db_context() as db:
                deleted = db.query(WritingTemplate).filter(
                    and_(
                        WritingTemplate.id == template_id,
                        WritingTemplate.user_id == user_id
                    )
                ).delete()

                db.commit()
                logger.info(f"Deleted writing template {template_id}")
                return deleted > 0
        except Exception as e:
            logger.error(f"Failed to delete template {template_id}: {e}")
            return False


# 单例导出
WritingTemplates = WritingTemplateTable()
