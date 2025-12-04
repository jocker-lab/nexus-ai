# -*- coding: utf-8 -*-
"""
Document Integrator - 智能文档整合节点

职责：
1. 将所有章节内容传递给 LLM
2. 让 LLM 自主完成文档整合、过渡、参考文献等
"""
from typing import Dict, Any
from loguru import logger
from app.agents.core.publisher.writing.state import DocumentState
from langchain.chat_models import init_chat_model
from app.agents.prompts.template import render_prompt_template


async def document_integrator(state: DocumentState) -> Dict[str, Any]:
    """
    智能文档整合节点（完全由 LLM 驱动）

    Args:
        state: DocumentState

    Returns:
        {"document": str}
    """
    logger.info("\n📚 [Document Integrator] 智能文档整合...")

    chapters = state["completed_chapters"]
    outline = state["document_outline"]

    # === 1. 准备章节内容（按顺序） ===
    logger.info("  ↳ 准备章节内容...")

    sorted_chapters = sorted(chapters.items(), key=lambda x: x[0])
    total_chapters = len(sorted_chapters)

    chapters_content = []
    for ch_id, ch_data in sorted_chapters:
        chapter_text = f"""
        ---
        章节 {ch_id}/{total_chapters}
        ---
        {ch_data['content']}
        """
        chapters_content.append(chapter_text)

    combined_chapters = "\n\n".join(chapters_content)

    # === 2. 构建 LLM Prompt ===
    logger.info("  ↳ 调用 LLM 进行智能整合...")

    llm = init_chat_model(
        "deepseek:deepseek-reasoner",
        max_tokens=16384,
        timeout=120,  # 推理模型耗时较长，加大超时
    )

    system_prompt = render_prompt_template(
        "publisher_prompts/document_writing/document_integrator_system",
        {
            "language": outline.language,
            "writing_style": outline.writing_style,
            "writing_tone": outline.writing_tone,
        }
    )

    user_prompt = render_prompt_template(
        "publisher_prompts/document_writing/document_integrator_task",
        {
            "outline": outline,
            "total_chapters": total_chapters,
            "combined_chapters": combined_chapters,
        }
    )

    try:
        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt}
        ]

        response = await llm.ainvoke(messages)
        integrated_document = response.content.strip()

        if not integrated_document or len(integrated_document) < 100:
            raise ValueError("LLM 返回的文档内容过短")

        metadata = state.get("document_metadata", {})
        logger.success(f"  ✓ 智能整合完成")
        logger.info(f"    - 章节数: {total_chapters}")
        logger.info(f"    - 总字数: {metadata.get('total_words', len(integrated_document))}")
        logger.info(f"    - 平均评分: {metadata.get('avg_score', 'N/A')}\n")

        return {"document": integrated_document}

    except Exception as e:
        logger.error(f"  ❌ LLM整合失败: {e}")
        logger.info("  ↳ 使用降级方案（简单拼接）...\n")

        fallback_document = f"# {outline.title}\n\n{combined_chapters}"
        return {"document": fallback_document}
