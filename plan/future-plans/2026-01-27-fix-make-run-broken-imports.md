# Fix `make run MODE=console` Broken Imports

> **Status:** COMPLETED

## Table of Contents

- [Overview](#overview)
- [Current State Analysis](#current-state-analysis)
- [Desired End State](#desired-end-state)
- [What We're NOT Doing](#what-were-not-doing)
- [Implementation Approach](#implementation-approach)
- [Dependencies](#dependencies)
- [Phase 1: Fix factories.py](#phase-1-fix-factoriespy)
- [Phase 2: Clean Up Unused Config](#phase-2-clean-up-unused-config)
- [Testing Strategy](#testing-strategy)
- [References](#references)

## Overview

The `make run MODE=console` command fails with `ModuleNotFoundError: No module named 'keyword_intercept_llm'`. This is because commit `ec18ea5` removed `src/keyword_intercept_llm.py` and `src/mock_llm.py` but did NOT update `src/factories.py` which still imports these non-existent modules.

## Current State Analysis

### Key Discoveries:

1. **Missing module imports in factories.py** (`src/factories.py:12-15`):
   ```python
   from keyword_intercept_llm import KeywordInterceptLLM
   from mock_llm import SimpleMockLLM
   ```
   These files were deleted in commit `ec18ea5` but the imports remain.

2. **Unused keyword intercept logic** (`src/factories.py:28-50`):
   - `create_llm()` function has type hints referencing deleted classes
   - Contains dead code for mock LLM handling (lines 36-37)
   - Contains dead code for keyword intercept wrapping (lines 42-48)

3. **Unused configuration options** (`src/config.py:51-63`):
   - `enable_keyword_intercept: bool` - Never used now
   - `intercept_keywords: list[str]` - Never used now
   - `intercept_response: str` - Never used now

### Error reproduction:
```bash
$ make run MODE=console
ModuleNotFoundError: No module named 'keyword_intercept_llm'
```

## Desired End State

All three agent run modes work correctly:
- `make run MODE=console` - Runs without import errors
- `make run MODE=dev` - Runs without import errors
- `make run MODE=start` - Runs without import errors

**Success Criteria:**
- [ ] `make run MODE=console` starts successfully (no import errors)
- [ ] `make run MODE=dev` starts successfully
- [ ] `make run MODE=start` starts successfully
- [ ] All existing tests pass (`uv run pytest`)
- [ ] No dead code or unused imports remain

**How to Verify:**
```bash
# Test each mode (Ctrl+C to exit after startup)
make run MODE=console
make run MODE=dev
make run MODE=start

# Run tests
uv run pytest
```

## What We're NOT Doing

- NOT restoring the deleted `keyword_intercept_llm.py` or `mock_llm.py` files
- NOT adding any new features
- NOT changing the Makefile (it's already correct)
- NOT modifying any agent behavior

## Implementation Approach

This is a simple cleanup task with two phases:
1. Fix the immediate import error in `factories.py`
2. Remove unused configuration options in `config.py`

## Dependencies

**Execution Order:**

1. Phase 1 (no dependencies) - Critical fix
2. Phase 2 (no dependencies, parallel with Phase 1) - Cleanup

**Parallelization:**
- Both phases can run in parallel as they touch different files

---

## Phase 1: Fix factories.py

### Overview
Remove broken imports and dead code from `factories.py`.

### Context
Before starting, read:
- `src/factories.py` - File with broken imports

### Dependencies
**Depends on:** None
**Required by:** None (critical path)

### Changes Required

#### 1.1: Update factories.py
**File:** `src/factories.py`

**Changes:**
1. Remove broken imports (lines 12, 15)
2. Simplify `create_llm()` function to just create `inference.LLM`
3. Remove type hints referencing deleted classes

**New content:**
```python
"""Factory functions for creating voice pipeline components.

This project previously used protocols/adapters/mocks for STT/LLM/TTS. After
removing that layer, these factories still provide separation of concerns:
- `config.py` owns configuration
- `factories.py` owns object construction
- `agent.py` wires the app together

The returned objects are concrete LiveKit Inference implementations.
"""

from livekit.agents import inference
from loguru import logger

from config import PipelineConfig


def create_stt(config: PipelineConfig) -> inference.STT:
    """Create an STT component from configuration."""
    logger.info(
        f"Creating STT with model: {config.stt_model}, lang: {config.stt_language}"
    )
    return inference.STT(model=config.stt_model, language=config.stt_language)


def create_llm(config: PipelineConfig) -> inference.LLM:
    """Create an LLM component from configuration."""
    logger.info(f"Creating LLM with model: {config.llm_model}")
    return inference.LLM(model=config.llm_model)


def create_tts(config: PipelineConfig) -> inference.TTS:
    """Create a TTS component from configuration."""
    logger.info(
        f"Creating TTS with model: {config.tts_model}, voice: {config.tts_voice}"
    )
    return inference.TTS(model=config.tts_model, voice=config.tts_voice)
```

**Rationale:** The `keyword_intercept_llm` and `mock_llm` modules were deleted, so all references to them must be removed. The `create_llm` function simplifies to just creating a standard `inference.LLM`.

### Success Criteria

#### Automated Verification:
- [ ] `make run MODE=console` starts without import errors (Ctrl+C to exit)
- [ ] `make run MODE=dev` starts without import errors
- [ ] All tests pass: `uv run pytest`
- [ ] Linting passes: `uv run ruff check`

---

## Phase 2: Clean Up Unused Config

### Overview
Remove unused keyword intercept configuration options from `config.py`.

### Context
Before starting, read:
- `src/config.py` - Configuration file

### Dependencies
**Depends on:** None
**Required by:** None

### Changes Required

#### 2.1: Remove unused config options
**File:** `src/config.py`

**Changes:**
Remove the following fields from `PipelineConfig` (lines 51-63):
- `enable_keyword_intercept`
- `intercept_keywords`
- `intercept_response`

**Updated PipelineConfig:**
```python
class PipelineConfig(BaseModel):
    """Configuration for the voice pipeline components (STT, LLM, TTS)."""

    # STT configuration
    stt_model: str = Field(
        default="assemblyai/universal-streaming",
        description="Speech-to-text model identifier",
    )
    stt_language: str = Field(
        default="en",
        description="Language code for speech recognition",
    )

    # LLM configuration
    llm_model: str = Field(
        default="openai/gpt-4.1-nano",
        description="Large language model identifier",
    )

    # TTS configuration
    tts_model: str = Field(
        default="inworld/inworld-tts-1",
        description="Text-to-speech model identifier",
    )
    tts_voice: str = Field(
        default="Ashley",
        description="Voice identifier for text-to-speech",
    )
```

**Rationale:** These configuration options are no longer used since the keyword intercept feature was removed. Keeping unused configuration creates confusion.

### Success Criteria

#### Automated Verification:
- [ ] All tests pass: `uv run pytest`
- [ ] Linting passes: `uv run ruff check`
- [ ] No references to removed fields in codebase: `grep -r "enable_keyword_intercept\|intercept_keywords\|intercept_response" src/`

---

## Testing Strategy

### Automated Tests:
- Run existing test suite: `uv run pytest`
- Run linting: `uv run ruff check`

### Manual Testing Steps:
1. Run `make run MODE=console` - should start without errors
2. Type a test message and verify agent responds
3. Press Ctrl+C to exit
4. Run `make run MODE=dev` - should start without errors
5. Run `make run MODE=start` - should start without errors

## References

- Commit that removed files: `ec18ea5` ("Remove generic voice assistant and focus on drive-thru agent")
- Error trace: `src/factories.py:12` → `ModuleNotFoundError: No module named 'keyword_intercept_llm'`
