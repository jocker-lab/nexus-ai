# -*- coding: utf-8 -*-
"""
@File    :   template_tasks.py
@Desc    :   Celery 模版处理任务
"""

import asyncio
import time
import threading
from pathlib import Path
from loguru import logger

from app.tasks.celery_app import celery_app
from app.services.docling_service import parse_document
from app.services.template_service import upload_template
from app.database.minio_db import get_minio_client
from app.curd.writing_templates import WritingTemplates
from app.models.writing_templates import TemplateStatus


# ============================================
# 模板任务专用日志配置
# ============================================
LOG_PREFIX = "[TemplateTask]"
TEMPLATE_LOG_DIR = Path("logs")
TEMPLATE_LOG_FILE = TEMPLATE_LOG_DIR / "template_tasks.log"

# 确保日志目录存在
TEMPLATE_LOG_DIR.mkdir(exist_ok=True)

# 创建专用的模板任务 logger
template_logger = logger.bind(task_type="template")

# 添加模板任务专用的文件 handler（只记录带有 task_type="template" 的日志）
logger.add(
    TEMPLATE_LOG_FILE,
    format="{time:YYYY-MM-DD HH:mm:ss.SSS} | {level: <8} | {message}",
    level="DEBUG",
    rotation="10 MB",      # 文件达到 10MB 时轮转
    retention="30 days",   # 保留 30 天
    compression="gz",      # 压缩旧日志
    encoding="utf-8",
    filter=lambda record: record["extra"].get("task_type") == "template",
)


def log_step(step_num: int, total_steps: int, message: str, task_id: str = None, **extra):
    """统一的步骤日志格式"""
    progress = int((step_num / total_steps) * 100)
    task_info = f"[{task_id}]" if task_id else ""
    extra_info = " | ".join(f"{k}={v}" for k, v in extra.items()) if extra else ""
    template_logger.info(f"{LOG_PREFIX} {task_info} [{progress}%] Step {step_num}/{total_steps}: {message}" + (f" | {extra_info}" if extra_info else ""))


class HeartbeatLogger:
    """心跳日志器 - 在长时间运行的操作中定期输出进度"""

    def __init__(self, task_id: str, operation: str, interval: int = 10):
        """
        Args:
            task_id: 任务短ID
            operation: 操作名称（如 "Docling 解析"）
            interval: 心跳间隔（秒）
        """
        self.task_id = task_id
        self.operation = operation
        self.interval = interval
        self.start_time = None
        self._stop_event = threading.Event()
        self._thread = None

    def _heartbeat_loop(self):
        """心跳线程循环"""
        while not self._stop_event.wait(self.interval):
            elapsed = time.time() - self.start_time
            template_logger.info(
                f"{LOG_PREFIX} [{self.task_id}]    ⏳ {self.operation}中... 已耗时 {elapsed:.0f}s"
            )

    def start(self):
        """开始心跳"""
        self.start_time = time.time()
        self._stop_event.clear()
        self._thread = threading.Thread(target=self._heartbeat_loop, daemon=True)
        self._thread.start()

    def stop(self):
        """停止心跳"""
        self._stop_event.set()
        if self._thread:
            self._thread.join(timeout=1)


def run_async(coro):
    """在同步环境中运行异步函数"""
    try:
        loop = asyncio.get_event_loop()
    except RuntimeError:
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
    return loop.run_until_complete(coro)


def find_template_id_by_filename(user_id: str, filename: str) -> str:
    """根据用户ID和文件名查找最近创建的模版ID"""
    templates, _ = WritingTemplates.get_templates_by_user_id(
        user_id=user_id,
        status=TemplateStatus.PENDING,
        limit=10
    )
    for t in templates:
        if t.original_filename == filename:
            return t.id
    return None


@celery_app.task(bind=True, name="process_template_file")
def process_template_file(
    self,
    task_id: str,
    file_url: str,
    object_name: str,
    filename: str,
    user_id: str,
):
    """
    处理上传的模版文件

    流程：
    1. 查找已创建的模版记录（由 API 端点预先创建）
    2. 更新状态为 parsing
    3. 从 MinIO URL 用 Docling 解析为 Markdown
    4. 调用 upload_template() 处理（LLM提取大纲 + 更新 SQL）
    5. 删除 pending bucket 中的原文件

    Args:
        task_id: 任务ID
        file_url: MinIO 文件的公开 URL
        object_name: MinIO 中的对象路径（用于删除）
        filename: 原始文件名
        user_id: 用户ID
    """
    total_steps = 5
    start_time = time.time()
    task_short_id = task_id[:8] if task_id else "unknown"

    template_logger.info(f"{LOG_PREFIX} ════════════════════════════════════════════════════════")
    template_logger.info(f"{LOG_PREFIX} 🚀 开始模版解析任务")
    template_logger.info(f"{LOG_PREFIX}    Task ID: {task_id}")
    template_logger.info(f"{LOG_PREFIX}    文件名: {filename}")
    template_logger.info(f"{LOG_PREFIX}    用户ID: {user_id}")
    template_logger.info(f"{LOG_PREFIX}    文件URL: {file_url}")
    template_logger.info(f"{LOG_PREFIX} ════════════════════════════════════════════════════════")

    # Step 1: 查找模版记录
    step_start = time.time()
    log_step(1, total_steps, "查找模版记录", task_short_id, filename=filename)

    template_id = find_template_id_by_filename(user_id, filename)
    if not template_id:
        template_logger.error(f"{LOG_PREFIX} [{task_short_id}] ❌ 找不到对应的模版记录: {filename}")
        template_logger.error(f"{LOG_PREFIX} [{task_short_id}] 任务失败，总耗时: {time.time() - start_time:.2f}s")
        return {
            "success": False,
            "task_id": task_id,
            "error": "找不到模版记录"
        }

    template_logger.info(f"{LOG_PREFIX} [{task_short_id}] ✓ 找到模版记录: {template_id[:8]}... | 耗时: {time.time() - step_start:.2f}s")

    try:
        # Step 2: 更新状态为 parsing
        step_start = time.time()
        log_step(2, total_steps, "更新状态为解析中", task_short_id, template_id=template_id[:8])

        WritingTemplates.update_template_status(template_id, TemplateStatus.PARSING)
        self.update_state(state="PROCESSING", meta={"step": "docling_parsing", "progress": 20})

        template_logger.info(f"{LOG_PREFIX} [{task_short_id}] ✓ 状态已更新为 PARSING | 耗时: {time.time() - step_start:.2f}s")

        # Step 3: Docling 解析为 Markdown
        step_start = time.time()
        log_step(3, total_steps, "Docling 文档解析", task_short_id, timeout="120s")
        template_logger.info(f"{LOG_PREFIX} [{task_short_id}]    正在调用 Docling 服务解析文档...")

        # 启动心跳日志（每10秒输出一次进度）
        docling_heartbeat = HeartbeatLogger(task_short_id, "Docling 解析", interval=10)
        docling_heartbeat.start()

        try:
            markdown_content = run_async(parse_document(file_url, timeout=120))
        finally:
            docling_heartbeat.stop()

        docling_duration = time.time() - step_start

        if not markdown_content:
            template_logger.error(f"{LOG_PREFIX} [{task_short_id}] ❌ Docling 解析失败 | 耗时: {docling_duration:.2f}s")
            WritingTemplates.update_template_status(
                template_id,
                TemplateStatus.FAILED,
                error_message="文件解析失败"
            )
            template_logger.error(f"{LOG_PREFIX} [{task_short_id}] 任务失败，总耗时: {time.time() - start_time:.2f}s")
            return {
                "success": False,
                "task_id": task_id,
                "template_id": template_id,
                "error": "文件解析失败"
            }

        content_length = len(markdown_content)
        template_logger.info(f"{LOG_PREFIX} [{task_short_id}] ✓ Docling 解析成功")
        template_logger.info(f"{LOG_PREFIX} [{task_short_id}]    内容长度: {content_length:,} 字符")
        template_logger.info(f"{LOG_PREFIX} [{task_short_id}]    耗时: {docling_duration:.2f}s")

        # 输出内容预览（前200字符）
        preview = markdown_content[:200].replace('\n', ' ')
        template_logger.debug(f"{LOG_PREFIX} [{task_short_id}]    内容预览: {preview}...")

        # Step 4: LLM 提取模版大纲
        step_start = time.time()
        log_step(4, total_steps, "LLM 提取模版大纲", task_short_id, content_chars=content_length)
        self.update_state(state="PROCESSING", meta={"step": "template_extraction", "progress": 60})
        template_logger.info(f"{LOG_PREFIX} [{task_short_id}]    正在调用 LLM 提取模版结构...")

        # 启动心跳日志（每15秒输出一次进度）
        llm_heartbeat = HeartbeatLogger(task_short_id, "LLM 提取", interval=15)
        llm_heartbeat.start()

        try:
            result = run_async(upload_template(
                file_content=markdown_content,
                original_filename=filename,
                user_id=user_id,
                template_id=template_id,
            ))
        finally:
            llm_heartbeat.stop()

        llm_duration = time.time() - step_start

        if not result or not result.get("success"):
            error_msg = result.get("error", "模版提取失败") if result else "模版提取失败"
            template_logger.error(f"{LOG_PREFIX} [{task_short_id}] ❌ LLM 提取失败: {error_msg} | 耗时: {llm_duration:.2f}s")
            WritingTemplates.update_template_status(
                template_id,
                TemplateStatus.FAILED,
                error_message=error_msg
            )
            template_logger.error(f"{LOG_PREFIX} [{task_short_id}] 任务失败，总耗时: {time.time() - start_time:.2f}s")
            return {
                "success": False,
                "task_id": task_id,
                "template_id": template_id,
                "error": error_msg
            }

        extracted_title = result.get("title", "未知")
        extracted_category = result.get("category", "未知")
        chapter_count = len(result.get("outline", {}).get("chapters", [])) if result.get("outline") else 0

        template_logger.info(f"{LOG_PREFIX} [{task_short_id}] ✓ LLM 提取成功")
        template_logger.info(f"{LOG_PREFIX} [{task_short_id}]    提取标题: {extracted_title}")
        template_logger.info(f"{LOG_PREFIX} [{task_short_id}]    分类: {extracted_category}")
        template_logger.info(f"{LOG_PREFIX} [{task_short_id}]    章节数: {chapter_count}")
        template_logger.info(f"{LOG_PREFIX} [{task_short_id}]    耗时: {llm_duration:.2f}s")

        # Step 5: 清理临时文件
        step_start = time.time()
        log_step(5, total_steps, "清理临时文件", task_short_id, object_name=object_name)
        self.update_state(state="PROCESSING", meta={"step": "cleanup", "progress": 90})

        minio_client = get_minio_client()
        minio_client.delete_pending_file(object_name)

        template_logger.info(f"{LOG_PREFIX} [{task_short_id}] ✓ 临时文件已删除 | 耗时: {time.time() - step_start:.2f}s")

        # 任务完成
        total_duration = time.time() - start_time
        template_logger.info(f"{LOG_PREFIX} ════════════════════════════════════════════════════════")
        template_logger.success(f"{LOG_PREFIX} [{task_short_id}] ✅ 模版解析任务完成!")
        template_logger.info(f"{LOG_PREFIX}    Template ID: {result.get('template_id')}")
        template_logger.info(f"{LOG_PREFIX}    标题: {extracted_title}")
        template_logger.info(f"{LOG_PREFIX}    分类: {extracted_category}")
        template_logger.info(f"{LOG_PREFIX}    总耗时: {total_duration:.2f}s")
        template_logger.info(f"{LOG_PREFIX}    - Docling 解析: {docling_duration:.2f}s ({docling_duration/total_duration*100:.1f}%)")
        template_logger.info(f"{LOG_PREFIX}    - LLM 提取: {llm_duration:.2f}s ({llm_duration/total_duration*100:.1f}%)")
        template_logger.info(f"{LOG_PREFIX} ════════════════════════════════════════════════════════")

        return {
            "success": True,
            "task_id": task_id,
            "template_id": result.get("template_id"),
            "title": extracted_title,
            "category": extracted_category,
            "duration": total_duration,
        }

    except Exception as e:
        total_duration = time.time() - start_time
        template_logger.error(f"{LOG_PREFIX} ════════════════════════════════════════════════════════")
        template_logger.error(f"{LOG_PREFIX} [{task_short_id}] ❌ 任务异常终止!")
        template_logger.error(f"{LOG_PREFIX}    错误类型: {type(e).__name__}")
        template_logger.error(f"{LOG_PREFIX}    错误信息: {str(e)}")
        template_logger.error(f"{LOG_PREFIX}    总耗时: {total_duration:.2f}s")
        template_logger.error(f"{LOG_PREFIX} ════════════════════════════════════════════════════════")

        import traceback
        template_logger.debug(f"{LOG_PREFIX} [{task_short_id}] 完整堆栈:\n{traceback.format_exc()}")

        if template_id:
            WritingTemplates.update_template_status(
                template_id,
                TemplateStatus.FAILED,
                error_message=str(e)
            )
        return {
            "success": False,
            "task_id": task_id,
            "template_id": template_id,
            "error": str(e),
            "duration": total_duration,
        }
