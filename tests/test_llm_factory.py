"""
测试 LLM Factory
"""

import pytest
from src.llm import LLMFactory, LLMProvider, ClaudeClient, KimiClient, QwenClient


def test_create_claude_client():
    """测试创建 Claude 客户端"""
    client = LLMFactory.create_client(
        provider=LLMProvider.ANTHROPIC,
        api_key="test_key"
    )
    assert isinstance(client, ClaudeClient)
    assert client.model == "claude-3-5-sonnet-20241022"


def test_create_kimi_client():
    """测试创建 Kimi 客户端"""
    client = LLMFactory.create_client(
        provider=LLMProvider.MOONSHOT,
        api_key="test_key"
    )
    assert isinstance(client, KimiClient)
    assert client.model == "moonshot-v1-8k"


def test_create_qwen_client():
    """测试创建 Qwen 客户端"""
    client = LLMFactory.create_client(
        provider=LLMProvider.QWEN,
        api_key="test_key"
    )
    assert isinstance(client, QwenClient)
    assert client.model == "qwen-max"


def test_custom_model():
    """测试自定义模型"""
    client = LLMFactory.create_client(
        provider=LLMProvider.ANTHROPIC,
        api_key="test_key",
        model="claude-3-opus-20240229"
    )
    assert client.model == "claude-3-opus-20240229"


def test_get_available_providers():
    """测试获取可用提供商"""
    providers = LLMFactory.get_available_providers()
    assert LLMProvider.ANTHROPIC in providers
    assert LLMProvider.MOONSHOT in providers
    assert LLMProvider.QWEN in providers
