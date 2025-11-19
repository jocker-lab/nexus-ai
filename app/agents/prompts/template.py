# Copyright (c) 2025 Bytedance Ltd. and/or its affiliates
# SPDX-License-Identifier: MIT


import os
from datetime import datetime
from langchain.messages import SystemMessage
from jinja2 import Environment, FileSystemLoader, select_autoescape
from typing import Dict, Any


# Initialize Jinja2 environment
env = Environment(
    loader=FileSystemLoader(os.path.dirname(__file__)),
    autoescape=select_autoescape(),
    trim_blocks=True,
    lstrip_blocks=True,
)


def get_prompt_template(prompt_name: str) -> str:
    """
    Load and return a prompt template using Jinja2.

    Args:
        prompt_name: Name of the prompt template file (without .md extension)

    Returns:
        The template string with proper variable substitution syntax
    """
    try:
        template = env.get_template(f"{prompt_name}.md")
        return template.render()
    except Exception as e:
        raise ValueError(f"Error loading template {prompt_name}: {e}")


def render_prompt_template(prompt_name: str, context: Dict[str, Any], add_timestamp: bool = True) -> str:
    """
    渲染 Jinja2 提示词模板为字符串
    - render_prompt_template: 仅渲染模板，返回纯文本字符串

    Args:
        prompt_name: 模板名称（不含 .md 扩展名）
                     支持子目录路径，如 "chapter_writing/writer_system"
        context: 模板变量的字典，用于填充 Jinja2 模板中的 {{ variable }}
        add_timestamp: 是否自动添加 CURRENT_TIME 变量（默认 True）

    Returns:
        渲染后的字符串内容

    """
    # 准备模板变量（添加时间戳等上下文）
    template_vars = dict(context)

    if add_timestamp:
        template_vars["CURRENT_TIME"] = datetime.now().strftime("%a %b %d %Y %H:%M:%S %z")

    try:
        # 加载并渲染模板
        template = env.get_template(f"{prompt_name}.md")
        rendered_content = template.render(**template_vars)
        return rendered_content

    except Exception as e:
        raise ValueError(f"Error rendering template '{prompt_name}': {e}")



def apply_prompt_template(prompt_name: str, state: Dict[str, Any]) -> list:
    """
    Apply template variables to a prompt template and return formatted messages.

    Args:
        prompt_name: Name of the prompt template to use
        state: Current agent state containing variables to substitute

    Returns:
        List of LangChain messages with the system prompt as the first message
    """

    state_vars = {
        "CURRENT_TIME": datetime.now().strftime("%a %b %d %Y %H:%M:%S %z"),
        **state,
    }

    try:
        template = env.get_template(f"{prompt_name}.md")
        system_prompt = template.render(**state_vars)
        messages = [SystemMessage(content=system_prompt)]

        # Add conversation messages
        conversation_messages = state.get("conversation_messages", [])
        if conversation_messages:
            messages.extend(conversation_messages)
        return messages

    except Exception as e:
        raise ValueError(f"Error applying template {prompt_name}: {e}")


