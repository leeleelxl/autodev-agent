---
name: AutoDev 项目架构和目标
description: AutoDev 多 agent 协作系统的完整设计方案
type: project
---

项目位置：~/Desktop/agent_project/

## 项目目标

构建 **AutoDev - 自主软件开发 Agent 系统**，用于简历展示和大厂 agent 实习申请。

**Why:**
- 展示多 agent 系统设计能力
- 证明 LLM 应用工程化经验
- 通过 baseline 对比展示创新价值
- 获得可量化的项目成果

## 核心架构

### 多 Agent 协作设计
1. **Architect Agent** - 需求分析、技术选型、架构设计
2. **Developer Agent** - 代码实现、模块开发
3. **Tester Agent** - 测试用例生成、bug 检测
4. **Reviewer Agent** - 代码审查、优化建议
5. **Orchestrator** - 协调各 agent，处理冲突，迭代改进

### 技术栈
- **框架**: LangChain/LangGraph（agent 编排）
- **LLM**: Claude API（推理）+ 本地模型（代码生成）
- **向量数据库**: Chroma/Pinecone（长期记忆）
- **代码分析**: Tree-sitter（AST 解析）
- **执行环境**: Docker（沙箱）
- **前端**: Streamlit/Gradio（演示界面）

### 创新点
- Planning & Reasoning（ReAct 模式）
- 三层 Memory 系统（短期/长期/经验学习）
- 工具集成（代码执行、Git、静态分析）
- 自我评估与改进机制

## Baseline 对比方案

### 对比对象
1. **GPT Engineer** - 单 agent 架构（主要对比）
2. **MetaGPT** - 多 agent 架构（协作机制对比）
3. **单一 LLM** - Claude/GPT-4 直接生成（基础 baseline）

### 测试集
- **SWE-bench** - 2,294 个真实 GitHub issues（业界标准）
- 选取 50-100 个中等难度任务进行对比

### 评估指标
- Pass@k（k 次尝试的成功率）
- 代码质量（Pylint/ESLint 分数）
- 测试覆盖率
- Bug 密度
- Token 效率
- 首次成功率

**How to apply:**
- 所有代码和配置在 ~/Desktop/agent_project/ 目录
- 项目记忆保存在 .claude/memory/ 目录
- 使用 `/sync-memory` 定期同步重要信息
- 参考 CLAUDE.md 了解工作流程
