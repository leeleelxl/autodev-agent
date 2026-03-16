"""
最简单的测试 - 不使用 Memory 系统

只测试核心 Agent 功能
"""

import asyncio
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from src.agents import ArchitectAgent
from src.llm import LLMFactory, LLMProvider
from dotenv import load_dotenv
import os

load_dotenv()


async def test_architect_only():
    """只测试 Architect Agent"""
    print("=" * 60)
    print("测试 Architect Agent (Kimi)")
    print("=" * 60)

    # 获取 API Key
    api_key = os.getenv("MOONSHOT_API_KEY")
    if not api_key:
        print("❌ 未找到 MOONSHOT_API_KEY")
        return

    print(f"\n✓ API Key: {api_key[:10]}...")

    # 创建 LLM 客户端
    print("\n创建 LLM 客户端...")
    llm = LLMFactory.create_client(
        provider=LLMProvider.MOONSHOT,
        api_key=api_key,
        model="moonshot-v1-8k"
    )
    print("✓ 使用 Kimi (moonshot-v1-8k)")

    # 创建 Architect Agent
    print("\n创建 Architect Agent...")
    architect = ArchitectAgent()
    architect.set_llm_client(llm)
    print("✓ Agent 已创建")

    # 执行任务
    print("\n执行架构设计任务...")
    print("-" * 60)

    task = "创建一个简单的计算器应用，支持加减乘除"

    print(f"任务: {task}")
    print("-" * 60)

    try:
        print("\n正在调用 Kimi API...")
        response = await architect.process(task, context={})

        print("\n" + "=" * 60)
        print("✅ 执行成功！")
        print("=" * 60)

        print(f"\n设计方案:")
        print(response.content[:500])
        print("...")

        if response.metadata.get("design"):
            design = response.metadata["design"]
            print(f"\n架构模式: {design.get('architecture', {}).get('pattern', 'N/A')}")
            print(f"技术栈: {design.get('tech_stack', {}).get('language', 'N/A')}")

        print("\n测试完成！Kimi API 工作正常。")

    except Exception as e:
        print(f"\n❌ 执行失败: {str(e)}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    asyncio.run(test_architect_only())
