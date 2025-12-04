from .chats import Chat
from .folders import Folder
from .tags import Tag
from .files import File
from .documents import Document, DocumentStatus, DocumentVersion, ChangeType
# 兼容性别名
from .documents import Report, ReportStatus
from .model_providers import ModelProvider, ProviderType, ModelType

# 写作模版
from .writing_templates import (
    WritingTemplate,
    WritingStyle,
    WritingTone,
    TemplateStatus,
    TemplateScope
)

# 认证相关模型 - 注意导入顺序：associations 必须在 users/groups 之后
# 但 relationship 使用字符串引用，所以需要确保所有模型都被导入
from .permissions import Permission
from .roles import Role
from .associations import UserGroup, GroupRole, RolePermission, RefreshToken
from .groups import Group
from .users import User