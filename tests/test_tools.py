"""
测试 Tools 工具集
"""

import pytest
from src.tools import CodeExecutor, CodeAnalyzer, Linter


@pytest.mark.asyncio
async def test_code_executor_simple():
    """测试简单代码执行"""
    executor = CodeExecutor(use_docker=False)

    code = """
print("Hello, World!")
result = 2 + 2
print(f"2 + 2 = {result}")
"""

    result = await executor.execute(code, language="python", timeout=5)

    assert result.success is True
    assert "Hello, World!" in result.output
    assert "2 + 2 = 4" in result.output


@pytest.mark.asyncio
async def test_code_executor_error():
    """测试错误代码执行"""
    executor = CodeExecutor(use_docker=False)

    code = """
print(undefined_variable)
"""

    result = await executor.execute(code, language="python", timeout=5)

    assert result.success is False
    assert "NameError" in result.error or "undefined_variable" in result.error


@pytest.mark.asyncio
async def test_code_executor_timeout():
    """测试超时"""
    executor = CodeExecutor(use_docker=False)

    code = """
import time
time.sleep(10)
"""

    result = await executor.execute(code, language="python", timeout=2)

    assert result.success is False
    assert "超时" in result.error


@pytest.mark.asyncio
async def test_code_analyzer():
    """测试代码分析"""
    analyzer = CodeAnalyzer()

    code = """
import os
import sys

def hello(name):
    '''Say hello'''
    return f"Hello, {name}!"

class Calculator:
    '''Simple calculator'''

    def add(self, a, b):
        return a + b

    def subtract(self, a, b):
        return a - b

if __name__ == "__main__":
    calc = Calculator()
    print(calc.add(1, 2))
"""

    result = await analyzer.execute(code, language="python")

    assert result.success is True
    assert len(result.output["functions"]) >= 1
    assert len(result.output["classes"]) >= 1
    assert "Calculator" in [c["name"] for c in result.output["classes"]]
    assert result.output["complexity"]["cyclomatic_complexity"] >= 0


@pytest.mark.asyncio
async def test_linter():
    """测试代码质量检查"""
    linter = Linter()

    # 好的代码
    good_code = """
def add(a, b):
    '''Add two numbers'''
    return a + b

result = add(1, 2)
print(result)
"""

    result = await linter.execute(good_code, language="python")

    # 如果 pylint 已安装
    if result.success:
        assert result.output["score"] >= 0
        assert "summary" in result.output


@pytest.mark.asyncio
async def test_code_executor_with_tests():
    """测试代码和测试一起执行"""
    executor = CodeExecutor(use_docker=False)

    code = """
def add(a, b):
    return a + b
"""

    test_code = """
assert add(1, 2) == 3
assert add(0, 0) == 0
assert add(-1, 1) == 0
print("All tests passed!")
"""

    result = await executor.execute_with_tests(code, test_code, timeout=5)

    assert result.success is True
    assert "All tests passed!" in result.output
