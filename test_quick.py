"""
快速测试脚本

测试 AutoDev 基本功能
"""

import asyncio
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from src.agents import Orchestrator, ArchitectAgent, DeveloperAgent, TesterAgent, ReviewerAgent
from src.llm import LLMFactory, LLMProvider
from src.tools import CodeExecutor, CodeAnalyzer, Linter
from src.memory import MemoryManager, ExperienceMemory
from dotenv import load_dotenv
import os

load_dotenv()


async def test_simple_task():
    """测试简单任务：计算器"""
    print("=" * 60)
    print("AutoDev 快速测试")
    print("=" * 60)

    # 创建 orchestrator
    orchestrator = Orchestrator()

    # 注册 agents
    print("\n1. 注册 Agents...")
    orchestrator.register_agent(ArchitectAgent())
    orchestrator.register_agent(DeveloperAgent())
    orchestrator.register_agent(TesterAgent())
    orchestrator.register_agent(ReviewerAgent())
    print(f"   ✓ 已注册: {list(orchestrator.agents.keys())}")

    # 注册工具
    print("\n2. 注册 Tools...")
    orchestrator.register_tools(
        code_executor=CodeExecutor(use_docker=False),
        code_analyzer=CodeAnalyzer(),
        linter=Linter()
    )
    print(f"   ✓ 已注册: {list(orchestrator.tools.keys())}")

    # 设置记忆
    print("\n3. 设置 Memory...")
    memory = MemoryManager(persist_dir="./data/chroma")
    experience = ExperienceMemory(persist_dir="./data/chroma")
    orchestrator.set_memory(memory, experience)
    print("   ✓ Memory 系统已启用")

    # 设置 LLM
    print("\n4. 设置 LLM...")
    api_key = os.getenv("MOONSHOT_API_KEY")
    if not api_key:
        print("   ✗ 未找到 MOONSHOT_API_KEY")
        return

    llm = LLMFactory.create_client(
        provider=LLMProvider.MOONSHOT,
        api_key=api_key,
        model="moonshot-v1-8k"
    )

    for agent in orchestrator.agents.values():
        agent.set_llm_client(llm)

    print("   ✓ 使用 Kimi (moonshot-v1-8k)")

    # 执行任务
    print("\n5. 执行任务...")
    print("-" * 60)

    task = """
创建一个简单的计算器：
- 支持加减乘除
- 命令行界面
- 错误处理
"""

    print(f"任务: {task.strip()}")
    print("-" * 60)

    try:
        result = await orchestrator.execute_workflow(task)

        print("\n" + "=" * 60)
        print("执行结果")
        print("=" * 60)

        print(f"\n状态: {'✅ 成功' if result['success'] else '❌ 失败'}")
        print(f"阶段数: {len(result['phases'])}")

        # 显示各阶段
        for i, phase in enumerate(result['phases'], 1):
            print(f"\n阶段 {i}: {phase['name'].upper()}")
            print(f"  结果: {phase['result'][:100]}...")

        # 显示最终输出
        if result.get('final_output'):
            output = result['final_output']

            # 代码文件
            if output.get('code_files'):
                print(f"\n生成的代码文件: {len(output['code_files'])} 个")
                for file in output['code_files']:
                    print(f"  - {file.get('path', 'unknown')}")

            # 审查结果
            if output.get('review'):
                review = output['review']
                print(f"\n代码质量分数: {review.get('score', 0)}/100")
                print(f"问题数量: {len(review.get('issues', []))}")

        print("\n" + "=" * 60)
        print("测试完成！")
        print("=" * 60)

    except Exception as e:
        print(f"\n❌ 执行失败: {str(e)}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    asyncio.run(test_simple_task())
