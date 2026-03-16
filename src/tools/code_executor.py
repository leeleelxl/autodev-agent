"""
代码执行工具 - Docker 沙箱
"""

import asyncio
import tempfile
import os
from typing import Dict, Any, Optional
from pathlib import Path
from .base_tool import BaseTool, ToolResult


class CodeExecutor(BaseTool):
    """代码执行器 - 在隔离的 Docker 环境中执行代码"""

    def __init__(self, use_docker: bool = False):
        super().__init__(
            name="code_executor",
            description="在隔离环境中执行代码"
        )
        self.use_docker = use_docker

    async def execute(self, code: str, language: str = "python", timeout: int = 30) -> ToolResult:
        """
        执行代码

        Args:
            code: 要执行的代码
            language: 编程语言
            timeout: 超时时间（秒）

        Returns:
            执行结果
        """
        if language == "python":
            return await self._execute_python(code, timeout)
        else:
            return ToolResult(
                success=False,
                output="",
                error=f"不支持的语言: {language}"
            )

    async def _execute_python(self, code: str, timeout: int) -> ToolResult:
        """执行 Python 代码"""
        if self.use_docker:
            return await self._execute_in_docker(code, timeout)
        else:
            return await self._execute_local(code, timeout)

    async def _execute_local(self, code: str, timeout: int) -> ToolResult:
        """
        在本地执行代码（使用 subprocess）

        注意：这不是完全隔离的，仅用于开发测试
        """
        # 创建临时文件
        with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as f:
            f.write(code)
            temp_file = f.name

        try:
            # 执行代码
            process = await asyncio.create_subprocess_exec(
                'python3', temp_file,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )

            try:
                stdout, stderr = await asyncio.wait_for(
                    process.communicate(),
                    timeout=timeout
                )

                return ToolResult(
                    success=process.returncode == 0,
                    output=stdout.decode('utf-8'),
                    error=stderr.decode('utf-8')
                )

            except asyncio.TimeoutError:
                process.kill()
                return ToolResult(
                    success=False,
                    output="",
                    error=f"执行超时（{timeout}秒）"
                )

        finally:
            # 清理临时文件
            if os.path.exists(temp_file):
                os.remove(temp_file)

    async def _execute_in_docker(self, code: str, timeout: int) -> ToolResult:
        """
        在 Docker 容器中执行代码

        使用 python:3.11-slim 镜像
        """
        # 创建临时目录
        with tempfile.TemporaryDirectory() as tmpdir:
            # 写入代码文件
            code_file = Path(tmpdir) / "script.py"
            code_file.write_text(code)

            # 构建 docker 命令
            docker_cmd = [
                'docker', 'run',
                '--rm',
                '--network', 'none',  # 禁用网络
                '--memory', '256m',   # 限制内存
                '--cpus', '1',        # 限制 CPU
                '-v', f'{tmpdir}:/workspace',
                '-w', '/workspace',
                'python:3.11-slim',
                'python', 'script.py'
            ]

            try:
                process = await asyncio.create_subprocess_exec(
                    *docker_cmd,
                    stdout=asyncio.subprocess.PIPE,
                    stderr=asyncio.subprocess.PIPE
                )

                try:
                    stdout, stderr = await asyncio.wait_for(
                        process.communicate(),
                        timeout=timeout
                    )

                    return ToolResult(
                        success=process.returncode == 0,
                        output=stdout.decode('utf-8'),
                        error=stderr.decode('utf-8')
                    )

                except asyncio.TimeoutError:
                    process.kill()
                    return ToolResult(
                        success=False,
                        output="",
                        error=f"执行超时（{timeout}秒）"
                    )

            except Exception as e:
                return ToolResult(
                    success=False,
                    output="",
                    error=f"Docker 执行失败: {str(e)}"
                )

    async def execute_with_tests(self, code: str, test_code: str, timeout: int = 30) -> ToolResult:
        """
        执行代码并运行测试

        Args:
            code: 主代码
            test_code: 测试代码
            timeout: 超时时间

        Returns:
            测试结果
        """
        # 合并代码和测试
        full_code = f"{code}\n\n{test_code}"

        return await self.execute(full_code, language="python", timeout=timeout)
