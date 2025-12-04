# -*- coding: utf-8 -*-
"""
@File    :   template_service.py
@Time    :   2025/11/28
@Desc    :   模版服务 - 文件解析 + 大纲提取 + SQL 存储
             （简化版：暂不启用向量化和重复检测）
"""

import uuid
from typing import Optional, List, Dict, Any

from dotenv import load_dotenv
from loguru import logger
from langchain.chat_models import init_chat_model

from app.schemas.template_outline_schema import TemplateOutline
from app.agents.prompts.template import render_prompt_template
from app.curd.writing_templates import WritingTemplates
from app.models.writing_templates import WritingStyle, WritingTone, TemplateStatus

load_dotenv(override=False)  # 不覆盖已存在的环境变量

# Prompt 模板路径
PROMPT_PATH = "template_prompts"


async def upload_template(
    file_content: str,
    original_filename: str,
    user_id: str,
    template_id: Optional[str] = None,
) -> Optional[Dict[str, Any]]:
    """
    上传模版处理（简化版，不含向量化和重复检测）

    流程：
    1. 接收文件内容（已经由 Docling 转换为 Markdown）
    2. LLM + structured_output 提取模版大纲
    3. 更新 SQL 记录

    Args:
        file_content: Markdown 格式的文件内容（Docling 转换后）
        original_filename: 原始文件名
        user_id: 用户ID
        template_id: 已存在的模版ID（用于更新），如果为 None 则创建新记录

    Returns:
        {"template_id": "xxx", "title": "...", "outline": {...}} 或 None
    """
    logger.info(f"[TemplateService] 开始处理模版上传: {original_filename}")

    if not file_content:
        logger.warning("[TemplateService] 文件内容为空")
        return None

    # === 1. LLM 提取模版大纲 ===
    logger.info("[TemplateService] 步骤 1/2: 提取模版大纲...")

    try:
        llm = init_chat_model("deepseek:deepseek-chat", temperature=0)
        llm_with_structure = llm.with_structured_output(TemplateOutline)

        # 文档预览（避免 token 过多）
        doc_preview = file_content[:10000]
        if len(file_content) > 10000:
            doc_preview += f"\n\n... [省略 {len(file_content) - 10000} 字符] ..."

        extract_prompt = render_prompt_template(f"{PROMPT_PATH}/extract_template_outline", {
            "document_content": doc_preview,
        })

        outline_result: TemplateOutline = await llm_with_structure.ainvoke(extract_prompt)

        logger.info(f"[TemplateService]   ✓ 标题: {outline_result.title}")
        logger.info(f"[TemplateService]   ✓ 分类: {outline_result.category}")
        logger.info(f"[TemplateService]   ✓ 章节数: {len(outline_result.sections)}")

    except Exception as e:
        logger.error(f"[TemplateService] 大纲提取失败: {e}")
        return None

    # === 2. 存储到 SQL ===
    logger.info("[TemplateService] 步骤 2/2: 存储到数据库...")

    try:
        # 将 sections 转换为可序列化的格式
        sections_data = [
            {
                "title": s.title,
                "description": s.description,
                "estimated_percentage": s.estimated_percentage,
                "key_points": s.key_points,
            }
            for s in outline_result.sections
        ]

        # 映射写作风格和语气
        writing_style_map = {
            "academic": WritingStyle.ACADEMIC,
            "business": WritingStyle.BUSINESS,
            "technical": WritingStyle.TECHNICAL,
            "creative": WritingStyle.CREATIVE,
            "journalistic": WritingStyle.JOURNALISTIC,
        }
        writing_tone_map = {
            "formal": WritingTone.FORMAL,
            "neutral": WritingTone.NEUTRAL,
            "casual": WritingTone.CASUAL,
            "professional": WritingTone.PROFESSIONAL,
            "persuasive": WritingTone.PERSUASIVE,
        }

        writing_style = writing_style_map.get(outline_result.writing_style.lower(), WritingStyle.BUSINESS)
        writing_tone = writing_tone_map.get(outline_result.writing_tone.lower(), WritingTone.NEUTRAL)

        if template_id:
            # 更新已存在的模版记录
            template = WritingTemplates.update_template(
                template_id=template_id,
                user_id=user_id,
                title=outline_result.title,
                summary=outline_result.summary,
                category=outline_result.category,
                markdown_content=file_content,
                writing_style=writing_style,
                writing_tone=writing_tone,
                target_audience=outline_result.target_audience,
                sections=sections_data,
                status=TemplateStatus.COMPLETED,
            )
        else:
            # 创建新的模版记录
            template_id = str(uuid.uuid4())
            template = WritingTemplates.create_template(
                user_id=user_id,
                title=outline_result.title,
                summary=outline_result.summary,
                category=outline_result.category,
                original_filename=original_filename,
                markdown_content=file_content,
                writing_style=writing_style,
                writing_tone=writing_tone,
                target_audience=outline_result.target_audience,
                sections=sections_data,
                status=TemplateStatus.COMPLETED,
            )
            if template:
                template_id = template.id

        if not template:
            logger.error("[TemplateService] SQL 存储失败")
            return None

        logger.info(f"[TemplateService]   ✓ SQL 存储成功")

    except Exception as e:
        logger.error(f"[TemplateService] 存储失败: {e}")
        return None

    logger.success(f"[TemplateService] ✓ 模版上传完成: {template_id}")

    return {
        "success": True,
        "template_id": template_id,
        "title": outline_result.title,
        "category": outline_result.category,
        "summary": outline_result.summary,
        "sections_count": len(outline_result.sections),
    }


async def get_template_by_id(template_id: str) -> Optional[Dict[str, Any]]:
    """
    根据ID获取模版详情

    Args:
        template_id: 模版ID

    Returns:
        模版详情字典
    """
    template = WritingTemplates.get_template_by_id(template_id)
    if not template:
        return None

    return {
        "template_id": template.id,
        "title": template.title,
        "summary": template.summary,
        "category": template.category,
        "writing_style": template.writing_style.value if hasattr(template.writing_style, 'value') else str(template.writing_style),
        "writing_tone": template.writing_tone.value if hasattr(template.writing_tone, 'value') else str(template.writing_tone),
        "target_audience": template.target_audience,
        "sections": template.sections,
        "markdown_content": template.markdown_content,
        "status": template.status.value if hasattr(template.status, 'value') else str(template.status),
    }


async def delete_template(template_id: str, user_id: str) -> bool:
    """
    删除模版

    Args:
        template_id: 模版ID
        user_id: 用户ID

    Returns:
        是否成功
    """
    logger.info(f"[TemplateService] 删除模版: {template_id}")

    try:
        sql_success = WritingTemplates.delete_template(template_id, user_id)

        if sql_success:
            logger.success(f"[TemplateService] ✓ 模版删除成功: {template_id}")
            return True
        else:
            logger.warning(f"[TemplateService] SQL 删除失败或无权限")
            return False

    except Exception as e:
        logger.error(f"[TemplateService] 删除失败: {e}")
        return False
