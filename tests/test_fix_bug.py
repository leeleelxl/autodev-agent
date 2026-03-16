"""
测试 AutoDev 的迭代改进能力

让系统自动修复计算器的减号 bug
"""

import asyncio
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from src.agents import DeveloperAgent
from src.llm import LLMFactory, LLMProvider
from src.tools import CodeAnalyzer, Linter
from dotenv import load_dotenv
import os

load_dotenv()


async def test_fix_bug():
    """测试 bug 修复"""
    print("=" * 60)
    print("测试 AutoDev 自动修复 Bug")
    print("=" * 60)

    # 读取有问题的代码
    with open("generated_calculator.py") as f:
        buggy_code = f.read()

    print("\n发现的问题:")
    print("- 输入 '10-2' 时，正则表达式将 '-2' 识别为负数")
    print("- 导致计算结果错误")

    # 创建 Developer Agent
    developer = DeveloperAgent()

    # 设置工具
    developer.set_tools(
        code_analyzer=CodeAnalyzer(),
        linter=Linter()
    )

    # 设置 LLM
    api_key = os.getenv("MOONSHOT_API_KEY")
    llm = LLMFactory.create_client(
        provider=LLMProvider.MOONSHOT,
        api_key=api_key,
        model="moonshot-v1-8k"
    )
    developer.set_llm_client(llm)

    # 让 Agent 修复 bug
    print("\n正在修复 bug...")

    context = {
        "code_files": [{
            "path": "generated_calculator.py",
            "content": buggy_code
        }],
        "review_issues": [{
            "severity": "high",
            "description": "正则表达式 r'-?\\d+' 会将减号后的数字识别为负数，导致 '10-2' 解析错误",
            "suggestion": "修改正则表达式，先提取运算符，再提取数字，避免负号混淆"
        }]
    }

    response = await developer.process(
        "修复计算器的减号解析 bug",
        context
    )

    # 保存修复后的代码
    if response.metadata.get("files"):
        fixed_code = response.metadata["files"][0].get("content", "")

        with open("generated_calculator_fixed.py", "w") as f:
            f.write(fixed_code)

        print("\n✓ 修复后的代码已保存到 generated_calculator_fixed.py")
        print("\n修复后的代码片段:")
        print("-" * 60)
        print(fixed_code[:800])
        print("...")

        return True

    return False


if __name__ == "__main__":
    asyncio.run(test_fix_bug())
