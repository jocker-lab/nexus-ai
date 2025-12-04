# -*- coding: utf-8 -*-
"""
Document Finalizer - 文档元数据提取节点

职责：
1. 使用 with_structured_output 从完整文档中提取元数据
2. 统计文档字数（排除图表、引用等）
3. 生成 description、category、tags 等信息
"""
import re
from typing import Dict, Any, List, Optional
from pydantic import BaseModel, Field
from loguru import logger
from langchain.chat_models import init_chat_model
from app.agents.core.publisher.writing.state import DocumentState
from app.agents.prompts.template import render_prompt_template


class DocumentMetadata(BaseModel):
    """文档元数据结构化输出模型"""

    title: str = Field(
        description="文档标题，简洁明了"
    )
    description: str = Field(
        description="文档摘要描述，100-200字，概括文档的核心内容和价值"
    )
    category: str = Field(
        description="文档分类，如：市场分析、信用评级、行业研究、政策解读、宏观经济、投资分析等"
    )
    tags: List[str] = Field(
        description="文档标签，3-8个关键词，用于搜索和分类",
        min_items=3,
        max_items=8
    )
    key_insights: List[str] = Field(
        description="核心洞察，3-5个要点，文档的关键结论或发现",
        min_items=1,
        max_items=5
    )
    target_audience: Optional[str] = Field(
        default=None,
        description="目标读者群体"
    )


def count_document_words(document: str) -> int:
    """
    统计文档字数（排除图表、引用、代码块等）

    统计规则：
    - 中文：按字符数统计
    - 英文：按单词数统计
    - 排除：Markdown 图片、表格、代码块、引用块、链接等

    Args:
        document: 文档内容

    Returns:
        有效字数
    """
    if not document:
        return 0

    text = document

    # 移除代码块 ```...```
    text = re.sub(r'```[\s\S]*?```', '', text)

    # 移除行内代码 `...`
    text = re.sub(r'`[^`]+`', '', text)

    # 移除图片 ![alt](url) 或 ![alt][ref]
    text = re.sub(r'!\[[^\]]*\]\([^)]*\)', '', text)
    text = re.sub(r'!\[[^\]]*\]\[[^\]]*\]', '', text)

    # 移除链接但保留文本 [text](url) -> text
    text = re.sub(r'\[([^\]]*)\]\([^)]*\)', r'\1', text)

    # 移除表格（简单处理：移除包含 | 的行）
    lines = text.split('\n')
    lines = [line for line in lines if not re.match(r'^\s*\|.*\|\s*$', line)]
    lines = [line for line in lines if not re.match(r'^\s*[\-\|:]+\s*$', line)]
    text = '\n'.join(lines)

    # 移除引用块 > ...
    text = re.sub(r'^>\s*.*$', '', text, flags=re.MULTILINE)

    # 移除参考文献/引用标记 [1], [^1], [[1]] 等
    text = re.sub(r'\[\^?\d+\]', '', text)
    text = re.sub(r'\[\[\d+\]\]', '', text)

    # 移除 Markdown 标题标记 #
    text = re.sub(r'^#+\s*', '', text, flags=re.MULTILINE)

    # 移除粗体/斜体标记
    text = re.sub(r'\*+([^*]+)\*+', r'\1', text)
    text = re.sub(r'_+([^_]+)_+', r'\1', text)

    # 移除多余空白
    text = re.sub(r'\s+', ' ', text).strip()

    # 统计字数
    # 中文字符
    chinese_chars = re.findall(r'[\u4e00-\u9fff]', text)
    chinese_count = len(chinese_chars)

    # 英文单词（连续的字母数字序列）
    # 先移除中文字符再统计英文
    text_without_chinese = re.sub(r'[\u4e00-\u9fff]', ' ', text)
    english_words = re.findall(r'[a-zA-Z0-9]+', text_without_chinese)
    english_count = len(english_words)

    total_count = chinese_count + english_count

    logger.debug(f"字数统计: 中文 {chinese_count} + 英文 {english_count} = {total_count}")

    return total_count


def calculate_reading_time(word_count: int, wpm: int = 300) -> int:
    """
    计算预估阅读时间（分钟）

    Args:
        word_count: 字数
        wpm: 每分钟阅读字数，默认300（中文平均阅读速度）

    Returns:
        阅读时间（分钟），至少1分钟
    """
    minutes = max(1, round(word_count / wpm))
    return minutes


async def document_finalizer(state: DocumentState) -> Dict[str, Any]:
    """
    文档最终化节点 - 提取元数据并完成统计

    Args:
        state: DocumentState，需要包含 document 字段

    Returns:
        {
            "document_metadata": {
                "title": str,
                "description": str,
                "category": str,
                "tags": str,  # 逗号分隔
                "word_count": int,
                "estimated_reading_time": int,
                "key_insights": list,
                "target_audience": str,
                "status": "completed"
            }
        }
    """
    logger.info("\n📋 [Document Finalizer] 提取文档元数据...")

    document = state.get("document", "")
    outline = state.get("document_outline")

    if not document:
        logger.warning("  ⚠️ 文档内容为空")
        return {
            "document_metadata": {
                "status": "failed",
                "error": "Document content is empty"
            }
        }

    # === 1. 统计字数 ===
    logger.info("  ↳ 统计文档字数...")
    word_count = count_document_words(document)
    reading_time = calculate_reading_time(word_count)
    logger.info(f"    - 有效字数: {word_count:,}")
    logger.info(f"    - 预估阅读: {reading_time} 分钟")

    # === 2. 使用 LLM 提取结构化元数据 ===
    logger.info("  ↳ 调用 LLM 提取元数据...")

    try:
        llm = init_chat_model(
            "deepseek:deepseek-chat",
            temperature=0.3,
        )

        # 使用 with_structured_output
        structured_llm = llm.with_structured_output(DocumentMetadata)

        # 构建提示词
        # 取文档前3000字作为分析样本（避免 token 过长）
        document_sample = document[:3000] if len(document) > 3000 else document

        system_prompt = """你是一个专业的文档分析助手。请根据提供的文档内容，提取关键元数据信息。
        
        分析要求：
        1. description: 撰写100-200字的摘要，概括核心内容和价值
        2. category: 选择最合适的分类（市场分析/信用评级/行业研究/政策解读/宏观经济/投资分析/企业调研/财务分析/其他）
        3. tags: 提取3-8个关键标签，便于搜索和分类
        4. key_insights: 提炼3-5个核心洞察或结论
        5. target_audience: 识别目标读者群体"""

        user_prompt = f"""请分析以下文档并提取元数据：
        
        文档标题：{outline.title if outline else "未知"}
        
        文档内容（节选）：
        {document_sample}
        
        请根据上述内容生成结构化的元数据。"""

        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt}
        ]

        metadata_result: DocumentMetadata = await structured_llm.ainvoke(messages)

        # 构建最终元数据
        document_metadata = {
            "title": metadata_result.title,
            "description": metadata_result.description,
            "category": metadata_result.category,
            "tags": ",".join(metadata_result.tags),  # 转为逗号分隔字符串
            "word_count": word_count,
            "estimated_reading_time": reading_time,
            "key_insights": metadata_result.key_insights,
            "target_audience": metadata_result.target_audience,
            "status": "completed"
        }

        logger.success("  ✓ 元数据提取完成")
        logger.info(f"    - 标题: {metadata_result.title}")
        logger.info(f"    - 分类: {metadata_result.category}")
        logger.info(f"    - 标签: {', '.join(metadata_result.tags)}")
        logger.info(f"    - 字数: {word_count:,}")
        logger.info(f"    - 阅读时间: {reading_time} 分钟\n")

        return {"document_metadata": document_metadata}

    except Exception as e:
        logger.error(f"  ❌ 元数据提取失败: {e}")

        # 降级方案：使用基础信息
        fallback_metadata = {
            "title": outline.title if outline else "未命名文档",
            "description": f"基于 {outline.title if outline else '主题'} 的分析报告" if outline else "",
            "category": "其他",
            "tags": "",
            "word_count": word_count,
            "estimated_reading_time": reading_time,
            "key_insights": [],
            "target_audience": None,
            "status": "partial",
            "error": str(e)
        }

        return {"document_metadata": fallback_metadata}
