# -*- coding: utf-8 -*-
"""
Document Integrator - 智能文档整合节点（简化版）

职责：
1. 将所有章节内容传递给 LLM
2. 让 LLM 自主完成文档整合、过渡、参考文献等
3. 完全依赖 LLM 的智能，不做任何规则处理
"""
from typing import Dict, Any
from loguru import logger
from langchain_deepseek import ChatDeepSeek
from app.agents.core.publisher.writing.state import DocumentState
from app.agents.core.publisher.writing import config


async def document_integrator(state: DocumentState) -> Dict[str, Any]:
    """
    智能文档整合节点（完全由 LLM 驱动）

    设计理念：
    - 不做任何手动处理（参考文献、字数统计、格式化等）
    - 完全信任 LLM 的能力
    - 只传递章节内容和基本指导
    """
    logger.info("\n📚 [Document Integrator] 智能文档整合...")

    chapters = state["completed_chapters"]
    outline = state["main_document_outline"]

    # === 1. 准备章节内容（按顺序） ===
    logger.info("  ↳ 准备章节内容...")

    sorted_chapters = sorted(chapters.items(), key=lambda x: x[0])
    total_chapters = len(sorted_chapters)

    # 构建章节列表文本（简单拼接，让 LLM 处理结构）
    chapters_content = []
    for ch_id, ch_data in sorted_chapters:
        chapter_text = f"""
    ---
    章节 {ch_id}/{total_chapters}
    ---
    {ch_data['final_content']}
    """
        chapters_content.append(chapter_text)

    combined_chapters = "\n\n".join(chapters_content)

    # === 2. 构建 LLM Prompt（简洁明确） ===
    logger.info("  ↳ 调用 LLM 进行智能整合...")

    llm = ChatDeepSeek(
        model=config.MODEL_NAME,
        max_tokens=config.MAX_TOKENS,
        temperature=config.TEMPERATURE,
    )

    # 系统提示：定义角色和任务
    system_prompt = f"""你是一位专业的文档编辑专家。

    任务：将以下{total_chapters}个独立章节整合成一份完整、连贯的文档。
    
    要求：
    1. **标题**：生成文档标题「{outline.title}」
    2. **目录**：自动生成完整目录（包含所有章节和小节）
    3. **章节过渡**：在章节之间添加自然的过渡语句，确保逻辑连贯
    4. **参考文献**：提取所有章节中的引用，在文档末尾生成统一的「参考文献」部分
    5. **格式统一**：确保 Markdown 格式规范、标题层级正确
    6. **语言风格**：{outline.writing_style}，语气：{outline.writing_tone}
    
    输出要求：
    - 直接输出完整的 Markdown 文档
    - 不要添加任何解释性文字
    - 不要使用代码块包裹（```markdown）
    - 保持原章节内容的完整性和准确性
    """

    user_prompt = f"""请整合以下章节：
    
    {combined_chapters}
    
    ---
    请输出完整的文档内容（Markdown 格式）。
    """

    try:
        # 调用 LLM
        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt}
        ]

        response = await llm.ainvoke(messages)
        integrated_document = response.content.strip()

        # 简单验证
        if not integrated_document or len(integrated_document) < 100:
            raise ValueError("LLM 返回的文档内容过短")

        # === 3. 生成元数据（简化） ===
        total_words = len(integrated_document)

        document_metadata = {
            "total_chapters": total_chapters,
            "total_words": total_words,
            "language": outline.language,
            "writing_style": outline.writing_style,
            "avg_quality_score": state.get("quality_stats", {}).get("avg_score", 0),
        }

        logger.success(f"  ✓ 智能整合完成")
        logger.info(f"    - 章节数: {total_chapters}")
        logger.info(f"    - 文档字数: {total_words}")
        logger.info(f"    - 平均质量分: {document_metadata['avg_quality_score']}\n")

        return {
            "integrated_document": integrated_document,
            "document_metadata": document_metadata,
        }

    except Exception as e:
        logger.error(f"  ❌ LLM整合失败: {e}")

        # 降级方案：简单拼接
        logger.info("  ↳ 使用降级方案（简单拼接）...\n")

        fallback_document = f"# {outline.title}\n\n{combined_chapters}"

        return {
            "integrated_document": fallback_document,
            "document_metadata": {
                "total_chapters": total_chapters,
                "total_words": len(fallback_document),
                "fallback_mode": True,
            },
        }
