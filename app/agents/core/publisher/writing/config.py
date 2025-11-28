# -*- coding: utf-8 -*-
"""
@File    :   config.py
@Time    :   2025/11/18
@Author  :   Claude
@Version :   1.0
@Desc    :   Document Writing Agent 配置
"""

# ========== LLM 配置 ==========
MODEL_NAME = "deepseek-chat"
TEMPERATURE = 0.8
MAX_TOKENS = 8000

# ========== 质量控制配置 ==========
MIN_QUALITY_SCORE = 75  # 最低质量分数阈值

# ========== 章节写作配置 ==========
DEFAULT_TARGET_WORD_COUNT = 1200  # 默认章节字数
WORD_COUNT_TOLERANCE = 0.1  # 字数容差（±10%）

# ========== 审查配置 ==========
MAX_REVISION_COUNT = 2  # 最大修订次数
PASS_SCORE_THRESHOLD = 85  # 通过分数阈值
