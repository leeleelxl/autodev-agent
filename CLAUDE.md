# Agent Project - Claude 工作指南

## 自动记忆加载

**重要：每次对话开始时，你必须立即执行以下操作：**

1. 读取 `.claude/memory/MEMORY.md` 获取记忆索引
2. 读取索引中列出的所有记忆文件
3. 基于这些记忆理解项目上下文

**记忆文件位置：** `.claude/memory/`

## 记忆管理规则

### 何时保存记忆

- **项目决策** - 技术选型、架构设计、实现方案
- **实验结果** - 测试数据、性能指标、对比结果
- **遇到的问题** - bug、解决方案、经验教训
- **用户偏好** - 代码风格、工作流程、特殊要求
- **重要里程碑** - 完成的功能模块、版本节点

### 记忆文件命名规范

- `project_*.md` - 项目相关信息
- `user_*.md` - 用户偏好和背景
- `feedback_*.md` - 用户反馈和指导
- `reference_*.md` - 外部资源引用
- `experiment_*.md` - 实验和测试结果

### 对话结束前检查清单

在每次对话即将结束时，主动询问用户是否需要保存：
- [ ] 新的技术决策
- [ ] 实验数据和结果
- [ ] 遇到的问题和解决方案
- [ ] 下一步计划

## 项目目标

构建 **AutoDev - 自主软件开发 Agent 系统**，一个多 agent 协作的代码生成系统，用于简历展示和大厂实习申请。

### 核心特性
- 多 agent 协作（Architect, Developer, Tester, Reviewer, Orchestrator）
- 自我反思和迭代改进
- 与 baseline（GPT Engineer, SWE-bench）对比

### 技术栈
- LangChain/LangGraph
- Claude API
- 向量数据库（Chroma/Pinecone）
- Docker 沙箱
