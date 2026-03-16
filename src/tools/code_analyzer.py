"""
代码分析工具 - AST 解析和静态分析
"""

import ast
import re
from typing import Dict, Any, List, Optional
from .base_tool import BaseTool, ToolResult


class CodeAnalyzer(BaseTool):
    """代码分析器 - 使用 AST 进行代码分析"""

    def __init__(self):
        super().__init__(
            name="code_analyzer",
            description="分析代码结构和质量"
        )

    async def execute(self, code: str, language: str = "python") -> ToolResult:
        """
        分析代码

        Args:
            code: 要分析的代码
            language: 编程语言

        Returns:
            分析结果
        """
        if language != "python":
            return ToolResult(
                success=False,
                output={},
                error=f"暂不支持 {language} 语言分析"
            )

        try:
            # 解析 AST
            tree = ast.parse(code)

            # 提取信息
            functions = self._extract_functions(tree)
            classes = self._extract_classes(tree)
            imports = self._extract_imports(tree)
            complexity = self._calculate_complexity(tree)
            issues = self._detect_issues(code, tree)

            result = {
                "functions": functions,
                "classes": classes,
                "imports": imports,
                "complexity": complexity,
                "issues": issues,
                "lines_of_code": len(code.split('\n')),
                "summary": self._generate_summary(functions, classes, complexity, issues)
            }

            return ToolResult(
                success=True,
                output=result,
                error=""
            )

        except SyntaxError as e:
            return ToolResult(
                success=False,
                output={},
                error=f"语法错误: {str(e)}"
            )
        except Exception as e:
            return ToolResult(
                success=False,
                output={},
                error=f"分析失败: {str(e)}"
            )

    def _extract_functions(self, tree: ast.AST) -> List[Dict[str, Any]]:
        """提取函数信息"""
        functions = []

        for node in ast.walk(tree):
            if isinstance(node, ast.FunctionDef):
                functions.append({
                    "name": node.name,
                    "args": [arg.arg for arg in node.args.args],
                    "lineno": node.lineno,
                    "is_async": isinstance(node, ast.AsyncFunctionDef),
                    "decorators": [self._get_decorator_name(d) for d in node.decorator_list],
                    "docstring": ast.get_docstring(node)
                })

        return functions

    def _extract_classes(self, tree: ast.AST) -> List[Dict[str, Any]]:
        """提取类信息"""
        classes = []

        for node in ast.walk(tree):
            if isinstance(node, ast.ClassDef):
                methods = []
                for item in node.body:
                    if isinstance(item, ast.FunctionDef):
                        methods.append(item.name)

                classes.append({
                    "name": node.name,
                    "bases": [self._get_name(base) for base in node.bases],
                    "methods": methods,
                    "lineno": node.lineno,
                    "docstring": ast.get_docstring(node)
                })

        return classes

    def _extract_imports(self, tree: ast.AST) -> List[str]:
        """提取导入信息"""
        imports = []

        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                for alias in node.names:
                    imports.append(alias.name)
            elif isinstance(node, ast.ImportFrom):
                module = node.module or ""
                for alias in node.names:
                    imports.append(f"{module}.{alias.name}")

        return imports

    def _calculate_complexity(self, tree: ast.AST) -> Dict[str, int]:
        """计算代码复杂度（简化版圈复杂度）"""
        complexity = 0

        for node in ast.walk(tree):
            # 每个分支点增加复杂度
            if isinstance(node, (ast.If, ast.While, ast.For, ast.ExceptHandler)):
                complexity += 1
            elif isinstance(node, ast.BoolOp):
                complexity += len(node.values) - 1

        return {
            "cyclomatic_complexity": complexity,
            "rating": self._complexity_rating(complexity)
        }

    def _complexity_rating(self, complexity: int) -> str:
        """复杂度评级"""
        if complexity <= 5:
            return "简单"
        elif complexity <= 10:
            return "中等"
        elif complexity <= 20:
            return "复杂"
        else:
            return "非常复杂"

    def _detect_issues(self, code: str, tree: ast.AST) -> List[Dict[str, Any]]:
        """检测潜在问题"""
        issues = []

        # 检查长函数
        for node in ast.walk(tree):
            if isinstance(node, ast.FunctionDef):
                func_lines = node.end_lineno - node.lineno if hasattr(node, 'end_lineno') else 0
                if func_lines > 50:
                    issues.append({
                        "severity": "medium",
                        "type": "长函数",
                        "location": f"line {node.lineno}",
                        "message": f"函数 {node.name} 有 {func_lines} 行，建议拆分"
                    })

        # 检查未使用的导入（简单检查）
        imports = self._extract_imports(tree)
        for imp in imports:
            module_name = imp.split('.')[0]
            if module_name not in code:
                issues.append({
                    "severity": "low",
                    "type": "未使用的导入",
                    "location": "imports",
                    "message": f"导入 {imp} 可能未使用"
                })

        # 检查空的异常处理
        for node in ast.walk(tree):
            if isinstance(node, ast.ExceptHandler):
                if len(node.body) == 1 and isinstance(node.body[0], ast.Pass):
                    issues.append({
                        "severity": "high",
                        "type": "空异常处理",
                        "location": f"line {node.lineno}",
                        "message": "空的 except 块会隐藏错误"
                    })

        return issues

    def _generate_summary(self, functions: List, classes: List, complexity: Dict, issues: List) -> str:
        """生成分析摘要"""
        high_issues = len([i for i in issues if i["severity"] == "high"])
        medium_issues = len([i for i in issues if i["severity"] == "medium"])

        summary = f"代码包含 {len(functions)} 个函数，{len(classes)} 个类。"
        summary += f"圈复杂度: {complexity['cyclomatic_complexity']} ({complexity['rating']})。"

        if high_issues > 0:
            summary += f" 发现 {high_issues} 个高优先级问题。"
        if medium_issues > 0:
            summary += f" 发现 {medium_issues} 个中优先级问题。"

        return summary

    def _get_decorator_name(self, node: ast.AST) -> str:
        """获取装饰器名称"""
        if isinstance(node, ast.Name):
            return node.id
        elif isinstance(node, ast.Call):
            return self._get_name(node.func)
        return "unknown"

    def _get_name(self, node: ast.AST) -> str:
        """获取节点名称"""
        if isinstance(node, ast.Name):
            return node.id
        elif isinstance(node, ast.Attribute):
            return f"{self._get_name(node.value)}.{node.attr}"
        return "unknown"
