# Implementation Plan: Custom Keyword-Intercepting LLM Module

## Overview
Create a custom LLM wrapper that intercepts user input containing fruit-related keywords ("cherries", "cherry", "banana", "apple", "fruit") and returns a fixed response "I don't like fruit" instead of calling the actual LLM. For all other input, it delegates to the underlying LLM.

## Architecture Approach

**Pattern: LLM Wrapper (Decorator Pattern)**
- Create a `KeywordInterceptLLM` class that wraps any existing LLM
- Intercepts the `chat()` method to check user input for keywords
- Returns a fixed response stream if keywords detected
- Delegates to the wrapped LLM otherwise

This approach is superior to:
- Subclassing specific LLM types (inflexible, tied to one implementation)
- Creating a brand-new LLM from scratch (unnecessary duplication)
- Modifying session handler (violates single responsibility)

## Critical Files

### Files to Create
1. `src/keyword_intercept_llm.py` - New wrapper LLM implementation
2. `tests/test_keyword_intercept.py` - Tests for keyword interception behavior

### Files to Modify
1. `src/factories.py` - Update `create_llm()` to support keyword interception
2. `src/config.py` - Add configuration for keyword interception feature

## Detailed Implementation Steps

### Step 1: Create KeywordInterceptLLM Wrapper
**File: `src/keyword_intercept_llm.py`**

- Create `KeywordInterceptLLM` class extending `livekit.agents.llm.LLM`
  - Constructor accepts:
    - `wrapped_llm`: The actual LLM to delegate to
    - `keywords`: List of keywords to intercept (default: fruit words)
    - `response_text`: Text to return when keywords detected (default: "I don't like fruit")
  - Override `chat()` method to:
    - Extract latest user message from `ChatContext`
    - Check if message contains any keywords (case-insensitive)
    - If match: return `KeywordInterceptStream` with fixed response
    - Else: delegate to `wrapped_llm.chat()`
  - Implement properties: `model`, `provider` (delegate to wrapped LLM)

- Create `KeywordInterceptStream` class extending `livekit.agents.llm.LLMStream`
  - Similar pattern to `SimpleMockLLMStream` in `mock_llm.py`
  - Streams the fixed response text as chunks
  - Includes realistic timing (ttft delay)

**Key Implementation Detail:**
Extract user's latest message from ChatContext:
```python
def _get_latest_user_message(self, chat_ctx: ChatContext) -> str:
    """Extract the most recent user message from chat context."""
    for msg in reversed(chat_ctx.messages):
        if msg.role == "user":
            return msg.content
    return ""
```

### Step 2: Update Configuration
**File: `src/config.py`**

Add to `PipelineConfig`:
```python
# Keyword interception configuration
enable_keyword_intercept: bool = Field(
    default=False,
    description="Enable keyword interception for LLM responses",
)
intercept_keywords: list[str] = Field(
    default_factory=lambda: ["cherries", "cherry", "banana", "apple", "fruit"],
    description="Keywords that trigger interception",
)
intercept_response: str = Field(
    default="I don't like fruit",
    description="Response to return when keywords are detected",
)
```

### Step 3: Update LLM Factory
**File: `src/factories.py`**

Update `create_llm()` function:
```python
def create_llm(config: PipelineConfig) -> inference.LLM | SimpleMockLLM:
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
        from keyword_intercept_llm import KeywordInterceptLLM
        logger.info("Wrapping LLM with keyword interceptor")
        return KeywordInterceptLLM(
            wrapped_llm=base_llm,
            keywords=config.intercept_keywords,
            response_text=config.intercept_response,
        )

    return base_llm
```

### Step 4: Write Comprehensive Tests (TDD)
**File: `tests/test_keyword_intercept.py`**

Test cases to implement:
1. **Test keyword detection** - Each fruit keyword triggers fixed response
   - Test "cherries", "cherry", "banana", "apple", "fruit"
   - Case-insensitive matching ("APPLE", "Cherry", "FruIT")

2. **Test delegation** - Non-keyword input goes to wrapped LLM
   - Input like "Hello" or "What's the weather?" should use actual LLM

3. **Test with mock LLM** - Verify wrapping works with SimpleMockLLM

4. **Test response content** - Fixed response is exactly "I don't like fruit"

5. **Test in context** - Keywords embedded in sentences trigger interception
   - "I love cherries" → fixed response
   - "Can you tell me about bananas?" → fixed response

6. **Integration test** - Full agent session with keyword intercept enabled

Example test structure:
```python
@pytest.mark.asyncio
async def test_intercepts_fruit_keywords():
    """Test that fruit keywords trigger fixed response."""
    base_llm = SimpleMockLLM(response_text="I would normally respond")
    intercept_llm = KeywordInterceptLLM(
        wrapped_llm=base_llm,
        keywords=["fruit", "apple"],
        response_text="I don't like fruit",
    )

    async with AgentSession(llm=intercept_llm) as session:
        await session.start(Assistant())
        result = await session.run(user_input="I love apples")

        # Verify exact response
        await (
            result.expect.next_event()
            .is_message(role="assistant")
            .has_content("I don't like fruit")
        )
```

### Step 5: Update app.py for Testing
**File: `src/app.py`**

Modify the main block to enable keyword interception:
```python
if __name__ == "__main__":
    config = AppConfig(
        pipeline=PipelineConfig(
            llm_model="mock",  # or your preferred LLM
            enable_keyword_intercept=True,
        )
    )
    app = VoiceAgentApp(config=config)
    app.run()
```

## Verification Steps

1. **Run tests**: `uv run pytest tests/test_keyword_intercept.py -v`
   - All keyword interception tests should pass

2. **Run existing tests**: `uv run pytest`
   - Ensure no regressions in existing functionality

3. **Console testing**: `uv run python src/app.py console`
   - Say "I love cherries" → should get "I don't like fruit"
   - Say "What's the weather?" → should get normal LLM response
   - Test case variations (uppercase, embedded in sentences)

4. **Code quality**:
   - Run formatter: `uv run ruff format`
   - Run linter: `uv run ruff check`

## Configuration Options

Users can customize via environment variables or code:
```python
# Enable via code
config = AppConfig(
    pipeline=PipelineConfig(
        enable_keyword_intercept=True,
        intercept_keywords=["custom", "keywords"],
        intercept_response="Custom response text",
    )
)

# Or via environment (if added to config)
# PIPELINE__ENABLE_KEYWORD_INTERCEPT=true
# PIPELINE__INTERCEPT_KEYWORDS=["word1","word2"]
# PIPELINE__INTERCEPT_RESPONSE="Custom response"
```

## Design Decisions

1. **Why wrapper pattern?**
   - Works with ANY LLM (inference.LLM, SimpleMockLLM, future LLMs)
   - No code duplication
   - Easy to enable/disable via configuration
   - Maintains clean separation of concerns

2. **Why check in chat() method?**
   - Access to full ChatContext
   - Can examine user message before LLM processing
   - Natural interception point in the flow

3. **Why case-insensitive substring matching?**
   - User voice input may have inconsistent capitalization from STT
   - Substring matching is simpler and more robust (catches "I love cherries")
   - No need for complex word boundary logic

4. **Why configurable keywords/response?**
   - Extensible for other use cases beyond fruit
   - Easy to customize without code changes
   - Testable with different configurations
