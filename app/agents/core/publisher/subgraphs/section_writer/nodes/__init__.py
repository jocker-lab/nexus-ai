# -*- coding: utf-8 -*-
"""
@File    :   __init__.py
@Time    :   2025/11/14 10:14
@Author  :   pygao
@Version :   1.0
@Contact :   pygao.1@outlook.com
@License :   (C)Copyright 2025, GienTech Technology Co.,Ltd. All rights reserved.
@Desc    :   Section Writer Nodes

Updated: 2025/11/27
- writer_node 和 researcher_node 已被 chapter_content_generation subgraph 替代
- 保留 reviewer_node, merger_node, revise_draft_node 用于 review/revise 循环
"""
# DEPRECATED: 以下两个节点已被 chapter_content_generation subgraph 替代
# from .writer_node import chapter_content_writer
# from .researcher_node import chapter_researcher

# 保留的节点：用于 review/revise 循环
from .reviewer_node import review_draft
from .merger_node import chapter_finalizer
from .revise_draft_node import revise_draft