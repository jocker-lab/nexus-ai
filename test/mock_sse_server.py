# -*- coding: utf-8 -*-
"""
@File    :   mock_sse_server.py
@Time    :   2025/12/02
@Author  :   Claude
@Desc    :   Mock SSE 测试服务器 - 使用录制的 JSONL 数据模拟真实 SSE 流
             用于前端开发测试，节省 LLM tokens
"""

import asyncio
import json
import os
from datetime import datetime
from pathlib import Path
from typing import Optional, List, Dict, Any
from contextlib import asynccontextmanager

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse, FileResponse
from pydantic import BaseModel
from loguru import logger

# ==================== 配置 ====================

# JSONL 数据目录
JSONL_DIR = Path(__file__).parent.parent / "logs" / "sse_streams_logs"

# 流式延迟配置（秒）
DEFAULT_CHUNK_DELAY = 0.02  # 默认 chunk 间隔
DEFAULT_NODE_DELAY = 0.1    # node_start 等事件间隔

# 可用的测试场景
SCENARIOS = {
    "start_to_interrupt": "sse_chat_001_20251202_110016.jsonl",  # 新对话到中断
    "resume_to_complete": "sse_chat_001_20251202_110551.jsonl",  # 从中断恢复到完成
}


# ==================== 数据模型 ====================

class MockChatRequest(BaseModel):
    """模拟聊天请求 - 简化版"""
    user_id: str = "user_001"
    chat_id: str = "mock_chat_001"
    message: str = ""
    agent_name: str = "publisher"  # 代理名称，预留字段，当前未使用


# ==================== JSONL 数据加载器 ====================

class JsonlDataLoader:
    """JSONL 数据加载和管理"""

    def __init__(self, jsonl_dir: Path):
        self.jsonl_dir = jsonl_dir
        self._cache: Dict[str, List[Dict]] = {}

    def list_available_files(self) -> List[str]:
        """列出所有可用的 JSONL 文件"""
        if not self.jsonl_dir.exists():
            return []
        return [f.name for f in self.jsonl_dir.glob("*.jsonl")]

    def load_file(self, filename: str) -> List[Dict[str, Any]]:
        """加载单个 JSONL 文件"""
        if filename in self._cache:
            return self._cache[filename]

        filepath = self.jsonl_dir / filename
        if not filepath.exists():
            raise FileNotFoundError(f"JSONL file not found: {filepath}")

        events = []
        with open(filepath, 'r', encoding='utf-8') as f:
            for line_num, line in enumerate(f, 1):
                line = line.strip()
                if not line:
                    continue
                try:
                    events.append(json.loads(line))
                except json.JSONDecodeError as e:
                    logger.warning(f"Skip invalid JSON at line {line_num}: {e}")

        self._cache[filename] = events
        logger.info(f"📂 Loaded {len(events)} events from {filename}")
        return events

    def get_scenario_events(self, scenario: str) -> List[Dict[str, Any]]:
        """根据场景名获取事件列表"""
        if scenario not in SCENARIOS:
            available = list(SCENARIOS.keys())
            raise ValueError(f"Unknown scenario: {scenario}. Available: {available}")

        filename = SCENARIOS[scenario]
        return self.load_file(filename)


# ==================== SSE 流模拟器 ====================

class SSEStreamSimulator:
    """SSE 流模拟器 - 带真实延迟和状态回调"""

    def __init__(self, events: List[Dict], speed_factor: float = 1.0,
                 on_interrupt: callable = None, on_complete: callable = None):
        self.events = events
        self.speed_factor = speed_factor
        self._prev_timestamp: Optional[datetime] = None
        self.on_interrupt = on_interrupt  # interrupt 事件回调
        self.on_complete = on_complete    # complete 事件回调

    def _parse_timestamp(self, ts_str: str) -> datetime:
        """解析时间戳"""
        return datetime.fromisoformat(ts_str)

    def _calculate_delay(self, event: Dict) -> float:
        """计算事件间的延迟时间"""
        event_type = event.get("type", "")

        # 基于事件类型的默认延迟
        if event_type == "chunk":
            base_delay = DEFAULT_CHUNK_DELAY
        elif event_type in ("node_start", "node_update", "usage"):
            base_delay = DEFAULT_NODE_DELAY
        elif event_type in ("start", "resume", "complete", "interrupt"):
            base_delay = 0.05
        else:
            base_delay = DEFAULT_CHUNK_DELAY

        # 如果有时间戳，使用真实的时间间隔
        if "timestamp" in event and self._prev_timestamp:
            try:
                current_ts = self._parse_timestamp(event["timestamp"])
                real_delay = (current_ts - self._prev_timestamp).total_seconds()
                # 使用真实延迟，但限制最大值
                base_delay = min(max(real_delay, 0.001), 1.0)
            except (ValueError, TypeError):
                pass

        return base_delay * self.speed_factor

    async def stream(self):
        """生成 SSE 流"""
        logger.info(f"🚀 Starting SSE stream simulation with {len(self.events)} events")

        for i, event in enumerate(self.events):
            # 计算延迟
            delay = self._calculate_delay(event)
            event_type = event.get("type", "message")

            # 更新上一个时间戳
            if "timestamp" in event:
                try:
                    self._prev_timestamp = self._parse_timestamp(event["timestamp"])
                except (ValueError, TypeError):
                    pass

            # 格式化为 SSE 格式 - 兼容 frontend_v4_mock.html
            # 前端期望格式: data: {"type": "...", "data": {...}}\n\n
            sse_event = {
                "type": event_type,
                "data": event.get("data", {})
            }
            sse_message = f"data: {json.dumps(sse_event, ensure_ascii=False)}\n\n"

            # 日志（仅记录关键事件）
            if event_type in ("start", "resume", "node_start", "interrupt", "complete", "usage"):
                logger.debug(f"📤 [{i+1}/{len(self.events)}] {event_type}")

            yield sse_message

            # 🔥 触发状态回调
            if event_type == "interrupt" and self.on_interrupt:
                self.on_interrupt()
            elif event_type == "complete" and self.on_complete:
                self.on_complete()

            # 延迟
            if delay > 0:
                await asyncio.sleep(delay)

        logger.info("✅ SSE stream simulation completed")


# ==================== FastAPI 应用 ====================

# 全局数据加载器
data_loader = JsonlDataLoader(JSONL_DIR)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """应用生命周期管理"""
    logger.info("=" * 60)
    logger.info("🎭 Mock SSE Server Starting...")
    logger.info(f"📂 JSONL Directory: {JSONL_DIR}")
    logger.info(f"📋 Available scenarios: {list(SCENARIOS.keys())}")

    # 预加载数据
    for scenario, filename in SCENARIOS.items():
        try:
            events = data_loader.load_file(filename)
            logger.info(f"  - {scenario}: {len(events)} events")
        except FileNotFoundError:
            logger.warning(f"  - {scenario}: FILE NOT FOUND ({filename})")

    logger.info("=" * 60)
    yield
    logger.info("🛑 Mock SSE Server Stopped")


app = FastAPI(
    title="Mock SSE Server",
    description="用于前端测试的 Mock SSE 服务器，使用录制的 JSONL 数据",
    version="1.0.0",
    lifespan=lifespan
)

# CORS 配置
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ==================== API 端点 ====================

@app.get("/")
async def root():
    """服务器信息"""
    return {
        "name": "Mock SSE Server",
        "version": "1.0.0",
        "description": "用于前端测试的 Mock SSE 服务器",
        "endpoints": {
            "/api/v1/chat/stream": "POST - 模拟 SSE 流",
            "/api/v1/scenarios": "GET - 列出可用场景",
            "/api/v1/files": "GET - 列出 JSONL 文件",
            "/health": "GET - 健康检查",
        }
    }


@app.get("/health")
async def health_check():
    """健康检查"""
    return {"status": "healthy", "timestamp": datetime.now().isoformat()}


@app.get("/api/v1/scenarios")
async def list_scenarios():
    """列出可用的测试场景"""
    result = {}
    for scenario, filename in SCENARIOS.items():
        try:
            events = data_loader.load_file(filename)
            # 获取场景摘要
            first_event = events[0] if events else {}
            last_event = events[-1] if events else {}
            result[scenario] = {
                "filename": filename,
                "event_count": len(events),
                "starts_with": first_event.get("type"),
                "ends_with": last_event.get("type"),
                "description": _get_scenario_description(scenario)
            }
        except FileNotFoundError:
            result[scenario] = {"error": "file not found", "filename": filename}

    return {"scenarios": result}


@app.get("/api/v1/files")
async def list_files():
    """列出所有可用的 JSONL 文件"""
    files = data_loader.list_available_files()
    return {
        "directory": str(JSONL_DIR),
        "files": files,
        "count": len(files)
    }


# 🔥 全局状态：记录每个 chat_id 是否处于中断状态
chat_interrupt_states: Dict[str, bool] = {}


@app.post("/api/v1/chat/stream")
async def mock_chat_stream(request: MockChatRequest):
    """
    模拟 SSE 聊天流 - 自动判断场景

    场景自动判断逻辑:
    - 如果 chat_id 处于中断状态 → resume_to_complete
    - 否则 → start_to_interrupt

    播放完 interrupt 事件后自动标记为中断状态
    播放完 complete 事件后自动清除中断状态
    """
    chat_id = request.chat_id

    # 🔥 自动判断场景
    is_interrupted = chat_interrupt_states.get(chat_id, False)
    scenario = "resume_to_complete" if is_interrupted else "start_to_interrupt"

    logger.info("=" * 50)
    logger.info(f"📨 Mock Stream Request")
    logger.info(f"   User ID: {request.user_id}")
    logger.info(f"   Chat ID: {chat_id}")
    logger.info(f"   Message: {request.message[:50]}..." if request.message else "   Message: (empty)")
    logger.info(f"   Is Interrupted: {is_interrupted}")
    logger.info(f"   Auto Scenario: {scenario}")
    logger.info("=" * 50)

    try:
        events = data_loader.get_scenario_events(scenario)
    except (FileNotFoundError, ValueError) as e:
        return {"error": str(e)}

    # 🔥 状态回调函数
    def on_interrupt():
        chat_interrupt_states[chat_id] = True
        logger.info(f"🔔 Chat {chat_id} marked as INTERRUPTED")

    def on_complete():
        chat_interrupt_states[chat_id] = False
        logger.info(f"✅ Chat {chat_id} marked as COMPLETED")

    # 创建流模拟器（带状态回调）
    # 使用固定 speed_factor=0.5（加速 2 倍）
    simulator = SSEStreamSimulator(
        events,
        speed_factor=0.5,
        on_interrupt=on_interrupt,
        on_complete=on_complete
    )

    return StreamingResponse(
        simulator.stream(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no",
            "Access-Control-Allow-Origin": "*",
        }
    )


@app.post("/api/chat/completions")
async def mock_chat_completions(request: Request):
    """
    兼容原 API 路径 - /api/chat/completions
    自动判断场景（基于 chat_id 状态）
    """
    body = await request.json()
    chat_id = body.get("chat_id", "mock_chat")

    # 🔥 自动判断场景
    is_interrupted = chat_interrupt_states.get(chat_id, False)
    scenario = "resume_to_complete" if is_interrupted else "start_to_interrupt"

    logger.info("=" * 50)
    logger.info(f"📨 Mock /api/chat/completions Request")
    logger.info(f"   Chat ID: {chat_id}")
    logger.info(f"   Is Interrupted: {is_interrupted}")
    logger.info(f"   Auto Scenario: {scenario}")
    logger.info("=" * 50)

    try:
        events = data_loader.get_scenario_events(scenario)
    except (FileNotFoundError, ValueError) as e:
        return {"error": str(e)}

    # 🔥 状态回调
    def on_interrupt():
        chat_interrupt_states[chat_id] = True
        logger.info(f"🔔 Chat {chat_id} marked as INTERRUPTED")

    def on_complete():
        chat_interrupt_states[chat_id] = False
        logger.info(f"✅ Chat {chat_id} marked as COMPLETED")

    simulator = SSEStreamSimulator(
        events,
        speed_factor=0.3,
        on_interrupt=on_interrupt,
        on_complete=on_complete
    )

    return StreamingResponse(
        simulator.stream(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no",
            "Access-Control-Allow-Origin": "*",
        }
    )


# ==================== 辅助函数 ====================

def _get_scenario_description(scenario: str) -> str:
    """获取场景描述"""
    descriptions = {
        "start_to_interrupt": "新对话开始，执行到 HUMAN_INVOLVEMENT 步骤时中断，等待用户输入",
        "resume_to_complete": "从中断状态恢复，继续执行直到完成 WRITING_BLUEPRINT 步骤",
    }
    return descriptions.get(scenario, "No description")


# ==================== 入口 ====================

if __name__ == "__main__":
    import uvicorn

    # 配置日志
    logger.remove()
    logger.add(
        lambda msg: print(msg, end=""),
        format="<green>{time:HH:mm:ss}</green> | <level>{level: <8}</level> | {message}",
        level="DEBUG",
        colorize=True
    )

    print("\n" + "=" * 60)
    print("🎭 Mock SSE Server for Frontend Testing")
    print("=" * 60)
    print(f"📂 Data source: {JSONL_DIR}")
    print(f"🌐 Server URL: http://localhost:8001")
    print(f"📋 API Docs: http://localhost:8001/docs")
    print("=" * 60 + "\n")

    uvicorn.run(
        "mock_sse_server:app",
        host="0.0.0.0",
        port=8001,
        reload=True,
        log_level="info"
    )
