# -*- coding: utf-8 -*-
"""
@File    :   __init__.py
@Time    :   2025/11/14 10:40
@Author  :   pygao
@Version :   1.0
@Contact :   pygao.1@outlook.com
@License :   (C)Copyright 2025, GienTech Technology Co.,Ltd. All rights reserved.
@Desc    :   Document Writing Nodes
"""
from .chapter_writing_aggregator import chapter_aggregator
from .chapter_writing_dispatcher import chapter_dispatcher
from .document_integrator import document_integrator
from .document_finalizer import document_finalizer
from .document_writing_role_builder import role_builder_node
from .chapter_subgraph_wrapper import chapter_subgraph_wrapper

# 保留旧导出以兼容（可选，后续可移除）
# from .document_reviewer import document_reviewer
# from .document_reviser import document_reviser