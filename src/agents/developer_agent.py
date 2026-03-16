"""
Developer Agent - 开发者

负责代码实现
"""

from typing import Dict, Any, Optional, List
import json
from .base_agent import BaseAgent, AgentConfig, AgentResponse, Message


class DeveloperAgent(BaseAgent):
    """开发者 Agent"""

    def __init__(self):
        config = AgentConfig(
            name="developer",
            role="软件开发者，负责代码实现"
        )
        super().__init__(config)
        self.code_analyzer = None
        self.linter = None

    def set_tools(self, code_analyzer=None, linter=None):
        """设置工具"""
        self.code_analyzer = code_analyzer
        self.linter = linter

    async def process(self, task: str, context: Optional[Dict[str, Any]] = None) -> AgentResponse:
        """
        处理代码开发任务

        根据设计文档生成代码
        """
        context = context or {}

        # 构建提示词
        system_prompt = self._build_system_prompt()
        user_prompt = self._build_user_prompt(task, context)

        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt}
        ]

        response_content = await self._call_llm(messages)

        # 解析代码
        code_files = self._parse_code(response_content)

        # 如果有工具，进行代码分析和质量检查
        analysis_results = []
        quality_results = []

        for file in code_files:
            code = file.get("content", "")

            # 代码分析
            if self.code_analyzer:
                analysis = await self.code_analyzer.execute(code)
                if analysis.success:
                    analysis_results.append({
                        "file": file.get("path"),
                        "analysis": analysis.output
                    })

            # 质量检查
            if self.linter:
                quality = await self.linter.execute(code)
                if quality.success:
                    quality_results.append({
                        "file": file.get("path"),
                        "quality": quality.output
                    })

        # 保存到记忆
        self.add_message(Message(
            role="assistant",
            content=response_content,
            metadata={
                "task": task,
                "phase": "development",
                "analysis": analysis_results,
                "quality": quality_results
            }
        ))

        return AgentResponse(
            content=response_content,
            actions=[
                {"type": "code_generated", "files": code_files}
            ],
            metadata={
                "phase": "development",
                "files": code_files,
                "analysis": analysis_results,
                "quality": quality_results
            }
        )

    def _build_system_prompt(self) -> str:
        """构建系统提示词"""
        return """你是一位资深软件开发工程师，擅长编写高质量、可维护的代码。

你的任务是：
1. 理解设计文档和需求
2. 编写清晰、简洁的代码
3. 遵循最佳实践和编码规范
4. 添加必要的注释和文档字符串
5. 考虑边界情况和错误处理

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
        """构建用户提示词"""
        prompt = f"开发任务：\n{task}\n\n"

        if context.get("design"):
            prompt += f"架构设计：\n{json.dumps(context['design'], ensure_ascii=False, indent=2)}\n\n"

        if context.get("existing_code"):
            prompt += f"现有代码：\n{context['existing_code']}\n\n"

        if context.get("requirements"):
            prompt += f"具体要求：\n{context['requirements']}\n\n"

        if context.get("review_issues"):
            prompt += f"需要修复的问题：\n{json.dumps(context['review_issues'], ensure_ascii=False, indent=2)}\n\n"

        prompt += "请实现代码并输出 JSON 格式的文件列表。"

        return prompt

    def _parse_code(self, response: str) -> List[Dict[str, str]]:
        """解析代码文件 - 使用 Markdown 代码块而不是 JSON"""
        import re

        files = []

        # 提取所有 Python 代码块
        pattern = r'```python\s*\n(.*?)\n```'
        code_blocks = re.findall(pattern, response, re.DOTALL)

        for code_block in code_blocks:
            # 从代码块中提取文件名和描述
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

            # 如果没有指定文件名，尝试从第一行注释提取
            if not filename and code_lines:
                first_line = code_lines[0].strip()
                if first_line.startswith('#') and '.py' in first_line:
                    filename = first_line.replace('#', '').strip()

            # 如果还是没有文件名，使用默认名
            if not filename:
                filename = f"file_{len(files) + 1}.py"

            code_content = '\n'.join(code_lines)

            if code_content.strip():
                files.append({
                    "path": filename,
                    "content": code_content,
                    "description": description
                })

        # 验证完整性
        if files:
            self._validate_completeness(files)

        return files

    def _validate_completeness(self, files: List[Dict[str, str]]):
        """验证代码完整性"""
        import re

        # 收集所有文件路径（不含扩展名）
        available_modules = set()
        for file in files:
            path = file.get("path", "")
            if path.endswith(".py"):
                module_name = path.replace(".py", "").replace("/", ".")
                available_modules.add(module_name)

        # 检查每个文件的 import
        missing_modules = set()
        for file in files:
            content = file.get("content", "")

            # 提取 from xxx import 和 import xxx
            imports = re.findall(r'(?:from|import)\s+([a-zA-Z_][a-zA-Z0-9_]*)', content)

            for imp in imports:
                # 跳过标准库和第三方库
                if imp in ['os', 'sys', 're', 'json', 'time', 'datetime', 'typing',
                          'flask', 'sqlite3', 'jwt', 'hashlib', 'werkzeug', 'marshmallow']:
                    continue

                # 检查是否在生成的文件中
                if imp not in available_modules and imp not in [m.split('.')[0] for m in available_modules]:
                    missing_modules.add(imp)

        if missing_modules:
            print(f"⚠️  警告：缺少依赖模块: {', '.join(missing_modules)}")
            print(f"   已生成的模块: {', '.join(available_modules)}")
