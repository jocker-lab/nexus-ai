#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Mock FastAPI SSE 服务器 - 完整模拟中断和恢复流程

功能:
1. 播放第一个日志文件（中断前）
2. 遇到 interrupt 事件时真正停止
3. 等待前端用户输入
4. resume 时播放第二个日志文件（中断后）
5. 完全兼容 frontend_v4.html
"""
import asyncio
import json
from pathlib import Path
from typing import AsyncGenerator, Optional, Dict
from datetime import datetime

from fastapi import FastAPI, HTTPException
from fastapi.responses import StreamingResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from loguru import logger
from fastapi.openapi.docs import get_swagger_ui_html


# ==================== 配置 ====================

# 日志文件配置
LOG_DIR = Path("logs/sse_streams")
LOG_DIR.mkdir(exist_ok=True)

# 🔥 关键配置：两个阶段的日志文件
STAGE_1_LOG = "sse_chat_001_20251111_191812.jsonl"  # 中断前
STAGE_2_LOG = "sse_chat_001_20251111_192251.jsonl"  # 中断后

# 延迟配置（毫秒）
CHUNK_DELAY_MS = 20  # chunk 事件延迟
OTHER_DELAY_MS = 50  # 其他事件延迟


# ==================== 数据模型 ====================

class ChatRequest(BaseModel):
    """聊天请求模型"""
    user_id: str = Field(..., description="用户ID")
    chat_id: str = Field(..., description="会话ID")
    message: str = Field(..., description="用户消息")
    resume_from_interrupt: bool = Field(False, description="是否从中断恢复")


# ==================== 全局状态管理 ====================

# 存储每个会话的中断状态
interrupt_states: Dict[str, Dict] = {}
# 格式: {
#     "user_001_chat_001": {
#         "interrupted": True,
#         "interrupt_data": {...},
#         "user_input": "用户的输入"
#     }
# }


# ==================== FastAPI 应用 ====================

app = FastAPI(
    title="Mock Plan-Execute Agent API",
    description="完整模拟中断和恢复流程的 SSE 接口",
    version="2.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/docs", include_in_schema=False)
async def custom_swagger_ui_html():
    return get_swagger_ui_html(
        openapi_url=app.openapi_url,
        title=app.title + " - Swagger UI",
        swagger_js_url="https://unpkg.com/swagger-ui-dist@5/swagger-ui-bundle.js",
        swagger_css_url="https://unpkg.com/swagger-ui-dist@5/swagger-ui.css",
    )

@app.get("/redoc", include_in_schema=False)
async def redoc_html():
    from fastapi.openapi.docs import get_redoc_html
    return get_redoc_html(
        openapi_url=app.openapi_url,
        title=app.title + " - ReDoc",
        redoc_js_url="https://unpkg.com/redoc@latest/bundles/redoc.standalone.js",
    )
# ==================== 工具函数 ====================

def get_log_file_path(filename: str) -> Path:
    """
    获取日志文件路径
    
    优先级:
    1. logs/ 目录
    2. /mnt/user-data/uploads/ 目录（查找带时间戳前缀的文件）
    """
    # 首先在 logs 目录查找
    log_path = LOG_DIR / filename
    if log_path.exists():
        return log_path
    
    # 在上传目录查找
    upload_path = Path("/mnt/user-data/uploads") / filename
    if upload_path.exists():
        return upload_path
    
    # 查找带时间戳前缀的文件
    upload_dir = Path("/mnt/user-data/uploads")
    if upload_dir.exists():
        matches = list(upload_dir.glob(f"*{filename}"))
        if matches:
            return matches[0]
    
    raise FileNotFoundError(f"找不到日志文件: {filename}")


def format_sse_event(event_data: dict) -> str:
    """
    格式化为 SSE 事件
    
    只保留 type 和 data，移除 timestamp
    """
    sse_event = {
        "type": event_data["type"],
        "data": event_data["data"]
    }
    json_data = json.dumps(sse_event, ensure_ascii=False)
    return f"data: {json_data}\n\n"


# ==================== 核心流式处理函数 ====================

async def stream_from_log_file(
    log_file: Path,
    chat_id: str,
    session_key: str,
    is_resume: bool = False
) -> AsyncGenerator[str, None]:
    """
    从日志文件流式读取并发送事件
    
    Args:
        log_file: 日志文件路径
        chat_id: 会话ID（用于更新事件中的 chat_id）
        session_key: 会话唯一标识（user_id_chat_id）
        is_resume: 是否是从中断恢复
    """
    logger.info(f"📂 开始读取日志文件: {log_file}")
    logger.info(f"🔄 是否恢复模式: {is_resume}")
    
    try:
        with open(log_file, "r", encoding="utf-8") as f:
            event_count = 0
            
            for line_num, line in enumerate(f, 1):
                line = line.strip()
                if not line:
                    continue
                
                try:
                    # 解析事件
                    event = json.loads(line)
                    event_type = event.get("type", "unknown")
                    
                    # 更新 chat_id（使用当前会话的 chat_id）
                    if "data" in event and "chat_id" in event["data"]:
                        event["data"]["chat_id"] = chat_id
                    
                    # 🔥 关键：如果遇到 interrupt 事件
                    if event_type == "interrupt":
                        logger.info(f"🔔 检测到 interrupt 事件，准备停止")
                        
                        # 保存中断状态
                        interrupt_states[session_key] = {
                            "interrupted": True,
                            "interrupt_data": event["data"]
                        }
                        
                        # 发送 interrupt 事件
                        yield format_sse_event(event)
                        
                        logger.info(f"🛑 已发送 interrupt 事件，停止流")
                        return  # 停止流
                    
                    # 根据事件类型决定延迟
                    if event_count > 0:
                        if event_type == "chunk":
                            delay = CHUNK_DELAY_MS / 1000.0
                        else:
                            delay = OTHER_DELAY_MS / 1000.0
                        
                        await asyncio.sleep(delay)
                    
                    # 发送事件
                    sse_data = format_sse_event(event)
                    yield sse_data
                    
                    event_count += 1
                    
                    # 每 200 个事件记录一次
                    if event_count % 200 == 0:
                        logger.info(f"📤 已发送 {event_count} 个事件")
                
                except json.JSONDecodeError as e:
                    logger.error(f"❌ 第 {line_num} 行 JSON 解析失败: {e}")
                    continue
                except Exception as e:
                    logger.error(f"❌ 第 {line_num} 行处理失败: {e}")
                    continue
            
            logger.info(f"✅ 完成，共发送 {event_count} 个事件")
    
    except Exception as e:
        logger.error(f"❌ 读取日志文件失败: {e}")
        error_event = {
            "type": "error",
            "data": {
                "error": str(e),
                "error_type": type(e).__name__,
                "chat_id": chat_id
            }
        }
        yield format_sse_event(error_event)


# ==================== API 端点 ====================

@app.get("/")
async def root():
    """根路径 - API 信息"""
    return {
        "name": "Mock Plan-Execute Agent API - V2",
        "version": "2.0.0",
        "features": [
            "完整模拟中断和恢复流程",
            "支持 interrupt 等待用户输入",
            "自动切换日志文件",
            "完全兼容 frontend_v4.html"
        ],
        "stages": {
            "stage1": STAGE_1_LOG,
            "stage2": STAGE_2_LOG
        }
    }


@app.get("/health")
async def health_check():
    """健康检查"""
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "active_sessions": len(interrupt_states),
        "interrupted_sessions": sum(
            1 for state in interrupt_states.values() 
            if state.get("interrupted")
        )
    }


@app.get("/sessions")
async def list_sessions():
    """列出当前会话状态"""
    return {
        "total": len(interrupt_states),
        "sessions": {
            key: {
                "interrupted": state.get("interrupted", False),
                "has_interrupt_data": "interrupt_data" in state,
                "has_user_input": "user_input" in state
            }
            for key, state in interrupt_states.items()
        }
    }


@app.post("/api/v1/chat/stream")
async def chat_stream(request: ChatRequest):
    """
    主要的聊天流式接口
    
    工作流程:
    1. 如果 resume_from_interrupt=False（新对话）:
       - 播放 STAGE_1_LOG（中断前的日志）
       - 遇到 interrupt 事件时停止
       
    2. 如果 resume_from_interrupt=True（恢复）:
       - 播放 STAGE_2_LOG（中断后的日志）
       - 直到 complete 事件
    """
    logger.info("=" * 80)
    logger.info(f"📝 收到请求 - User: {request.user_id}, Chat: {request.chat_id}")
    logger.info(f"💬 消息: {request.message[:100]}...")
    logger.info(f"🔄 恢复模式: {request.resume_from_interrupt}")
    
    session_key = f"{request.user_id}_{request.chat_id}"
    
    try:
        # 🔥 判断是新对话还是恢复
        if not request.resume_from_interrupt:
            # ========== 阶段 1: 新对话，播放中断前的日志 ==========
            logger.info(f"🆕 新对话，播放阶段 1: {STAGE_1_LOG}")
            
            # 清除之前的状态
            if session_key in interrupt_states:
                del interrupt_states[session_key]
            
            # 获取日志文件
            log_file = get_log_file_path(STAGE_1_LOG)
            
            # 返回流式响应
            return StreamingResponse(
                stream_from_log_file(
                    log_file=log_file,
                    chat_id=request.chat_id,
                    session_key=session_key,
                    is_resume=False
                ),
                media_type="text/event-stream",
                headers={
                    "Cache-Control": "no-cache",
                    "Connection": "keep-alive",
                    "X-Accel-Buffering": "no",
                }
            )
        
        else:
            # ========== 阶段 2: 从中断恢复，播放中断后的日志 ==========
            logger.info(f"🔄 从中断恢复，播放阶段 2: {STAGE_2_LOG}")
            
            # 检查是否有中断状态
            if session_key not in interrupt_states:
                logger.warning(f"⚠️ 没有找到中断状态: {session_key}")
                # 仍然继续播放阶段 2
            else:
                logger.info(f"✅ 找到中断状态: {interrupt_states[session_key]}")
                # 保存用户输入
                interrupt_states[session_key]["user_input"] = request.message
                interrupt_states[session_key]["interrupted"] = False
            
            # 获取日志文件
            log_file = get_log_file_path(STAGE_2_LOG)
            
            # 返回流式响应
            return StreamingResponse(
                stream_from_log_file(
                    log_file=log_file,
                    chat_id=request.chat_id,
                    session_key=session_key,
                    is_resume=True
                ),
                media_type="text/event-stream",
                headers={
                    "Cache-Control": "no-cache",
                    "Connection": "keep-alive",
                    "X-Accel-Buffering": "no",
                }
            )
    
    except FileNotFoundError as e:
        logger.error(f"❌ 文件未找到: {e}")
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        logger.error(f"❌ 处理请求失败: {e}")
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))


# ==================== 启动配置 ====================

if __name__ == "__main__":
    import uvicorn
    import shutil
    
    logger.info("🚀 启动 Mock FastAPI 服务器 V2...")
    
    # 🔥 自动复制日志文件到 logs/ 目录
    upload_dir = Path("/mnt/user-data/uploads")
    if upload_dir.exists():
        for filename in [STAGE_1_LOG, STAGE_2_LOG]:
            target = LOG_DIR / filename
            
            if not target.exists():
                # 查找带时间戳前缀的文件
                matches = list(upload_dir.glob(f"*{filename}"))
                if matches:
                    source = matches[0]
                    shutil.copy(source, target)
                    logger.info(f"📋 复制日志文件: {source.name} -> {target}")
                else:
                    logger.warning(f"⚠️ 未找到日志文件: {filename}")
            else:
                logger.info(f"✅ 日志文件已存在: {filename}")
    
    # 验证日志文件
    for stage, filename in [("阶段1", STAGE_1_LOG), ("阶段2", STAGE_2_LOG)]:
        try:
            log_path = get_log_file_path(filename)
            # 统计行数
            with open(log_path, "r", encoding="utf-8") as f:
                line_count = sum(1 for _ in f)
            logger.info(f"📊 {stage} ({filename}): {line_count} 个事件")
        except FileNotFoundError:
            logger.error(f"❌ {stage} 日志文件未找到: {filename}")
    
    logger.info("=" * 80)
    logger.info("📡 服务器配置:")
    logger.info(f"   地址: http://localhost:8088")
    logger.info(f"   阶段1: {STAGE_1_LOG} (新对话 → 中断)")
    logger.info(f"   阶段2: {STAGE_2_LOG} (恢复 → 完成)")
    logger.info(f"   Chunk延迟: {CHUNK_DELAY_MS}ms")
    logger.info(f"   其他延迟: {OTHER_DELAY_MS}ms")
    logger.info("=" * 80)
    
    uvicorn.run(
        "mock_sse_server_v2:app",
        host="0.0.0.0",
        port=8088,
        reload=True,
        log_level="info"
    )
