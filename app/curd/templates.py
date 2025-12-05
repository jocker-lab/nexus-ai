# -*- coding: utf-8 -*-
"""
@File    :   templates.py
@Time    :   2025/11/28
@Desc    :   模版 CRUD 操作
"""

import uuid
from typing import Optional, List
from sqlalchemy import desc, and_
from loguru import logger

from app.models.templates import Template
from app.database.db import get_db


class TemplateTable:
    """模版表 CRUD 操作"""

    # ==================== 创建（Create） ====================

    def create_template(
        self,
        user_id: str,
        title: str,
        summary: str,
        category: str,
        original_filename: Optional[str] = None,
        markdown_content: Optional[str] = None,
        writing_style: str = "business",
        writing_tone: str = "neutral",
        target_audience: Optional[str] = None,
        sections: Optional[list] = None,
        special_requirements: Optional[str] = None,
        template_id: Optional[str] = None,
    ) -> Optional[Template]:
        """
        创建新模版

        Args:
            user_id: 用户ID
            title: 模版名称
            summary: 模版简介
            category: 分类
            original_filename: 原始文件名
            markdown_content: Markdown 内容
            writing_style: 写作风格
            writing_tone: 写作语气
            target_audience: 目标读者
            sections: 章节结构（每个章节包含 estimated_percentage）
            special_requirements: 特殊要求
            template_id: 指定的模版ID（可选，用于与 Milvus 同步）

        Returns:
            创建的 Template 对象，失败返回 None
        """
        try:
            with get_db() as db:
                tid = template_id if template_id else str(uuid.uuid4())
                template = Template(
                    id=tid,
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
                    special_requirements=special_requirements,
                )
                db.add(template)
                db.commit()
                db.refresh(template)

                logger.info(f"Created template: {tid} for user: {user_id}")
                return template
        except Exception as e:
            logger.error(f"Failed to create template: {e}")
            return None

    # ==================== 读取（Read） ====================

    def get_template_by_id(self, template_id: str) -> Optional[Template]:
        """根据 ID 获取模版"""
        try:
            with get_db() as db:
                return db.query(Template).filter(Template.id == template_id).first()
        except Exception as e:
            logger.error(f"Failed to get template {template_id}: {e}")
            return None

    def get_template_by_id_and_user_id(self, template_id: str, user_id: str) -> Optional[Template]:
        """根据模版ID和用户ID获取模版（权限验证）"""
        try:
            with get_db() as db:
                return db.query(Template).filter(
                    and_(Template.id == template_id, Template.user_id == user_id)
                ).first()
        except Exception as e:
            logger.error(f"Failed to get template {template_id} for user {user_id}: {e}")
            return None

    def get_templates_by_user_id(
        self,
        user_id: str,
        category: Optional[str] = None,
        limit: int = 50,
        offset: int = 0
    ) -> List[Template]:
        """
        获取用户的所有模版

        Args:
            user_id: 用户ID
            category: 筛选分类（可选）
            limit: 返回数量限制
            offset: 偏移量

        Returns:
            模版列表
        """
        try:
            with get_db() as db:
                query = db.query(Template).filter(Template.user_id == user_id)

                if category:
                    query = query.filter(Template.category == category)

                return query.order_by(desc(Template.created_at)).limit(limit).offset(offset).all()
        except Exception as e:
            logger.error(f"Failed to get templates for user {user_id}: {e}")
            return []

    def get_templates_by_ids(self, template_ids: List[str]) -> List[Template]:
        """
        根据多个 ID 获取模版（用于 Milvus 搜索后查询详情）

        Args:
            template_ids: 模版 ID 列表

        Returns:
            模版列表
        """
        try:
            with get_db() as db:
                return db.query(Template).filter(Template.id.in_(template_ids)).all()
        except Exception as e:
            logger.error(f"Failed to get templates by ids: {e}")
            return []

    # ==================== 更新（Update） ====================

    def update_template(
        self,
        template_id: str,
        user_id: str,
        title: Optional[str] = None,
        summary: Optional[str] = None,
        category: Optional[str] = None,
        sections: Optional[list] = None,
        special_requirements: Optional[str] = None,
    ) -> Optional[Template]:
        """
        更新模版

        Args:
            template_id: 模版ID
            user_id: 用户ID（权限验证）
            其他参数: 要更新的字段

        Returns:
            更新后的 Template 对象
        """
        try:
            with get_db() as db:
                template = db.query(Template).filter(
                    and_(Template.id == template_id, Template.user_id == user_id)
                ).first()

                if not template:
                    logger.warning(f"Template {template_id} not found or access denied")
                    return None

                if title is not None:
                    template.title = title
                if summary is not None:
                    template.summary = summary
                if category is not None:
                    template.category = category
                if sections is not None:
                    template.sections = sections
                if special_requirements is not None:
                    template.special_requirements = special_requirements

                db.commit()
                db.refresh(template)

                logger.info(f"Updated template {template_id}")
                return template
        except Exception as e:
            logger.error(f"Failed to update template {template_id}: {e}")
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
            with get_db() as db:
                deleted = db.query(Template).filter(
                    and_(Template.id == template_id, Template.user_id == user_id)
                ).delete()

                db.commit()
                logger.info(f"Deleted template {template_id}")
                return deleted > 0
        except Exception as e:
            logger.error(f"Failed to delete template {template_id}: {e}")
            return False


# 单例导出
Templates = TemplateTable()
