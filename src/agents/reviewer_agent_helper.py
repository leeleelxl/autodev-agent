    def _check_completeness(self, code_files: List[Dict[str, str]]) -> set:
        """检查代码完整性，返回缺失的模块"""
        import re

        # 收集所有文件路径
        available_modules = set()
        for file in code_files:
            path = file.get("path", "")
            if path.endswith(".py"):
                module_name = path.replace(".py", "").replace("/", ".")
                available_modules.add(module_name)
                # 也添加不带路径的模块名
                if "/" in path:
                    simple_name = path.split("/")[-1].replace(".py", "")
                    available_modules.add(simple_name)

        # 检查每个文件的 import
        missing_modules = set()
        standard_libs = {
            'os', 'sys', 're', 'json', 'time', 'datetime', 'typing', 'pathlib',
            'collections', 'itertools', 'functools', 'asyncio', 'unittest',
            'sqlite3', 'hashlib', 'getpass', 'jwt'
        }
        third_party_libs = {
            'flask', 'werkzeug', 'marshmallow', 'sqlalchemy', 'pydantic',
            'requests', 'numpy', 'pandas', 'pytest', 'flask_pyjwt'
        }

        for file in code_files:
            content = file.get("content", "")

            # 提取 from xxx import 和 import xxx
            from_imports = re.findall(r'from\s+([a-zA-Z_][a-zA-Z0-9_]*)', content)
            direct_imports = re.findall(r'^import\s+([a-zA-Z_][a-zA-Z0-9_]*)', content, re.MULTILINE)

            all_imports = set(from_imports + direct_imports)

            for imp in all_imports:
                # 跳过标准库和第三方库
                if imp in standard_libs or imp in third_party_libs:
                    continue

                # 检查是否在生成的文件中
                if imp not in available_modules:
                    missing_modules.add(imp)

        return missing_modules
