# Fix Missing item_name Parameter in Tool Calls

> **Status:** DRAFT

## Table of Contents

- [Overview](#overview)
- [Current State Analysis](#current-state-analysis)
- [Root Cause Analysis](#root-cause-analysis)
- [Desired End State](#desired-end-state)
- [What We're NOT Doing](#what-were-not-doing)
- [Implementation Approach](#implementation-approach)
- [Dependencies](#dependencies)
- [Phase 1: Improve Tool Schema and Instructions](#phase-1-improve-tool-schema-and-instructions)
- [Phase 2: Add Runtime Validation](#phase-2-add-runtime-validation)
- [Phase 3: Add E2E Test Coverage](#phase-3-add-e2e-test-coverage)
- [Testing Strategy](#testing-strategy)
- [References](#references)

## Overview

The LLM (gpt-4.1-nano) is intermittently calling the `add_item_to_order` tool without the required `item_name` parameter, causing a `TypeError: missing a required argument: 'item_name'` error. This happens specifically when the user declines modifiers (e.g., says "No thank you" after being asked about modifications).

The error occurs in the LiveKit Agents SDK when binding function arguments, before our tool code even executes.

## Current State Analysis

### Error Flow
```
1. User: "Can I have a big mac with extra onions"
2. Agent asks: "Would you like to add any other modifications to the big mac?"
3. User: "No thank you"
4. LLM incorrectly calls: add_item_to_order() with NO parameters
5. LiveKit SDK throws: TypeError: missing a required argument: 'item_name'
```

### Key Files
- `src/tools/order_tools.py:48-100` - Tool definition with schema
- `src/drive_thru_agent.py:80-139` - Agent instructions
- `src/config.py:36-38` - LLM model config (gpt-4.1-nano)

### What's Already in Place
- Tool schema explicitly marks `item_name` as required (line 97)
- Schema description emphasizes "REQUIRED" and "MANDATORY" (lines 73-76)
- Agent instructions include examples of correct behavior (lines 104-129)
- Agent instructions say "NEVER call add_item_to_order without item_name" (line 133)
- Tests verify the schema is correct (`test_add_item_requires_item_name_in_schema`)

### Key Discovery
The problem is NOT in our code - the schema and instructions are correct. The issue is that:
1. **gpt-4.1-nano is a smaller model** with less reliable tool-calling behavior
2. The LLM misinterprets "No thank you" as a signal to call the tool without remembering the context
3. The error happens at the SDK level, not in our tool code

## Root Cause Analysis

The root cause is **LLM behavior** combined with **lack of defensive runtime validation**:

1. **LLM Model Limitation**: gpt-4.1-nano is a smaller, faster model that may not reliably follow complex tool schemas
2. **Conversational Context Loss**: When user says "No thank you", the LLM loses track that it was asking about an item that hasn't been added yet
3. **No Runtime Defense**: If the LLM sends bad parameters, the error crashes in the SDK before we can handle it gracefully

## Desired End State

**Success Criteria:**
- [ ] Agent correctly adds items when user declines modifiers
- [ ] No `TypeError: missing a required argument` errors in production
- [ ] If LLM sends bad tool call, agent recovers gracefully (doesn't crash)
- [ ] E2E tests verify the "decline modifiers" flow works correctly

**How to Verify:**
1. Run `make console` and test the conversation:
   - "Can I have a Big Mac"
   - "No thanks" (when asked about modifiers)
   - Order should have one Big Mac
2. Run `uv run pytest tests/ -v` - all tests pass
3. No errors in logs during normal conversation flow

## What We're NOT Doing

- **Changing LLM models**: This would be a separate decision (cost/latency tradeoffs)
- **Modifying LiveKit SDK**: We work within the SDK constraints
- **Adding complex retry logic**: Keep it simple with validation
- **Implementing semantic search**: Out of scope for this fix

## Implementation Approach

We'll use a **defense-in-depth** strategy:

1. **Layer 1**: Improve instructions/schema to guide LLM better
2. **Layer 2**: Add runtime parameter validation before SDK binds arguments
3. **Layer 3**: Add E2E test coverage for the specific failure case

The key insight is that we can use LiveKit's `@function_tool` wrapper to intercept calls before the SDK validates them.

## Dependencies

**Execution Order:**

1. Phase 1 (no dependencies) - Improve prompts/schema
2. Phase 2 (no dependencies) - Add runtime validation
3. Phase 3 (depends on Phase 1 & 2) - Add E2E tests

**Parallelization:**
- Phase 1 and Phase 2 can run in parallel (independent changes)
- Phase 3 must wait for Phase 1 and Phase 2

---

## Phase 1: Improve Tool Schema and Instructions

### Overview
Enhance the tool schema and agent instructions to more strongly guide the LLM toward correct behavior.

### Context
Before starting, read these files:
- `src/tools/order_tools.py` - current tool schema
- `src/drive_thru_agent.py` - current agent instructions

### Dependencies
**Depends on:** None
**Required by:** Phase 3

### Changes Required

#### 1.1: Enhance Tool Schema Description
**File:** `src/tools/order_tools.py`

**Changes:**
Update the `raw_schema` description to be even more explicit about the required workflow:

```python
@function_tool(
    name="add_item_to_order",
    description=(
        "Add a menu item to the customer's order. "
        "REQUIRES item_name - this tool CANNOT be called without it. "
        "If user declines modifiers, call with item_name and empty modifiers list."
    ),
    raw_schema={
        "name": "add_item_to_order",
        "description": (
            "Add a menu item to the order. This tool MUST be called with item_name. "
            "WORKFLOW: "
            "1. Customer says item name -> remember it "
            "2. Ask about modifiers "
            "3. Customer responds -> call this tool with item_name, modifiers (can be []), quantity "
            "IMPORTANT: If customer says 'No thanks' to modifiers, call with the remembered item_name and modifiers=[]"
        ),
        "parameters": {
            "type": "object",
            "properties": {
                "item_name": {
                    "type": "string",
                    "description": (
                        "REQUIRED. The menu item name the customer wants. "
                        "This MUST be provided. If you asked about modifiers and "
                        "customer declined, use the item name from earlier in the conversation."
                    ),
                },
                # ... rest unchanged
            },
            "required": ["item_name"],
        },
    },
)
```

**Rationale:** More explicit workflow description helps smaller models follow the correct sequence.

#### 1.2: Add Explicit "No Thanks" Handling to Instructions
**File:** `src/drive_thru_agent.py`

**Changes:**
Add a specific example for the "decline modifiers" case to the instructions:

```python
"""
CRITICAL: When customer declines modifiers ("No thanks", "No", "That's it"):
- You MUST still call add_item_to_order with the item name they mentioned earlier
- Use modifiers=[] (empty list) when they don't want modifications
- Example:
  - User: "I want a Big Mac"
  - You: "Would you like any modifications?"
  - User: "No thanks"
  - You call: add_item_to_order(item_name="Big Mac", modifiers=[], quantity=1)
  - NEVER call: add_item_to_order() without item_name - this will fail!
"""
```

**Rationale:** Explicit counter-example helps prevent the specific failure mode.

### Success Criteria

#### Automated Verification:
- [ ] Lint passes: `uv run ruff check src/tools/order_tools.py src/drive_thru_agent.py`
- [ ] Existing tests pass: `uv run pytest tests/test_order_tools.py tests/test_drive_thru_agent_integration.py -v`

#### Manual Verification:
- [ ] Run `make console` and test the "decline modifiers" flow 3 times - should work consistently

---

## Phase 2: Add Runtime Validation

### Overview
Add defensive validation in the tool function to catch invalid parameters before they cause cryptic errors.

### Context
Before starting, read these files:
- `src/tools/order_tools.py` - current tool implementation
- LiveKit Agents `function_tool` documentation for understanding wrapper behavior

### Dependencies
**Depends on:** None
**Required by:** Phase 3

### Changes Required

#### 2.1: Add Parameter Validation to add_item_to_order
**File:** `src/tools/order_tools.py`

**Changes:**
Unfortunately, we cannot validate BEFORE the LiveKit SDK binds arguments - the error happens in `prepare_function_arguments()` before our code runs.

However, we can improve the error message by catching the TypeError at a higher level, or we can explore if LiveKit supports a pre-validation hook.

**Alternative approach**: Make `item_name` have a default value and validate in the function body:

```python
async def add_item_to_order(
    item_name: str | None = None,  # Make optional at Python level
    modifiers: list[str] | None = None,
    quantity: int = 1,
) -> str:
    # Validate required parameter
    if not item_name:
        logger.error("add_item_to_order called without item_name - LLM error")
        return (
            "I need to know which item you'd like to add. "
            "What would you like to order?"
        )

    # ... rest of function unchanged
```

**Important**: This requires also updating the schema to not mark item_name as required:
```python
"required": [],  # Remove item_name from required, handle in code
```

**Rationale:** This allows the function to receive the call and respond gracefully instead of crashing.

**Trade-off:** This is a bit of a hack - ideally the LLM would always provide required parameters. But this provides a graceful fallback.

#### 2.2: Add Logging for Diagnostic Purposes
**File:** `src/tools/order_tools.py`

**Changes:**
Add logging at the start of the function to help diagnose issues:

```python
async def add_item_to_order(...) -> str:
    logger.debug(
        f"add_item_to_order called: item_name={item_name!r}, "
        f"modifiers={modifiers!r}, quantity={quantity!r}"
    )

    if not item_name:
        logger.warning(
            "LLM called add_item_to_order without item_name - "
            "prompting user for item"
        )
        return "I need to know which item you'd like. What would you like to order?"
```

**Rationale:** Helps debug production issues and understand LLM behavior patterns.

### Success Criteria

#### Automated Verification:
- [ ] Lint passes: `uv run ruff check src/tools/order_tools.py`
- [ ] New test passes: Test that calling `add_item_to_order(item_name=None)` returns graceful error
- [ ] Existing tests still pass: `uv run pytest tests/test_order_tools.py -v`

#### Manual Verification:
- [ ] If LLM sends bad tool call, agent responds gracefully (no crash)
- [ ] Check logs show the warning message when this happens

---

## Phase 3: Add E2E Test Coverage

### Overview
Add end-to-end test that specifically covers the "decline modifiers" conversation flow.

### Context
Before starting, read these files:
- `tests/test_drive_thru_agent_integration.py` - existing integration tests
- `tests/conftest.py` - shared fixtures

### Dependencies
**Depends on:** Phase 1, Phase 2
**Required by:** None

### Changes Required

#### 3.1: Add Test for Missing item_name Graceful Handling
**File:** `tests/test_order_tools.py`

**Changes:**
Add a test that verifies the tool handles missing item_name gracefully:

```python
@pytest.mark.asyncio
async def test_add_item_handles_missing_item_name_gracefully(order_tools):
    """
    Test that add_item_to_order returns helpful message when item_name is missing.

    This tests the defensive validation added to handle LLM misbehavior where
    it calls the tool without the required item_name parameter.
    """
    add_item_tool = order_tools[0]

    # Call without item_name (simulating LLM error)
    result = await add_item_tool(item_name=None)

    # Should return helpful message, not crash
    assert "need to know" in result.lower() or "which item" in result.lower()

    # Should NOT have added anything to the order
    # (This is verified by the order_state fixture being empty)
```

**Rationale:** Ensures our defensive validation works correctly.

#### 3.2: Update Existing Test Expectations
**File:** `tests/test_order_tools.py`

**Changes:**
If we changed item_name to be optional in the function signature, we need to update the test that verifies the signature:

```python
@pytest.mark.asyncio
async def test_add_item_requires_item_name_in_schema(order_tools):
    """
    Verify that add_item_to_order tool handles missing item_name gracefully.

    Note: item_name is validated in the function body rather than the schema
    to allow graceful error handling when LLM sends invalid calls.
    """
    add_item_tool = order_tools[0]

    # Verify the tool can be called without item_name (for graceful handling)
    result = await add_item_tool(item_name=None)

    # Should return a helpful message
    assert isinstance(result, str)
    assert "need" in result.lower() or "item" in result.lower()
```

**Rationale:** Tests should match the new behavior.

### Success Criteria

#### Automated Verification:
- [ ] All tests pass: `uv run pytest tests/test_order_tools.py tests/test_drive_thru_agent_integration.py -v`
- [ ] New test specifically passes: `uv run pytest tests/test_order_tools.py::test_add_item_handles_missing_item_name_gracefully -v`

#### Manual Verification:
- [ ] Run the full test suite: `uv run pytest`
- [ ] Manually test in console mode to verify the fix works in practice

---

## Testing Strategy

### Unit Tests:
- Test `add_item_to_order(item_name=None)` returns graceful error message
- Test `add_item_to_order(item_name="")` returns graceful error message
- Existing tests continue to pass with valid parameters

### Integration Tests:
- Test that agent tools are created correctly
- Test that the full order flow still works

### Manual Testing Steps:
1. Run `make console`
2. Say "I want a Big Mac"
3. When asked about modifiers, say "No thanks"
4. Verify agent confirms the Big Mac was added (not an error)
5. Say "That's all"
6. Verify order is complete with one Big Mac

## Alternative Approaches Considered

### Option A: Change LLM Model (Not Recommended)
- Use a larger model like gpt-4o instead of gpt-4.1-nano
- **Pro**: More reliable tool calling
- **Con**: Higher latency, higher cost
- **Verdict**: Not worth it for this specific issue - defensive validation is cheaper

### Option B: Structured Output Mode (Future Consideration)
- Use OpenAI's structured output mode if available
- **Pro**: Guarantees schema compliance
- **Con**: Not sure if LiveKit Agents supports this directly
- **Verdict**: Worth investigating but out of scope for this fix

### Option C: Retry Logic (Not Recommended)
- Catch the error and retry the LLM call
- **Pro**: Might get correct result on retry
- **Con**: Adds latency, complexity, may still fail
- **Verdict**: Better to handle gracefully than retry

## Performance Considerations

The changes in this plan have minimal performance impact:
- Phase 1: No runtime impact (just schema/instruction changes)
- Phase 2: One extra `if` check per tool call (nanoseconds)
- Phase 3: Test-only, no production impact

## References

- Error trace from user's console run (provided in task)
- `src/tools/order_tools.py:48-100` - current tool definition
- `src/drive_thru_agent.py:80-139` - current agent instructions
- `tests/test_order_tools.py:475-512` - existing schema validation test
- `tests/test_drive_thru_agent_integration.py:289-371` - existing integration tests for this issue
