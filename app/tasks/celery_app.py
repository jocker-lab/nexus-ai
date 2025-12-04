# -*- coding: utf-8 -*-
"""
@File    :   celery_app.py
@Desc    :   Celery 应用配置
"""

from celery import Celery

from app.config import (
    CELERY_BROKER_URL,
    CELERY_RESULT_BACKEND,
    CELERY_CONFIG,
    CELERY_TASK_TIME_LIMIT,
)

# 创建 Celery 应用
celery_app = Celery(
    "nexus_tasks",
    broker=CELERY_BROKER_URL,
    backend=CELERY_RESULT_BACKEND,
    include=["app.tasks.template_tasks"],  # 任务模块
)

# Celery 配置（从 config.yaml 读取）
celery_app.conf.update(
    # 任务序列化
    task_serializer=CELERY_CONFIG.get("task_serializer", "json"),
    accept_content=CELERY_CONFIG.get("accept_content", ["json"]),
    result_serializer=CELERY_CONFIG.get("result_serializer", "json"),

    # 时区
    timezone=CELERY_CONFIG.get("timezone", "Asia/Shanghai"),
    enable_utc=CELERY_CONFIG.get("enable_utc", True),

    # 任务配置
    task_track_started=CELERY_CONFIG.get("task_track_started", True),
    task_time_limit=CELERY_TASK_TIME_LIMIT,

    # 结果过期时间
    result_expires=CELERY_CONFIG.get("result_expires", 3600),
)
