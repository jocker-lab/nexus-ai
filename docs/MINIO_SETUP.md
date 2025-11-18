# MinIO 集成使用指南

## 概述

本项目已集成 MinIO 对象存储，用于存储 Agent 生成的图表文件。图表生成流程如下：

```
Docker 沙箱生成图片 (内存) → Base64编码 → MinIO上传 → 返回URL → 嵌入Markdown
```

## 快速开始

### 1. 安装 MinIO（本地开发）

**方式一：Docker 快速启动**
```bash
docker run -d \
  -p 9000:9000 \
  -p 9001:9001 \
  --name minio \
  -e "MINIO_ROOT_USER=minioadmin" \
  -e "MINIO_ROOT_PASSWORD=minioadmin" \
  -v ~/minio/data:/data \
  quay.io/minio/minio server /data --console-address ":9001"
```

**方式二：二进制安装（macOS）**
```bash
brew install minio/stable/minio
minio server ~/minio/data --console-address ":9001"
```

**方式三：二进制安装（Linux）**
```bash
wget https://dl.min.io/server/minio/release/linux-amd64/minio
chmod +x minio
./minio server ~/minio/data --console-address ":9001"
```

### 2. 访问 MinIO 控制台

启动后，访问：
- **API地址**: http://localhost:9000
- **控制台**: http://localhost:9001
- **默认账号**: minioadmin / minioadmin

### 3. 配置环境变量

项目使用 **Pydantic Settings 统一配置管理**，MinIO 配置从 `.env` 文件读取。

确保 `.env` 文件包含以下配置（已默认配置）：

```env
# MinIO对象存储配置
MINIO_ENDPOINT=localhost:9000
MINIO_ACCESS_KEY=minioadmin
MINIO_SECRET_KEY=minioadmin
MINIO_BUCKET=nexus-reports
MINIO_SECURE=false
```

**配置说明**：
- 所有 MinIO 配置通过 `app.config.settings.Settings` 类管理
- 配置在应用启动时自动加载，支持类型验证
- 可通过 `from app.config import MINIO_ENDPOINT` 导入使用
- 修改配置后需要重启应用

### 4. 安装 Python 依赖

```bash
pip install minio==7.2.10
# 或者
pip install -r requirements.txt
```

## 使用方法

### 在 Agent 中生成图表（推荐 - MinIO模式）

```python
from app.agents.tools.generation.chart_generation import generate_chart

# 图表代码（使用BytesIO输出base64）
code = """
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import pandas as pd
import base64
from io import BytesIO

# 创建数据
data = pd.DataFrame({
    '月份': ['1月', '2月', '3月'],
    '销售额': [100, 150, 200]
})

# 绘制图表
fig, ax = plt.subplots(figsize=(10, 6))
ax.bar(data['月份'], data['销售额'])
ax.set_title('Monthly Sales')

# 输出到内存并转base64
buffer = BytesIO()
plt.savefig(buffer, format='png', dpi=300, bbox_inches='tight')
plt.close()

buffer.seek(0)
image_base64 = base64.b64encode(buffer.read()).decode('utf-8')
print(f'IMAGE_BASE64:{image_base64}')
"""

# 生成并上传到MinIO
minio_url = generate_chart(code, report_id="report_123", use_minio=True)
# 返回: http://localhost:9000/nexus-reports/reports/report_123/charts/chart_abc123.png

# 在Markdown中使用
markdown = f"## 销售趋势\n\n![销售图表]({minio_url})"
```

### 本地文件模式（兼容旧代码）

```python
# 禁用MinIO，使用本地文件
local_path = generate_chart(code, use_minio=False)
# 返回: charts/chart_abc123.png
```

### 直接使用 MinIO 客户端

```python
from app.database.minio_db import upload_chart, delete_chart, get_minio_client
from app.config import MINIO_ENDPOINT, MINIO_BUCKET

# 上传图片
with open('chart.png', 'rb') as f:
    image_data = f.read()

url = upload_chart(
    file_data=image_data,
    report_id="report_123",
    filename="custom_chart.png",
    content_type="image/png"
)

# 删除图片
delete_chart(url)
# 或
delete_chart("reports/report_123/charts/custom_chart.png")

# 获取客户端实例
client = get_minio_client()
client.delete_report_charts("report_123")  # 删除报告所有图表

# 查看当前配置
print(f"MinIO Endpoint: {MINIO_ENDPOINT}")
print(f"MinIO Bucket: {MINIO_BUCKET}")
```

## 存储结构

MinIO 中的文件按以下结构组织：

```
nexus-reports/                    # Bucket名称
├── reports/
│   ├── report_123/               # 报告ID
│   │   └── charts/
│   │       ├── chart_abc123.png
│   │       └── chart_def456.png
│   ├── report_456/
│   │   └── charts/
│   │       └── chart_xyz789.png
│   └── temp/                     # 临时文件（没有report_id时）
│       └── charts/
│           └── chart_temp123.png
```

## 图表代码模板

### 基础柱状图（中文支持）

```python
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.font_manager as fm
import seaborn as sns
import pandas as pd
import base64
from io import BytesIO

# 中文字体配置
FONT_PATH = '/usr/share/fonts/opentype/noto/NotoSerifCJK-Regular.ttc'
font_prop = fm.FontProperties(fname=FONT_PATH)

# 设置样式
plt.rcParams['axes.unicode_minus'] = False
sns.set_theme(style="whitegrid", palette="husl")

# 创建数据
data = pd.DataFrame({
    '类别': ['产品A', '产品B', '产品C'],
    '销售额': [100, 150, 200]
})

# 绘制图表
fig, ax = plt.subplots(figsize=(10, 6))
sns.barplot(data=data, x='类别', y='销售额', palette='viridis', ax=ax)

# 设置中文标题
ax.set_title('销售数据对比', fontsize=16, fontproperties=font_prop)
ax.set_xlabel('产品类别', fontsize=12, fontproperties=font_prop)
ax.set_ylabel('销售额 (万元)', fontsize=12, fontproperties=font_prop)

# 输出base64
buffer = BytesIO()
plt.savefig(buffer, format='png', dpi=300, bbox_inches='tight')
plt.close()

buffer.seek(0)
image_base64 = base64.b64encode(buffer.read()).decode('utf-8')
print(f'IMAGE_BASE64:{image_base64}')
```

## 生产环境配置

### 1. 修改环境变量

```env
# 生产环境MinIO配置
MINIO_ENDPOINT=minio.yourdomain.com:9000
MINIO_ACCESS_KEY=your_access_key
MINIO_SECRET_KEY=your_secret_key
MINIO_BUCKET=nexus-reports
MINIO_SECURE=true  # 使用HTTPS
```

### 2. 配置 Bucket 策略（公开访问）

登录 MinIO 控制台，为 `nexus-reports` bucket 设置访问策略：

```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Principal": {"AWS": ["*"]},
      "Action": ["s3:GetObject"],
      "Resource": ["arn:aws:s3:::nexus-reports/reports/*"]
    }
  ]
}
```

或使用 MinIO Client (mc)：

```bash
mc anonymous set download myminio/nexus-reports/reports
```

### 3. 配置 CDN（可选）

为了提高图片访问速度，可以在 MinIO 前配置 CDN：

- 使用 Cloudflare CDN
- 使用 AWS CloudFront
- 使用阿里云 CDN

## 故障排查

### 问题1：连接失败

**症状**：`Failed to initialize MinIO client`

**解决**：
1. 检查 MinIO 服务是否运行：`curl http://localhost:9000/minio/health/live`
2. 检查环境变量是否正确
3. 检查防火墙是否开放 9000 端口

### 问题2：上传失败

**症状**：`Failed to upload chart to MinIO: Access Denied`

**解决**：
1. 检查 Access Key 和 Secret Key 是否正确
2. 检查 Bucket 是否存在
3. 检查账号是否有写入权限

### 问题3：图片无法访问

**症状**：返回 MinIO URL 但浏览器无法打开

**解决**：
1. 检查 Bucket 访问策略是否设置为公开读取
2. 检查网络连接
3. 使用预签名URL（临时访问）：

```python
from app.database.minio_db import get_minio_client

client = get_minio_client()
presigned_url = client.get_presigned_url(
    "reports/report_123/charts/chart_abc.png",
    expires=3600  # 1小时有效期
)
```

## 测试

创建测试脚本 `test_minio.py`：

```python
import asyncio
from app.agents.tools.generation.chart_generation import generate_chart

async def test_minio_upload():
    code = """
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import base64
from io import BytesIO

fig, ax = plt.subplots()
ax.plot([1, 2, 3], [1, 4, 9])
ax.set_title('Test Chart')

buffer = BytesIO()
plt.savefig(buffer, format='png')
plt.close()

buffer.seek(0)
image_base64 = base64.b64encode(buffer.read()).decode('utf-8')
print(f'IMAGE_BASE64:{image_base64}')
"""

    url = generate_chart(code, report_id="test_123", use_minio=True)
    print(f"MinIO URL: {url}")
    assert url.startswith("http"), "应该返回MinIO URL"
    print("✅ 测试通过!")

if __name__ == "__main__":
    asyncio.run(test_minio_upload())
```

运行测试：
```bash
python test_minio.py
```

## 迁移指南

如果你之前使用本地文件存储，迁移到MinIO：

1. **更新图表生成代码**：使用 BytesIO + base64 模式
2. **确保 `use_minio=True`** 在调用 `generate_chart` 时
3. **清理旧的本地文件**：`rm -rf charts/`
4. **更新数据库中的图片URL**（如果已有数据）

```sql
-- 示例：将本地路径替换为MinIO URL（需要先迁移文件）
UPDATE reports
SET content = REPLACE(
    content,
    'charts/',
    'http://localhost:9000/nexus-reports/reports/[report_id]/charts/'
);
```

## 性能优化

1. **启用 MinIO 缓存**：在 MinIO 配置中启用磁盘缓存
2. **使用 CDN**：为 MinIO 配置 CDN 加速
3. **批量上传**：如果有多个图表，考虑并发上传
4. **图片压缩**：在上传前压缩图片（调整 DPI）

```python
# 降低DPI减小文件大小
plt.savefig(buffer, format='png', dpi=150, bbox_inches='tight')  # 默认300
```

## 安全建议

1. **生产环境使用强密码**：不要使用 `minioadmin/minioadmin`
2. **启用 HTTPS**：设置 `MINIO_SECURE=true`
3. **最小权限原则**：为应用创建专用的 MinIO 用户，只授予必要权限
4. **定期清理**：删除过期或废弃的报告图表

```python
from app.database.minio_db import delete_report_charts

# 删除某个报告的所有图表
deleted_count = delete_report_charts("old_report_id")
print(f"已删除 {deleted_count} 个图表")
```

## 参考资料

- [MinIO 官方文档](https://min.io/docs/minio/linux/index.html)
- [MinIO Python SDK](https://min.io/docs/minio/linux/developers/python/minio-py.html)
- [Matplotlib 中文字体配置](https://matplotlib.org/stable/tutorials/text/text_props.html)
