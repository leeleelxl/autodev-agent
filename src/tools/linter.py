"""
Linter 工具 - 代码质量检查
"""

import asyncio
import tempfile
import os
from pathlib import Path
from typing import Dict, Any, List
from .base_tool import BaseTool, ToolResult


class Linter(BaseTool):
    """代码质量检查工具 - 使用 pylint"""

    def __init__(self):
        super().__init__(
            name="linter",
            description="使用 pylint 检查代码质量"
        )

    async def execute(self, code: str, language: str = "python") -> ToolResult:
        """
        检查代码质量

        Args:
            code: 要检查的代码
            language: 编程语言

        Returns:
            检查结果
        """
        if language != "python":
            return ToolResult(
                success=False,
                output={},
                error=f"暂不支持 {language} 语言检查"
            )

        # 创建临时文件
        with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as f:
            f.write(code)
            temp_file = f.name

        try:
            # 运行 pylint
            process = await asyncio.create_subprocess_exec(
                'pylint',
                '--output-format=json',
                '--disable=C0114,C0115,C0116',  # 禁用文档字符串检查
                temp_file,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )

            stdout, stderr = await process.communicate()

            # 解析结果
            import json
            try:
                messages = json.loads(stdout.decode('utf-8'))
            except:
                messages = []

            # 计算分数
            score = self._calculate_score(messages)

            result = {
                "score": score,
                "messages": messages,
                "summary": self._generate_summary(messages, score)
            }

            return ToolResult(
                success=True,
                output=result,
                error=""
            )

        except FileNotFoundError:
            return ToolResult(
                success=False,
                output={},
                error="pylint 未安装，请运行: pip install pylint"
            )
        except Exception as e:
            return ToolResult(
                success=False,
                output={},
                error=f"检查失败: {str(e)}"
            )
        finally:
            # 清理临时文件
            if os.path.exists(temp_file):
                os.remove(temp_file)

    def _calculate_score(self, messages: List[Dict]) -> float:
        """计算代码质量分数"""
        # 基础分数
        score = 10.0

        # 根据问题严重程度扣分
        for msg in messages:
            msg_type = msg.get('type', '')
            if msg_type == 'error':
                score -= 1.0
            elif msg_type == 'warning':
                score -= 0.5
            elif msg_type == 'convention':
                score -= 0.1
            elif msg_type == 'refactor':
                score -= 0.2

        return max(0.0, score)

    def _generate_summary(self, messages: List[Dict], score: float) -> str:
        """生成检查摘要"""
        errors = len([m for m in messages if m.get('type') == 'error'])
        warnings = len([m for m in messages if m.get('type') == 'warning'])
        conventions = len([m for m in messages if m.get('type') == 'convention'])

        summary = f"代码质量分数: {score:.2f}/10.0。"

        if errors > 0:
            summary += f" {errors} 个错误。"
        if warnings > 0:
            summary += f" {warnings} 个警告。"
        if conventions > 0:
            summary += f" {conventions} 个规范问题。"

        if score >= 9.0:
            summary += " 代码质量优秀！"
        elif score >= 7.0:
            summary += " 代码质量良好。"
        elif score >= 5.0:
            summary += " 代码质量一般，建议改进。"
        else:
            summary += " 代码质量较差，需要重构。"

        return summary