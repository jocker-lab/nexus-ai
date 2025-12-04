import uuid
import time
from typing import Optional
from app.schemas.folders import FolderModel
from app.curd.chats import Chats
from app.models.folders import Folder
from loguru import logger
from app.database.db import get_db_context


class FolderTable:
    # ----------------------------
    # Create
    # ----------------------------

    # 新建一个文件夹
    def insert_new_folder(self, user_id: str, name: str, parent_id: Optional[str] = None) -> Optional[FolderModel]:
        with get_db_context() as db:
            id = str(uuid.uuid4())
            folder = FolderModel(
                **{
                    "id": id,
                    "user_id": user_id,
                    "name": name,
                    "parent_id": parent_id,
                    "created_at": int(time.time()),
                    "updated_at": int(time.time()),
                }
            )
            try:
                result = Folder(**folder.model_dump())
                db.add(result)
                db.commit()
                db.refresh(result)
                return FolderModel.model_validate(result) if result else None
            except Exception as e:
                logger.error(e)
                return None

    # ----------------------------
    # Read
    # ----------------------------

    # 根据 folder_id 和 user_id 获取文件夹
    def get_folder_by_id_and_user_id(self, id: str, user_id: str) -> Optional[FolderModel]:
        try:
            with get_db_context() as db:
                folder = db.query(Folder).filter_by(id=id, user_id=user_id).first()
                return FolderModel.model_validate(folder) if folder else None
        except Exception as e:
            logger.error(e)
            return None

    # 获取用户所有的根/子文件夹
    def get_folders_by_user_id(self, user_id: str) -> list[FolderModel]:
        with get_db_context() as db:
            return [FolderModel.model_validate(folder) for folder in db.query(Folder).filter_by(user_id=user_id).all()]

    # 根据 parent_id 和 user_id 获取子文件夹列表
    def get_folders_by_parent_id_and_user_id(self, parent_id: Optional[str], user_id: str) -> list[FolderModel]:
        with get_db_context() as db:
            return [
                FolderModel.model_validate(folder)
                for folder in db.query(Folder).filter_by(parent_id=parent_id, user_id=user_id).all()
            ]

    # 根据 parent_id、user_id 和 name 获取文件夹（用于命名检查）
    def get_folder_by_parent_id_and_user_id_and_name(self, parent_id: Optional[str], user_id: str, name: str) -> Optional[FolderModel]:
        try:
            with get_db_context() as db:
                folder = (
                    db.query(Folder)
                    .filter_by(parent_id=parent_id, user_id=user_id)
                    .filter(Folder.name.ilike(name))
                    .first()
                )
                return FolderModel.model_validate(folder) if folder else None
        except Exception as e:
            logger.error(f"get_folder_by_parent_id_and_user_id_and_name: {e}")
            return None

    # 获取某个文件夹及其所有子文件夹（递归）
    def get_children_folders_by_id_and_user_id(self, id: str, user_id: str) -> Optional[list[FolderModel]]:
        try:
            with get_db_context() as db:
                folders = []

                def get_children(folder):
                    children = self.get_folders_by_parent_id_and_user_id(folder.id, user_id)
                    for child in children:
                        get_children(child)
                        folders.append(child)

                folder = db.query(Folder).filter_by(id=id, user_id=user_id).first()
                if not folder:
                    return None

                get_children(folder)
                return folders
        except Exception:
            return None

    # ----------------------------
    # Update
    # ----------------------------

    # 更新文件夹的父节点 ID
    def update_folder_parent_id_by_id_and_user_id(self, id: str, user_id: str, parent_id: str) -> Optional[FolderModel]:
        try:
            with get_db_context() as db:
                folder = db.query(Folder).filter_by(id=id, user_id=user_id).first()
                if not folder:
                    return None
                folder.parent_id = parent_id
                folder.updated_at = int(time.time())
                db.commit()
                return FolderModel.model_validate(folder)
        except Exception as e:
            logger.error(f"update_folder: {e}")
            return None

    # 更新文件夹名称（避免同级重名）
    def update_folder_name_by_id_and_user_id(self, id: str, user_id: str, name: str) -> Optional[FolderModel]:
        try:
            with get_db_context() as db:
                folder = db.query(Folder).filter_by(id=id, user_id=user_id).first()
                if not folder:
                    return None
                existing_folder = (
                    db.query(Folder)
                    .filter_by(name=name, parent_id=folder.parent_id, user_id=user_id)
                    .first()
                )
                if existing_folder:
                    return None
                folder.name = name
                folder.updated_at = int(time.time())
                db.commit()
                return FolderModel.model_validate(folder)
        except Exception as e:
            logger.error(f"update_folder: {e}")
            return None

    # 更新文件夹是否展开的状态
    def update_folder_is_expanded_by_id_and_user_id(self, id: str, user_id: str, is_expanded: bool) -> Optional[FolderModel]:
        try:
            with get_db_context() as db:
                folder = db.query(Folder).filter_by(id=id, user_id=user_id).first()
                if not folder:
                    return None
                folder.is_expanded = is_expanded
                folder.updated_at = int(time.time())
                db.commit()
                return FolderModel.model_validate(folder)
        except Exception as e:
            logger.error(f"update_folder: {e}")
            return None

    # ----------------------------
    # Delete
    # ----------------------------

    # 删除指定文件夹（递归删除所有子文件夹及关联的聊天记录）
    def delete_folder_by_id_and_user_id(self, id: str, user_id: str) -> bool:
        try:
            with get_db_context() as db:
                folder = db.query(Folder).filter_by(id=id, user_id=user_id).first()
                if not folder:
                    return False

                # 删除文件夹下的所有聊天记录
                Chats.delete_chats_by_user_id_and_folder_id(user_id, folder.id)

                # 递归删除所有子文件夹及其聊天记录
                def delete_children(folder):
                    folder_children = self.get_folders_by_parent_id_and_user_id(folder.id, user_id)
                    for folder_child in folder_children:
                        Chats.delete_chats_by_user_id_and_folder_id(user_id, folder_child.id)
                        delete_children(folder_child)
                        child_obj = db.query(Folder).filter_by(id=folder_child.id).first()
                        db.delete(child_obj)
                        db.commit()

                delete_children(folder)

                db.delete(folder)
                db.commit()
                return True
        except Exception as e:
            logger.error(f"delete_folder: {e}")
            return False

# 单例对象
Folders = FolderTable()