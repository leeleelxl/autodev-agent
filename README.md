# AutoDev - 自主软件开发 Agent 系统

多 agent 协作的代码生成系统，用于自动化软件开发流程。

## 项目状态

🚧 **开发中** - 基础架构搭建阶段

## 快速开始

### 重要：对话开始时
每次打开此项目时，Claude 会自动读取 `.claude/memory/` 中的所有记忆文件，恢复项目上下文。

### 记忆管理
- 查看记忆索引：`.claude/memory/MEMORY.md`
- 同步记忆：使用 `/sync-memory` 命令
- 工作指南：查看 `CLAUDE.md`

## 项目结构

```
agent_project/
├── .claude/
│   ├── memory/              # 记忆系统
│   │   ├── MEMORY.md       # 记忆索引
│   │   ├── project_setup.md
│   │   ├── user_preferences.md
│   │   └── memory_workflow.md
│   └── skills/
│       └── sync-memory/    # 记忆同步工具
├── CLAUDE.md               # Claude 工作指南
└── README.md               # 本文件
```

## 核心特性

- 🤖 多 agent 协作（Architect, Developer, Tester, Reviewer, Orchestrator）
- 🧠 三层记忆系统（短期/长期/经验学习）
- 🔄 自我反思和迭代改进
- 📊 与 baseline 对比（GPT Engineer, SWE-bench）

## 技术栈

- LangChain/LangGraph - Agent 编排
- 多 LLM 支持 - Claude / Kimi / Qwen（可自由选择）
- Chroma/Pinecone - 向量数据库
- Tree-sitter - 代码分析
- Docker - 执行沙箱
- Streamlit/Gradio - 演示界面

## 支持的 LLM

✅ **Anthropic Claude** - 推理能力强，代码生成质量高
✅ **Moonshot Kimi** - 长上下文，中文友好
✅ **Qwen (通义千问)** - 国产模型，性价比高

详见 [LLM 提供商文档](docs/LLM_PROVIDERS.md)

## 开发计划

- [ ] 基础架构搭建
- [ ] 单个 agent 实现
- [ ] 多 agent 协作机制
- [ ] 记忆系统集成
- [ ] Baseline 对比实验
- [ ] 演示界面开发

## 目标

构建一个可展示的项目，用于：
- 简历展示
- 大厂 agent 实习申请
- 证明多 agent 系统设计能力
- 展示 LLM 应用工程化经验
