 # 配置管理使用指南

## 概述

项目使用 **Pydantic Settings** 实现类型安全的统一配置管理系统。

## 配置分层

```
.env (敏感信息)
    ↓
app/config/settings.py (Pydantic Settings)
    ↓
app/config/__init__.py (导出常用配置)
    ↓
业务代码 (导入使用)
```

## 配置文件

### 1. `.env` - 环境变量（敏感信息）

```env
# API Keys
OPENAI_API_KEY=sk-xxx
DEEPSEEK_API_KEY=sk-xxx
TAVILY_API_KEY=tvly-xxx

# 数据库
DATABASE_URL=mysql+pymysql://user:pass@localhost:3306/db

# MinIO
MINIO_ENDPOINT=localhost:9000
MINIO_ACCESS_KEY=minioadmin
MINIO_SECRET_KEY=minioadmin
MINIO_BUCKET=nexus-reports
MINIO_SECURE=false
```

### 2. `config.yaml` - 应用配置（非敏感）

```yaml
# 数据库连接池
database:
  pool:
    pool_size: 5
    max_overflow: 10

# 模型参数
model_params:
  model: "Qwen3-32B-AWQ"
  temperature: 0.7
  max_tokens: 8192
```

## 使用方式

### 方式一：导入配置常量（推荐）

```python
from app.config import (
    MINIO_ENDPOINT,
    MINIO_BUCKET,
    MYSQL_DATABASE_URL,
    LOCAL_BIG_MODEL_PARAMS,
)

# 直接使用
print(f"MinIO: {MINIO_ENDPOINT}/{MINIO_BUCKET}")
print(f"Database: {MYSQL_DATABASE_URL}")
print(f"Model: {LOCAL_BIG_MODEL_PARAMS['model']}")
```

### 方式二：使用 settings 对象

```python
from app.config import settings

# 访问配置属性
endpoint = settings.MINIO_ENDPOINT
api_key = settings.OPENAI_API_KEY
model_params = settings.model_params

# 数据库连接池配置
pool_size = settings.DATABASE_POOL_SIZE
max_overflow = settings.DATABASE_POOL_MAX_OVERFLOW
```

### 方式三：在类中使用（依赖注入）

```python
from app.config import settings

class MyService:
    def __init__(self):
        self.endpoint = settings.MINIO_ENDPOINT
        self.bucket = settings.MINIO_BUCKET

    def upload(self, data: bytes):
        print(f"Uploading to {self.endpoint}/{self.bucket}")
```

## 添加新配置

### 步骤1：在 `.env` 添加环境变量

```env
# 新的配置项
MY_NEW_API_KEY=abc123
MY_NEW_FEATURE_ENABLED=true
```

### 步骤2：在 `settings.py` 添加字段

```python
class Settings(BaseSettings):
    # ... 现有配置 ...

    # 新配置
    MY_NEW_API_KEY: str = Field(
        ...,  # 必填
        description="My New API Key"
    )

    MY_NEW_FEATURE_ENABLED: bool = Field(
        False,  # 可选，默认值
        description="是否启用新功能"
    )
```

### 步骤3：在 `__init__.py` 导出（可选）

```python
# 导出常用配置
MY_NEW_API_KEY = settings.MY_NEW_API_KEY

__all__ = [
    # ... 现有导出 ...
    'MY_NEW_API_KEY',
]
```

### 步骤4：在业务代码中使用

```python
from app.config import MY_NEW_API_KEY, settings

# 方式1：直接导入
print(MY_NEW_API_KEY)

# 方式2：通过 settings
if settings.MY_NEW_FEATURE_ENABLED:
    print("新功能已启用")
```

## 从 YAML 读取配置

对于非敏感的应用配置，可以添加到 `config.yaml` 并通过 `settings._yaml_config` 访问。

### 示例：添加缓存配置

**config.yaml**:
```yaml
cache:
  ttl: 3600
  max_size: 1000
  enabled: true
```

**settings.py**:
```python
class Settings(BaseSettings):
    # ... 现有配置 ...

    @property
    def CACHE_TTL(self) -> int:
        """缓存过期时间（秒）"""
        return self._yaml_config.get('cache', {}).get('ttl', 3600)

    @property
    def CACHE_MAX_SIZE(self) -> int:
        """缓存最大条目数"""
        return self._yaml_config.get('cache', {}).get('max_size', 1000)

    @property
    def CACHE_ENABLED(self) -> bool:
        """是否启用缓存"""
        return self._yaml_config.get('cache', {}).get('enabled', True)
```

**使用**:
```python
from app.config import settings

if settings.CACHE_ENABLED:
    cache.set_ttl(settings.CACHE_TTL)
    cache.set_max_size(settings.CACHE_MAX_SIZE)
```

## 配置验证

Pydantic 自动验证配置类型和必填项：

```python
class Settings(BaseSettings):
    # 必填字段（无默认值）
    DATABASE_URL: str = Field(..., description="数据库URL")

    # 可选字段（有默认值）
    DEBUG: bool = Field(False, description="调试模式")

    # 类型验证
    PORT: int = Field(8000, ge=1, le=65535, description="服务端口")

    # 枚举验证
    LOG_LEVEL: str = Field("INFO", pattern="^(DEBUG|INFO|WARNING|ERROR)$")
```

启动时，如果配置不合法会报错：

```
ValidationError: 1 validation error for Settings
DATABASE_URL
  field required (type=value_error.missing)
```

## 测试环境配置

在测试中覆盖配置：

```python
import pytest
from app.config import settings

def test_with_custom_config():
    # 临时覆盖配置
    original = settings.MINIO_BUCKET
    settings.MINIO_BUCKET = "test-bucket"

    # 测试代码
    assert settings.MINIO_BUCKET == "test-bucket"

    # 恢复
    settings.MINIO_BUCKET = original
```

或使用 pytest fixture：

```python
@pytest.fixture
def override_minio_config(monkeypatch):
    monkeypatch.setenv("MINIO_BUCKET", "test-bucket")
    monkeypatch.setenv("MINIO_ENDPOINT", "localhost:9001")

    # 重新加载 settings
    from importlib import reload
    import app.config.settings
    reload(app.config.settings)
```

## 实际案例

### MinIO 客户端配置

**minio_db.py**:
```python
from app.config import (
    MINIO_ENDPOINT,
    MINIO_ACCESS_KEY,
    MINIO_SECRET_KEY,
    MINIO_BUCKET,
    MINIO_SECURE,
)

class MinIOClient:
    def initialize(self):
        self.client = Minio(
            endpoint=MINIO_ENDPOINT,
            access_key=MINIO_ACCESS_KEY,
            secret_key=MINIO_SECRET_KEY,
            secure=MINIO_SECURE
        )
        self.bucket_name = MINIO_BUCKET
```

### 数据库连接池配置

**database.py**:
```python
from app.config import (
    MYSQL_DATABASE_URL,
    DATABASE_POOL_SIZE,
    DATABASE_POOL_MAX_OVERFLOW,
    DATABASE_POOL_TIMEOUT,
    DATABASE_POOL_RECYCLE,
)

engine = create_engine(
    MYSQL_DATABASE_URL,
    pool_size=DATABASE_POOL_SIZE,
    max_overflow=DATABASE_POOL_MAX_OVERFLOW,
    pool_timeout=DATABASE_POOL_TIMEOUT,
    pool_recycle=DATABASE_POOL_RECYCLE,
)
```

### LLM 配置

**llm.py**:
```python
from app.config import LOCAL_BIG_MODEL_PARAMS, settings

llm = ChatOpenAI(
    model=LOCAL_BIG_MODEL_PARAMS['model'],
    temperature=LOCAL_BIG_MODEL_PARAMS['temperature'],
    max_tokens=LOCAL_BIG_MODEL_PARAMS['max_tokens'],
    api_key=settings.OPENAI_API_KEY,
    base_url=LOCAL_BIG_MODEL_PARAMS['openai_api_base'],
)
```

## 最佳实践

### ✅ 推荐

1. **敏感信息放 `.env`**：API keys, 密码, 数据库连接
2. **应用配置放 `config.yaml`**：连接池参数、模型参数
3. **使用类型注解**：利用 Pydantic 的类型验证
4. **提供默认值**：对于可选配置
5. **添加描述**：使用 `Field(description=...)`
6. **导出常用配置**：在 `__init__.py` 中导出

### ❌ 避免

1. **硬编码配置**：不要在代码中写死配置值
2. **直接读取环境变量**：使用 settings 而不是 `os.getenv()`
3. **重复读取 YAML**：配置已在启动时加载
4. **忽略类型**：充分利用 Pydantic 的类型系统
5. **混合配置源**：统一使用 settings 系统

## 配置优先级

```
环境变量 > .env 文件 > 默认值
```

示例：
```python
# settings.py
MINIO_BUCKET: str = Field("default-bucket", ...)

# .env
MINIO_BUCKET=env-bucket

# 运行时
$ MINIO_BUCKET=runtime-bucket python app.py

# 最终值: runtime-bucket (环境变量优先级最高)
```

## 调试配置

查看当前所有配置：

```python
from app.config import settings

# 打印所有环境变量配置
print("MinIO Endpoint:", settings.MINIO_ENDPOINT)
print("Database URL:", settings.DATABASE_URL)
print("Model Params:", settings.model_params)

# 打印 YAML 配置
import json
print("YAML Config:", json.dumps(settings._yaml_config, indent=2))
```

## 参考

- [Pydantic Settings 文档](https://docs.pydantic.dev/latest/concepts/pydantic_settings/)
- [项目配置模块](../app/config/settings.py)
