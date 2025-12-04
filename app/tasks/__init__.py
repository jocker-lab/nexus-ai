# -*- coding: utf-8 -*-
"""
@File    :   __init__.py
@Desc    :   Celery 任务模块
"""

from app.tasks.celery_app import celery_app

__all__ = ["celery_app"]
