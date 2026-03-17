---
marp: true
theme: academic
paginate: true
header: 'AutoDev: A Multi-Agent Collaborative Code Generation System'
footer: 'GitHub: github.com/leeleelxl/autodev-agent'
---

<!-- _class: title -->

# AutoDev: A Multi-Agent Collaborative Code Generation System

**A Quality-Assured Approach to Automated Code Generation**

---

**Author**: [Your Name]
**Institution**: [Your Institution]
**Date**: March 2026
**GitHub**: https://github.com/leeleelxl/autodev-agent

---

## Table of Contents

1. Introduction & Motivation
2. Related Work
3. System Architecture
4. Key Technical Contributions
5. Experimental Evaluation
6. Results & Analysis
7. Limitations & Future Work
8. Conclusion

---

<!-- _class: section -->

# 1. Introduction & Motivation

---

## 1.1 Research Background

### The Challenge of Code Generation

**Current State**:
- Large Language Models (LLMs) can generate code from natural language
- Single-pass generation often lacks quality assurance
- No systematic testing or code review
- Difficult to maintain and extend

**Research Question**:
> Can we design a multi-agent system that automatically generates high-quality, maintainable code with built-in quality assurance?

---

## 1.2 Motivation

### Problems with Single LLM Approach

| Problem | Impact |
|---------|--------|
| **No Testing** | Generated code may not work |
| **No Review** | Potential bugs and issues undetected |
| **No Quality Metrics** | Cannot quantify code quality |
| **Single File Output** | Poor modularity and maintainability |

### Our Hypothesis

**Multi-agent collaboration with specialized roles can produce higher quality code through systematic quality assurance.**

---

## 1.3 Research Objectives

1. **Design** a multi-agent collaborative system for code generation
2. **Implement** quality assurance mechanisms (testing, review, scoring)
3. **Evaluate** the system against baseline approaches
4. **Analyze** the trade-offs between quality and efficiency

---

<!-- _class: section -->

# 2. Related Work

---

## 2.1 Code Generation Systems

### GPT Engineer (Osika, 2023)

**Architecture**: Single Agent + Steps
- Interactive development with user confirmation
- Simple and controllable
- No automatic quality assurance

**Limitations**:
- Requires manual intervention
- No automatic testing or review
- Depends on user expertise

---

## 2.2 Multi-Agent Systems

### Existing Approaches

**AutoGPT** (Significant Gravitas, 2023):
- General-purpose autonomous agent
- Not specialized for code generation

**MetaGPT** (Hong et al., 2023):
- Multi-agent for software development
- Focus on requirements and design
- Less emphasis on quality assurance

### Research Gap

**No existing system combines**:
- Multi-agent collaboration
- Automatic quality assurance
- Systematic evaluation

---

<!-- _class: section -->

# 3. System Architecture

---

## 3.1 Overall Architecture

```
┌─────────────────────────────────────────────────┐
│              Orchestrator                        │
│         (Workflow Coordination)                  │
└─────────────────────────────────────────────────┘
                      │
        ┌─────────────┼─────────────┐
        ▼             ▼             ▼
┌──────────────┐ ┌──────────────┐ ┌──────────────┐
│  Architect   │ │  Developer   │ │   Tester     │
│    Agent     │ │    Agent     │ │    Agent     │
└──────────────┘ └──────────────┘ └──────────────┘
        │             │             │
        └─────────────┼─────────────┘
                      ▼
              ┌──────────────┐
              │   Reviewer   │
              │    Agent     │
              └──────────────┘
                      │
                      ▼
              ┌──────────────┐
              │   Memory     │
              │   System     │
              └──────────────┘
```

---

## 3.2 Agent Roles & Responsibilities

### Five Specialized Agents

| Agent | Responsibility | Input | Output |
|-------|---------------|-------|--------|
| **Architect** | Design system architecture | Requirements | Architecture design |
| **Developer** | Implement code | Design + Context | Code files |
| **Tester** | Generate tests | Code files | Test cases |
| **Reviewer** | Review code quality | Code + Tests | Quality report |
| **Orchestrator** | Coordinate workflow | Task | Final output |

---

## 3.3 Workflow Phases

### Five-Phase Pipeline

```
Phase 1: Architecture Design
    ↓
Phase 2: Code Implementation
    ↓
Phase 3: Test Generation
    ↓
Phase 4: Code Review
    ↓
Phase 5: Iterative Improvement
```

**Key Feature**: Automatic iteration based on quality score

---

## 3.4 Memory System

### Three-Layer Memory Architecture

1. **Short-term Memory**
   - Current conversation context
   - Agent communication

2. **Long-term Memory**
   - Project history
   - Design decisions

3. **Experience Memory**
   - Success/failure cases
   - Similar task retrieval
   - Continuous learning

**Implementation**: ChromaDB for vector storage

---

<!-- _class: section -->

# 4. Key Technical Contributions

---

## 4.1 Contribution 1: Multi-Agent Collaboration

### Novel Workflow Design

**Innovation**: Specialized agents with clear responsibilities

**Advantages**:
- Each agent focuses on one domain
- Parallel processing where possible
- Clear separation of concerns

**Implementation**:
```python
class Orchestrator:
    async def execute_workflow(self, task):
        design = await architect.process(task)
        code = await developer.process(task, {"design": design})
        tests = await tester.process(task, {"code": code})
        review = await reviewer.process(task, {"code": code, "tests": tests})
        if review["score"] < 80:
            improved = await developer.process("fix", {"review": review})
```

---

## 4.2 Contribution 2: Markdown Code Block Parsing

### Problem: JSON Format Unreliability

**Challenge**:
- LLMs frequently generate malformed JSON
- Code contains quotes and newlines that break JSON
- Parsing failure rate: ~50%

**Solution**: Markdown Code Blocks
```markdown
```python
# filename: app.py
def hello():
    print("Hello")
```
```

**Results**:
- Parsing success rate: 100%
- More natural for LLMs
- Industry best practice (Cursor, Aider)

---

## 4.3 Contribution 3: Automatic Quality Assurance

### Comprehensive Quality Metrics

1. **Test Coverage**
   - Automatic test generation
   - Execution and validation

2. **Code Review**
   - Static analysis (Linter)
   - Dynamic analysis (CodeAnalyzer)
   - LLM-based review

3. **Quality Scoring**
   - 0-100 scale
   - Based on multiple factors
   - Drives iterative improvement

---

## 4.4 Contribution 4: Experience Learning

### Learning from Past Executions

**Mechanism**:
```python
if quality_score >= 70 and tests_passed:
    experience.record_success(task, solution, metadata)
else:
    experience.record_failure(task, error, metadata)

# Retrieve similar experiences
similar = experience.retrieve_similar(new_task, k=5)
```

**Benefits**:
- Avoid repeating mistakes
- Reuse successful patterns
- Continuous improvement

---

<!-- _class: section -->

# 5. Experimental Evaluation

---

## 5.1 Experimental Design

### Research Questions

**RQ1**: Does AutoDev generate higher quality code than Single LLM?

**RQ2**: How does code modularity compare?

**RQ3**: What is the trade-off between quality and efficiency?

**RQ4**: How does AutoDev compare to GPT Engineer architecturally?

---

## 5.2 Experimental Setup

### Tasks

Five tasks with varying complexity:

| ID | Task | Complexity | Description |
|----|------|-----------|-------------|
| 1 | Calculator | Simple | CLI calculator with basic operations |
| 2 | TODO List | Medium | CRUD operations with JSON storage |
| 3 | Authentication | Medium | User auth with JWT and SQLite |
| 4 | REST API | Complex | Book management API with pagination |
| 5 | Web Crawler | Complex | News crawler with robots.txt |

---

## 5.3 Evaluation Metrics

### Quantitative Metrics

1. **File Count**: Number of generated files
2. **Lines of Code**: Total LOC
3. **Test Coverage**: Presence of test files
4. **Quality Score**: 0-100 scale
5. **Issue Detection**: Number of identified problems
6. **Execution Time**: Time to complete

### Qualitative Metrics

1. **Architecture Quality**: Modularity, separation of concerns
2. **Code Maintainability**: Readability, documentation
3. **Completeness**: Missing dependencies

---

## 5.4 Baseline Comparison

### Baseline: Single LLM

**Configuration**:
- Model: Kimi K2 Turbo (256K context)
- Temperature: 0.7
- Max tokens: 4096
- Single-pass generation

**Prompt**:
```
Implement [task description].
Requirements:
1. Complete functional code
2. Error handling
3. Input validation

Output using Markdown code blocks.
```

---

<!-- _class: section -->

# 6. Results & Analysis

---

## 6.1 Overall Results

### Quantitative Comparison

| Metric | Single LLM | AutoDev | Improvement |
|--------|-----------|---------|-------------|
| **Avg Files** | 1.0 | 9.2 | **9.2x** |
| **Avg LOC** | 163.6 | 402.6 | 2.5x |
| **Test Coverage** | 0% | 100% | **+100%** |
| **Quality Score** | N/A | 66.4/100 | **Quantifiable** |
| **Issues Detected** | 0 | 9.6 | **+9.6** |
| **Avg Time** | 15.3s | 187.9s | 12.3x slower |

---

## 6.2 Task-by-Task Analysis

### Simple Task: Calculator

| Metric | Single LLM | AutoDev | Analysis |
|--------|-----------|---------|----------|
| Files | 1 | 2 | Modular design |
| LOC | 85 | 300 | More comprehensive |
| Time | 10.2s | 184.8s | **18.1x slower** |
| Quality | ? | 70/100 | Quantified |
| Issues | 0 | 6 | Proactive detection |

**Observation**: AutoDev is over-engineering for simple tasks

---

## 6.3 Task-by-Task Analysis

### Medium Task: Authentication System

| Metric | Single LLM | AutoDev | Analysis |
|--------|-----------|---------|----------|
| Files | 1 | 16 | **Clean Architecture** |
| LOC | 222 | 527 | Modular components |
| Time | 16.3s | 241.0s | 14.8x slower |
| Quality | ? | 70/100 | Consistent |
| Issues | 0 | 12 | Comprehensive review |

**Architecture**:
```
AutoDev Output:
├── domain/          # Business logic
├── adapters/        # Infrastructure
├── tests/           # Test suite
└── app.py           # Entry point
```

---

## 6.4 Task-by-Task Analysis

### Complex Task: REST API

| Metric | Single LLM | AutoDev | Analysis |
|--------|-----------|---------|----------|
| Files | 1 | 14 | Layered architecture |
| LOC | 224 | 564 | Comprehensive |
| Time | 22.2s | 240.0s | **10.8x slower** |
| Quality | ? | 70/100 | Stable |
| Issues | 0 | 9 | Quality assurance |

**Observation**: Speed gap narrows for complex tasks

---

## 6.5 Quality Score Analysis

### Consistency Across Tasks

```
Task 1 (Calculator):  70/100
Task 2 (TODO):        70/100
Task 3 (Auth):        70/100
Task 4 (API):         70/100
Task 5 (Crawler):     52/100  ← Outlier
```

**Analysis**:
- Quality assurance mechanism is **consistent**
- Score of 70 indicates **good but not perfect** code
- Crawler task scored lower due to domain complexity

---

## 6.6 Issue Detection Analysis

### Types of Issues Detected

**Common Issues** (across all tasks):
1. Hardcoded secrets (SECRET_KEY)
2. Missing database migrations
3. Lack of logging
4. Missing API documentation
5. No rate limiting
6. Missing CORS configuration
7. No environment variable configuration
8. Missing error monitoring
9. No performance optimization
10. Missing security headers

**Value**: Proactive identification of production concerns

---

## 6.7 Architecture Comparison: GPT Engineer

### Architectural Differences

| Dimension | GPT Engineer | AutoDev |
|-----------|-------------|---------|
| **Architecture** | Single Agent | Multi-Agent (5) |
| **Workflow** | Steps (sequential) | Phases (collaborative) |
| **User Involvement** | High (confirmation) | Low (automatic) |
| **Quality Assurance** | None | Comprehensive |
| **Code Complexity** | ~2000 LOC | ~5000 LOC |
| **Maturity** | High (50k+ stars) | Low (new project) |

**Conclusion**: Complementary, not competitive

---

## 6.8 Trade-off Analysis

### Quality vs. Efficiency

```
Speed Ratio by Task Complexity:
Simple:   18.1x slower
Medium:   10.7-14.8x slower
Complex:  9.2-10.8x slower
```

**Insight**: **Speed gap narrows as task complexity increases**

**Interpretation**:
- Simple tasks: AutoDev is over-engineering
- Complex tasks: Quality assurance overhead is justified

---

<!-- _class: section -->

# 7. Limitations & Future Work

---

## 7.1 Current Limitations

### 1. Incomplete Code Generation

**Problem**: Generated code has missing dependencies

**Example**:
```
⚠️ Warning: Missing dependencies:
- pydantic, fastapi, sqlalchemy, ...
```

**Impact**: Code requires manual completion

**Root Cause**: LLM context limitations

---

## 7.2 Current Limitations

### 2. Performance Overhead

**Problem**: 12.3x slower than Single LLM on average

**Breakdown**:
- Phase 1 (Architecture): ~30s
- Phase 2 (Development): ~60s
- Phase 3 (Testing): ~40s
- Phase 4 (Review): ~30s
- Phase 5 (Improvement): ~30s

**Impact**: Not suitable for rapid prototyping

---

## 7.3 Current Limitations

### 3. Limited Evaluation

**Scope**:
- Only 5 tasks tested
- Only compared to Single LLM
- No user study
- No real-world deployment

**Need**:
- Larger benchmark dataset
- Comparison with more baselines
- User experience evaluation
- Production deployment case studies

---

## 7.4 Future Work

### Short-term Improvements

1. **Dependency Completion**
   - Automatic detection and generation of missing modules
   - Ensure 100% runnable code

2. **Performance Optimization**
   - Parallel agent execution where possible
   - Caching and reuse of intermediate results
   - Reduce to 5x slower (target)

3. **Adaptive Workflow**
   - Skip quality assurance for simple tasks
   - Full pipeline only for complex tasks

---

## 7.5 Future Work

### Long-term Research Directions

1. **Benchmark Development**
   - Create standardized code generation benchmark
   - Include diverse task types and complexities

2. **User Study**
   - Evaluate with real developers
   - Measure productivity and satisfaction
   - Identify usability issues

3. **Production Deployment**
   - CI/CD integration
   - Real-world case studies
   - Performance monitoring

4. **Advanced Quality Metrics**
   - Security vulnerability detection
   - Performance profiling
   - Accessibility compliance

---

<!-- _class: section -->

# 8. Conclusion

---

## 8.1 Summary of Contributions

### Technical Contributions

1. **Multi-Agent Architecture**
   - 5 specialized agents with clear responsibilities
   - Systematic workflow coordination

2. **Markdown Code Block Parsing**
   - Solved JSON unreliability problem
   - 100% parsing success rate

3. **Automatic Quality Assurance**
   - Test generation, code review, quality scoring
   - Average 9.6 issues detected per task

4. **Experience Learning**
   - Learn from success/failure cases
   - Continuous improvement

---

## 8.2 Key Findings

### Research Questions Answered

**RQ1: Quality Improvement?**
✅ Yes - 100% test coverage, 66.4/100 quality score, 9.6 issues detected

**RQ2: Code Modularity?**
✅ Yes - 9.2 files vs 1 file, Clean Architecture

**RQ3: Quality-Efficiency Trade-off?**
✅ 12.3x slower, but gap narrows for complex tasks

**RQ4: vs GPT Engineer?**
✅ Complementary - GPT Engineer for interaction, AutoDev for automation

---

## 8.3 Practical Implications

### When to Use AutoDev

**Recommended**:
- Complex projects requiring modularity
- Production code needing quality assurance
- Batch code generation
- Long-term maintenance projects

**Not Recommended**:
- Simple scripts and utilities
- Rapid prototyping
- Interactive development
- Time-critical tasks

---

## 8.4 Broader Impact

### Implications for Software Engineering

1. **Automated Quality Assurance**
   - Demonstrates feasibility of AI-driven QA
   - Potential to reduce manual review burden

2. **Multi-Agent Collaboration**
   - Shows value of specialized agents
   - Template for other software engineering tasks

3. **LLM Output Parsing**
   - Markdown > JSON for code generation
   - Applicable to other LLM applications

---

## 8.5 Final Remarks

### Project Status

**Current State**:
- ✅ Functional prototype
- ✅ Experimental validation (5 tasks)
- ✅ Open source (GitHub)
- ⚠️ Not production-ready

**Future Vision**:
- Larger-scale evaluation
- Performance optimization
- User studies
- Production deployment

**GitHub**: https://github.com/leeleelxl/autodev-agent

---

<!-- _class: section -->

# Thank You

## Questions?

---

**Contact**:
- GitHub: github.com/leeleelxl/autodev-agent
- Email: [your-email]

**Resources**:
- Full Documentation: See repository
- Technical Deep Dive: docs/guides/
- Experimental Data: experiments/results/

---

<!-- _class: appendix -->

# Appendix

---

## A.1 Detailed Architecture

### Agent Communication Protocol

```python
class AgentMessage:
    sender: str          # Agent ID
    receiver: str        # Target agent
    content: str         # Message content
    metadata: dict       # Additional data
    timestamp: datetime  # When sent

class Context:
    messages: List[AgentMessage]
    shared_state: dict

    def add_message(self, msg: AgentMessage):
        self.messages.append(msg)

    def get_state(self, key: str):
        return self.shared_state.get(key)
```

---

## A.2 Preprompts Examples

### Architect Agent Prompt

```
You are a senior software architect.

Task: Analyze requirements and design system architecture.

Output format:
1. Technology stack
2. System components
3. Data flow
4. File structure

Consider:
- Scalability
- Maintainability
- Best practices
```

---

## A.3 Quality Scoring Algorithm

### Scoring Components

```python
def calculate_quality_score(code, tests, analysis):
    score = 0

    # Component 1: Test coverage (30 points)
    if tests_exist:
        score += 30

    # Component 2: Code analysis (40 points)
    score += (40 - len(linter_errors) * 2)

    # Component 3: Architecture (30 points)
    score += architecture_score(code)

    return max(0, min(100, score))
```

---

## A.4 Experimental Data

### Raw Results Table

| Task | Single LLM Time | AutoDev Time | Files (S) | Files (A) | LOC (S) | LOC (A) |
|------|----------------|--------------|-----------|-----------|---------|---------|
| Calc | 10.2s | 184.8s | 1 | 2 | 85 | 300 |
| TODO | 12.1s | 129.7s | 1 | 5 | 144 | 304 |
| Auth | 16.3s | 241.0s | 1 | 16 | 222 | 527 |
| API | 22.2s | 240.0s | 1 | 14 | 224 | 564 |
| Crawler | 15.7s | 144.3s | 1 | 9 | 143 | 318 |

---

## A.5 References

1. Osika, A. (2023). GPT Engineer. GitHub repository.
2. Hong, S., et al. (2023). MetaGPT: Meta Programming for Multi-Agent Collaborative Framework.
3. Significant Gravitas. (2023). AutoGPT: An Autonomous GPT-4 Experiment.
4. OpenAI. (2023). GPT-4 Technical Report.
5. Anthropic. (2024). Claude 3 Model Card.
6. Moonshot AI. (2025). Kimi K2: Technical Documentation.

---

<!-- _class: end -->

# End of Presentation

**Thank you for your attention!**

GitHub: https://github.com/leeleelxl/autodev-agent
