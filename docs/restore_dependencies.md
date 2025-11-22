# 恢复源码修改 - 依赖重装清单

**创建时间**: 2025-11-21
**用途**: 如果决定放弃research功能的源码修改，使用此文档恢复环境

---

## 📋 被修改的源码包

根据 `docs/source_code_modifications.md`，以下包的源码被修改：

### 1. **langchain**
- **修改文件**: `langchain/agents/middleware/summarization.py`
- **修改内容**: `_DEFAULT_TRIM_TOKEN_LIMIT` 从 4000 → 20000

### 2. **deepagents**
- **修改文件**: `deepagents/graph.py`
- **修改内容**: `max_tokens_before_summary` 从 80000 → 15000

---

## 🔧 恢复方案

### 方案1：强制重装修改的包（推荐，最快）

```bash
# 激活虚拟环境
conda activate nexus

# 强制重装langchain（覆盖修改）
pip install --force-reinstall --no-cache-dir langchain

# 强制重装deepagents（覆盖修改）
pip install --force-reinstall --no-cache-dir deepagents
```

**时间**: 约2-3分钟
**优点**: 快速，只重装必要的包
**缺点**: 可能需要重装依赖包

---

### 方案2：卸载后重装（更干净）

```bash
# 激活虚拟环境
conda activate nexus

# 卸载修改的包
pip uninstall langchain deepagents -y

# 重新安装
pip install langchain deepagents
```

**时间**: 约2-3分钟
**优点**: 完全干净
**缺点**: 稍慢

---

### 方案3：创建全新虚拟环境（最彻底）

```bash
# 创建新环境
conda create -n nexus-clean python=3.12 -y

# 激活新环境
conda activate nexus-clean

# 安装所有依赖（从requirements.txt）
cd /Users/seanxiao/PycharmProjects/nexus-ai
pip install -r requirements.txt
```

**时间**: 约10-15分钟
**优点**: 完全干净，保留原nexus环境作为backup
**缺点**: 需要重装所有包

---

## ✅ 验证恢复成功

运行以下命令检查修改是否已恢复：

```bash
# 检查 langchain 是否恢复
python -c "
import inspect
from langchain.agents.middleware.summarization import _DEFAULT_TRIM_TOKEN_LIMIT
print(f'_DEFAULT_TRIM_TOKEN_LIMIT = {_DEFAULT_TRIM_TOKEN_LIMIT}')
print('Expected: 4000 (original)')
"

# 检查 deepagents 是否恢复
python -c "
import inspect
from deepagents.graph import create_deep_agent
source = inspect.getsource(create_deep_agent)
if '测试阶段配置B' in source:
    print('❌ deepagents still modified')
else:
    print('✅ deepagents restored to original')
"
```

**预期输出**（恢复成功）:
```
_DEFAULT_TRIM_TOKEN_LIMIT = 4000
Expected: 4000 (original)
✅ deepagents restored to original
```

---

## 📦 完整依赖清单（用于方案3）

如果选择方案3（创建新环境），需要安装的包：

### 核心包（被修改的）
```bash
langchain
deepagents
```

### 相关依赖（可能需要）
```bash
langchain-core
langchain-anthropic
langchain-openai
langgraph
```

### 其他项目依赖
根据你的 `requirements.txt` 安装

---

## ⚠️ 注意事项

### 1. **项目代码不受影响**
以下文件是你的项目代码，**不需要恢复**（除非你想删除）：
- ✅ `app/agents/middleware/goal_driven_summarization.py` (新增)
- ✅ `app/agents/core/agent_factory.py` (新增)
- ✅ `test/test_minimal_goal_driven.py` (新增)
- ⚠️ `app/agents/tools/search/tavily_search.py` (修改了max_results=5)

### 2. **Git不会恢复site-packages**
```bash
git checkout <another-branch>
```
只会恢复项目代码，**不会恢复site-packages中的修改**

### 3. **虚拟环境隔离**
如果创建新环境（方案3），原nexus环境的修改仍然存在：
- `nexus` 环境：包含修改
- `nexus-clean` 环境：干净的

---

## 🚀 快速执行脚本

### 一键恢复（推荐）

```bash
#!/bin/bash
# restore_packages.sh

echo "🔄 开始恢复源码包..."

# 激活环境
conda activate nexus

# 强制重装
echo "📦 重装 langchain..."
pip install --force-reinstall --no-cache-dir langchain

echo "📦 重装 deepagents..."
pip install --force-reinstall --no-cache-dir deepagents

echo "✅ 重装完成！"

# 验证
echo "🔍 验证恢复..."
python -c "
from langchain.agents.middleware.summarization import _DEFAULT_TRIM_TOKEN_LIMIT
print(f'TRIM_LIMIT = {_DEFAULT_TRIM_TOKEN_LIMIT} (Expected: 4000)')
"

echo "✅ 完成！"
```

**使用方式**：
```bash
chmod +x restore_packages.sh
./restore_packages.sh
```

---

## 📊 影响评估

### 恢复后的变化

| 配置项 | 修改后 | 恢复后 | 影响 |
|--------|--------|--------|------|
| `_DEFAULT_TRIM_TOKEN_LIMIT` | 20000 | 4000 | Summarization可能失败 |
| `max_tokens_before_summary` | 15000 | 80000 | Token可能溢出 |
| `messages_to_keep` | 3 | 20 | 压缩效果变差 |

### 可能的后果
- ⚠️ Token溢出问题会重新出现
- ⚠️ Summarization失败率提高（"too long to summarize"）
- ⚠️ 需要其他方案解决token问题

---

## 💡 建议

如果你要恢复源码修改，建议：

1. **先备份当前环境**（方案3，创建新环境）
2. **在新环境中测试其他方案**（如优化prompt）
3. **确认新方案可行后，再删除旧环境**

这样可以随时回退到有效的配置。
