"""
Qwen (通义千问) 客户端
"""

from typing import List
import dashscope
from dashscope import Generation

from .base_client import BaseLLMClient, LLMMessage, LLMResponse, LLMProvider


class QwenClient(BaseLLMClient):
    """Qwen API 客户端"""

    def __init__(self, api_key: str, model: str = "qwen-max"):
        super().__init__(api_key, model)
        dashscope.api_key = api_key

    async def chat(
        self,
        messages: List[LLMMessage],
        temperature: float = 0.7,
        max_tokens: int = 4096,
        **kwargs
    ) -> LLMResponse:
        """发送聊天请求"""
        # 转换消息格式
        qwen_messages = [
            {"role": msg.role, "content": msg.content}
            for msg in messages
        ]

        response = Generation.call(
            model=self.model,
            messages=qwen_messages,
            temperature=temperature,
            max_tokens=max_tokens,
            result_format='message',
            **kwargs
        )

        if response.status_code == 200:
            return LLMResponse(
                content=response.output.choices[0].message.content,
                model=self.model,
                usage={
                    "input_tokens": response.usage.input_tokens,
                    "output_tokens": response.usage.output_tokens,
                }
            )
        else:
            raise Exception(f"Qwen API 错误: {response.message}")

    def get_provider(self) -> LLMProvider:
        return LLMProvider.QWEN
