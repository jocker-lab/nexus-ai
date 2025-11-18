# -*- coding: utf-8 -*-
"""
@File    :   reports.py
@Time    :   2025/11/16 14:40
@Author  :   Claude Code
@Version :   1.0
@Desc    :   报告CRUD操作 - 支持版本管理和交互式生成
"""
import uuid
import time
from typing import Optional, List
from datetime import datetime
from sqlalchemy import desc, and_
from sqlalchemy.orm import Session

from app.models.reports import Report, ReportVersion, ReportStatus, ChangeType
from app.database.db import get_db
from loguru import logger


class ReportTable:
    """报告表CRUD操作"""

    # ==================== 创建（Create） ====================

    def create_report(
        self,
        user_id: str,
        title: str,
        content: str = "",
        description: Optional[str] = None,
        chat_id: Optional[str] = None,
        outline: Optional[dict] = None,
        category: Optional[str] = None,
        tags: Optional[str] = None,
        status: ReportStatus = ReportStatus.DRAFT
    ) -> Optional[Report]:
        """
        创建新报告

        Args:
            user_id: 用户ID
            title: 报告标题
            content: Markdown内容（默认为空）
            description: 报告描述
            chat_id: 关联的会话ID
            outline: 章节大纲JSON
            category: 分类
            tags: 标签（逗号分隔）
            status: 报告状态

        Returns:
            创建的Report对象，失败返回None
        """
        try:
            with get_db() as db:
                report_id = str(uuid.uuid4())
                report = Report(
                    id=report_id,
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
                db.add(report)
                db.commit()
                db.refresh(report)

                # 创建初始版本
                self._create_version(
                    db=db,
                    report=report,
                    change_type=ChangeType.AI_GENERATED,
                    changed_by="ai",
                    change_summary="初始版本"
                )

                logger.info(f"Created report: {report_id} for user: {user_id}")
                return report
        except Exception as e:
            logger.error(f"Failed to create report: {e}")
            return None

    # ==================== 读取（Read） ====================

    def get_report_by_id(self, report_id: str) -> Optional[Report]:
        """根据ID获取报告"""
        try:
            with get_db() as db:
                return db.query(Report).filter(Report.id == report_id).first()
        except Exception as e:
            logger.error(f"Failed to get report {report_id}: {e}")
            return None

    def get_report_by_id_and_user_id(self, report_id: str, user_id: str) -> Optional[Report]:
        """根据报告ID和用户ID获取报告（权限验证）"""
        try:
            with get_db() as db:
                return db.query(Report).filter(
                    and_(Report.id == report_id, Report.user_id == user_id)
                ).first()
        except Exception as e:
            logger.error(f"Failed to get report {report_id} for user {user_id}: {e}")
            return None

    def get_reports_by_user_id(
        self,
        user_id: str,
        status: Optional[ReportStatus] = None,
        limit: int = 50,
        offset: int = 0
    ) -> List[Report]:
        """
        获取用户的所有报告列表

        Args:
            user_id: 用户ID
            status: 筛选状态（可选）
            limit: 返回数量限制
            offset: 偏移量

        Returns:
            报告列表
        """
        try:
            with get_db() as db:
                query = db.query(Report).filter(Report.user_id == user_id)

                if status:
                    query = query.filter(Report.status == status)

                return query.order_by(desc(Report.updated_at)).limit(limit).offset(offset).all()
        except Exception as e:
            logger.error(f"Failed to get reports for user {user_id}: {e}")
            return []

    def get_report_by_chat_id(self, chat_id: str) -> Optional[Report]:
        """根据会话ID获取关联的报告"""
        try:
            with get_db() as db:
                return db.query(Report).filter(Report.chat_id == chat_id).first()
        except Exception as e:
            logger.error(f"Failed to get report by chat_id {chat_id}: {e}")
            return None

    # ==================== 更新（Update） ====================

    def update_report(
        self,
        report_id: str,
        user_id: str,
        title: Optional[str] = None,
        content: Optional[str] = None,
        description: Optional[str] = None,
        outline: Optional[dict] = None,
        status: Optional[ReportStatus] = None,
        category: Optional[str] = None,
        tags: Optional[str] = None,
        change_summary: Optional[str] = None,
        changed_by: str = "user"
    ) -> Optional[Report]:
        """
        更新报告（会创建新版本）

        Args:
            report_id: 报告ID
            user_id: 用户ID（权限验证）
            title/content/description/outline/status/category/tags: 更新字段
            change_summary: 变更摘要
            changed_by: 变更来源 ("ai" or "user")

        Returns:
            更新后的Report对象
        """
        try:
            with get_db() as db:
                report = db.query(Report).filter(
                    and_(Report.id == report_id, Report.user_id == user_id)
                ).first()

                if not report:
                    logger.warning(f"Report {report_id} not found or access denied")
                    return None

                # 更新字段
                if title is not None:
                    report.title = title
                if content is not None:
                    report.content = content
                    report.word_count = len(content)
                    report.estimated_reading_time = self._calculate_reading_time(content)
                if description is not None:
                    report.description = description
                if outline is not None:
                    report.outline = outline
                if status is not None:
                    report.status = status
                if category is not None:
                    report.category = category
                if tags is not None:
                    report.tags = tags

                # 版本管理
                if changed_by == "user":
                    report.is_manually_edited = True

                report.current_version += 1

                db.commit()
                db.refresh(report)

                # 创建版本快照
                change_type = ChangeType.MANUAL_EDIT if changed_by == "user" else ChangeType.AI_GENERATED
                self._create_version(
                    db=db,
                    report=report,
                    change_type=change_type,
                    changed_by=changed_by,
                    user_id=user_id if changed_by == "user" else None,
                    change_summary=change_summary
                )

                logger.info(f"Updated report {report_id} to version {report.current_version}")
                return report
        except Exception as e:
            logger.error(f"Failed to update report {report_id}: {e}")
            return None

    def update_outline(self, report_id: str, outline: dict) -> Optional[Report]:
        """仅更新章节大纲（不创建版本）"""
        try:
            with get_db() as db:
                report = db.query(Report).filter(Report.id == report_id).first()
                if report:
                    report.outline = outline
                    db.commit()
                    db.refresh(report)
                    logger.info(f"Updated outline for report {report_id}")
                return report
        except Exception as e:
            logger.error(f"Failed to update outline for {report_id}: {e}")
            return None

    def publish_report(self, report_id: str, user_id: str) -> Optional[Report]:
        """发布报告（状态变更为PUBLISHED）"""
        try:
            with get_db() as db:
                report = db.query(Report).filter(
                    and_(Report.id == report_id, Report.user_id == user_id)
                ).first()

                if not report:
                    return None

                report.status = ReportStatus.PUBLISHED
                report.published_at = datetime.now()
                report.current_version += 1

                db.commit()
                db.refresh(report)

                # 创建发布版本
                self._create_version(
                    db=db,
                    report=report,
                    change_type=ChangeType.STATUS_CHANGED,
                    changed_by="user",
                    user_id=user_id,
                    change_summary="报告已发布"
                )

                logger.info(f"Published report {report_id}")
                return report
        except Exception as e:
            logger.error(f"Failed to publish report {report_id}: {e}")
            return None

    # ==================== 删除（Delete） ====================

    def delete_report(self, report_id: str, user_id: str) -> bool:
        """
        删除报告（同时删除所有版本历史）

        Args:
            report_id: 报告ID
            user_id: 用户ID（权限验证）

        Returns:
            是否删除成功
        """
        try:
            with get_db() as db:
                # 删除版本历史
                db.query(ReportVersion).filter(ReportVersion.report_id == report_id).delete()

                # 删除报告
                deleted = db.query(Report).filter(
                    and_(Report.id == report_id, Report.user_id == user_id)
                ).delete()

                db.commit()
                logger.info(f"Deleted report {report_id} and its versions")
                return deleted > 0
        except Exception as e:
            logger.error(f"Failed to delete report {report_id}: {e}")
            return False

    # ==================== 私有辅助方法 ====================

    def _create_version(
        self,
        db: Session,
        report: Report,
        change_type: ChangeType,
        changed_by: str,
        user_id: Optional[str] = None,
        change_summary: Optional[str] = None
    ) -> Optional[ReportVersion]:
        """创建版本快照（内部方法）"""
        try:
            version = ReportVersion(
                id=str(uuid.uuid4()),
                report_id=report.id,
                version_number=report.current_version,
                title=report.title,
                content=report.content,
                outline=report.outline,
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


class ReportVersionTable:
    """报告版本历史CRUD操作"""

    def get_versions_by_report_id(
        self,
        report_id: str,
        limit: int = 50
    ) -> List[ReportVersion]:
        """获取报告的所有版本历史"""
        try:
            with get_db() as db:
                return db.query(ReportVersion)\
                    .filter(ReportVersion.report_id == report_id)\
                    .order_by(desc(ReportVersion.version_number))\
                    .limit(limit)\
                    .all()
        except Exception as e:
            logger.error(f"Failed to get versions for report {report_id}: {e}")
            return []

    def get_version_by_number(
        self,
        report_id: str,
        version_number: int
    ) -> Optional[ReportVersion]:
        """获取指定版本"""
        try:
            with get_db() as db:
                return db.query(ReportVersion)\
                    .filter(
                        and_(
                            ReportVersion.report_id == report_id,
                            ReportVersion.version_number == version_number
                        )
                    ).first()
        except Exception as e:
            logger.error(f"Failed to get version {version_number} for report {report_id}: {e}")
            return None

    def rollback_to_version(
        self,
        report_id: str,
        user_id: str,
        version_number: int
    ) -> Optional[Report]:
        """
        回滚到指定版本

        实现方式：从历史版本复制内容，创建新版本
        """
        try:
            # 获取目标版本
            target_version = self.get_version_by_number(report_id, version_number)
            if not target_version:
                logger.warning(f"Version {version_number} not found for report {report_id}")
                return None

            # 使用ReportTable更新报告
            report_table = ReportTable()
            return report_table.update_report(
                report_id=report_id,
                user_id=user_id,
                title=target_version.title,
                content=target_version.content,
                outline=target_version.outline,
                change_summary=f"回滚到版本 {version_number}",
                changed_by="user"
            )
        except Exception as e:
            logger.error(f"Failed to rollback report {report_id} to version {version_number}: {e}")
            return None


# 单例导出
Reports = ReportTable()
ReportVersions = ReportVersionTable()
