# -*- coding: utf-8 -*-
"""
@File    :   celery_app.py
@Desc    :   Celery 应用配置
"""

from celery import Celery

# 创建 Celery 应用
celery_app = Celery(
    "nexus_tasks",
    broker="redis://localhost:6379/0",  # Redis 作为消息队列
    backend="redis://localhost:6379/1",  # Redis 作为结果存储
    include=["app.service.file_tasks"],  # 任务模块
)

# Celery 配置
celery_app.conf.update(
    # 任务序列化
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",

    # 时区
    timezone="Asia/Shanghai",
    enable_utc=True,

    # 任务配置
    task_track_started=True,  # 追踪任务开始状态
    task_time_limit=600,  # 任务超时时间（秒）

    # 结果过期时间
    result_expires=3600,  # 1小时后过期
)
