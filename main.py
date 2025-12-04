import re
import time
import json
from langgraph_sdk import get_client
from pydantic import BaseModel
from fastapi import FastAPI, Request, HTTPException
from langchain_deepseek import ChatDeepSeek
from langchain_openai import ChatOpenAI
from fastapi.responses import StreamingResponse
from typing import AsyncGenerator, Dict

from app.config import LOCAL_BIG_MODEL_PARAMS, settings

from app.api.endpoints import chats, folders, documents, model_providers, writing_templates
from app.api.endpoints import auth, users, groups, roles
from loguru import logger
# from langchain.prompts import ChatPromptTemplate
# from app.core.prompts.chart_generate_prompt import CHART_GENERATE_PROMPTS
from langchain_core.output_parsers import JsonOutputParser
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager

from app.database.db import SessionLocal
from app.auth.init_admin import ensure_admin_exists

# from app.core.agents.system_assistant_agent.src.agent.graph import SystemAssistantAgent
# from app.core.agents.system_assistant_agent.src.agent.tools import vector_store_menu_collect, vector_store_system_collect


@asynccontextmanager
async def lifespan(app: FastAPI):
    """应用生命周期管理"""
    # 启动时执行
    logger.info("Application starting up...")

    # 初始化默认 admin 用户
    db = SessionLocal()
    try:
        ensure_admin_exists(db)
    finally:
        db.close()

    yield

    # 关闭时执行
    logger.info("Application shutting down...")


app = FastAPI(title="LangGraph API Service", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 允许的源列表
    allow_credentials=True,  # 是否允许发送凭证（如 Cookies、Authorization 头）
    allow_methods=["*"],  # 允许的 HTTP 方法（"*" 表示所有方法，如 GET、POST、PUT 等）
    allow_headers=["*"],  # 允许的请求头（"*" 表示所有头）
)


# 注册路由

app.include_router(chats.router, prefix="/api/v1/chats", tags=["chat"])

app.include_router(folders.router, prefix="/api/v1/folders", tags=["folder"])

app.include_router(documents.router, prefix="/api/v1/documents", tags=["documents"])

app.include_router(model_providers.router, prefix="/api/v1/model-providers", tags=["model-providers"])

# 写作模版路由
app.include_router(writing_templates.router, prefix="/api/v1/writing-templates", tags=["writing-templates"])

# 认证和用户管理路由
app.include_router(auth.router, prefix="/api/v1/auth", tags=["auth"])
app.include_router(users.router, prefix="/api/v1/users", tags=["users"])
app.include_router(groups.router, prefix="/api/v1/groups", tags=["groups"])
app.include_router(roles.router, prefix="/api/v1/roles", tags=["roles"])

@app.get("/")
def read_root():
    return {"message": "Welcome to LangGraph API Service!"}



# class ChatRequest(BaseModel):
#     agent_name: str
#     user_id: str
#     chart_id: str
#     message: str
#
# model = ChatDeepSeek(api_key=settings.DEEPSEEK_API_KEY, model="deepseek-chat")
#
# # @app.post("/api/chat/echarts_option")
# # async def generate_echarts_option(request: Request, data: Dict):
# #     try:
# #         # Validate input data
# #         if not data or not isinstance(data, dict):
# #             raise HTTPException(status_code=400, detail="Invalid or empty data provided")
# #
# #         # Create prompt template
# #         assistant_prompt = ChatPromptTemplate.from_messages(
# #             [
# #                 ("system", CHART_GENERATE_PROMPTS),
# #                 ("placeholder", "{messages}"),
# #             ]
# #         )
# #         # Prepare messages for the model
# #         messages = [("user", json.dumps(data))]
# #
# #         # Invoke the model
# #         response = (assistant_prompt | model).invoke({"messages": messages})
# #
# #         # Clean the response: remove code block markers and language identifiers
# #         cleaned_response = re.sub(r'```(?:json|javascript)?\n?', '', response.content).strip()
# #         cleaned_response = re.sub(r'```$', '', cleaned_response).strip()
# #
# #         # Parse the cleaned response as JSON
# #         parser = JsonOutputParser()
# #         parsed_option = parser.parse(cleaned_response)
# #
# #         # Validate that the parsed output is a dict
# #         if not isinstance(parsed_option, dict):
# #             raise HTTPException(status_code=500, detail="Model did not return a valid ECharts option object")
# #
# #         return parsed_option
# #
# #     except json.JSONDecodeError as e:
# #         raise HTTPException(status_code=500, detail=f"Failed to parse model response as JSON: {str(e)}")
# #     except Exception as e:
# #         raise HTTPException(status_code=500, detail=f"Error generating ECharts option: {str(e)}")
#
# async def stream_metric_vision_response(request: Request, form_data: ChatRequest) -> AsyncGenerator[str, None]:
#     client_ip = request.client.host
#     logger.info(f"Received chat completion request from IP: {client_ip}, message: {form_data.message}")
#
#     client = get_client(url="http://localhost:2024")
#     assistant_id = "MetricVisionAgent"
#
#     try:
#         logger.info(f"Creating thread for request from IP: {client_ip}")
#         thread = await client.threads.create()
#         thread_id = thread["thread_id"]
#         logger.info(f"Thread created with ID: {thread_id} for IP: {client_ip}")
#
#         logger.info(f"Starting stream response for thread {thread_id} from IP: {client_ip}")
#         async for chunk in client.runs.stream(
#             thread_id,
#             assistant_id,
#             input={"messages": [{"role": "human", "content": form_data.message}]}, config={"recursion_limit": 100},
#             stream_mode="messages-tuple"
#         ):
#             if "messages" not in chunk.event:
#                 continue
#             message_chunk, metadata = chunk.data
#             current_tag = metadata.get("tags", [None])[0]
#             logger.info(f"Processing chunk with tag: {current_tag} for thread {thread_id}, IP: {client_ip}")
#
#             if message_chunk.get("type") == "AIMessageChunk":
#                 if current_tag == "sql_assistant":
#                     message_chunk["type"] = "ThinkingMessageChunk"
#                     message_chunk["thinking_content"] = message_chunk["content"]
#                     message_chunk["content"] = ""
#                     logger.info(f"Converted to ThinkingMessageChunk for tag sql_assistant, thread {thread_id}, IP: {client_ip}")
#
#                 tool_call_chunks = message_chunk.get("tool_call_chunks", [])
#                 if tool_call_chunks:
#                     if current_tag == "sql_assistant":
#                         message_chunk["type"] = "ToolMessageChunk"
#                         logger.info(f"Yielding ToolMessageChunk for tag sql_assistant, thread {thread_id}, IP: {client_ip}")
#                         yield f"data: {json.dumps(message_chunk, ensure_ascii=False)}\n\n"
#                         continue
#                     else:
#                         logger.info(f"Skipping tool call chunk for non-sql_assistant tag, thread {thread_id}, IP: {client_ip}")
#                         continue
#                 else:
#                     if message_chunk["content"] or message_chunk.get("thinking_content", None):
#                         logger.info(f"Yielding AIMessageChunk content, thread {thread_id}, IP: {client_ip}")
#                         yield f"data: {json.dumps(message_chunk, ensure_ascii=False)}\n\n"
#             elif message_chunk.get("type") == "tool":
#                 message_chunk["type"] = "ToolResultChunk"
#                 logger.info(f"Yielding ToolResultChunk, thread {thread_id}, IP: {client_ip}")
#                 yield f"data: {json.dumps(message_chunk, ensure_ascii=False)}\n\n"
#                 yield f"data: TOOL_DONE\n\n"
#         logger.info(f"Stream completed for thread {thread_id}, IP: {client_ip}")
#         yield f"data: DONE\n\n"  # Only yield DONE on successful completion
#     except Exception as e:
#         logger.error(f"Error processing request from IP: {client_ip}, thread {thread_id if 'thread_id' in locals() else 'unknown'}: {str(e)}")
#         error_chunk = {
#             "type": "error",
#             "error": str(e)
#         }
#         yield f"data: {json.dumps(error_chunk, ensure_ascii=False)}\n\n"
#     finally:
#         if hasattr(client, 'close'):
#             await client.close()
#
# async def stream_deep_research_response(request: Request, form_data: ChatRequest) -> AsyncGenerator[str, None]:
#     client_ip = request.client.host
#     logger.info(f"Chat deep research request from IP: {client_ip}, User: {form_data.user_id}, Session: {form_data.user_id}")
#
#     if not form_data.message.strip():
#         logger.warning(f"Empty message from IP: {client_ip}, User: {form_data.user_id}")
#         raise HTTPException(status_code=400, detail="Message cannot be empty")
#
#     client = get_client(url="http://localhost:2023")
#     assistant_id = "DeepResearcher"
#
#     try:
#         thread = await client.threads.create()
#         thread_id = thread.get("thread_id")
#         if not thread_id:
#             logger.error(f"Failed to create thread for User: {form_data.user_id}")
#             yield f"data: {json.dumps({'error': 'Failed to create thread'}, ensure_ascii=False)}\n\n"
#             return
#
#         logger.debug(f"Created thread {thread_id} for User: {form_data.user_id}")
#
#         async for chunk in client.runs.stream(
#             thread_id,
#             assistant_id,
#             input={"messages": [{"role": "human", "content": form_data.message}]},
#             stream_mode=["updates", "messages-tuple"]
#         ):
#             if chunk.event == "messages" and chunk.data[0].get("content"):
#                 logger.debug(f"Streaming AIMessageChunk: {chunk.data[0]}")
#                 yield f"data: {json.dumps(chunk.data[0], ensure_ascii=False)}\n\n"
#             elif chunk.event == "updates":
#                 logger.debug(f"Streaming ToolMessageChunk: {chunk.data}")
#                 yield f"data: {json.dumps(chunk.data, ensure_ascii=False)}\n\n"
#         yield f"data: DONE\n\n"  # Only yield DONE on successful completion
#     except ValueError as e:
#         logger.error(f"Value error from IP: {client_ip}, User: {form_data.user_id}: {str(e)}")
#         yield f"data: {json.dumps({'error': f'Invalid response: {str(e)}'}, ensure_ascii=False)}\n\n"
#     except Exception as e:
#         logger.error(f"Unexpected error from IP: {client_ip}, User: {form_data.user_id}: {str(e)}")
#         yield f"data: {json.dumps({'error': 'Internal server error'}, ensure_ascii=False)}\n\n"
#     finally:
#         if hasattr(client, 'close'):
#             await client.close()
#
#
# # async def stream_system_assistant_response(request: Request, form_data: ChatRequest) -> AsyncGenerator[str, None]:
# #     start_time = time.perf_counter()  # High-resolution timer for measuring processing time
# #     client_ip = request.client.host
# #     logger.info(
# #         f"Chat deep research request received from IP: {client_ip}, User: {form_data.user_id}, Session: {form_data.user_id}, Message: {form_data.message[:50]}...")  # Truncate long messages for log brevity
# #
# #     try:
# #         llm = ChatOpenAI(
# #             **LOCAL_BIG_MODEL_PARAMS)  # Assuming LOCAL_BIG_MODEL_PARAMS is defined elsewhere; consider caching if possible for optimization
# #         assistant = SystemAssistantAgent(llm=llm)
# #         system_assistant = assistant._create_graph()
# #
# #         async for message_type, chunk in system_assistant.astream(
# #                 {"messages": [{"role": "user", "content": form_data.message}]}, stream_mode=["messages", "updates"]):
# #
# #
# #             if message_type == "messages":
# #                 message_chunk, metadata = chunk
# #                 if message_chunk.content and metadata["langgraph_node"] in ["system_feature_guide_input_parser",
# #                                                                             "system_feature_guide_generate_answer",
# #                                                                             "system_route_assistant"]:
# #                     node = metadata["langgraph_node"]
# #                     if node in ("system_feature_guide_input_parser", "system_feature_guide_generate_answer", "system_route_assistant"):
# #                         yield f"data: {json.dumps({'format': 'messages', 'type': 'AIMessageChunk', 'content': message_chunk.content, 'additional_kwargs': message_chunk.additional_kwargs, 'response_metadata': message_chunk.response_metadata, 'id': message_chunk.id}, ensure_ascii=False)}\n\n"
# #             elif message_type == "updates" and "system_route_assistant" in chunk:
# #                 yield f"data: {json.dumps({'format': 'json', 'type': 'AIMessageChunk', 'content': chunk["system_route_assistant"]}, ensure_ascii=False)}\n\n"
# #
# #             else:
# #                 pass
# #         yield f"data: DONE\n\n"
# #
# #     except Exception as e:
# #         logger.error(f"Error processing request from IP: {client_ip}, User: {form_data.user_id}: {str(e)}",
# #                      exc_info=True)
# #         error_message = json.dumps(
# #             {"format": "error", "type": "Error", "content": "An unexpected error occurred. Please try again later."},
# #             ensure_ascii=False)
# #         yield f"data: {error_message}\n\n"
# #         yield f"data: DONE\n\n"  # Ensure stream closes properly even on error
# #         # Optionally, raise HTTPException(500, detail="Internal Server Error") if you want to terminate the response with an HTTP error, but since it's streaming, yielding is better
# #
# #     finally:
# #         end_time = time.perf_counter()
# #         processing_time = end_time - start_time
# #         logger.info(f"Chat deep research request completed from IP: {client_ip}, User: {form_data.user_id}. Processing time: {processing_time:.2f} seconds")
#
#
# async def stream_base_response(request: Request, form_data: ChatRequest) -> AsyncGenerator[str, None]:
#     client_ip = request.client.host
#     logger.info(f"Chat deep research request from IP: {client_ip}, User: {form_data.user_id}, Session: {form_data.user_id}")
#     if not form_data.message.strip():
#         logger.warning(f"Empty message from IP: {client_ip}, User: {form_data.user_id}")
#         raise HTTPException(status_code=400, detail="Message cannot be empty")
#
#     client = get_client(url="http://localhost:2025")
#     assistant_id = "base_agent"
#     try:
#         thread = await client.threads.create()
#         thread_id = thread.get("thread_id")
#         if not thread_id:
#             logger.error(f"Failed to create thread for User: {form_data.user_id}")
#             yield f"data: {json.dumps({'error': 'Failed to create thread'}, ensure_ascii=False)}\n\n"
#             return
#
#         logger.debug(f"Created thread {thread_id} for User: {form_data.user_id}")
#
#         logger.info(thread_id)
#         logger.info(assistant_id)
#         logger.info(form_data.message)
#         async for chunk in client.runs.stream(
#             thread_id,
#             assistant_id,
#             input={"messages": [{"role": "human", "content": form_data.message}]},
#             stream_mode=["messages-tuple"]
#         ):
#             if chunk.event == "messages" and chunk.data[0].get("type") == "tool" :
#                 if chunk.data[0].get("name") == "weather_search_tool":
#                     yield f"data: {json.dumps({"searching": False}, ensure_ascii=False)}\n\n"
#                     chunk_data = chunk.data[0]
#                     chunk_data["urls"] = ["https://openweathermap.org/"]
#                     yield f"data: {json.dumps(chunk_data, ensure_ascii=False)}\n\n"
#                 else:
#                     chunk_data = chunk.data[0]
#                     logger.info(chunk.data[0].get("artifact").get("results", []))
#                     chunk_data["urls"] = [i.get("url", None) for i in chunk.data[0].get("artifact").get("results", [])]
#
#                     yield f"data: {json.dumps(chunk_data, ensure_ascii=False)}\n\n"
#
#             elif chunk.event == "messages" and "tool_calls" in chunk.data[0].get("additional_kwargs", {}):
#                 yield f"data: {json.dumps({"searching" : True}, ensure_ascii=False)}\n\n"
#
#             elif chunk.event == "messages" and chunk.data[0].get("content"):
#                 yield f"data: {json.dumps(chunk.data[0], ensure_ascii=False)}\n\n"
#
#         yield f"data: DONE\n\n"  # Only yield DONE on successful completion
#     except ValueError as e:
#         logger.error(f"Value error from IP: {client_ip}, User: {form_data.user_id}: {str(e)}")
#         yield f"data: {json.dumps({'error': f'Invalid response: {str(e)}'}, ensure_ascii=False)}\n\n"
#     except Exception as e:
#         logger.error(f"Unexpected error from IP: {client_ip}, User: {form_data.user_id}: {str(e)}")
#         yield f"data: {json.dumps({'error': 'Internal server error'}, ensure_ascii=False)}\n\n"
#     finally:
#         if hasattr(client, 'close'):
#             await client.close()
#
#
# @app.post("/api/chat/completions")
# async def chat_completions(request: Request, form_data: ChatRequest):
#     """Chat completions endpoint with streaming response, supporting multiple agents types"""
#     stream_handler = {
#         "base": stream_base_response,
#         "metric_vision": stream_metric_vision_response,
#         "deep_research": stream_deep_research_response,
#         # "system_assistant": stream_system_assistant_response,
#     }.get(form_data.agent_name)
#
#     if not stream_handler:
#         raise HTTPException(status_code=400, detail=f"Invalid agent_name: {form_data.agent_name}")
#
#     return StreamingResponse(
#         stream_handler(request, form_data),
#         media_type="text/event-stream",
#         headers={
#             "Cache-Control": "no-cache",
#             "Connection": "keep-alive",
#             "X-Accel-Buffering": "no"
#         }
#     )
