# GPT Engineer 完整技术深度解析

> 基于源码分析的完整技术文档，帮助你彻底理解 GPT Engineer 的设计和实现

---

## 目录

1. [项目概述](#1-项目概述)
2. [核心架构](#2-核心架构)
3. [关键组件详解](#3-关键组件详解)
4. [工作流程](#4-工作流程)
5. [Preprompts 系统](#5-preprompts-系统)
6. [代码生成机制](#6-代码生成机制)
7. [Diff 系统](#7-diff-系统)
8. [Memory 系统](#8-memory-系统)
9. [与 AutoDev 的对比](#9-与-autodev-的对比)
10. [总结](#10-总结)

---

## 1. 项目概述

### 1.1 基本信息

**项目名称**: GPT Engineer  
**GitHub**: https://github.com/gpt-engineer-org/gpt-engineer  
**Stars**: 50k+  
**语言**: Python  
**代码量**: ~2000 行核心代码（47 个 Python 文件）  
**发布时间**: 2023 年  

### 1.2 核心理念

**"Specify what you want it to build, the AI asks for clarification, and then builds it."**

GPT Engineer 的设计哲学：
- **简单直接**：最小化复杂度
- **用户可控**：每一步都可以确认
- **快速迭代**：适合探索性开发
- **交互式**：AI 和用户对话式协作

---

## 2. 核心架构

### 2.1 整体架构图

```
GPT Engineer 架构
├── CLI (命令行入口)
│   └── main.py
├── AI (LLM 接口层)
│   ├── 支持 OpenAI
│   ├── 支持 Anthropic (Claude)
│   └── 支持 Azure OpenAI
├── BaseAgent (抽象基类)
│   ├── init() - 初始化代码
│   └── improve() - 改进代码
├── SimpleAgent (具体实现)
│   └── 执行预定义的 Steps
├── Steps (步骤函数)
│   ├── setup_sys_prompt
│   ├── gen_code
│   ├── gen_entrypoint
│   ├── execute_entrypoint
│   └── improve
├── PrepromptsHolder (提示词管理)
│   └── 加载 preprompts/ 目录
├── Memory (存储系统)
│   └── DiskMemory (文件系统)
└── Tools
    ├── chat_to_files (解析代码)
    ├── diff (处理差异)
    └── git (版本控制)
```

### 2.2 目录结构

```
gpt-engineer/
├── gpt_engineer/
│   ├── core/                    # 核心功能
│   │   ├── ai.py               # AI 接口
│   │   ├── base_agent.py       # Agent 基类
│   │   ├── chat_to_files.py    # 代码解析
│   │   ├── diff.py             # Diff 处理
│   │   ├── files_dict.py       # 文件字典
│   │   ├── git.py              # Git 集成
│   │   └── default/            # 默认实现
│   │       ├── simple_agent.py # 简单 Agent
│   │       └── steps.py        # 步骤函数
│   ├── preprompts/             # 提示词模板
│   │   ├── generate            # 生成代码提示
│   │   ├── improve             # 改进代码提示
│   │   ├── clarify             # 澄清需求提示
│   │   ├── philosophy          # 编程哲学
│   │   └── file_format         # 文件格式
│   ├── applications/           # 应用层
│   │   └── cli/               # 命令行工具
│   └── tools/                  # 工具函数
└── README.md
```

---

## 3. 关键组件详解

### 3.1 AI 类 (core/ai.py)

**职责**: 封装 LLM 调用，提供统一接口

**核心代码**:
```python
class AI:
    def __init__(self, 
                 model_name="gpt-4",
                 temperature=0.1,
                 streaming=True):
        self.model_name = model_name
        self.temperature = temperature
        
        # 支持多种 LLM
        if "gpt" in model_name:
            self.llm = ChatOpenAI(...)
        elif "claude" in model_name:
            self.llm = ChatAnthropic(...)
        elif "azure" in model_name:
            self.llm = AzureChatOpenAI(...)
    
    def start(self, system: str, user: str, step_name: str):
        """开始对话"""
        messages = [
            SystemMessage(content=system),
            HumanMessage(content=user)
        ]
        response = self.backoff_inference(messages)
        messages.append(response)
        return messages
    
    def next(self, messages, prompt, step_name):
        """继续对话"""
        if prompt:
            messages.append(HumanMessage(content=prompt))
        response = self.backoff_inference(messages)
        messages.append(response)
        return messages
    
    @backoff.on_exception(backoff.expo, openai.RateLimitError)
    def backoff_inference(self, messages):
        """带重试的推理"""
        return self.llm(messages)
```

**关键特性**:
- **多 LLM 支持**: OpenAI, Anthropic, Azure
- **重试机制**: 使用 backoff 处理 rate limit
- **流式输出**: 支持实时显示生成过程
- **Token 统计**: 记录使用量

---

### 3.2 BaseAgent 类 (core/base_agent.py)

**职责**: 定义 Agent 接口

**核心代码**:
```python
class BaseAgent(ABC):
    """Agent 抽象基类"""
    
    @abstractmethod
    def init(self, prompt: Prompt) -> FilesDict:
        """初始化代码生成"""
        pass
    
    @abstractmethod
    def improve(self, files_dict: FilesDict, prompt: Prompt) -> FilesDict:
        """改进现有代码"""
        pass
```

**设计理念**:
- **简单接口**: 只有 2 个方法
- **职责单一**: init 生成，improve 改进
- **易于扩展**: 可以实现不同的 Agent

---

### 3.3 SimpleAgent 类 (core/default/simple_agent.py)

**职责**: BaseAgent 的具体实现

**核心代码**:
```python
class SimpleAgent(BaseAgent):
    def __init__(self, memory, execution_env, ai, preprompts_holder):
        self.memory = memory
        self.execution_env = execution_env
        self.ai = ai
        self.preprompts_holder = preprompts_holder
    
    def init(self, prompt: Prompt) -> FilesDict:
        """初始化：生成代码"""
        # Step 1: 生成代码
        files_dict = gen_code(
            self.ai, 
            prompt, 
            self.memory, 
            self.preprompts_holder
        )
        
        # Step 2: 生成入口文件
        entrypoint = gen_entrypoint(
            self.ai, 
            prompt, 
            files_dict, 
            self.memory, 
            self.preprompts_holder
        )
        
        # 合并文件
        combined_dict = {**files_dict, **entrypoint}
        return FilesDict(combined_dict)
    
    def improve(self, files_dict, prompt) -> FilesDict:
        """改进：根据用户反馈修改代码"""
        files_dict = improve_fn(
            self.ai, 
            prompt, 
            files_dict, 
            self.memory, 
            self.preprompts_holder
        )
        return files_dict
```

**工作流程**:
1. `init()`: 生成初始代码
2. `improve()`: 迭代改进代码

---

## 4. 工作流程

### 4.1 完整流程图

```
用户输入 prompt
    ↓
[可选] Clarify 澄清需求
    ↓
Step 1: setup_sys_prompt()
    设置系统提示词
    ↓
Step 2: gen_code()
    生成代码文件
    ↓
Step 3: gen_entrypoint()
    生成入口文件
    ↓
Step 4: execute_entrypoint()
    执行代码
    ↓
[用户查看结果]
    ↓
[用户提供反馈]
    ↓
Step 5: improve()
    根据反馈改进代码
    ↓
重复 Step 4-5 直到满意
```

### 4.2 详细步骤

#### Step 1: setup_sys_prompt

**代码**:
```python
def setup_sys_prompt(preprompts):
    return (
        preprompts["roadmap"] +
        preprompts["generate"].replace("FILE_FORMAT", preprompts["file_format"]) +
        "\nUseful to know:\n" +
        preprompts["philosophy"]
    )
```

**作用**: 组合多个 preprompt，形成完整的系统提示词

**组成部分**:
- `roadmap`: 思考步骤指导
- `generate`: 代码生成指令
- `file_format`: 文件格式规范
- `philosophy`: 编程哲学

#### Step 2: gen_code

**代码**:
```python
def gen_code(ai, prompt, memory, preprompts_holder):
    preprompts = preprompts_holder.get_preprompts()
    
    # 构建系统提示
    system_prompt = setup_sys_prompt(preprompts)
    
    # 调用 LLM
    messages = ai.start(
        system=system_prompt,
        user=prompt.to_langchain_content(),
        step_name="gen_code"
    )
    
    # 提取代码
    chat = messages[-1].content.strip()
    files_dict = chat_to_files_dict(chat)
    
    # 记录日志
    memory.log("code_gen.txt", "\n\n".join(x.pretty_repr() for x in messages))
    
    return files_dict
```

**流程**:
1. 加载 preprompts
2. 构建系统提示
3. 调用 LLM 生成代码
4. 解析 LLM 输出，提取文件
5. 保存日志

#### Step 3: gen_entrypoint

**作用**: 生成项目的入口文件（如 `run.sh`）

**代码**:
```python
def gen_entrypoint(ai, prompt, files_dict, memory, preprompts_holder):
    preprompts = preprompts_holder.get_preprompts()
    
    messages = ai.start(
        system=preprompts["entrypoint"],
        user=f"Information about the codebase:\n\n{files_dict}",
        step_name="gen_entrypoint"
    )
    
    chat = messages[-1].content.strip()
    entrypoint = chat_to_files_dict(chat)
    
    return entrypoint
```

#### Step 4: execute_entrypoint

**作用**: 执行生成的代码

**代码**:
```python
def execute_entrypoint(ai, execution_env, files_dict, preprompts_holder):
    command = files_dict.get("run.sh", "")
    
    print(colored("Do you want to execute this code? (Y/n)", "red"))
    if input().lower() not in ["", "y", "yes"]:
        print("Skipping execution.")
        return
    
    # 执行命令
    execution_env.upload(files_dict)
    execution_env.execute(command)
```

**安全机制**: 需要用户确认才执行

#### Step 5: improve

**代码**:
```python
def improve_fn(ai, prompt, files_dict, memory, preprompts_holder):
    preprompts = preprompts_holder.get_preprompts()
    
    # 构建上下文
    messages = [
        SystemMessage(content=setup_sys_prompt_existing_code(preprompts)),
        HumanMessage(content=f"Current code:\n\n{files_dict}"),
        HumanMessage(content=f"User feedback:\n\n{prompt}")
    ]
    
    # 调用 LLM
    messages = ai.next(messages, None, "improve")
    
    # 解析 diff
    chat = messages[-1].content.strip()
    diffs = parse_diffs(chat)
    
    # 应用 diff
    files_dict = apply_diffs(diffs, files_dict)
    
    return files_dict
```

**关键**: 使用 **diff 格式**而不是重新生成所有代码

---

## 5. Preprompts 系统

### 5.1 什么是 Preprompts

Preprompts 是预定义的提示词模板，存储在 `gpt_engineer/preprompts/` 目录。

**作用**:
- 指导 LLM 的行为
- 定义输出格式
- 传递编程哲学

### 5.2 核心 Preprompts

#### roadmap
```
You will get instructions for code to write.
You will write a very long answer. Make sure that every detail of the architecture is, in the end, implemented as code.
```

**作用**: 告诉 LLM 要详细实现

#### generate
```
Think step by step and reason yourself to the correct decisions to make sure we get it right.
First lay out the names of the core classes, functions, methods that will be necessary, As well as a quick comment on their purpose.

FILE_FORMAT

You will start with the "entrypoint" file, then go to the ones that are imported by that file, and so on.
Please note that the code should be fully functional. No placeholders.

Follow a language and framework appropriate best practice file naming convention.
Make sure that files contain all imports, types etc.  The code should be fully functional. Make sure that code in different files are compatible with each other.
Ensure to implement all code, if you are unsure, write a plausible implementation.
Include module dependency or package manager dependency definition file.
Before you finish, double check that all parts of the architecture is present in the files.

When you are done, write finish with "this concludes a fully working implementation".
```

**关键要求**:
- 先列出核心类/函数
- 从入口文件开始
- 代码必须完整可运行
- 包含依赖文件
- 最后写 "this concludes a fully working implementation"

#### file_format
```
You will output the content of each file necessary to achieve the goal, including ALL code.
Represent files like so:

FILENAME
```
CODE
```

The following tokens must be replaced like so:
FILENAME is the lowercase combined path and file name including the file extension
CODE is the code in the file

Example representation of a file:

src/hello_world.py
```
print("Hello World")
```

Do not comment on what every file does. Please note that the code should be fully functional. No placeholders.
```

**格式规范**:
```
filename
```
code
```
```

#### philosophy
```
Almost always put different classes in different files.
Always use the programming language the user asks for.
For Python, you always create an appropriate requirements.txt file.
For NodeJS, you always create an appropriate package.json file.
Always add a comment briefly describing the purpose of the function definition.
Add comments explaining very complex bits of logic.
Always follow the best practices for the requested languages for folder/file structure and how to package the project.

Python toolbelt preferences:
- pytest
- dataclasses
```

**编程原则**:
- 不同类放不同文件
- 创建依赖文件
- 添加注释
- 遵循最佳实践

#### clarify
```
Given some instructions, determine if anything needs to be clarified, do not carry them out.
You can make reasonable assumptions, but if you are unsure, ask a single clarification question.
Otherwise state: "Nothing to clarify"
```

**作用**: 在生成代码前，先澄清需求

#### improve
```
Think step by step and reason yourself to the correct decisions to make sure we get it right.
Make changes to existing code and implement new code in the unified git diff syntax.

FILE_FORMAT

As far as compatible with the user request, start with the "entrypoint" file, then go to the ones that are imported by that file, and so on.
Please note that the code should be fully functional. No placeholders.
```

**关键**: 使用 **unified git diff 格式**

---

## 6. 代码生成机制

### 6.1 chat_to_files_dict

**作用**: 从 LLM 输出中提取文件

**代码**:
```python
def chat_to_files_dict(chat: str) -> FilesDict:
    # 正则表达式匹配文件
    regex = r"(\S+)\n\s*```[^\n]*\n(.+?)```"
    matches = re.finditer(regex, chat, re.DOTALL)
    
    files_dict = FilesDict()
    for match in matches:
        # 清理文件路径
        path = re.sub(r'[\:<>"|?*]', "", match.group(1))
        path = re.sub(r"^\[(.*)\]$", r"\1", path)
        path = re.sub(r"^`(.*)`$", r"\1", path)
        path = re.sub(r"[\]\:]$", "", path)
        
        # 提取代码内容
        content = match.group(2)
        
        # 添加到字典
        files_dict[path.strip()] = content.strip()
    
    return files_dict
```

**匹配模式**:
```
filename
```language
code
```
```

**示例**:
```
src/hello.py
```python
print("Hello World")
```
```

解析为:
```python
{
    "src/hello.py": "print(\"Hello World\")"
}
```

### 6.2 FilesDict

**作用**: 文件字典，key 是路径，value 是内容

**代码**:
```python
class FilesDict(dict):
    """文件字典，继承自 dict"""
    
    def __str__(self):
        """格式化输出"""
        return "\n\n".join(
            f"{path}\n```\n{content}\n```"
            for path, content in self.items()
        )
```

---

## 7. Diff 系统

### 7.1 为什么需要 Diff

**问题**: 改进代码时，如果重新生成所有文件：
- Token 消耗大
- 容易出错
- 丢失上下文

**解决方案**: 使用 **unified git diff 格式**

### 7.2 Diff 格式

**示例**:
```diff
src/hello.py
```diff
@@ -1,3 +1,4 @@
 def hello():
-    print("Hello")
+    print("Hello World")
+    print("Welcome!")
```
```

**解释**:
- `@@ -1,3 +1,4 @@`: 行号信息
- `-`: 删除的行
- `+`: 添加的行
- 空格: 保留的行

### 7.3 Diff 类

**代码**:
```python
class Hunk:
    """Diff 的一个块"""
    def __init__(self, start_line_pre, hunk_len_pre, 
                 start_line_post, hunk_len_post, lines):
        self.start_line_pre_edit = start_line_pre
        self.hunk_len_pre_edit = hunk_len_pre
        self.start_line_post_edit = start_line_post
        self.hunk_len_post_edit = hunk_len_post
        self.lines = lines  # [(type, content), ...]

class Diff:
    """完整的文件 diff"""
    def __init__(self, filename_pre, filename_post, hunks):
        self.filename_pre = filename_pre
        self.filename_post = filename_post
        self.hunks = hunks
    
    def is_new_file(self):
        return self.filename_pre is None
```

### 7.4 apply_diffs

**作用**: 将 diff 应用到文件

**代码**:
```python
def apply_diffs(diffs: Dict[str, Diff], files: FilesDict) -> FilesDict:
    files = FilesDict(files.copy())
    
    for diff in diffs.values():
        if diff.is_new_file():
            # 新文件：直接创建
            files[diff.filename_post] = "\n".join(
                line[1] for hunk in diff.hunks for line in hunk.lines
            )
        else:
            # 修改文件：应用 diff
            line_dict = file_to_lines_dict(files[diff.filename_pre])
            
            for hunk in diff.hunks:
                current_line = hunk.start_line_pre_edit
                for line in hunk.lines:
                    if line[0] == RETAIN:
                        current_line += 1
                    elif line[0] == ADD:
                        # 添加行
                        line_dict[current_line + 0.5] = line[1]
                    elif line[0] == REMOVE:
                        # 删除行
                        line_dict[current_line] = "<REMOVE_LINE>"
                        current_line += 1
            
            # 重建文件
            lines = [v for k, v in sorted(line_dict.items()) 
                     if v != "<REMOVE_LINE>"]
            files[diff.filename_pre] = "\n".join(lines)
    
    return files
```

---

## 8. Memory 系统

### 8.1 BaseMemory

**接口**:
```python
class BaseMemory(ABC):
    @abstractmethod
    def __getitem__(self, key: str) -> str:
        pass
    
    @abstractmethod
    def __setitem__(self, key: str, value: str):
        pass
    
    @abstractmethod
    def log(self, filename: str, content: str):
        pass
```

### 8.2 DiskMemory

**实现**: 使用文件系统存储

**代码**:
```python
class DiskMemory(BaseMemory):
    def __init__(self, path: Path):
        self.path = path
        self.path.mkdir(parents=True, exist_ok=True)
    
    def __getitem__(self, key: str) -> str:
        file_path = self.path / key
        return file_path.read_text()
    
    def __setitem__(self, key: str, value: str):
        file_path = self.path / key
        file_path.write_text(value)
    
    def log(self, filename: str, content: str):
        self[filename] = content
```

**存储位置**: `projects/<project_name>/.gpteng/memory/`

**存储内容**:
- `code_gen.txt`: 代码生成日志
- `improve.txt`: 改进日志
- `entrypoint.txt`: 入口文件日志

---

## 9. 与 AutoDev 的对比

### 9.1 架构对比

| 维度 | GPT Engineer | AutoDev |
|------|-------------|---------|
| **Agent 数量** | 1 | 5 |
| **Agent 类型** | SimpleAgent | Architect, Developer, Tester, Reviewer, Orchestrator |
| **工作流** | Steps（步骤式） | Phases（阶段式） |
| **用户参与** | 高（需要确认） | 低（全自动） |
| **代码量** | ~2000 行 | ~5000 行 |

### 9.2 设计理念对比

**GPT Engineer**:
- **简单优先**: 最小化复杂度
- **用户驱动**: 用户控制每一步
- **快速迭代**: 适合探索

**AutoDev**:
- **质量优先**: 自动测试和审查
- **自动化**: 无需人工介入
- **完整性**: 生成完整项目

### 9.3 适用场景对比

**GPT Engineer 适合**:
- 需求不明确，需要探索
- 快速原型开发
- 用户希望参与过程
- 简单项目

**AutoDev 适合**:
- 需求明确
- 需要质量保证
- 批量生成代码
- 复杂项目

### 9.4 优劣势对比

**GPT Engineer 优势**:
- ✅ 简单易懂
- ✅ 用户可控
- ✅ 快速迭代
- ✅ 成熟稳定

**GPT Engineer 劣势**:
- ❌ 无质量保证
- ❌ 需要人工介入
- ❌ 无经验学习

**AutoDev 优势**:
- ✅ 质量保证完善
- ✅ 全自动流程
- ✅ 经验学习
- ✅ 架构更好

**AutoDev 劣势**:
- ❌ 复杂度高
- ❌ 速度慢
- ❌ 用户可控性低

---

## 10. 总结

### 10.1 GPT Engineer 的核心价值

1. **简单性**: 代码少，易于理解和修改
2. **可控性**: 用户可以控制每一步
3. **成熟性**: 经过 2 年的迭代，稳定可靠
4. **社区**: 50k+ stars，活跃的社区

### 10.2 关键设计决策

1. **Single Agent**: 简化架构，降低复杂度
2. **Steps 模式**: 清晰的步骤，易于理解
3. **Preprompts**: 通过提示词控制行为
4. **Diff 格式**: 高效的代码改进
5. **用户确认**: 安全机制，避免误操作

### 10.3 学到的经验

1. **简单 > 复杂**: 不要过度设计
2. **用户参与**: 交互式开发更可控
3. **Preprompts 重要**: 好的提示词是关键
4. **Diff > 重新生成**: 更高效
5. **社区驱动**: 开源项目需要社区支持

### 10.4 与 AutoDev 的关系

**不是竞争，是互补**:
- GPT Engineer: 交互式开发，探索阶段
- AutoDev: 自动化质量保证，生产阶段

**可以结合使用**:
1. 用 GPT Engineer 快速探索
2. 用 AutoDev 生成生产代码

---

## 附录

### A. 完整的工作流示例

```bash
# 1. 创建项目目录
mkdir my-project
cd my-project

# 2. 创建 prompt 文件
echo "Create a simple TODO app with Flask" > prompt

# 3. 运行 GPT Engineer
gpte .

# 输出：
# [Clarify] Do you want to use SQLite or PostgreSQL?
# > SQLite
# 
# [Generate] Generating code...
# ✓ Generated 5 files
# 
# [Execute] Do you want to execute? (Y/n)
# > Y
# 
# [Running] python app.py
# * Running on http://127.0.0.1:5000
# 
# [Improve] Any feedback? (or press Enter to finish)
# > Add user authentication
# 
# [Improve] Applying changes...
# ✓ Updated 3 files
# 
# [Execute] Do you want to execute? (Y/n)
# > Y
```

### B. 参考资料

- [GPT Engineer GitHub](https://github.com/gpt-engineer-org/gpt-engineer)
- [GPT Engineer 文档](https://gpt-engineer.readthedocs.io/)
- [AutoDev GitHub](https://github.com/leeleelxl/autodev-agent)

---

**文档版本**: 1.0  
**最后更新**: 2026-03-17  
**作者**: 基于 GPT Engineer 源码分析
