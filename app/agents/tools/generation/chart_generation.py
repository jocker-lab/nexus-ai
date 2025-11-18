# -*- coding: utf-8 -*-
"""
@File    :   chart_generation.py
@Time    :   2025/11/12 08:34
@Author  :   pygao
@Version :   1.0
@Contact :   pygao.1@outlook.com
@License :   (C)Copyright 2025, GienTech Technology Co.,Ltd. All rights reserved.
@Desc    :   文件描述
"""
import re
import os
import uuid
import base64
from langchain_core.tools import tool


from app.agents.execution.docker_sandbox import DockerSandbox
from app.database.minio_db import upload_chart


_sandbox = None

def get_sandbox():
    """获取或创建 DockerSandbox 实例"""
    global _sandbox
    if _sandbox is None:
        _sandbox = DockerSandbox(
            output_dir='charts',
            image='sandbox:latest',
            mem_limit='512m',
            cpu_quota=50000
        )
    return _sandbox


@tool
def generate_chart(code: str, report_id: str = None) -> str:
    """
    在安全的 Docker 容器中执行绘图代码并上传到 MinIO。

    **核心要求：**
    1. 代码必须输出 base64 编码图片到 stdout
    2. 输出格式：`IMAGE_BASE64:<base64_string>`
    3. 必须使用 Agg 后端：`matplotlib.use('Agg')`

    **推荐代码模板：**
    ```python
        import matplotlib
        matplotlib.use('Agg')
        import matplotlib.pyplot as plt
        import seaborn as sns
        import pandas as pd
        import base64
        from io import BytesIO

        # 中文字体配置
        from matplotlib.font_manager import FontProperties
        FONT = FontProperties(fname='/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc')
        plt.rcParams['axes.unicode_minus'] = False

        # 绘图逻辑
        fig, ax = plt.subplots(figsize=(10, 6))
        # ... 你的绘图代码 ...

        # 所有中文文本必须显式指定 fontproperties=FONT
        ax.set_title('标题', fontproperties=FONT)

        # 输出 base64
        buf = BytesIO()
        plt.savefig(buf, format='png', dpi=300, bbox_inches='tight')
        plt.close()
        buf.seek(0)
        print(f'IMAGE_BASE64:{base64.b64encode(buf.read()).decode()}')
    ```

    **参数：**
    - code: 完整的 Python 绘图代码
    - report_id: 报告ID（可选，默认为 'temp'）

    **返回：**
    - MinIO 图片 URL (例如: http://localhost:9000/nexus-reports/reports/123/charts/chart_abc.png)

    **异常：**
    - ValueError: 代码执行失败或输出格式错误
    - Exception: MinIO 上传失败或其他系统错误
    """
    sandbox = get_sandbox()

    # 执行代码
    print(f"🔧 执行绘图代码 ({len(code)} 字符)...")

    try:
        result = sandbox.execute(code, timeout=240, enable_network=False)
    except Exception as e:
        raise ValueError(f"Docker 执行失败: {e}")

    # 检查执行错误
    if any(marker in result for marker in ["❌", "Error", "Traceback"]):
        raise ValueError(f"代码执行错误:\n{result[:1000]}")

    # 提取 base64 数据
    match = re.search(r'IMAGE_BASE64:([A-Za-z0-9+/=]+)', result, re.DOTALL)
    if not match:
        raise ValueError(
            f"输出中未找到 IMAGE_BASE64 标记\n"
            f"预期格式: IMAGE_BASE64:<base64_string>\n"
            f"实际输出: {result[:500]}"
        )

    image_base64 = match.group(1).strip()

    # 解码并上传到 MinIO
    try:
        image_data = base64.b64decode(image_base64)
    except Exception as e:
        raise ValueError(f"Base64 解码失败: {e}")

    # 生成文件名并上传
    chart_id = str(uuid.uuid4())[:8]
    filename = f"chart_{chart_id}.png"
    report_id = report_id or "temp"

    try:
        minio_url = upload_chart(
            file_data=image_data,
            report_id=report_id,
            filename=filename,
            content_type="image/png"
        )
    except Exception as e:
        raise Exception(f"MinIO 上传失败: {e}")

    print(f"✅ 图表已上传: {minio_url}")
    return minio_url