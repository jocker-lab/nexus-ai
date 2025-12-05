# -*- coding: utf-8 -*-
"""
测试 Blueprint Agent 完整流程
"""
import asyncio
import sys
sys.path.insert(0, "/Users/seanxiao/PycharmProjects/nexus-ai")

from dotenv import load_dotenv
load_dotenv()  # 加载 .env 文件中的环境变量

from langchain_core.messages import HumanMessage
from app.agents.core.publisher.blueprint.agent import build_agent


async def test_blueprint():
    print("=" * 60)
    print("Blueprint Agent 测试")
    print("=" * 60)

    # 构建 agent
    print("\n🏗️  构建 Blueprint Agent...")
    agent = build_agent()

    # 准备输入
    user_input = "帮我写一份克罗恩病病历模版"
    print(f"\n📝 用户输入: {user_input}")
    print("=" * 60)

    # 初始状态
    initial_state = {
        "conversation_messages": [HumanMessage(content=user_input)],
        "pending_steps": [],
        "completed_steps": [],
        "blueprint_draft": "",
        "response": "",
        "matched_template": None,
        "language": "zh-CN",
    }

    # 配置（需要 thread_id 用于 checkpointer）
    config = {"configurable": {"thread_id": "test-blueprint-001"}}

    # 运行 agent
    print("\n🚀 开始运行 Blueprint Agent...\n")

    try:
        # 使用 astream 来观察每个节点的输出
        async for event in agent.astream(initial_state, config=config):
            # 打印当前节点名称和输出
            for node_name, node_output in event.items():
                print(f"\n{'='*40}")
                print(f"📍 节点: {node_name}")
                print(f"{'='*40}")

                if isinstance(node_output, dict):
                    for key, value in node_output.items():
                        if key == "conversation_messages":
                            print(f"  💬 {key}: {len(value)} 条消息")
                        elif key == "pending_steps":
                            print(f"  📋 {key}: {len(value)} 个待执行步骤")
                            for i, step in enumerate(value, 1):
                                print(f"      {i}. [{step.step_type.value}] {step.target}")
                        elif key == "completed_steps":
                            print(f"  ✅ {key}: {len(value)} 个已完成步骤")
                        elif key == "matched_template":
                            if value:
                                print(f"  🎯 {key}: {value.get('title', 'N/A')}")
                            else:
                                print(f"  🎯 {key}: None")
                        elif key == "blueprint_draft" and value:
                            print(f"  📝 {key}: {len(value)} 字符")
                            print(f"      预览: {value[:200]}...")
                        elif key == "response" and value:
                            print(f"  💡 {key}: {value[:200]}...")
                        else:
                            print(f"  {key}: {value}")
                else:
                    print(f"  输出: {node_output}")

    except Exception as e:
        print(f"\n❌ 运行出错: {e}")
        import traceback
        traceback.print_exc()

    print("\n" + "=" * 60)
    print("测试完成")
    print("=" * 60)


if __name__ == "__main__":
    asyncio.run(test_blueprint())
