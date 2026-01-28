"""LiveKit Inference model identifiers.

This module provides a StrEnum of all available LLM models in LiveKit Inference.
Use these constants for type-safe model selection in configuration.
"""

from enum import StrEnum


class LiveKitInferenceLLMModel(StrEnum):
    """Available models in LiveKit Inference."""

    # OpenAI models
    GPT_4O = "openai/gpt-4o"
    GPT_4O_MINI = "openai/gpt-4o-mini"
    GPT_4_1 = "openai/gpt-4.1"
    GPT_4_1_MINI = "openai/gpt-4.1-mini"
    GPT_4_1_NANO = "openai/gpt-4.1-nano"
    GPT_5 = "openai/gpt-5"
    GPT_5_MINI = "openai/gpt-5-mini"
    GPT_5_NANO = "openai/gpt-5-nano"
    GPT_5_1 = "openai/gpt-5.1"
    GPT_5_1_CHAT_LATEST = "openai/gpt-5.1-chat-latest"
    GPT_5_2 = "openai/gpt-5.2"
    GPT_5_2_CHAT_LATEST = "openai/gpt-5.2-chat-latest"
    GPT_OSS_120B = "openai/gpt-oss-120b"

    # Gemini models
    GEMINI_3_PRO = "google/gemini-3-pro"
    GEMINI_3_FLASH = "google/gemini-3-flash"
    GEMINI_2_5_PRO = "google/gemini-2.5-pro"
    GEMINI_2_5_FLASH = "google/gemini-2.5-flash"
    GEMINI_2_5_FLASH_LITE = "google/gemini-2.5-flash-lite"
    GEMINI_2_0_FLASH = "google/gemini-2.0-flash"
    GEMINI_2_0_FLASH_LITE = "google/gemini-2.0-flash-lite"

    # Kimi models
    KIMI_K2_INSTRUCT = "moonshotai/kimi-k2-instruct"

    # DeepSeek models
    DEEPSEEK_V3 = "deepseek-ai/deepseek-v3"
    DEEPSEEK_V3_2 = "deepseek-ai/deepseek-v3.2"
