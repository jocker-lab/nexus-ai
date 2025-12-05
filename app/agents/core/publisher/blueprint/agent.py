# -*- coding: utf-8 -*-
"""
@File    :   agent.py
@Time    :   2025/10/31 20:51
@Author  :   pygao
@Version :   1.0
@Contact :   pygao.1@outlook.com
@License :   (C)Copyright 2025, GienTech Technology Co.,Ltd. All rights reserved.
@Desc    :   重构为独立节点架构 - Plan-Execute-Replan 工作流
"""
from loguru import logger
from langgraph.graph import StateGraph, START, END
from langgraph.checkpoint.memory import MemorySaver

from app.agents.core.publisher.blueprint.state import PlanExecuteState
from app.agents.core.publisher.blueprint.nodes.nodes import (
    # 核心节点
    coordinator_step,
    plan_step,
    replan_step,

    # 路由节点和路由决策函数
    route_step,
    _route_decision,  # 条件函数，用于 add_conditional_edges

    # 四个独立的执行节点
    execute_research_node,
    execute_human_involvement_node,
    execute_template_search_node,
    execute_writing_blueprint_node,

    # 条件判断函数
    should_replan,
    should_end,
)


def build_agent():
    """
    构建完整的 Plan-Execute-Replan 工作流

    🔥 新架构：基于独立节点的设计

    工作流程：
    1. START -> coordinator: 协调器（判断是否需要规划）
    2. coordinator -> planner: 生成初始计划
    3. planner -> route_step: 路由到对应的执行节点
    4. route_step -> execute_research/execute_human_involvement/execute_writing_blueprint: 执行具体步骤
    5. 执行节点 -> (should_replan) -> route_step (继续) / replan (重新规划) / END (结束)
    6. replan -> (should_end) -> route_step (继续) / END (完成)

    节点说明：
    🎯 coordinator - 协调器，判断是直接回复还是需要规划
    📋 planner - 规划器，生成执行计划
    🔀 route_step - 路由器，根据步骤类型分发到不同执行节点
    🔬 execute_research - 研究节点，调用研究子图进行信息收集
    👤 execute_human_involvement - 人类参与节点，中断工作流等待用户输入
    📝 execute_writing_blueprint - 蓝图构建节点，生成写作蓝图
    🔄 replan - 重新规划节点，根据执行结果调整计划
    """
    logger.info("=" * 80)
    logger.info("🏗️  开始构建 Plan-Execute-Replan 工作流")
    logger.info("=" * 80)
    logger.info("")
    logger.info("📐 架构说明：")
    logger.info("   • 独立节点设计：每个执行节点有清晰的职责和日志标识")
    logger.info("   • 灵活路由：通过 route_step 动态分发任务")
    logger.info("   • 智能规划：支持动态重新规划和人类参与")
    logger.info("")

    # 创建状态图
    workflow = StateGraph(PlanExecuteState)

    # ==================== 添加节点 ====================
    logger.info("📦 添加节点...")

    # 核心流程节点
    workflow.add_node("coordinator", coordinator_step)
    workflow.add_node("planner", plan_step)
    workflow.add_node("replan", replan_step)
    logger.info("   ✓ 核心节点: coordinator, planner, replan")

    # 路由节点
    workflow.add_node("route_step", route_step)
    logger.info("   ✓ 路由节点: route_step")

    # 四个独立的执行节点
    workflow.add_node("execute_research", execute_research_node)
    workflow.add_node("execute_human_involvement", execute_human_involvement_node)
    workflow.add_node("execute_template_search", execute_template_search_node)
    workflow.add_node("execute_writing_blueprint", execute_writing_blueprint_node)
    logger.info("   ✓ 执行节点: execute_research, execute_human_involvement, execute_template_search, execute_writing_blueprint")
    logger.info("")

    # ==================== 定义工作流转换 ====================
    logger.info("🔗 配置工作流转换...")

    # 1. START -> coordinator
    workflow.add_edge(START, "coordinator")
    logger.info("   ✓ START -> coordinator")

    # 2. coordinator -> planner (由 Command 控制，也可能直接到 END)
    # coordinator 使用 Command 返回，不需要显式添加边

    # 3. planner -> route_step
    workflow.add_edge("planner", "route_step")
    logger.info("   ✓ planner -> route_step")

    # 4. route_step -> 不同的执行节点（条件边）
    # 🔥 关键修复：使用 _route_decision 条件函数，而不是 route_step 节点
    workflow.add_conditional_edges(
        "route_step",
        _route_decision,  # 使用条件函数（返回字符串）
        {
            "execute_research": "execute_research",
            "execute_human_involvement": "execute_human_involvement",
            "execute_template_search": "execute_template_search",
            "execute_writing_blueprint": "execute_writing_blueprint",
            "__end__": END
        }
    )
    logger.info("   ✓ route_step -> [execute_research | execute_human_involvement | execute_template_search | execute_writing_blueprint | END]")

    # 5. 四个执行节点完成后 -> should_replan 判断
    # 根据情况：继续执行(route_step) / 重新规划(replan) / 结束(END)
    for node_name in ["execute_research", "execute_human_involvement", "execute_template_search", "execute_writing_blueprint"]:
        workflow.add_conditional_edges(
            node_name,
            should_replan,  # 判断函数
            {
                "route_step": "route_step",  # 继续执行下一个步骤
                "replan": "replan",  # 重新规划
                END: END  # 结束
            }
        )
        logger.info(f"   ✓ {node_name} -> [route_step | replan | END] (via should_replan)")

    # 6. replan -> should_end 判断
    # 根据情况：继续执行(route_step) / 结束(END)
    workflow.add_conditional_edges(
        "replan",
        should_end,  # 判断函数
        {
            "route_step": "route_step",  # 继续执行
            END: END  # 结束
        }
    )
    logger.info("   ✓ replan -> [route_step | END] (via should_end)")
    logger.info("")

    # ==================== 编译工作流 ====================
    logger.info("⚙️  编译工作流...")

    # 启用内存检查点，支持中断后恢复
    checkpointer = MemorySaver()
    app = workflow.compile(checkpointer=checkpointer)

    logger.info("")
    logger.info("=" * 80)
    logger.success("🎉 工作流构建完成!")
    logger.info("=" * 80)
    logger.info("")
    logger.info("📊 工作流结构:")
    logger.info("   START")
    logger.info("     ↓")
    logger.info("   coordinator ─→ [planner / END]")
    logger.info("     ↓")
    logger.info("   planner")
    logger.info("     ↓")
    logger.info("   route_step ─→ [execute_research / execute_human_involvement / execute_writing_blueprint / END]")
    logger.info("     ↓                        ↓                           ↓")
    logger.info("   (should_replan) ←────────┴───────────────────────────┘")
    logger.info("     ├─→ route_step (继续执行)")
    logger.info("     ├─→ replan (重新规划)")
    logger.info("     └─→ END (结束)")
    logger.info("            ↓")
    logger.info("   replan ─→ [route_step / END] (via should_end)")
    logger.info("")
    logger.info("🔍 节点类型说明:")
    logger.info("   🎯 coordinator          - 协调器，判断任务类型")
    logger.info("   📋 planner              - 规划器，生成执行计划")
    logger.info("   🔀 route_step           - 路由器，分发到执行节点")
    logger.info("   🔬 execute_research     - 研究分析节点")
    logger.info("   👤 execute_human_involvement - 人类参与节点")
    logger.info("   📝 execute_writing_blueprint - 蓝图构建节点")
    logger.info("   🔄 replan               - 重新规划节点")
    logger.info("")
    logger.info("💡 扩展提示:")
    logger.info("   • 添加新的步骤类型：")
    logger.info("     1. 在 blueprint_schema.py 的 StepType 枚举中添加新类型")
    logger.info("     2. 在 nodes.py 中创建新的执行节点函数")
    logger.info("     3. 在 _route_decision 函数中添加路由规则")
    logger.info("     4. 在 agent.py 中注册新节点并配置边")
    logger.info("=" * 80)
    logger.info("")

    return app
