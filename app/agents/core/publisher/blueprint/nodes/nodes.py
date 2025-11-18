# -*- coding: utf-8 -*-
"""
@File    :   nodes.py
@Time    :   2025/10/31 20:42
@Author  :   pygao
@Version :   1.0
@Contact :   pygao.1@outlook.com
@License :   (C)Copyright 2025, GienTech Technology Co.,Ltd. All rights reserved.
@Desc    :   重构为独立节点架构 - 每个节点有清晰的日志标识
"""
import json
from loguru import logger
from langchain.chat_models import init_chat_model
from langgraph.types import interrupt, Command
from typing import Literal

from langgraph.graph import END

from langchain.messages import AIMessage
from app.agents.core.publisher.blueprint.state import PlanExecuteState
from app.agents.schemas.blueprint_schema import Plan, StepType, Step, StepExecution, ReplanSteps, \
    CoordinatorDecision
from app.agents.prompts.planner.replanner_prompt import replanner_prompt
from app.agents.prompts.template import apply_prompt_template


# ==================== 协调器和规划器节点 ====================

async def coordinator_step(state: PlanExecuteState) -> Command[Literal["planner", "__end__"]]:
    """
    协调器节点：与客户沟通并根据请求的清晰度路由任务
    """
    messages = apply_prompt_template("coordinator", state)
    llm = init_chat_model("deepseek:deepseek-chat")
    response = await llm.with_structured_output(CoordinatorDecision).ainvoke(messages)

    messages = state.get("conversation_messages", [])
    if response.message:
        messages.append(AIMessage(content=response.message, name="Coordinator"))

    logger.info(f"🎯 [COORDINATOR] 决策: {response.next_action}")
    goto_node = response.goto if response.goto else "__end__"

    update_state = {
        "conversation_messages": messages,
        "language": response.language,
    }

    logger.info(f"   ➡️  路由到: {goto_node}")
    return Command(goto=response.goto, update=update_state)


async def plan_step(state: PlanExecuteState):
    """
    规划器节点：根据用户输入生成初步执行计划
    """
    language_code = state.get('language', 'zh-CN')

    logger.info("📋 [PLANNER] 开始生成执行计划...")

    llm = init_chat_model("deepseek:deepseek-reasoner")
    messages = apply_prompt_template("planner/planner", state)
    planner = llm.with_structured_output(Plan)

    plan = await planner.ainvoke(messages)

    logger.success(f"✅ [PLANNER] 生成了 {len(plan.steps)} 个执行步骤:")
    for idx, step in enumerate(plan.steps, start=1):
        logger.info(f"   {idx}. [{step.step_type.value.upper()}] {step.target}")

    update_state = {
        "conversation_messages": [AIMessage(content=plan.thought)],
        "pending_steps": plan.steps,
        "language": language_code
    }

    return update_state


# ==================== 路由节点 ====================

async def route_step(state: PlanExecuteState):
    """
    路由节点：记录日志并准备路由
    这是一个真正的节点函数，必须返回字典
    """
    pending_steps = state.get("pending_steps", [])

    if not pending_steps:
        logger.info("🏁 [ROUTER] 没有待执行步骤，准备结束工作流")
        return {}

    current_step = pending_steps[0]
    logger.info(f"🔀 [ROUTER] 当前步骤类型: {current_step.step_type.value}")
    logger.info(f"   📝 步骤目标: {current_step.target}")

    return {}  # 节点函数必须返回字典


def _route_decision(state: PlanExecuteState) -> Literal[
    "execute_research", "execute_human_involvement", "execute_writing_blueprint", "__end__"]:
    """
    路由决策函数：根据当前待执行步骤的类型决定路由
    这是条件函数，用于 add_conditional_edges，返回字符串

    返回值：
    - "execute_research": 路由到研究节点
    - "execute_human_involvement": 路由到人类参与节点
    - "execute_writing_blueprint": 路由到蓝图构建节点
    - "__end__": 没有待执行步骤，结束工作流
    """
    pending_steps = state.get("pending_steps", [])

    if not pending_steps:
        return "__end__"

    current_step = pending_steps[0]
    step_type = current_step.step_type

    # 根据步骤类型路由到不同节点
    route_map = {
        StepType.RESEARCH: "execute_research",
        StepType.HUMAN_INVOLVEMENT: "execute_human_involvement",
        StepType.WRITING_BLUEPRINT: "execute_writing_blueprint",
    }

    next_node = route_map.get(step_type, "__end__")
    logger.info(f"   ➡️  路由决策: {next_node}")

    return next_node


# ==================== 三个独立的执行节点 ====================

async def execute_research_node(state: PlanExecuteState):
    """
    🔬 研究节点：执行研究类型的步骤

    功能：
    - 使用 Research Subgraph 进行并行研究
    - 支持多个搜索主题（actions 为 list）
    - 更新完成的步骤和待执行步骤
    """
    logger.info("=" * 60)
    logger.info("🔬 [RESEARCH NODE] 节点启动")
    logger.info("=" * 60)

    pending_steps = state.get("pending_steps", [])

    if not pending_steps:
        logger.warning("⚠️  [RESEARCH NODE] 没有待执行的步骤")
        return {"pending_steps": []}

    # 获取当前步骤
    current_step = pending_steps[0]
    remaining_steps = pending_steps[1:]

    logger.info(f"📌 [RESEARCH NODE] 当前任务: {current_step.target}")

    # 调用研究子图
    result = await _execute_research_logic(current_step, state)

    # 创建执行记录
    execution = StepExecution(
        step=current_step,
        execution_res=result,
        status="completed"
    )

    logger.success(f"✅ [RESEARCH NODE] 研究完成")
    logger.info(f"   📊 结果长度: {len(result)} 字符")
    logger.info(f"   📋 剩余步骤: {len(remaining_steps)} 个")
    logger.info("=" * 60)

    return {
        "pending_steps": remaining_steps,
        "completed_steps": [execution]
    }


async def execute_human_involvement_node(state: PlanExecuteState):
    """
    👤 人类参与节点：需要人类输入的步骤

    功能：
    - 生成与用户交互的消息
    - 使用 interrupt 中断工作流等待用户输入
    - 收集用户反馈并记录
    """
    logger.info("=" * 60)
    logger.warning("👤 [HUMAN NODE] 节点启动 - 需要人类参与")
    logger.info("=" * 60)

    pending_steps = state.get("pending_steps", [])

    if not pending_steps:
        logger.warning("⚠️  [HUMAN NODE] 没有待执行的步骤")
        return {"pending_steps": []}

    # 获取当前步骤
    current_step = pending_steps[0]
    remaining_steps = pending_steps[1:]

    logger.info(f"📌 [HUMAN NODE] 当前任务: {current_step.target}")
    logger.info(f"   🎯 行动要求: {current_step.actions}")

    # 执行人类参与逻辑
    result = await _execute_human_involvement_logic(current_step, state)

    # 创建执行记录
    execution = StepExecution(
        step=current_step,
        execution_res=result,
        status="completed"
    )

    logger.success(f"✅ [HUMAN NODE] 用户反馈已收集")
    logger.info(f"   📋 剩余步骤: {len(remaining_steps)} 个")
    logger.info("=" * 60)

    return {
        "pending_steps": remaining_steps,
        "completed_steps": [execution]
    }


async def execute_writing_blueprint_node(state: PlanExecuteState):
    """
    📝 蓝图构建节点：构建写作蓝图

    功能：
    - 收集所有已完成的研究结果
    - 基于研究内容生成写作蓝图
    - 更新 blueprint_draft 字段
    """
    logger.info("=" * 60)
    logger.info("📝 [BLUEPRINT NODE] 节点启动")
    logger.info("=" * 60)

    pending_steps = state.get("pending_steps", [])

    if not pending_steps:
        logger.warning("⚠️  [BLUEPRINT NODE] 没有待执行的步骤")
        return {"pending_steps": []}

    # 获取当前步骤
    current_step = pending_steps[0]
    remaining_steps = pending_steps[1:]

    logger.info(f"📌 [BLUEPRINT NODE] 当前任务: {current_step.target}")

    # 执行蓝图构建逻辑
    result = await _execute_blueprint_logic(current_step, state)

    # 创建执行记录
    execution = StepExecution(
        step=current_step,
        execution_res=result,
        status="completed"
    )

    logger.success(f"✅ [BLUEPRINT NODE] 蓝图构建完成")
    logger.info(f"   📊 蓝图长度: {len(result)} 字符")
    logger.info(f"   📋 剩余步骤: {len(remaining_steps)} 个")
    logger.info("=" * 60)

    return {
        "pending_steps": remaining_steps,
        "completed_steps": [execution],
        "blueprint_draft": result  # 更新蓝图字段
    }


# ==================== 执行逻辑辅助函数（内部使用）====================

async def _execute_research_logic(step: Step, state: PlanExecuteState) -> str:
    """
    研究执行逻辑 - 使用 Research Subgraph
    """
    from app.agents.core.publisher.subgraphs.research.agent import run_research_subgraph

    logger.info("   🔍 [RESEARCH] 开始调用研究子图")

    actions = step.actions if isinstance(step.actions, list) else [step.actions]
    logger.info(f"   📚 [RESEARCH] 需要研究 {len(actions)} 个主题:")
    for idx, topic in enumerate(actions, start=1):
        logger.info(f"      {idx}. {topic}")

    language_code = state.get('language', 'zh-CN')

    # 调用 research subgraph
    logger.info("   ⚙️  [RESEARCH] 执行中...")
    final_result = await run_research_subgraph(
        topics=actions,
        need_search=True,
        language=language_code
    )

    logger.info(f"   ✓ [RESEARCH] 研究子图执行完成")
    return final_result


async def _execute_human_involvement_logic(step: Step, state: PlanExecuteState) -> str:
    """
    人类参与执行逻辑 - 生成提示并中断等待用户输入
    """
    logger.info("   💬 [HUMAN] 准备生成用户交互消息")

    lang = state.get("language")
    language_code = state.get('language', 'zh-CN')
    completed_steps = state.get("completed_steps", [])

    # 构建已完成步骤的摘要
    completed_steps_json = json.dumps(
        [step.model_dump() for step in completed_steps],
        indent=2,
        ensure_ascii=False
    )

    task_formatted = f"""
    You are an AI assistant guiding a user through a multi-step task.
    The current step target is "{step.target}" with action: "{step.actions}".
    Previous completed steps are: {completed_steps_json}.
    - Based on the completed steps and the current step's actions, generate a concise, engaging message to interact with the user. 
    - This message should initiate or continue the discussion as outlined in the actions, prompting user input where needed to fulfill the step's goal. 
    - Keep the tone collaborative and focused on the task. Output only the message, nothing else.
    - Always use the language specified by the language {language_code}
    """

    logger.info("   🤖 [HUMAN] 调用 LLM 生成交互消息")
    llm = init_chat_model("deepseek:deepseek-chat")
    response = await llm.ainvoke(task_formatted)

    # 通过 LangGraph 的 interrupt 机制中断等待用户输入
    interrupt_payload = {
        "type": "human_involvement",
        "target": step.target,
        "actions": step.actions,
        "message": response.content,
        "language": lang,
    }

    logger.info(f"   ⏸️  [HUMAN] 中断工作流，等待用户反馈")
    logger.debug(f"   💭 [HUMAN] 提示消息: {response.content[:100]}...")

    user_feedback = interrupt(interrupt_payload)

    feedback_str = str(user_feedback)
    if len(feedback_str) > 100:
        logger.success(f"   ✓ [HUMAN] 收到用户反馈: {feedback_str[:100]}...")
    else:
        logger.success(f"   ✓ [HUMAN] 收到用户反馈: {feedback_str}")

    # 返回结构化文本
    return f"[HUMAN FEEDBACK]\nTask: {step.target}\nFeedback: {user_feedback}"


async def _execute_blueprint_logic(step: Step, state: PlanExecuteState) -> str:
    """
    蓝图构建执行逻辑 - 基于研究结果生成写作蓝图
    """
    logger.info("   📖 [BLUEPRINT] 收集研究结果")
    language_code = state.get('language', 'zh-CN')

    # 收集之前所有研究步骤的结果
    past_research = []
    for execution in state.get("completed_steps", []):
        if execution.step.step_type == StepType.RESEARCH:
            past_research.append(f"{execution.step.target}:\n{execution.execution_res}")
            logger.info(f"      ✓ 引用研究: {execution.step.target}")

    context = "\n\n".join(past_research) if past_research else "No previous research available."
    logger.info(f"   📚 [BLUEPRINT] 基于 {len(past_research)} 个研究结果构建蓝图")

    task_formatted = f"""
    Based on the following research and information, create a detailed writing blueprint:

    Previous Research:
    {context}

    Task: {step.target}
    Requirements: {step.actions}

    Please create a comprehensive writing blueprint including:
    1. Main structure and outline
    2. Key points to cover
    3. Supporting arguments and evidence
    4. Recommended writing style and tone

    Language: {language_code}
    """

    logger.info("   🤖 [BLUEPRINT] 调用 LLM 生成蓝图")
    llm = init_chat_model("deepseek:deepseek-chat")
    response = await llm.ainvoke(task_formatted)

    logger.info(f"   ✓ [BLUEPRINT] 蓝图生成完成")
    return response.content


# ==================== 重新规划节点 ====================

async def replan_step(state: PlanExecuteState):
    """
    重新规划节点：根据已执行的步骤和剩余任务，决定下一步行动
    """
    logger.info("=" * 60)
    logger.info("🔄 [REPLAN] 重新规划节点启动")
    logger.info("=" * 60)

    # 从状态中获取数据
    completed_steps = state.get("completed_steps", [])
    pending_steps = state.get("pending_steps", [])
    conversation_messages = state.get("conversation_messages", [])

    logger.info(f"   📊 [REPLAN] 已完成: {len(completed_steps)} 个步骤")
    logger.info(f"   📋 [REPLAN] 待执行: {len(pending_steps)} 个步骤")

    # 构建已完成步骤摘要
    completed_summary = []
    for execution in completed_steps:
        step = execution.step
        result = execution.execution_res
        result_preview = result[:10000] + "..." if len(result) > 10000 else result

        completed_summary.append({
            "step_number": len(completed_summary) + 1,
            "step_type": step.step_type.value,
            "target": step.target,
            "result_preview": result_preview,
            "status": execution.status,
        })

    # 构建待执行步骤摘要
    pending_summary = []
    for idx, step in enumerate(pending_steps):
        pending_summary.append({
            "step_number": len(completed_steps) + idx + 1,
            "step_type": step.step_type.value,
            "target": step.target,
            "actions": step.actions
        })

    # 调用 LLM 进行重新规划
    logger.info("   🤖 [REPLAN] 调用 LLM 分析当前状态")

    llm = init_chat_model("deepseek:deepseek-chat")
    replanner = replanner_prompt | llm.with_structured_output(ReplanSteps)

    prompt_input = {
        "conversation_messages": conversation_messages,
        "completed_steps": completed_summary,
        "pending_steps": pending_summary,
        "total_completed": len(completed_steps),
        "total_pending": len(pending_steps),
    }

    output = await replanner.ainvoke(prompt_input)

    logger.info(f"   🎯 [REPLAN] 规划结果: {len(output.steps)} 个新步骤")
    logger.info(f"   💭 [REPLAN] 推理: {output.reasoning[:200]}...")

    if not output.steps:
        # 项目完成
        logger.success("🎊 [REPLAN] 项目完成，准备结束工作流")
        logger.info("=" * 60)

        return {
            "response": output.reasoning,
            "pending_steps": []
        }
    else:
        # 继续执行
        logger.info(f"   📋 [REPLAN] 更新执行计划:")
        for idx, step in enumerate(output.steps, start=1):
            logger.info(f"      {idx}. [{step.step_type.value.upper()}] {step.target}")
        logger.info("=" * 60)

        return {
            "pending_steps": output.steps
        }


# ==================== 条件判断函数 ====================

def should_replan(state: PlanExecuteState) -> Literal["route_step", "replan", "END"]:
    """
    条件判断：执行节点完成后，决定下一步行动

    逻辑：
    1. 如果没有待执行步骤 -> 结束
    2. 如果刚完成的是 HUMAN_INVOLVEMENT -> 重新规划
    3. 其他情况 -> 继续执行下一个步骤
    """
    pending_steps = state.get("pending_steps", [])

    # 没有待执行步骤，结束工作流
    if not pending_steps:
        logger.info("🏁 [SHOULD_REPLAN] 没有待执行步骤，准备结束")
        return END

    # 检查刚完成的步骤类型
    completed = state.get("completed_steps", [])
    if completed:
        last_step_type = completed[-1].step.step_type

        # 如果是人类参与，需要重新规划
        if last_step_type == StepType.HUMAN_INVOLVEMENT:
            logger.info(f"🔄 [SHOULD_REPLAN] 检测到 {last_step_type.value}，触发重新规划")
            return "replan"

    # 其他情况继续执行
    logger.info("➡️  [SHOULD_REPLAN] 继续执行下一个步骤")
    return "route_step"


def should_end(state: PlanExecuteState) -> Literal["route_step", "END"]:
    """
    条件判断：重新规划后，决定是继续执行还是结束

    逻辑：
    1. 如果有 response（项目完成标志）-> 结束
    2. 如果没有待执行步骤 -> 结束
    3. 其他情况 -> 继续执行
    """
    has_response = bool(state.get("response"))
    has_pending = bool(state.get("pending_steps"))

    if has_response:
        logger.info("🏁 [SHOULD_END] 检测到最终响应，工作流将结束")
        return END
    elif not has_pending:
        logger.warning("⚠️  [SHOULD_END] 没有待执行步骤且没有响应，异常情况，结束工作流")
        return END
    else:
        logger.info("➡️  [SHOULD_END] 继续执行新的步骤")
        return "route_step"