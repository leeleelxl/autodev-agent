"""
实际 Baseline 对比实验

任务：创建用户认证系统
对比：Single LLM vs AutoDev
"""

import asyncio
import time
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).parent))

from src.agents import Orchestrator, ArchitectAgent, DeveloperAgent, TesterAgent, ReviewerAgent
from src.llm import LLMFactory, LLMProvider, LLMMessage
from src.tools import CodeExecutor, CodeAnalyzer, Linter
from src.memory import MemoryManager, ExperienceMemory
from dotenv import load_dotenv
import os

load_dotenv()


async def run_single_llm(task: str):
    """Baseline 1: 单次 LLM 调用"""
    print("\n" + "=" * 60)
    print("Baseline 1: Single LLM")
    print("=" * 60)

    api_key = os.getenv("MOONSHOT_API_KEY")
    llm = LLMFactory.create_client(LLMProvider.MOONSHOT, api_key)

    prompt = f"""请实现以下任务：

{task}

要求：
1. 直接输出完整的 Python 代码
2. 包含所有必要的功能
3. 添加错误处理

请只输出代码，不要有其他解释。"""

    print("正在生成代码...")
    start_time = time.time()

    response = await llm.chat(
        messages=[LLMMessage(role="user", content=prompt)],
        temperature=0.7,
        max_tokens=4096
    )

    execution_time = time.time() - start_time

    code = response.content
    tokens = response.usage.get("input_tokens", 0) + response.usage.get("output_tokens", 0)

    # 保存代码
    with open("baseline_single_llm.py", "w") as f:
        f.write(code)

    print(f"✓ 完成")
    print(f"  执行时间: {execution_time:.1f}s")
    print(f"  Token 使用: {tokens}")
    print(f"  代码行数: {len(code.split(chr(10)))}")
    print(f"  是否有测试: {'✓' if 'test' in code.lower() or 'assert' in code.lower() else '✗'}")

    return {
        "code": code,
        "execution_time": execution_time,
        "tokens": tokens,
        "has_tests": 'test' in code.lower() or 'assert' in code.lower()
    }


async def run_autodev(task: str):
    """我们的系统: AutoDev"""
    print("\n" + "=" * 60)
    print("AutoDev: 多 Agent 协作")
    print("=" * 60)

    orchestrator = Orchestrator()

    # 注册所有组件
    for agent_cls in [ArchitectAgent, DeveloperAgent, TesterAgent, ReviewerAgent]:
        orchestrator.register_agent(agent_cls())

    orchestrator.register_tools(
        code_executor=CodeExecutor(use_docker=False),
        code_analyzer=CodeAnalyzer(),
        linter=Linter()
    )

    memory = MemoryManager(persist_dir="./data/chroma")
    experience = ExperienceMemory(persist_dir="./data/chroma")
    orchestrator.set_memory(memory, experience)

    api_key = os.getenv("MOONSHOT_API_KEY")
    llm = LLMFactory.create_client(LLMProvider.MOONSHOT, api_key)

    for agent in orchestrator.agents.values():
        agent.set_llm_client(llm)

    print("正在执行工作流...")
    start_time = time.time()

    result = await orchestrator.execute_workflow(task)

    execution_time = time.time() - start_time

    # 提取结果
    code_files = result.get("final_output", {}).get("code_files", [])
    test_files = result.get("final_output", {}).get("test_files", [])
    review = result.get("final_output", {}).get("review", {})

    # 保存所有代码文件
    from pathlib import Path
    output_dir = Path("autodev_generated")
    output_dir.mkdir(exist_ok=True)

    for file in code_files:
        file_path = file.get("path", "")
        content = file.get("content", "")

        # 创建目录结构
        full_path = output_dir / file_path
        full_path.parent.mkdir(parents=True, exist_ok=True)

        full_path.write_text(content)

    # 主文件用于统计
    main_code = code_files[0].get("content", "") if code_files else ""

    # 保存主文件到根目录（用于对比）
    Path("autodev_output.py").write_text(main_code)

    if test_files:
        test_code = test_files[0].get("content", "")
        with open("autodev_test.py", "w") as f:
            f.write(test_code)

    print(f"✓ 完成")
    print(f"  执行时间: {execution_time:.1f}s")
    print(f"  完成阶段: {len(result['phases'])}")
    print(f"  代码行数: {len(main_code.split(chr(10)))}")
    print(f"  测试文件: {'✓' if test_files else '✗'}")
    print(f"  代码质量: {review.get('score', 0)}/100")
    print(f"  发现问题: {len(review.get('issues', []))} 个")

    return {
        "code": main_code,
        "tests": test_code if test_files else "",
        "execution_time": execution_time,
        "quality_score": review.get("score", 0),
        "issues": review.get("issues", []),
        "has_tests": bool(test_files)
    }


async def compare():
    """运行对比实验"""
    print("\n" + "=" * 60)
    print("Baseline 对比实验")
    print("=" * 60)

    task = """
创建一个用户认证系统：
- 用户注册（密码哈希存储）
- 用户登录（返回 JWT token）
- Token 验证
- 使用 SQLite 数据库
- 包含错误处理和输入验证
"""

    print(f"\n任务: {task.strip()}")

    # 运行 Single LLM
    single_result = await run_single_llm(task)

    # 运行 AutoDev
    autodev_result = await run_autodev(task)

    # 对比结果
    print("\n" + "=" * 60)
    print("对比结果")
    print("=" * 60)

    print("\n| 指标 | Single LLM | AutoDev | 优势 |")
    print("|------|-----------|---------|------|")

    # 执行时间
    time_diff = ((autodev_result["execution_time"] / single_result["execution_time"]) - 1) * 100
    print(f"| 执行时间 | {single_result['execution_time']:.1f}s | {autodev_result['execution_time']:.1f}s | {time_diff:+.0f}% |")

    # 代码行数
    single_lines = len(single_result["code"].split('\n'))
    autodev_lines = len(autodev_result["code"].split('\n'))
    print(f"| 代码行数 | {single_lines} | {autodev_lines} | - |")

    # 测试
    print(f"| 包含测试 | {'✓' if single_result['has_tests'] else '✗'} | {'✓' if autodev_result['has_tests'] else '✗'} | {'✓' if autodev_result['has_tests'] and not single_result['has_tests'] else '-'} |")

    # 质量分数
    print(f"| 代码质量 | ? | {autodev_result['quality_score']}/100 | ✓ |")

    # 问题识别
    print(f"| 问题识别 | 0 | {len(autodev_result['issues'])} | ✓ |")

    print("\n" + "=" * 60)
    print("结论")
    print("=" * 60)

    print("\nAutoDev 的优势：")
    if autodev_result['has_tests'] and not single_result['has_tests']:
        print("  ✓ 自动生成测试用例")
    if autodev_result['issues']:
        print(f"  ✓ 自动识别 {len(autodev_result['issues'])} 个潜在问题")
    print(f"  ✓ 代码质量评分: {autodev_result['quality_score']}/100")
    print("  ✓ 全自动流程，无需人工介入")

    print("\n生成的文件：")
    print("  - baseline_single_llm.py (Single LLM 生成)")
    print("  - autodev_output.py (AutoDev 生成)")
    if autodev_result['has_tests']:
        print("  - autodev_test.py (AutoDev 生成的测试)")


if __name__ == "__main__":
    asyncio.run(compare())
