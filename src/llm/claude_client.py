"""
Anthropic Claude 客户端
"""

from typing import List
from anthropic import AsyncAnthropic

from .base_client import BaseLLMClient, LLMMessage, LLMResponse, LLMProvider


class ClaudeClient(BaseLLMClient):
    """Claude API 客户端"""

    def __init__(self, api_key: str, model: str = "claude-3-5-sonnet-20241022"):
        super().__init__(api_key, model)
        self.client = AsyncAnthropic(
            api_key=api_key,
            timeout=120.0  # 增加超时时间到 120 秒
        )

    async def chat(
        self,
        messages: List[LLMMessage],
        temperature: float = 0.7,
        max_tokens: int = 4096,
        **kwargs
    ) -> LLMResponse:
        """发送聊天请求"""
        # 转换消息格式
        claude_messages = [
            {"role": msg.role, "content": msg.content}
            for msg in messages
        ]

        response = await self.client.messages.create(
            model=self.model,
            messages=claude_messages,
            temperature=temperature,
            max_tokens=max_tokens,
            **kwargs
        )

        return LLMResponse(
            content=response.content[0].text,
            model=response.model,
            usage={
                "input_tokens": response.usage.input_tokens,
                "output_tokens": response.usage.output_tokens,
            }
        )

    def get_provider(self) -> LLMProvider:
        return LLMProvider.ANTHROPIC
