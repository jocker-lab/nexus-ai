import json
from loguru import logger
from typing import Optional
import asyncio

from app.schemas.chats import (
    ChatForm,
    ChatResponse,
    ChatTitleIdResponse,
)
from app.schemas.tags import TagModel

from app.curd.chats import Chats
from app.curd.tags import Tags
from app.curd.folders import Folders
from app.curd.model_providers import ModelProviders

from fastapi import APIRouter, HTTPException, status
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
from app.constants import ERROR_MESSAGES

# LangChain imports for streaming chat
from langchain_openai import ChatOpenAI
from langchain_deepseek import ChatDeepSeek
from langchain_core.messages import HumanMessage, AIMessage, SystemMessage, BaseMessage

router = APIRouter()

# 系统提示词
SYSTEM_PROMPT = "你是一个友好、专业的AI助手。请用简洁、准确的语言回答用户的问题。"

@router.get("", response_model=list[ChatTitleIdResponse])
@router.get("/list", response_model=list[ChatTitleIdResponse], include_in_schema=False)
async def get_session_user_chat_list(user_id: str, page: Optional[int] = None):
    if page is not None:
        limit = 60
        skip = (page - 1) * limit
        return Chats.get_chat_title_id_list_by_user_id(user_id, skip=skip, limit=limit)
    else:
        return Chats.get_chat_title_id_list_by_user_id(user_id)


@router.delete("", response_model=bool)
async def delete_all_user_chats(user_id: str):
    result = Chats.delete_chats_by_user_id(user_id)
    return result


@router.get("/list/user/{user_id}", response_model=list[ChatTitleIdResponse])
async def get_user_chat_list_by_user_id(user_id: str, skip: int = 0, limit: int = 50):
    return Chats.get_chat_list_by_user_id(
        user_id, include_archived=True, skip=skip, limit=limit
    )


@router.post("/new", response_model=Optional[ChatResponse])
async def create_new_chat(form_data: ChatForm, user_id: str):
    try:
        chat = Chats.insert_new_chat(user_id, form_data)
        return ChatResponse(**chat.model_dump())
    except Exception as e:
        logger.exception(e)
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail=ERROR_MESSAGES.DEFAULT()
        )


@router.get("/folder/{folder_id}", response_model=list[ChatResponse])
async def get_chats_by_folder_id(folder_id: str, user_id: str):
    folder_ids = [folder_id]
    children_folders = Folders.get_children_folders_by_id_and_user_id(
        folder_id, user_id
    )
    if children_folders:
        folder_ids.extend([folder.id for folder in children_folders])

    return [
        ChatResponse(**chat.model_dump())
        for chat in Chats.get_chats_by_folder_ids_and_user_id(folder_ids, user_id)
    ]


@router.get("/pinned", response_model=list[ChatResponse])
async def get_user_pinned_chats(user_id: str):
    return [
        ChatResponse(**chat.model_dump())
        for chat in Chats.get_pinned_chats_by_user_id(user_id)
    ]


@router.get("/all", response_model=list[ChatResponse])
async def get_user_chats(user_id: str):
    return [
        ChatResponse(**chat.model_dump())
        for chat in Chats.get_chats_by_user_id(user_id)
    ]


@router.get("/all/archived", response_model=list[ChatResponse])
async def get_user_archived_chats(user_id: str):
    return [
        ChatResponse(**chat.model_dump())
        for chat in Chats.get_archived_chats_by_user_id(user_id)
    ]


@router.get("/all/tags", response_model=list[TagModel])
async def get_all_user_tags(user_id: str):
    try:
        tags = Tags.get_tags_by_user_id(user_id)
        return tags
    except Exception as e:
        logger.exception(e)
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail=ERROR_MESSAGES.DEFAULT()
        )


@router.get("/all/db", response_model=list[ChatResponse])
async def get_all_user_chats_in_db():
    return [ChatResponse(**chat.model_dump()) for chat in Chats.get_chats()]


@router.get("/archived", response_model=list[ChatTitleIdResponse])
async def get_archived_session_user_chat_list(
    user_id: str, skip: int = 0, limit: int = 50
):
    return Chats.get_archived_chat_list_by_user_id(user_id, skip, limit)


@router.post("/archive/all", response_model=bool)
async def archive_all_chats(user_id: str):
    return Chats.archive_all_chats_by_user_id(user_id)


class TagForm(BaseModel):
    name: str


class TagFilterForm(TagForm):
    skip: Optional[int] = 0
    limit: Optional[int] = 50


@router.post("/tags", response_model=list[ChatTitleIdResponse])
async def get_user_chat_list_by_tag_name(
    form_data: TagFilterForm, user_id: str
):
    chats = Chats.get_chat_list_by_user_id_and_tag_name(
        user_id, form_data.name, form_data.skip, form_data.limit
    )
    if len(chats) == 0:
        Tags.delete_tag_by_name_and_user_id(form_data.name, user_id)

    return chats


# ==================== 流式聊天功能 (LangChain 1.0) ====================

class StreamChatRequest(BaseModel):
    message: str
    chat_id: Optional[str] = None  # 首次调用时可为空，会自动创建
    user_id: str
    stream: bool = True
    provider_id: Optional[str] = None  # 模型供应商配置ID
    model_name: Optional[str] = None   # 模型名称（用于Ollama等需要指定具体模型的场景）


def convert_messages_to_langchain(messages: dict) -> list[BaseMessage]:
    """将数据库中的消息格式转换为LangChain消息格式"""
    langchain_messages = [SystemMessage(content=SYSTEM_PROMPT)]

    if not messages:
        return langchain_messages

    # messages格式: {message_id: {role: "user/assistant", content: "...", ...}, ...}
    # 需要按照消息顺序排序（可以通过timestamp或其他字段）
    sorted_messages = sorted(messages.items(), key=lambda x: x[1].get("timestamp", 0))

    for msg_id, msg_data in sorted_messages:
        role = msg_data.get("role", "user")
        content = msg_data.get("content", "")

        if role == "user":
            langchain_messages.append(HumanMessage(content=content))
        elif role == "assistant":
            langchain_messages.append(AIMessage(content=content))

    return langchain_messages


def trim_langchain_messages(messages: list[BaseMessage], max_rounds: int = 10) -> list[BaseMessage]:
    """保留系统消息和最近N轮对话（每轮包含一个human和一个ai消息）"""
    system_messages = [msg for msg in messages if isinstance(msg, SystemMessage)]
    conversation_messages = [msg for msg in messages if not isinstance(msg, SystemMessage)]

    max_messages = max_rounds * 2
    if len(conversation_messages) > max_messages:
        conversation_messages = conversation_messages[-max_messages:]

    return system_messages + conversation_messages


async def stream_chat_response(
    message: str,
    chat_id: Optional[str],
    user_id: str,
    provider_id: Optional[str] = None,
    model_name: Optional[str] = None
):
    """流式生成聊天响应并保存到数据库"""
    try:
        logger.info(f"Starting chat stream for chat_id: {chat_id}, user_id: {user_id}")
        logger.info(f"User message: {message}")
        logger.info(f"Provider ID: {provider_id}, Model Name: {model_name}")

        # 标记是否为新会话
        is_new_chat = False

        # 如果没有chat_id，创建新的chat
        if not chat_id:
            import uuid
            import time

            is_new_chat = True
            chat_id = str(uuid.uuid4())
            chat_form = ChatForm(chat={
                "title": "新对话",  # 临时标题，稍后会使用LLM生成
                "history": {"messages": {}}
            })
            chat = Chats.insert_new_chat(user_id, chat_form)
            chat_id = chat.id
            logger.info(f"Created new chat: {chat_id}")

        # 获取现有聊天记录
        chat = Chats.get_chat_by_id_and_user_id(chat_id, user_id)
        if not chat:
            raise HTTPException(status_code=404, detail="Chat not found")

        # 首先发送chat_id给前端（如果是新创建的）
        yield f"data: {json.dumps({'chat_id': chat_id}, ensure_ascii=False)}\n\n"

        # 获取历史消息并转换为LangChain格式
        history_messages = chat.chat.get("history", {}).get("messages", {})
        langchain_messages = convert_messages_to_langchain(history_messages)

        # 添加当前用户消息
        langchain_messages.append(HumanMessage(content=message))

        # 修剪历史，保留最近10轮对话
        langchain_messages = trim_langchain_messages(langchain_messages, max_rounds=10)

        # 获取模型配置
        llm_model = "qwen2.5:32b"  # 默认模型
        llm_base_url = "http://localhost:11434/v1"  # 默认 Ollama
        llm_api_key = "ollama"  # 默认
        extra_kwargs = {}  # 额外参数

        if provider_id:
            # 使用 get_provider_by_id 而不是 get_provider_by_id_and_user_id
            # 因为前端的 useChat 和 useModelProviders 可能使用不同的默认 user_id
            provider = ModelProviders.get_provider_by_id(provider_id)
            if provider:
                logger.info(f"Found provider: {provider.name}, type: {provider.provider_type}")

                # 根据 provider_type 配置 LLM
                if provider.provider_type == "ollama":
                    llm_base_url = (provider.base_url or "http://localhost:11434") + "/v1"
                    llm_api_key = "ollama"
                    # Ollama 模型名从 provider_config 或 model_name 参数获取
                    config = provider.provider_config or {}
                    llm_model = model_name or config.get("model_name", "qwen2.5:32b")
                elif provider.provider_type == "deepseek":
                    llm_base_url = provider.base_url or "https://api.deepseek.com/v1"
                    llm_api_key = provider.api_key or ""
                    llm_model = model_name or "deepseek-chat"
                    # DeepSeek Reasoner 模型需要特殊处理
                    if llm_model in ["deepseek-reasoner"]:
                        extra_kwargs["model_kwargs"] = {"stream_options": {"include_usage": True}}
                elif provider.provider_type == "openai":
                    llm_base_url = provider.base_url or "https://api.openai.com/v1"
                    llm_api_key = provider.api_key or ""
                    llm_model = model_name or "gpt-4o"
                elif provider.provider_type == "anthropic":
                    # Anthropic 需要使用专门的 ChatAnthropic
                    # 这里暂时用 OpenAI 兼容模式（如果有代理）
                    llm_base_url = provider.base_url or "https://api.anthropic.com/v1"
                    llm_api_key = provider.api_key or ""
                    llm_model = model_name or "claude-3-opus-20240229"
                else:
                    # 其他供应商使用通用 OpenAI 兼容方式
                    if provider.base_url:
                        llm_base_url = provider.base_url
                    if provider.api_key:
                        llm_api_key = provider.api_key
                    if model_name:
                        llm_model = model_name

                logger.info(f"Configured LLM: model={llm_model}, base_url={llm_base_url}")
            else:
                logger.warning(f"Provider not found: {provider_id}, using default config")
        else:
            logger.info("No provider_id specified, using default Ollama config")

        # 配置LLM
        # 对于 DeepSeek 使用专门的 ChatDeepSeek 以获得 reasoning_content 支持
        if provider and provider.provider_type == "deepseek":
            llm = ChatDeepSeek(
                model=llm_model,
                api_key=llm_api_key,
                streaming=True,
            )
            logger.info(f"Using ChatDeepSeek for model={llm_model}")
        else:
            llm = ChatOpenAI(
                model=llm_model,
                base_url=llm_base_url,
                api_key=llm_api_key,
                temperature=0.7,
                streaming=True,
                **extra_kwargs
            )

        # 流式调用LLM
        accumulated_content = ""
        accumulated_reasoning = ""
        async for chunk in llm.astream(langchain_messages):
            # 检查 reasoning_content (DeepSeek Reasoner 推理模型的思考过程)
            # LangChain 会将非标准字段放到 additional_kwargs 中
            reasoning_content = chunk.additional_kwargs.get('reasoning_content', '')
            if reasoning_content:
                accumulated_reasoning += reasoning_content
                # 发送思考过程
                yield f"data: {json.dumps({'reasoning_content': reasoning_content}, ensure_ascii=False)}\n\n"
                await asyncio.sleep(0.01)

            # 处理正式内容
            if chunk.content:
                accumulated_content += chunk.content
                # 发送SSE格式的数据
                yield f"data: {json.dumps({'content': chunk.content}, ensure_ascii=False)}\n\n"
                await asyncio.sleep(0.01)

        # 保存用户消息和AI响应到数据库
        import uuid
        import time

        user_message_id = str(uuid.uuid4())
        ai_message_id = str(uuid.uuid4())
        timestamp = int(time.time() * 1000)

        # 添加用户消息
        Chats.upsert_message_to_chat_by_id_and_message_id(
            chat_id,
            user_message_id,
            {
                "id": user_message_id,
                "role": "user",
                "content": message,
                "timestamp": timestamp,
            }
        )

        # 添加AI响应
        Chats.upsert_message_to_chat_by_id_and_message_id(
            chat_id,
            ai_message_id,
            {
                "id": ai_message_id,
                "role": "assistant",
                "content": accumulated_content,
                "timestamp": timestamp + 1,
            }
        )

        # 如果是新会话，使用LLM生成标题
        if is_new_chat:
            try:
                title_llm = ChatOpenAI(
                    model="qwen2.5:32b",
                    base_url="http://localhost:11434/v1",
                    api_key="ollama",
                    temperature=0.3,
                    streaming=False
                )

                title_prompt = f"""请根据以下对话内容，生成一个简洁、准确的标题（不超过20个字）。
只需要返回标题本身，不要包含引号或其他说明文字。

用户: {message}
助手: {accumulated_content[:200]}

标题:"""

                title_response = await title_llm.ainvoke([HumanMessage(content=title_prompt)])
                generated_title = title_response.content.strip()

                # 清理标题（去除可能的引号等）
                generated_title = generated_title.replace('"', '').replace("'", '').replace('《', '').replace('》', '')

                # 限制标题长度
                if len(generated_title) > 30:
                    generated_title = generated_title[:30] + "..."

                # 更新标题
                Chats.update_chat_title_by_id(chat_id, generated_title)
                logger.info(f"Generated title for chat {chat_id}: {generated_title}")

                # 通知前端标题已更新
                yield f"data: {json.dumps({'title': generated_title}, ensure_ascii=False)}\n\n"
            except Exception as e:
                logger.error(f"Failed to generate title: {str(e)}")
                # 如果生成标题失败，使用默认标题
                default_title = message[:20] + ("..." if len(message) > 20 else "")
                Chats.update_chat_title_by_id(chat_id, default_title)

        # 发送完成信号
        yield "data: [DONE]\n\n"
        logger.info(f"Chat stream completed for chat_id: {chat_id}")

    except Exception as e:
        logger.error(f"Error in chat stream: {str(e)}", exc_info=True)
        yield f"data: {json.dumps({'error': str(e)}, ensure_ascii=False)}\n\n"
        yield "data: [DONE]\n\n"


@router.post("/stream")
async def chat_stream_endpoint(request: StreamChatRequest):
    """聊天流式接口 - 自动创建或使用现有chat"""
    try:
        logger.info(f"Received chat stream request: chat_id={request.chat_id}, user_id={request.user_id}")

        if not request.message.strip():
            raise HTTPException(status_code=400, detail="Message cannot be empty")

        # 如果提供了chat_id，验证其存在且属于该用户
        if request.chat_id:
            chat = Chats.get_chat_by_id_and_user_id(request.chat_id, request.user_id)
            if not chat:
                raise HTTPException(status_code=404, detail="Chat not found")

        return StreamingResponse(
            stream_chat_response(
                request.message,
                request.chat_id,
                request.user_id,
                request.provider_id,
                request.model_name
            ),
            media_type="text/event-stream",
            headers={
                "Cache-Control": "no-cache",
                "Connection": "keep-alive",
                "Access-Control-Allow-Origin": "*",
            }
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Chat stream error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{id}/messages")
async def get_chat_messages(id: str, user_id: str):
    """获取聊天的所有消息（用于前端展示）"""
    try:
        chat = Chats.get_chat_by_id_and_user_id(id, user_id)
        if not chat:
            raise HTTPException(status_code=404, detail="Chat not found")

        messages = chat.chat.get("history", {}).get("messages", {})

        # 转换为列表格式并按时间排序
        messages_list = []
        for msg_id, msg_data in messages.items():
            messages_list.append({
                "id": msg_id,
                "type": "user" if msg_data.get("role") == "user" else "ai",
                "content": msg_data.get("content", ""),
                "timestamp": msg_data.get("timestamp", 0)
            })

        # 按时间戳排序
        messages_list.sort(key=lambda x: x["timestamp"])

        return {
            "chat_id": id,
            "messages": messages_list
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting messages: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{id}", response_model=Optional[ChatResponse])
async def get_chat_by_id(id: str, user_id: str):
    chat = Chats.get_chat_by_id_and_user_id(id, user_id)
    if chat:
        return ChatResponse(**chat.model_dump())
    else:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail=ERROR_MESSAGES.NOT_FOUND
        )


@router.post("/{id}", response_model=Optional[ChatResponse])
async def update_chat_by_id(
    id: str, form_data: ChatForm, user_id: str
):
    chat = Chats.get_chat_by_id_and_user_id(id, user_id)
    if chat:
        updated_chat = {**chat.chat, **form_data.chat}
        chat = Chats.update_chat_by_id(id, updated_chat)
        return ChatResponse(**chat.model_dump())
    else:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail=ERROR_MESSAGES.NOT_FOUND
        )


@router.delete("/{id}", response_model=bool)
async def delete_chat_by_id(id: str, user_id: str):
    chat = Chats.get_chat_by_id(id)
    for tag in chat.meta.get("tags", []):
        if Chats.count_chats_by_tag_name_and_user_id(tag, user_id) == 1:
            Tags.delete_tag_by_name_and_user_id(tag, user_id)
    result = Chats.delete_chat_by_id_and_user_id(id, user_id)
    return result


@router.get("/{id}/pinned", response_model=Optional[bool])
async def get_pinned_status_by_id(id: str, user_id: str):
    chat = Chats.get_chat_by_id_and_user_id(id, user_id)
    if chat:
        return chat.pinned
    else:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail=ERROR_MESSAGES.NOT_FOUND
        )


@router.post("/{id}/pin", response_model=Optional[ChatResponse])
async def pin_chat_by_id(id: str, user_id: str):
    chat = Chats.get_chat_by_id_and_user_id(id, user_id)
    if chat:
        chat = Chats.toggle_chat_pinned_by_id(id)
        return chat
    else:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail=ERROR_MESSAGES.NOT_FOUND
        )


@router.post("/{id}/archive", response_model=Optional[ChatResponse])
async def archive_chat_by_id(id: str, user_id: str):
    chat = Chats.get_chat_by_id_and_user_id(id, user_id)
    if chat:
        chat = Chats.toggle_chat_archive_by_id(id)
        if chat.archived:
            for tag_id in chat.meta.get("tags", []):
                if Chats.count_chats_by_tag_name_and_user_id(tag_id, user_id) == 0:
                    logger.debug(f"deleting tag: {tag_id}")
                    Tags.delete_tag_by_name_and_user_id(tag_id, user_id)
        else:
            for tag_id in chat.meta.get("tags", []):
                tag = Tags.get_tag_by_name_and_user_id(tag_id, user_id)
                if tag is None:
                    logger.debug(f"inserting tag: {tag_id}")
                    tag = Tags.insert_new_tag(tag_id, user_id)
        return ChatResponse(**chat.model_dump())
    else:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail=ERROR_MESSAGES.NOT_FOUND
        )


class ChatFolderIdForm(BaseModel):
    folder_id: Optional[str] = None


@router.post("/{id}/folder", response_model=Optional[ChatResponse])
async def update_chat_folder_id_by_id(
    id: str, form_data: ChatFolderIdForm, user_id: str
):
    chat = Chats.get_chat_by_id_and_user_id(id, user_id)
    if chat:
        chat = Chats.update_chat_folder_id_by_id_and_user_id(
            id, user_id, form_data.folder_id
        )
        return ChatResponse(**chat.model_dump())
    else:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail=ERROR_MESSAGES.NOT_FOUND
        )


@router.get("/{id}/tags", response_model=list[TagModel])
async def get_chat_tags_by_id(id: str, user_id: str):
    chat = Chats.get_chat_by_id_and_user_id(id, user_id)
    if chat:
        tags = chat.meta.get("tags", [])
        return Tags.get_tags_by_ids_and_user_id(tags, user_id)
    else:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail=ERROR_MESSAGES.NOT_FOUND
        )


@router.post("/{id}/tags", response_model=list[TagModel])
async def add_tag_by_id_and_tag_name(id: str, form_data: TagForm, user_id: str):
    chat = Chats.get_chat_by_id_and_user_id(id, user_id)
    if chat:
        tags = chat.meta.get("tags", [])
        tag_id = form_data.name.replace(" ", "_").lower()
        if tag_id == "none":
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=ERROR_MESSAGES.DEFAULT("Tag name cannot be 'None'"),
            )
        if tag_id not in tags:
            Chats.add_chat_tag_by_id_and_user_id_and_tag_name(
                id, user_id, form_data.name
            )
        chat = Chats.get_chat_by_id_and_user_id(id, user_id)
        tags = chat.meta.get("tags", [])
        return Tags.get_tags_by_ids_and_user_id(tags, user_id)
    else:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail=ERROR_MESSAGES.NOT_FOUND
        )


@router.delete("/{id}/tags", response_model=list[TagModel])
async def delete_tag_by_id_and_tag_name(
    id: str, form_data: TagForm, user_id: str
):
    chat = Chats.get_chat_by_id_and_user_id(id, user_id)
    if chat:
        Chats.delete_tag_by_id_and_user_id_and_tag_name(id, user_id, form_data.name)
        if Chats.count_chats_by_tag_name_and_user_id(form_data.name, user_id) == 0:
            Tags.delete_tag_by_name_and_user_id(form_data.name, user_id)
        chat = Chats.get_chat_by_id_and_user_id(id, user_id)
        tags = chat.meta.get("tags", [])
        return Tags.get_tags_by_ids_and_user_id(tags, user_id)
    else:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail=ERROR_MESSAGES.NOT_FOUND
        )


@router.delete("/{id}/tags/all", response_model=Optional[bool])
async def delete_all_tags_by_id(id: str, user_id: str):
    chat = Chats.get_chat_by_id_and_user_id(id, user_id)
    if chat:
        Chats.delete_all_tags_by_id_and_user_id(id, user_id)
        for tag in chat.meta.get("tags", []):
            if Chats.count_chats_by_tag_name_and_user_id(tag, user_id) == 0:
                Tags.delete_tag_by_name_and_user_id(tag, user_id)
        return True
    else:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail=ERROR_MESSAGES.NOT_FOUND
        )


# ==================== 新增功能 ====================

class ChatTitleForm(BaseModel):
    title: str


@router.patch("/{id}/title", response_model=Optional[ChatResponse])
async def update_chat_title_by_id(id: str, form_data: ChatTitleForm, user_id: str):
    """更新会话标题"""
    chat = Chats.get_chat_by_id_and_user_id(id, user_id)
    if chat:
        updated_chat = Chats.update_chat_title_by_id(id, form_data.title)
        return ChatResponse(**updated_chat.model_dump())
    else:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail=ERROR_MESSAGES.NOT_FOUND
        )


@router.post("/{id}/clone", response_model=Optional[ChatResponse])
async def clone_chat_by_id(id: str, user_id: str):
    """复制会话"""
    import uuid
    import time

    chat = Chats.get_chat_by_id_and_user_id(id, user_id)
    if not chat:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail=ERROR_MESSAGES.NOT_FOUND
        )

    # 创建新的会话副本
    new_chat_id = str(uuid.uuid4())
    cloned_chat_data = chat.chat.copy()
    cloned_chat_data["title"] = f"{chat.chat.get('title', '新对话')} (副本)"

    chat_form = ChatForm(chat=cloned_chat_data)
    new_chat = Chats.insert_new_chat(user_id, chat_form)

    return ChatResponse(**new_chat.model_dump())


@router.get("/{id}/export")
async def export_chat_by_id(id: str, user_id: str):
    """导出会话为JSON文件"""
    from fastapi.responses import Response

    chat = Chats.get_chat_by_id_and_user_id(id, user_id)
    if not chat:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail=ERROR_MESSAGES.NOT_FOUND
        )

    # 准备导出数据
    export_data = {
        "id": chat.id,
        "title": chat.chat.get("title", "新对话"),
        "created_at": chat.created_at,
        "updated_at": chat.updated_at,
        "messages": []
    }

    # 提取消息历史
    messages = chat.chat.get("history", {}).get("messages", {})
    sorted_messages = sorted(messages.items(), key=lambda x: x[1].get("timestamp", 0))

    for msg_id, msg_data in sorted_messages:
        export_data["messages"].append({
            "role": msg_data.get("role", "user"),
            "content": msg_data.get("content", ""),
            "timestamp": msg_data.get("timestamp", 0)
        })

    # 返回JSON文件
    json_content = json.dumps(export_data, ensure_ascii=False, indent=2)
    filename = f"chat_{chat.id}_{export_data['title'][:20]}.json"

    return Response(
        content=json_content,
        media_type="application/json",
        headers={
            "Content-Disposition": f'attachment; filename="{filename}"'
        }
    )