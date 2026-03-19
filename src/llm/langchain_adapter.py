"""
LangChain LLM 适配层

将 Kimi/Qwen 等 OpenAI 兼容接口包装为 LangChain ChatModel，
使 LangChain Agent 框架（ReAct、Tool Calling）能直接使用。
"""

from typing import Optional
from langchain_openai import ChatOpenAI


def create_langchain_llm(
    provider: str = "moonshot",
    api_key: str = "",
    model: str = "kimi-k2-turbo-preview",
    temperature: float = 0.7,
    max_tokens: int = 4096,
    timeout: int = 120,
) -> ChatOpenAI:
    """
    创建 LangChain ChatModel 实例

    支持所有 OpenAI 兼容接口（Kimi、Qwen、OpenAI）

    Args:
        provider: 提供商 (moonshot / qwen / openai)
        api_key: API Key
        model: 模型名称
        temperature: 温度
        max_tokens: 最大 token 数
        timeout: 超时时间（秒）

    Returns:
        ChatOpenAI 实例（LangChain 标准接口）
    """
    # 不同提供商的 base_url
    BASE_URLS = {
        "moonshot": "https://api.moonshot.cn/v1",
        "qwen": "https://dashscope.aliyuncs.com/compatible-mode/v1",
        "openai": "https://api.openai.com/v1",
    }

    base_url = BASE_URLS.get(provider)
    if not base_url:
        raise ValueError(f"不支持的提供商: {provider}，支持: {list(BASE_URLS.keys())}")

    return ChatOpenAI(
        model=model,
        api_key=api_key,
        base_url=base_url,
        temperature=temperature,
        max_tokens=max_tokens,
        timeout=timeout,
        max_retries=3,
    )
