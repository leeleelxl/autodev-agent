# AutoDev - 多 LLM 支持

## 支持的 LLM 提供商

### 1. Anthropic Claude
- 模型：`claude-3-5-sonnet-20241022`, `claude-3-opus-20240229`
- 特点：推理能力强，代码生成质量高

### 2. Moonshot (Kimi)
- 模型：`moonshot-v1-8k`, `moonshot-v1-32k`, `moonshot-v1-128k`
- 特点：长上下文，中文友好

### 3. Qwen (通义千问)
- 模型：`qwen-max`, `qwen-plus`, `qwen-turbo`
- 特点：国产模型，性价比高

## 使用方式

### 配置 API Keys

复制 `.env.example` 为 `.env`，填入你的 API Keys：

```bash
cp .env.example .env
```

编辑 `.env`：
```env
ANTHROPIC_API_KEY=your_anthropic_key
MOONSHOT_API_KEY=your_kimi_key
DASHSCOPE_API_KEY=your_qwen_key

DEFAULT_PROVIDER=anthropic
DEFAULT_MODEL=claude-3-5-sonnet-20241022
```

### 代码中使用

```python
from src.llm import LLMFactory, LLMProvider, LLMMessage

# 创建客户端
client = LLMFactory.create_client(
    provider=LLMProvider.ANTHROPIC,
    api_key="your_key",
    model="claude-3-5-sonnet-20241022"  # 可选
)

# 发送请求
messages = [
    LLMMessage(role="user", content="写一个快速排序")
]

response = await client.chat(
    messages=messages,
    temperature=0.7,
    max_tokens=2000
)

print(response.content)
print(response.usage)  # token 使用情况
```

### Agent 中配置 LLM

```python
from src.agents import ArchitectAgent, AgentConfig

# 使用 Claude
architect = ArchitectAgent()
architect.config.provider = "anthropic"
architect.config.model = "claude-3-5-sonnet-20241022"

# 使用 Kimi
architect.config.provider = "moonshot"
architect.config.model = "moonshot-v1-32k"

# 使用 Qwen
architect.config.provider = "qwen"
architect.config.model = "qwen-max"
```

## 获取 API Keys

- **Claude**: https://console.anthropic.com/
- **Kimi**: https://platform.moonshot.cn/
- **Qwen**: https://dashscope.aliyun.com/
