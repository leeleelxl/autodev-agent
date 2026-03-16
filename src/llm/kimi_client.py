"""
Moonshot (Kimi) 客户端
"""

from typing import List
from openai import AsyncOpenAI

from .base_client import BaseLLMClient, LLMMessage, LLMResponse, LLMProvider


class KimiClient(BaseLLMClient):
    """Kimi API 客户端 (使用 OpenAI 兼容接口)"""

    def __init__(self, api_key: str, model: str = "moonshot-v1-8k"):
        super().__init__(api_key, model)
        self.client = AsyncOpenAI(
            api_key=api_key,
            base_url="https://api.moonshot.cn/v1"
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
        openai_messages = [
            {"role": msg.role, "content": msg.content}
            for msg in messages
        ]

        response = await self.client.chat.completions.create(
            model=self.model,
            messages=openai_messages,
            temperature=temperature,
            max_tokens=max_tokens,
            **kwargs
        )

        return LLMResponse(
            content=response.choices[0].message.content,
            model=response.model,
            usage={
                "input_tokens": response.usage.prompt_tokens,
                "output_tokens": response.usage.completion_tokens,
            }
        )

    def get_provider(self) -> LLMProvider:
        return LLMProvider.MOONSHOT
