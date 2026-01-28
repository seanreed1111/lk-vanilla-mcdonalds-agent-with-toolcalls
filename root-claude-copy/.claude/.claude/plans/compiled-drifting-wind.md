# Plan: Update LLMProtocol to Match LiveKit Agents API

## Overview

Update `LLMProtocol` to include the `chat` method signature that matches the actual LiveKit Agents API at https://github.com/livekit/agents/blob/main/livekit-agents/livekit/agents/llm/llm.py#L152.

## Current State

### What I Found

1. **LLMProtocol is currently empty** (`src/protocols.py:25-35`)
   - Just a placeholder with documentation
   - No method signatures defined
   - No type enforcement

2. **LiveKitLLM uses `__getattr__` delegation** (`src/adapters/livekit_adapters.py:44-69`)
   - Wraps `inference.LLM` in `_llm` attribute
   - Delegates all method calls via `__getattr__`
   - Works because `inference.LLM` already has the `chat()` method

3. **MockLLM uses `__getattr__` fallback** (`src/adapters/mock_adapters.py:126-170`)
   - Returns `lambda *args, **kwargs: None` for any attribute access
   - Never actually implements `chat()`
   - Works because application code never calls `chat()` directly

4. **The `chat()` method is never called in application code**
   - `AgentSession` internally calls `chat()` on the LLM
   - Application just passes the LLM to `AgentSession`
   - ChatContext is created and managed internally by `AgentSession`

### LiveKit Agents API Signature

```python
@abstractmethod
def chat(
    self,
    *,
    chat_ctx: ChatContext,
    tools: list[Tool] | None = None,
    conn_options: APIConnectOptions = DEFAULT_API_CONNECT_OPTIONS,
    parallel_tool_calls: NotGivenOr[bool] = NOT_GIVEN,
    tool_choice: NotGivenOr[ToolChoice] = NOT_GIVEN,
    extra_kwargs: NotGivenOr[dict[str, Any]] = NOT_GIVEN,
) -> LLMStream:
    ...
```

**Key aspects:**
- Keyword-only parameters (after `*`)
- Required: `chat_ctx: ChatContext`
- Returns: `LLMStream`
- Optional parameters: `tools`, `conn_options`, etc.

## Implementation Approach

Based on user's selections:
- ✅ **Minimal signature:** `chat(self, *, chat_ctx, **kwargs) -> LLMStream`
- ✅ **LiveKitLLM:** Keep `__getattr__` delegation (no changes)
- ✅ **MockLLM:** Keep `__getattr__` fallback (no changes)

### Files to Modify

**Only one file needs changes:**

1. **`src/protocols.py`**
   - Add imports for `ChatContext` and `LLMStream` from `livekit.agents.llm`
   - Add `chat()` method signature to `LLMProtocol`

**No changes needed to:**
- ❌ `src/adapters/livekit_adapters.py` - delegation already works
- ❌ `src/adapters/mock_adapters.py` - fallback already works

## Detailed Changes

### `src/protocols.py`

```python
# Add to imports at top of file
from livekit.agents.llm import ChatContext, LLMStream

# Update LLMProtocol class
@runtime_checkable
class LLMProtocol(Protocol):
    """Protocol for Large Language Model implementations.

    This protocol defines the interface that all LLM adapters must implement
    to be compatible with the voice pipeline.
    """

    def chat(
        self,
        *,
        chat_ctx: ChatContext,
        **kwargs,
    ) -> LLMStream:
        """Generate a response stream for the given chat context.

        Args:
            chat_ctx: The conversation context containing message history
            **kwargs: Additional arguments passed to the LLM (e.g., tools, conn_options)

        Returns:
            A stream of chat responses from the LLM
        """
        ...
```

**Why this works:**
- `LiveKitLLM._llm` (which is `inference.LLM`) already has the correct `chat()` method
- The `__getattr__` delegation in `LiveKitLLM` will pass through calls to `_llm.chat()`
- `MockLLM.__getattr__` returns `lambda *args, **kwargs: None`, which satisfies the protocol at runtime
- Type checkers will validate the protocol signature exists

## Verification Steps

After implementing the changes, verify everything works:

1. **Verify imports resolve correctly:**
   ```bash
   uv run python -c "from src.protocols import LLMProtocol; from livekit.agents.llm import ChatContext, LLMStream; print('Imports successful')"
   ```

2. **Run existing tests (should still pass):**
   ```bash
   make test
   ```

3. **Run with mock adapters to ensure no breakage:**
   ```bash
   make mock-console
   ```

4. **Optional - Type checking (if mypy is configured):**
   ```bash
   uv run mypy src/protocols.py
   ```

5. **Verify protocol compliance in adapters:**
   The existing type-check code at the bottom of adapter files should continue to work:
   ```python
   # In livekit_adapters.py and mock_adapters.py
   if False:  # TYPE_CHECKING
       _: LLMProtocol = LiveKitLLM(PipelineConfig())  # Should not raise type errors
   ```

## Risk Assessment

**Low Risk Changes:**
- Only adding method signature to protocol
- No changes to adapter implementations
- Delegation pattern already works correctly
- Application code doesn't call `chat()` directly

**Potential Issues:**
- Import errors if `livekit.agents.llm` module structure has changed
  - Mitigation: Test imports after implementation
- Type checking may reveal protocol violations
  - Mitigation: Existing adapters already satisfy the interface via delegation

## Success Criteria

- ✅ `LLMProtocol` has `chat(self, *, chat_ctx, **kwargs) -> LLMStream` method
- ✅ Imports from `livekit.agents.llm` work correctly
- ✅ All existing tests pass
- ✅ Mock console runs without errors
- ✅ No changes needed to adapter implementations
