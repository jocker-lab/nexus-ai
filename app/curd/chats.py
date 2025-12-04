import uuid
import time
from typing import Optional
from app.schemas.chats import ChatForm, ChatModel, ChatTitleIdResponse
from app.models.chats import Chat
from sqlalchemy import or_
from app.database.db import get_db_context
from loguru import logger

class ChatTable:

    # ---------------------- 创建（Create） ----------------------
    # 插入新的聊天记录
    def insert_new_chat(self, user_id: str, form_data: ChatForm) -> Optional[ChatModel]:
        """
        创建一条新的聊天记录，包含聊天标题、历史消息等
        """
        with get_db_context() as db:
            id = str(uuid.uuid4())
            chat = ChatModel(
                **{
                    "id": id,
                    "user_id": user_id,
                    "title": form_data.chat.get("title", "New Chat"),
                    "chat": form_data.chat,
                    "created_at": int(time.time()),
                    "updated_at": int(time.time()),
                }
            )
            result = Chat(**chat.model_dump())
            db.add(result)
            db.commit()
            db.refresh(result)
            return ChatModel.model_validate(result)

    # 插入或更新指定消息
    def upsert_message_to_chat_by_id_and_message_id(self, id: str, message_id: str, message: dict) -> Optional[ChatModel]:
        """
        添加或更新聊天记录中的指定消息
        """
        chat = self.get_chat_by_id(id)
        if not chat:
            return None

        history = chat.chat.setdefault("history", {})
        messages = history.setdefault("messages", {})
        messages[message_id] = {**messages.get(message_id, {}), **message}
        history["currentId"] = message_id
        return self.update_chat_by_id(id, chat.chat)

    # 添加消息状态
    def add_message_status_to_chat_by_id_and_message_id(self, id: str, message_id: str, status: dict) -> Optional[ChatModel]:
        """
        向某条消息追加状态历史记录
        """
        chat = self.get_chat_by_id(id)
        if not chat:
            return None

        history = chat.chat.setdefault("history", {})
        if message_id in history.get("messages", {}):
            status_history = history["messages"][message_id].setdefault("statusHistory", [])
            status_history.append(status)

        return self.update_chat_by_id(id, chat.chat)


    # ---------------------- 读取（Read） ----------------------

    def get_chat_by_id(self, id: str) -> Optional[ChatModel]:
        """根据聊天ID获取完整聊天对象"""
        try:
            with get_db_context() as db:
                return ChatModel.model_validate(db.get(Chat, id))
        except Exception:
            return None

    def get_chat_by_id_and_user_id(self, id: str, user_id: str) -> Optional[ChatModel]:
        """根据聊天ID与用户ID获取聊天"""
        try:
            with get_db_context() as db:
                chat = db.query(Chat).filter_by(id=id, user_id=user_id).first()
                return ChatModel.model_validate(chat)
        except Exception:
            return None

    def get_chat_title_by_id(self, id: str) -> Optional[str]:
        """获取聊天标题"""
        chat = self.get_chat_by_id(id)
        return chat.chat.get("title", "New Chat") if chat else None

    def get_messages_by_chat_id(self, id: str) -> Optional[dict]:
        """获取指定聊天的所有消息"""
        chat = self.get_chat_by_id(id)
        return chat.chat.get("history", {}).get("messages", {}) if chat else None

    def get_message_by_id_and_message_id(self, id: str, message_id: str) -> Optional[dict]:
        """获取指定聊天中指定消息"""
        chat = self.get_chat_by_id(id)
        return chat.chat.get("history", {}).get("messages", {}).get(message_id, {}) if chat else None

    def get_chat_list_by_user_id(self, user_id: str, include_archived: bool = False, skip: int = 0, limit: int = 50) -> list[ChatModel]:
        """获取用户下所有聊天列表"""
        with get_db_context() as db:
            query = db.query(Chat).filter_by(user_id=user_id)
            if not include_archived:
                query = query.filter_by(archived=False)
            # logger.info([ChatModel.model_validate(c) for c in query.order_by(Chat.updated_at.desc()).offset(skip).limit(limit).all()][0])
            return [ChatModel.model_validate(c) for c in query.order_by(Chat.updated_at.desc()).offset(skip).limit(limit).all()]

    def get_pinned_chats_by_user_id(self, user_id: str) -> list[ChatModel]:
        """获取用户置顶的聊天"""
        with get_db_context() as db:
            return [ChatModel.model_validate(c) for c in db.query(Chat).filter_by(user_id=user_id, pinned=True, archived=False).order_by(Chat.updated_at.desc()).all()]

    def get_archived_chats_by_user_id(self, user_id: str) -> list[ChatModel]:
        """获取用户归档聊天"""
        with get_db_context() as db:
            return [ChatModel.model_validate(c) for c in db.query(Chat).filter_by(user_id=user_id, archived=True).order_by(Chat.updated_at.desc()).all()]

    def get_chat_title_id_list_by_user_id(self, user_id: str, include_archived: bool = False, skip: Optional[int] = None, limit: Optional[int] = None) -> list[ChatTitleIdResponse]:
        """获取用户聊天ID和标题的简要列表"""
        with get_db_context() as db:
            query = db.query(Chat).filter_by(user_id=user_id, folder_id=None)
            query = query.filter(or_(Chat.pinned == False, Chat.pinned == None))
            if not include_archived:
                query = query.filter_by(archived=False)
            query = query.order_by(Chat.updated_at.desc()).with_entities(Chat.id, Chat.title, Chat.pinned, Chat.updated_at, Chat.created_at)
            if skip: query = query.offset(skip)
            if limit: query = query.limit(limit)
            return [ChatTitleIdResponse.model_validate({"id": r[0], "title": r[1], "pinned": r[2] or False, "updated_at": r[3], "created_at": r[4]}) for r in query.all()]

    def get_chats_by_folder_id_and_user_id(self, folder_id: str, user_id: str) -> list[ChatModel]:
        """获取指定文件夹下的聊天"""
        with get_db_context() as db:
            query = db.query(Chat).filter_by(folder_id=folder_id, user_id=user_id, archived=False)
            query = query.filter(or_(Chat.pinned == False, Chat.pinned == None))
            return [ChatModel.model_validate(chat) for chat in query.order_by(Chat.updated_at.desc()).all()]


    # ---------------------- 更新（Update） ----------------------

    def update_chat_by_id(self, id: str, chat: dict) -> Optional[ChatModel]:
        """更新整个聊天内容，包括标题和消息"""
        try:
            with get_db_context() as db:
                chat_item = db.get(Chat, id)
                chat_item.chat = chat
                chat_item.title = chat.get("title", "New Chat")
                chat_item.updated_at = int(time.time())
                db.commit()
                db.refresh(chat_item)
                return ChatModel.model_validate(chat_item)
        except Exception:
            return None

    def update_chat_title_by_id(self, id: str, title: str) -> Optional[ChatModel]:
        """仅更新聊天标题"""
        chat = self.get_chat_by_id(id)
        if chat is None:
            return None
        chat.chat["title"] = title
        return self.update_chat_by_id(id, chat.chat)

    def toggle_chat_pinned_by_id(self, id: str) -> Optional[ChatModel]:
        """切换聊天置顶状态"""
        try:
            with get_db_context() as db:
                chat = db.get(Chat, id)
                chat.pinned = not chat.pinned
                chat.updated_at = int(time.time())
                db.commit()
                db.refresh(chat)
                return ChatModel.model_validate(chat)
        except Exception:
            return None

    def toggle_chat_archive_by_id(self, id: str) -> Optional[ChatModel]:
        """切换聊天归档状态"""
        try:
            with get_db_context() as db:
                chat = db.get(Chat, id)
                chat.archived = not chat.archived
                chat.updated_at = int(time.time())
                db.commit()
                db.refresh(chat)
                return ChatModel.model_validate(chat)
        except Exception:
            return None

    def update_chat_folder_id_by_id_and_user_id(self, id: str, user_id: str, folder_id: str) -> Optional[ChatModel]:
        """将聊天移动到指定文件夹"""
        try:
            with get_db_context() as db:
                chat = db.get(Chat, id)
                chat.folder_id = folder_id
                chat.updated_at = int(time.time())
                chat.pinned = False
                db.commit()
                db.refresh(chat)
                return ChatModel.model_validate(chat)
        except Exception:
            return None


    # ---------------------- 删除（Delete） ----------------------

    def delete_chat_by_id(self, id: str) -> bool:
        """删除单个聊天（包括分享记录）"""
        try:
            with get_db_context() as db:
                db.query(Chat).filter_by(id=id).delete()
                db.commit()
                return True
        except Exception:
            return False

    def delete_chat_by_id_and_user_id(self, id: str, user_id: str) -> bool:
        """删除指定用户的某条聊天"""
        try:
            with get_db_context() as db:
                db.query(Chat).filter_by(id=id, user_id=user_id).delete()
                db.commit()
                return True
        except Exception:
            return False

    def delete_chats_by_user_id(self, user_id: str) -> bool:
        """删除用户下所有聊天"""
        try:
            with get_db_context() as db:
                self.delete_shared_chats_by_user_id(user_id)
                db.query(Chat).filter_by(user_id=user_id).delete()
                db.commit()
                return True
        except Exception:
            return False

    def delete_chats_by_user_id_and_folder_id(self, user_id: str, folder_id: str) -> bool:
        """删除文件夹下所有聊天"""
        try:
            with get_db_context() as db:
                db.query(Chat).filter_by(user_id=user_id, folder_id=folder_id).delete()
                db.commit()
                return True
        except Exception:
            return False

    def archive_all_chats_by_user_id(self, user_id: str) -> bool:
        """批量归档用户下所有聊天"""
        try:
            with get_db_context() as db:
                db.query(Chat).filter_by(user_id=user_id).update({"archived": True})
                db.commit()
                return True
        except Exception:
            return False

Chats = ChatTable()
