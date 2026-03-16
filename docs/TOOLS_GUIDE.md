# Tools 工具集使用指南

## 概述

AutoDev 提供三个核心工具：

1. **CodeExecutor** - 代码执行器（支持本地和 Docker）
2. **CodeAnalyzer** - 代码分析器（AST 解析）
3. **Linter** - 代码质量检查（Pylint）

## 1. CodeExecutor - 代码执行器

### 基础使用

```python
from src.tools import CodeExecutor

# 创建执行器（本地模式）
executor = CodeExecutor(use_docker=False)

# 执行代码
code = """
def fibonacci(n):
    if n <= 1:
        return n
    return fibonacci(n-1) + fibonacci(n-2)

print(fibonacci(10))
"""

result = await executor.execute(code, language="python", timeout=5)

if result.success:
    print("输出:", result.output)
else:
    print("错误:", result.error)
```

### Docker 模式（推荐用于生产）

```python
# 使用 Docker 隔离执行
executor = CodeExecutor(use_docker=True)

result = await executor.execute(code, language="python", timeout=10)
```

**Docker 模式特性：**
- 完全隔离的执行环境
- 禁用网络访问
- 限制内存（256MB）和 CPU（1核）
- 自动清理容器

### 执行代码和测试

```python
code = """
def add(a, b):
    return a + b
"""

test_code = """
assert add(1, 2) == 3
assert add(0, 0) == 0
print("Tests passed!")
"""

result = await executor.execute_with_tests(code, test_code, timeout=5)
```

## 2. CodeAnalyzer - 代码分析器

### 分析代码结构

```python
from src.tools import CodeAnalyzer

analyzer = CodeAnalyzer()

code = """
import os

class DataProcessor:
    def __init__(self, data):
        self.data = data

    def process(self):
        return [x * 2 for x in self.data]

def main():
    processor = DataProcessor([1, 2, 3])
    print(processor.process())
"""

result = await analyzer.execute(code, language="python")

if result.success:
    analysis = result.output

    print("函数:", analysis["functions"])
    print("类:", analysis["classes"])
    print("导入:", analysis["imports"])
    print("复杂度:", analysis["complexity"])
    print("问题:", analysis["issues"])
```

### 分析结果示例

```python
{
    "functions": [
        {
            "name": "main",
            "args": [],
            "lineno": 9,
            "is_async": False,
            "decorators": [],
            "docstring": None
        }
    ],
    "classes": [
        {
            "name": "DataProcessor",
            "bases": [],
            "methods": ["__init__", "process"],
            "lineno": 3,
            "docstring": None
        }
    ],
    "imports": ["os"],
    "complexity": {
        "cyclomatic_complexity": 2,
        "rating": "简单"
    },
    "issues": [],
    "lines_of_code": 12,
    "summary": "代码包含 1 个函数, 1 个类, 复杂度: 简单"
}
```

## 3. Linter - 代码质量检查

### 检查代码质量

```python
from src.tools import Linter

linter = Linter()

code = """
def calculate_sum(numbers):
    total = 0
    for num in numbers:
        total += num
    return total

result = calculate_sum([1, 2, 3, 4, 5])
print(result)
"""

result = await linter.execute(code, language="python")

if result.success:
    quality = result.output

    print(f"质量分数: {quality['score']}/10.0")
    print(f"摘要: {quality['summary']}")

    for msg in quality['messages']:
        print(f"[{msg['type']}] {msg['message']}")
```

### 质量评分标准

- **9.0-10.0**: 优秀
- **7.0-8.9**: 良好
- **5.0-6.9**: 一般
- **< 5.0**: 较差

### 扣分规则

- Error: -1.0
- Warning: -0.5
- Convention: -0.1
- Refactor: -0.2

## 在 Agent 中使用

### 集成到 Developer Agent

```python
from src.agents import DeveloperAgent
from src.tools import CodeExecutor, CodeAnalyzer, Linter

# 生成代码
developer = DeveloperAgent()
response = await developer.process("实现快速排序", context)

# 分析代码
analyzer = CodeAnalyzer()
analysis = await analyzer.execute(response.content)

# 检查质量
linter = Linter()
quality = await linter.execute(response.content)

# 执行测试
executor = CodeExecutor()
test_result = await executor.execute_with_tests(
    response.content,
    test_code
)

# 根据结果决定是否需要改进
if quality.output["score"] < 7.0 or not test_result.success:
    # 触发改进流程
    pass
```

## 安装依赖

```bash
# 基础依赖
pip install -r requirements.txt

# Linter 依赖
pip install pylint

# Docker 模式（可选）
# 确保已安装 Docker
docker pull python:3.11-slim
```

## 注意事项

1. **安全性**: 生产环境建议使用 Docker 模式
2. **超时设置**: 根据代码复杂度调整 timeout
3. **资源限制**: Docker 模式已设置内存和 CPU 限制
4. **错误处理**: 始终检查 result.success
