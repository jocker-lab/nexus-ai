"""
Model Provider CRUD Operations
模型供应商配置的数据库操作
"""

import uuid
import time
from typing import Optional, List
from loguru import logger

from app.models.model_providers import ModelProvider
from app.schemas.model_providers import (
    ModelProviderModel,
    ModelProviderCreateForm,
    ModelProviderUpdateForm,
    OllamaCreateForm,
    OllamaUpdateForm,
    ProviderType,
    ModelType,
)
from app.database.db import get_db_context


class ModelProviderTable:
    """模型供应商 CRUD 操作类"""

    # ===================== Create =====================

    def create_provider(
        self, user_id: str, form_data: ModelProviderCreateForm
    ) -> Optional[ModelProviderModel]:
        """
        创建新的模型供应商配置

        Args:
            user_id: 用户 ID
            form_data: 创建表单数据

        Returns:
            创建的供应商配置，失败返回 None
        """
        try:
            with get_db_context() as db:
                provider_id = str(uuid.uuid4())
                now = int(time.time())

                # 转换模型类型列表为字符串列表
                model_types = None
                if form_data.supported_model_types:
                    model_types = [mt.value for mt in form_data.supported_model_types]

                # 如果设置为默认，先取消其他同类型的默认
                if form_data.is_default:
                    self._unset_defaults_for_type(
                        db, user_id, form_data.provider_type.value
                    )

                provider = ModelProvider(
                    id=provider_id,
                    user_id=user_id,
                    provider_type=form_data.provider_type.value,
                    name=form_data.name,
                    api_key=form_data.api_key,
                    base_url=form_data.base_url,
                    provider_config=form_data.provider_config,
                    supported_model_types=model_types,
                    is_active=form_data.is_active,
                    is_default=form_data.is_default,
                    connection_status="unknown",
                    created_at=now,
                    updated_at=now,
                )

                db.add(provider)
                db.commit()
                db.refresh(provider)

                logger.info(f"Created model provider: {provider_id} for user: {user_id}")
                return ModelProviderModel.model_validate(provider)

        except Exception as e:
            logger.exception(f"Failed to create model provider: {e}")
            return None

    def create_ollama_provider(
        self, user_id: str, form_data: OllamaCreateForm
    ) -> Optional[ModelProviderModel]:
        """
        创建 Ollama 专用供应商配置

        Args:
            user_id: 用户 ID
            form_data: Ollama 创建表单

        Returns:
            创建的供应商配置，失败返回 None
        """
        try:
            with get_db_context() as db:
                provider_id = str(uuid.uuid4())
                now = int(time.time())

                # Ollama 特定配置
                provider_config = {
                    "context_length": form_data.context_length,
                    "model_name": form_data.model_name,
                    "model_type": form_data.model_type.value,
                }

                # 如果设置为默认，先取消其他 Ollama 的默认
                if form_data.is_default:
                    self._unset_defaults_for_type(db, user_id, ProviderType.OLLAMA.value)

                provider = ModelProvider(
                    id=provider_id,
                    user_id=user_id,
                    provider_type=ProviderType.OLLAMA.value,
                    name=form_data.name,
                    api_key=None,  # Ollama 不需要 API Key
                    base_url=form_data.base_url,
                    provider_config=provider_config,
                    supported_model_types=[form_data.model_type.value],
                    is_active=form_data.is_active,
                    is_default=form_data.is_default,
                    connection_status="unknown",
                    created_at=now,
                    updated_at=now,
                )

                db.add(provider)
                db.commit()
                db.refresh(provider)

                logger.info(f"Created Ollama provider: {provider_id} for user: {user_id}")
                return ModelProviderModel.model_validate(provider)

        except Exception as e:
            logger.exception(f"Failed to create Ollama provider: {e}")
            return None

    # ===================== Read =====================

    def get_provider_by_id(self, provider_id: str) -> Optional[ModelProviderModel]:
        """根据 ID 获取供应商配置"""
        try:
            with get_db_context() as db:
                provider = db.query(ModelProvider).filter(
                    ModelProvider.id == provider_id
                ).first()

                if provider:
                    return ModelProviderModel.model_validate(provider)
                return None

        except Exception as e:
            logger.exception(f"Failed to get provider by id: {e}")
            return None

    def get_provider_by_id_and_user_id(
        self, provider_id: str, user_id: str
    ) -> Optional[ModelProviderModel]:
        """根据 ID 和用户 ID 获取供应商配置（所有权验证）"""
        try:
            with get_db_context() as db:
                provider = db.query(ModelProvider).filter(
                    ModelProvider.id == provider_id,
                    ModelProvider.user_id == user_id
                ).first()

                if provider:
                    return ModelProviderModel.model_validate(provider)
                return None

        except Exception as e:
            logger.exception(f"Failed to get provider by id and user_id: {e}")
            return None

    def get_providers_by_user_id(
        self, user_id: str, active_only: bool = False
    ) -> List[ModelProviderModel]:
        """获取用户的所有供应商配置"""
        try:
            with get_db_context() as db:
                query = db.query(ModelProvider).filter(
                    ModelProvider.user_id == user_id
                )

                if active_only:
                    query = query.filter(ModelProvider.is_active == True)

                providers = query.order_by(ModelProvider.created_at.desc()).all()

                return [ModelProviderModel.model_validate(p) for p in providers]

        except Exception as e:
            logger.exception(f"Failed to get providers by user_id: {e}")
            return []

    def get_providers_by_user_and_type(
        self, user_id: str, provider_type: str, active_only: bool = False
    ) -> List[ModelProviderModel]:
        """根据用户和供应商类型获取配置"""
        try:
            with get_db_context() as db:
                query = db.query(ModelProvider).filter(
                    ModelProvider.user_id == user_id,
                    ModelProvider.provider_type == provider_type
                )

                if active_only:
                    query = query.filter(ModelProvider.is_active == True)

                providers = query.order_by(ModelProvider.created_at.desc()).all()

                return [ModelProviderModel.model_validate(p) for p in providers]

        except Exception as e:
            logger.exception(f"Failed to get providers by user and type: {e}")
            return []

    def get_default_provider_by_type(
        self, user_id: str, provider_type: str
    ) -> Optional[ModelProviderModel]:
        """获取指定类型的默认供应商"""
        try:
            with get_db_context() as db:
                provider = db.query(ModelProvider).filter(
                    ModelProvider.user_id == user_id,
                    ModelProvider.provider_type == provider_type,
                    ModelProvider.is_default == True,
                    ModelProvider.is_active == True
                ).first()

                if provider:
                    return ModelProviderModel.model_validate(provider)
                return None

        except Exception as e:
            logger.exception(f"Failed to get default provider: {e}")
            return None

    # ===================== Update =====================

    def update_provider(
        self, provider_id: str, user_id: str, form_data: ModelProviderUpdateForm
    ) -> Optional[ModelProviderModel]:
        """更新供应商配置"""
        try:
            with get_db_context() as db:
                provider = db.query(ModelProvider).filter(
                    ModelProvider.id == provider_id,
                    ModelProvider.user_id == user_id
                ).first()

                if not provider:
                    return None

                # 更新非空字段
                if form_data.name is not None:
                    provider.name = form_data.name
                if form_data.api_key is not None:
                    provider.api_key = form_data.api_key
                if form_data.base_url is not None:
                    provider.base_url = form_data.base_url
                if form_data.provider_config is not None:
                    provider.provider_config = form_data.provider_config
                if form_data.supported_model_types is not None:
                    provider.supported_model_types = [
                        mt.value for mt in form_data.supported_model_types
                    ]
                if form_data.is_active is not None:
                    provider.is_active = form_data.is_active
                if form_data.is_default is not None:
                    if form_data.is_default:
                        self._unset_defaults_for_type(
                            db, user_id, provider.provider_type, exclude_id=provider_id
                        )
                    provider.is_default = form_data.is_default

                provider.updated_at = int(time.time())

                db.commit()
                db.refresh(provider)

                logger.info(f"Updated model provider: {provider_id}")
                return ModelProviderModel.model_validate(provider)

        except Exception as e:
            logger.exception(f"Failed to update provider: {e}")
            return None

    def update_ollama_provider(
        self, provider_id: str, user_id: str, form_data: OllamaUpdateForm
    ) -> Optional[ModelProviderModel]:
        """更新 Ollama 供应商配置"""
        try:
            with get_db_context() as db:
                provider = db.query(ModelProvider).filter(
                    ModelProvider.id == provider_id,
                    ModelProvider.user_id == user_id,
                    ModelProvider.provider_type == ProviderType.OLLAMA.value
                ).first()

                if not provider:
                    return None

                # 更新非空字段
                if form_data.name is not None:
                    provider.name = form_data.name
                if form_data.base_url is not None:
                    provider.base_url = form_data.base_url
                if form_data.is_active is not None:
                    provider.is_active = form_data.is_active
                if form_data.is_default is not None:
                    if form_data.is_default:
                        self._unset_defaults_for_type(
                            db, user_id, ProviderType.OLLAMA.value, exclude_id=provider_id
                        )
                    provider.is_default = form_data.is_default

                # 更新 Ollama 特定配置
                config = provider.provider_config or {}
                if form_data.model_name is not None:
                    config["model_name"] = form_data.model_name
                if form_data.model_type is not None:
                    config["model_type"] = form_data.model_type.value
                    provider.supported_model_types = [form_data.model_type.value]
                if form_data.context_length is not None:
                    config["context_length"] = form_data.context_length
                provider.provider_config = config

                provider.updated_at = int(time.time())

                db.commit()
                db.refresh(provider)

                logger.info(f"Updated Ollama provider: {provider_id}")
                return ModelProviderModel.model_validate(provider)

        except Exception as e:
            logger.exception(f"Failed to update Ollama provider: {e}")
            return None

    def update_connection_status(
        self, provider_id: str, status: str
    ) -> Optional[ModelProviderModel]:
        """更新供应商连接状态"""
        try:
            with get_db_context() as db:
                provider = db.query(ModelProvider).filter(
                    ModelProvider.id == provider_id
                ).first()

                if not provider:
                    return None

                provider.connection_status = status
                provider.last_tested_at = int(time.time())
                provider.updated_at = int(time.time())

                db.commit()
                db.refresh(provider)

                return ModelProviderModel.model_validate(provider)

        except Exception as e:
            logger.exception(f"Failed to update connection status: {e}")
            return None

    def toggle_provider_active(
        self, provider_id: str, user_id: str
    ) -> Optional[ModelProviderModel]:
        """切换供应商启用状态"""
        try:
            with get_db_context() as db:
                provider = db.query(ModelProvider).filter(
                    ModelProvider.id == provider_id,
                    ModelProvider.user_id == user_id
                ).first()

                if not provider:
                    return None

                provider.is_active = not provider.is_active
                provider.updated_at = int(time.time())

                db.commit()
                db.refresh(provider)

                logger.info(f"Toggled provider active: {provider_id} -> {provider.is_active}")
                return ModelProviderModel.model_validate(provider)

        except Exception as e:
            logger.exception(f"Failed to toggle provider active: {e}")
            return None

    def set_default_provider(
        self, provider_id: str, user_id: str
    ) -> Optional[ModelProviderModel]:
        """设置供应商为默认"""
        try:
            with get_db_context() as db:
                provider = db.query(ModelProvider).filter(
                    ModelProvider.id == provider_id,
                    ModelProvider.user_id == user_id
                ).first()

                if not provider:
                    return None

                # 取消其他同类型的默认
                self._unset_defaults_for_type(
                    db, user_id, provider.provider_type, exclude_id=provider_id
                )

                provider.is_default = True
                provider.updated_at = int(time.time())

                db.commit()
                db.refresh(provider)

                logger.info(f"Set default provider: {provider_id}")
                return ModelProviderModel.model_validate(provider)

        except Exception as e:
            logger.exception(f"Failed to set default provider: {e}")
            return None

    # ===================== Delete =====================

    def delete_provider(self, provider_id: str, user_id: str) -> bool:
        """删除供应商配置"""
        try:
            with get_db_context() as db:
                result = db.query(ModelProvider).filter(
                    ModelProvider.id == provider_id,
                    ModelProvider.user_id == user_id
                ).delete()

                db.commit()

                if result > 0:
                    logger.info(f"Deleted provider: {provider_id}")
                    return True
                return False

        except Exception as e:
            logger.exception(f"Failed to delete provider: {e}")
            return False

    def delete_providers_by_user_id(self, user_id: str) -> bool:
        """删除用户的所有供应商配置"""
        try:
            with get_db_context() as db:
                result = db.query(ModelProvider).filter(
                    ModelProvider.user_id == user_id
                ).delete()

                db.commit()

                logger.info(f"Deleted {result} providers for user: {user_id}")
                return True

        except Exception as e:
            logger.exception(f"Failed to delete providers by user_id: {e}")
            return False

    # ===================== Helpers =====================

    def _unset_defaults_for_type(
        self, db, user_id: str, provider_type: str, exclude_id: str = None
    ):
        """取消指定类型的所有默认供应商"""
        query = db.query(ModelProvider).filter(
            ModelProvider.user_id == user_id,
            ModelProvider.provider_type == provider_type,
            ModelProvider.is_default == True
        )

        if exclude_id:
            query = query.filter(ModelProvider.id != exclude_id)

        query.update({"is_default": False})


# 单例导出
ModelProviders = ModelProviderTable()
