"""Factory functions for creating voice pipeline components.

This project previously used protocols/adapters/mocks for STT/LLM/TTS. After
removing that layer, these factories still provide separation of concerns:
- `config.py` owns configuration
- `factories.py` owns object construction
- `agent.py` wires the app together

The returned objects are concrete LiveKit Inference implementations.
"""

from keyword_intercept_llm import KeywordInterceptLLM
from livekit.agents import inference
from loguru import logger
from mock_llm import SimpleMockLLM

from config import PipelineConfig


def create_stt(config: PipelineConfig) -> inference.STT:
    """Create an STT component from configuration."""
    logger.info(
        f"Creating STT with model: {config.stt_model}, lang: {config.stt_language}"
    )
    return inference.STT(model=config.stt_model, language=config.stt_language)


def create_llm(
    config: PipelineConfig,
) -> inference.LLM | SimpleMockLLM | KeywordInterceptLLM:
    """Create an LLM component from configuration."""
    logger.info(f"Creating LLM with model: {config.llm_model}")

    # Create base LLM
    match config.llm_model:
        case "mock":
            base_llm = SimpleMockLLM()
        case _:
            base_llm = inference.LLM(model=config.llm_model)

    # Wrap with keyword interceptor if enabled
    if config.enable_keyword_intercept:
        logger.info("Wrapping LLM with keyword interceptor")
        return KeywordInterceptLLM(
            wrapped_llm=base_llm,
            keywords=config.intercept_keywords,
            response_text=config.intercept_response,
        )

    return base_llm


def create_tts(config: PipelineConfig) -> inference.TTS:
    """Create a TTS component from configuration."""
    logger.info(
        f"Creating TTS with model: {config.tts_model}, voice: {config.tts_voice}"
    )
    return inference.TTS(model=config.tts_model, voice=config.tts_voice)
