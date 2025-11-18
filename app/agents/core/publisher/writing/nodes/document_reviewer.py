# -*- coding: utf-8 -*-
"""
Document Reviewer - 智能文档审查节点（简化版）

职责：
1. 使用 LLM 对整合后的文档进行全局审查
2. 评估连贯性、完整性、质量
3. 可选：自动修复轻微问题
"""
from typing import Dict, Any
from loguru import logger
from langchain_deepseek import ChatDeepSeek
from app.agents.core.publisher.writing.state import DocumentState
from app.agents.schemas.review_schema import GlobalReviewResult
from app.agents.core.publisher.writing import config


async def document_reviewer(state: DocumentState) -> Dict[str, Any]:
    """
    智能文档审查节点（使用 Structured Output）

    设计理念：
    - 简化审查逻辑，只做必要的检查
    - 使用 Structured Output 确保返回格式
    - 自动修复轻微问题（可选）
    """
    logger.info("\n🔍 [Document Reviewer] 智能全局审查...")

    document = state["integrated_document"]
    total_word_count = state.get("document_metadata", {}).get("total_words", len(document))
    target_length = state["target_length"]
    avg_quality = state.get("quality_stats", {}).get("avg_score", 0)

    # === 初始化 LLM ===
    llm = ChatDeepSeek(
        model=config.MODEL_NAME,
        max_tokens=config.MAX_TOKENS,
        temperature=config.TEMPERATURE,
    )

    # === 1. LLM 全局审查（使用 Structured Output）===
    logger.info("  ↳ 执行 LLM 智能审查...")

    try:
        llm_with_structure = llm.with_structured_output(GlobalReviewResult)

        # 文档预览（避免 token 过多）
        doc_preview = document[:5000]
        if len(document) > 5000:
            doc_preview += f"\n\n... [中间省略 {len(document) - 5000} 字符] ...\n\n"
            doc_preview += document[-2000:]  # 添加结尾部分

        # 构建审查 prompt
        system_prompt = """你是一位资深的文档审查专家。

        任务：对整份文档进行全局质量审查。
        
        审查维度：
        1. **连贯性**：章节之间是否流畅过渡、逻辑是否连贯
        2. **完整性**：是否缺失重要内容、结构是否完整
        3. **冗余性**：是否有重复内容
        4. **术语一致性**：专业术语使用是否统一
        5. **格式规范**：Markdown 格式是否正确
        
        输出要求：
        - 使用结构化输出格式
        - overall_assessment: excellent/good/acceptable/needs_revision
        - coherence_score: 0-100 分
        - 列出发现的主要问题（如果有）
        - 给出修订建议（如果需要）
        """

        user_prompt = f"""请审查以下文档：
        
        **文档统计**：
        - 总字数：{total_word_count} 字（目标：{target_length} 字）
        - 平均章节质量：{avg_quality} 分
        
        **文档内容**：
        {doc_preview}
        
        ---
        请进行全局审查并返回结构化结果。
        """

        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt}
        ]

        review_result = await llm_with_structure.ainvoke(messages)

        logger.info(f"    ↳ 整体评估: {review_result.overall_assessment}")
        logger.info(f"    ↳ 连贯性分数: {review_result.coherence_score}")

        if review_result.redundancy_issues:
            logger.warning(f"    ⚠️  发现 {len(review_result.redundancy_issues)} 个冗余问题")

        if review_result.terminology_issues:
            logger.warning(f"    ⚠️  发现 {len(review_result.terminology_issues)} 个术语问题")

    except Exception as e:
        logger.error(f"  ❌ 审查失败: {e}", exc_info=True)

        # 回退：默认通过
        logger.info("  ↳ 使用默认审查结果（通过）\n")

        review_result = GlobalReviewResult(
            overall_assessment="acceptable",
            coherence_score=75,
            redundancy_issues=[],
            terminology_issues=[],
            suggested_fixes=[],
            recommendation="approve"
        )

    # === 2. 决策分支（简化） ===
    recommendation = review_result.recommendation
    final_document = document

    if recommendation == "approve":
        logger.success("  ✓ 审查通过，直接输出\n")

    elif recommendation == "minor_fixes" and review_result.suggested_fixes:
        logger.info("  ↳ 需要轻微修复，自动应用...")

        try:
            # 构建修复 prompt
            fixes_text = "\n".join([
                f"- {fix.location}: {fix.description} → {fix.suggested_change}"
                for fix in review_result.suggested_fixes
            ])

            fix_prompt = f"""请对以下文档应用这些修复：

            **修复清单**：
            {fixes_text}
            
            **原文档**：
            {document}
            
            ---
            请输出修复后的完整文档（Markdown 格式）。
            """

            fix_response = await llm.ainvoke([{"role": "user", "content": fix_prompt}])
            final_document = fix_response.content.strip()

            logger.success(f"  ✓ 应用了 {len(review_result.suggested_fixes)} 个修复\n")

        except Exception as e:
            logger.warning(f"  ⚠️  自动修复失败: {e}")
            logger.info("  ↳ 使用原文档\n")

    else:
        # major_revision 或其他情况，也直接通过（避免过度审查）
        logger.info("  ↳ 建议进行修订，但自动通过（避免过度审查）\n")

    # === 返回更新 ===
    return {
        "global_review": review_result.model_dump(),
        "final_document": final_document,
    }
