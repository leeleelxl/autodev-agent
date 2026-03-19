"""
Developer Agent - 开发者

基于 ReAct + CoT 模式，负责代码实现。
可通过 Tool Calling 自主调用代码分析器和 Linter 检查代码质量。
"""

from typing import Dict, Any, Optional, List
import json
import re
from .base_agent import BaseReActAgent, AgentConfig, AgentResponse


class DeveloperAgent(BaseReActAgent):
    """开发者 Agent - ReAct 模式"""

    def __init__(self):
        config = AgentConfig(
            name="developer",
            role="软件开发者，负责代码实现"
        )
        super().__init__(config)

    def _build_system_prompt(self) -> str:
        return """你是一位资深软件开发工程师，擅长编写高质量、可维护的代码。

你的任务是：
1. 理解设计文档和需求
2. 编写清晰、简洁的代码
3. 遵循最佳实践和编码规范
4. 添加必要的注释和文档字符串
5. 考虑边界情况和错误处理

你可以使用工具来分析代码结构、检查代码质量、执行代码验证。
当你不确定代码是否正确时，主动使用工具进行验证。

**重要：生成完整可运行的项目**
- 必须生成所有必要的文件（主文件、模型、工具类、配置等）
- 确保所有 import 的模块都有对应的文件
- 代码必须可以直接运行，不能有缺失的依赖

**输出格式：使用 Markdown 代码块**

对于每个文件，使用以下格式：

```python
# filename: app.py
# description: 主应用文件

代码内容...
```

```python
# filename: models.py
# description: 数据模型

代码内容...
```

**不要使用 JSON 格式！直接输出 Markdown 代码块即可。**"""

    def _build_user_prompt(self, task: str, context: Dict[str, Any]) -> str:
        prompt = f"开发任务：\n{task}\n\n"

        if context.get("design"):
            prompt += f"架构设计：\n{json.dumps(context['design'], ensure_ascii=False, indent=2)}\n\n"

        if context.get("existing_code"):
            prompt += f"现有代码：\n{context['existing_code']}\n\n"

        if context.get("requirements"):
            prompt += f"具体要求：\n{context['requirements']}\n\n"

        if context.get("review_issues"):
            prompt += f"需要修复的问题：\n{json.dumps(context['review_issues'], ensure_ascii=False, indent=2)}\n\n"

        prompt += "请实现代码，使用 Markdown 代码块格式输出。"
        return prompt

    def _parse_response(self, response: str) -> Dict[str, Any]:
        code_files = self._parse_code(response)
        return {
            "actions": [{"type": "code_generated", "files": code_files}],
            "metadata": {"files": code_files}
        }

    def _parse_code(self, response: str) -> List[Dict[str, str]]:
        """解析代码文件 - 使用 Markdown 代码块"""
        files = []

        pattern = r'```python\s*\n(.*?)\n```'
        code_blocks = re.findall(pattern, response, re.DOTALL)

        for code_block in code_blocks:
            filename = None
            description = ""
            code_lines = []

            for line in code_block.split('\n'):
                if line.strip().startswith('# filename:'):
                    filename = line.split(':', 1)[1].strip()
                elif line.strip().startswith('# description:'):
                    description = line.split(':', 1)[1].strip()
                else:
                    code_lines.append(line)

            if not filename and code_lines:
                first_line = code_lines[0].strip()
                if first_line.startswith('#') and '.py' in first_line:
                    filename = first_line.replace('#', '').strip()

            if not filename:
                filename = f"file_{len(files) + 1}.py"

            code_content = '\n'.join(code_lines)

            if code_content.strip():
                files.append({
                    "path": filename,
                    "content": code_content,
                    "description": description
                })

        if files:
            self._validate_completeness(files)

        return files

    def _validate_completeness(self, files: List[Dict[str, str]]):
        """验证代码完整性"""
        available_modules = set()
        for file in files:
            path = file.get("path", "")
            if path.endswith(".py"):
                module_name = path.replace(".py", "").replace("/", ".")
                available_modules.add(module_name)

        missing_modules = set()
        for file in files:
            content = file.get("content", "")
            imports = re.findall(r'(?:from|import)\s+([a-zA-Z_][a-zA-Z0-9_]*)', content)

            for imp in imports:
                if imp in ['os', 'sys', 're', 'json', 'time', 'datetime', 'typing',
                          'flask', 'sqlite3', 'jwt', 'hashlib', 'werkzeug', 'marshmallow']:
                    continue
                if imp not in available_modules and imp not in [m.split('.')[0] for m in available_modules]:
                    missing_modules.add(imp)

        if missing_modules:
            print(f"  ⚠️  缺少依赖模块: {', '.join(missing_modules)}")
