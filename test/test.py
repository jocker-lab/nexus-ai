# -*- coding: utf-8 -*-
"""
@File    :   test_total.py
@Time    :   2025/11/1 13:04
@Author  :   pygao
@Version :   1.0
@Contact :   pygao.1@outlook.com
@License :   (C)Copyright 2025, GienTech Technology Co.,Ltd. All rights reserved.
@Desc    :   文件描述
"""
from dotenv import load_dotenv

load_dotenv()
from langchain_core.messages import HumanMessage
import json
from datetime import datetime

load_dotenv()
from loguru import logger
from app.agents.core.publisher.blueprint import build_agent
from langgraph.types import Command


async def main():
    """
    使用示例
    """
    logger.info("🚀 启动 Plan-Execute-Replan Agent")

    app = build_agent()

    initial_input = "帮我写一篇中原银行的2025年度风险评估报告，总字数要求1w字以上,写作要求：结构框架：采用总 - 分 - 总金字塔结构，包括引言（概述行业背景与银行状况）、宏观监管政策、行业整体情况、同业对标、银行自身财务分析、主要问题与风险、针对性建议。分析逻辑：遵循漏斗模型，由外（宏观环境）到内（自身问题），层层递进，确保全面性和聚焦性。数据指标：覆盖规模增长、盈利能力（重点净息差、ROE）、运营效率（重点成本收入比）、资产质量（重点不良率、拨备覆盖率）、资本充足性（重点核心一级资本充足率）、市场回报等，进行纵横向对比。风格语调：客观审慎、数据驱动、批判性直接；问题导向，注重对比分析和解决方案；逻辑严密，论证基于事实，避免情绪化。报告长度控制在简洁实用，确保决策价值。"

    logger.info(f"📝 用户查询: {initial_input}")
    logger.info("")

    # 使用固定 thread_id 以支持中断后恢复
    config = {"recursion_limit": 50, "configurable": {"thread_id": "demo-thread"}}

    # 创建输出文件
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    output_file = f"stream_chunks_{timestamp}.jsonl"

    # 驱动循环:遇到中断通过 __interrupt__ 处理
    current_payload = {"conversation_messages": [HumanMessage(initial_input)]}
    iteration = 0

    while True:
        iteration += 1
        logger.info(f"\n{'🔄' * 40}")
        logger.info(f"第 {iteration} 轮执行")
        logger.info(f"{'🔄' * 40}\n")

        # 使用 astream 并写入文件
        with open(output_file, 'a', encoding='utf-8') as f:
            async for chunk in app.astream(
                    current_payload,
                    config=config,
                    stream_mode=["messages", "updates"],
                    subgraphs=True
            ):
                # 写入文件（每个chunk一行）
                f.write(json.dumps(chunk, ensure_ascii=False, default=str) + '\n')
                f.flush()

        # stream 结束后，通过 aget_state 检查是否有 interrupt
        state = await app.aget_state(config)

        # 检查是否被中断（state.next 不为空说明还有待执行的节点）
        if state.next:
            logger.warning("\n⏸️  工作流中断,需要用户输入")

            # 从 state.tasks 获取 interrupt 信息
            if state.tasks and len(state.tasks) > 0:
                task = state.tasks[0]
                if task.interrupts and len(task.interrupts) > 0:
                    interrupt_obj = task.interrupts[0]
                    interrupt_payload = interrupt_obj.value

                    # 获取中断信息
                    title = interrupt_payload.get("title", interrupt_payload.get("target", "需要你的反馈"))
                    message = interrupt_payload.get("message", "")
                    prompt = interrupt_payload.get("prompt", "请输入你的反馈:")

                    print(f"\n{'=' * 50}")
                    if title:
                        print(f"标题: {title}")
                    if message:
                        print(f"说明: {message}")

                    user_feedback = input(f"{prompt} ")
                    logger.info(f"📥 用户输入: {user_feedback}")

                    # 用用户反馈恢复执行
                    current_payload = Command(resume=user_feedback)
                    continue

        # 没有 next，说明工作流完成
        logger.info(f"\n{'🎉' * 40}")
        logger.success("工作流执行完成!")
        logger.info(f"{'🎉' * 40}\n")

        # 打印最终响应
        final_state = state.values
        if final_state:
            final_response = final_state.get("response", "No response generated")
            print(f"\n{'=' * 50}")
            print("最终响应:")
            print(f"{'=' * 50}")
            print(final_response)
            print(f"{'=' * 50}\n")

            logger.info(f"📊 执行统计:")
            logger.info(f"   总轮次: {iteration}")
            logger.info(f"   已完成步骤: {len(final_state.get('completed_steps', []))}")
            logger.info(f"   数据已保存到: {output_file}")

        break


if __name__ == "__main__":
    import asyncio

    asyncio.run(main())