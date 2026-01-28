# Plan: Fix Drive-Thru Agent Responsiveness Issue

## Problem Summary

The McDonald's drive-thru agent connects successfully and plays the initial greeting, but then becomes unresponsive to user input. After thorough exploration, the **root cause** has been identified:

**Critical Bug:** The `DriveThruAgent` class creates order management tools but fails to pass them to the LiveKit `Agent` base class constructor. This prevents the LLM from accessing the tools needed to take orders.

## Root Cause Analysis

### Location
`/Users/seanreed/PythonProjects/voice-ai/lk-agent-1/src/drive_thru_agent.py:51`

### The Bug
```python
# Current code (BROKEN):
super().__init__(instructions=self._get_instructions())
# Tools are created at line 64-66 but never passed to parent class
```

### Why This Breaks Conversation Flow
1. The greeting works because it's sent directly via `session.say()` in `agent.py:94`
2. When user responds, `AgentSession` tries to call the LLM with available tools
3. Since agent was initialized without tools, the LLM has no access to:
   - `add_item_to_order`
   - `complete_order`
   - `remove_item_from_order`
4. The agent cannot fulfill its core ordering responsibility
5. The LLM likely produces generic responses or enters an error state

## Implementation Plan

### Phase 1: Fix Tool Registration (CRITICAL)

**File:** `src/drive_thru_agent.py`

**Change at line 51:**
```python
# Before:
super().__init__(instructions=self._get_instructions())

# After:
super().__init__(
    instructions=self._get_instructions(),
    tools=self._tools  # Pass tools to parent Agent class
)
```

**Note:** The tools must be created BEFORE the `super().__init__()` call, so we need to reorder the initialization:

```python
def __init__(
    self,
    llm: DriveThruLLM,
    menu_provider: MenuProvider,
    session_id: str,
) -> None:
    """Initialize the drive-thru agent."""
    # Create dependencies first
    self._llm = llm
    self._menu_provider = menu_provider
    self._order_state = OrderStateManager(session_id=session_id)

    # Create tools BEFORE calling super().__init__()
    self._tools = create_order_tools(
        order_state=self._order_state,
        menu_provider=self._menu_provider,
    )

    # Now initialize parent Agent with tools
    super().__init__(
        instructions=self._get_instructions(),
        tools=self._tools  # PASS TOOLS HERE
    )
```

### Phase 2: Add Diagnostic Logging

**File:** `src/drive_thru_agent.py`

Add logging after tool creation to verify tools are properly initialized:

```python
import logging

logger = logging.getLogger(__name__)

# In __init__, after creating tools:
logger.info(f"Created {len(self._tools)} tools for drive-thru agent")
for tool in self._tools:
    logger.info(f"  - Tool: {tool.name}")
```

**File:** `src/agent.py`

Add logging when agent session starts to verify the agent has tools:

```python
# After creating drive_thru_agent (around line 65):
logger.info(f"Agent has {len(drive_thru_agent.tools)} tools available")
```

### Phase 3: Verify Agent Instructions

**File:** `src/drive_thru_agent.py`

Review the `_get_instructions()` method (lines 68-91) to ensure it correctly references the available tools. The instructions should explicitly mention the tools by name to help the LLM understand when to use them.

Current instructions should already reference:
- Adding items to the order
- Confirming items as they're added
- Reading back the complete order

Verify these instructions align with the tool names:
- `add_item_to_order`
- `complete_order`
- `remove_item_from_order`

### Phase 4: Testing Strategy

#### Test 1: Console Mode (Basic Tool Registration)
```bash
uv run python src/agent.py console
```

**Expected behavior:**
- Agent greets with "Welcome to McDonald's! What can I get for you today?"
- User types: "I'd like a Big Mac"
- Agent should call `add_item_to_order` tool and respond with confirmation
- Check logs for tool creation messages

#### Test 2: Dev Mode (Full Voice Pipeline)
```bash
uv run python src/agent.py dev
```

**Expected behavior:**
- Agent connects to LiveKit room
- User speaks an order via meet.livekit.io
- Agent transcribes via STT, processes with LLM + tools, responds via TTS
- Order is added and confirmed

#### Test 3: Order Completion Flow
Test the full ordering workflow:
1. Add multiple items: "Big Mac, large fries, and a Coke"
2. Agent should call `add_item_to_order` multiple times
3. Say "That's all" or "Complete my order"
4. Agent should call `complete_order` tool
5. Verify `orders/{session_id}/final_order.json` is created

#### Test 4: Error Handling
Test edge cases:
1. Request invalid item: "I'd like a Whopper" (Burger King item)
2. Agent should respond that item isn't available
3. Remove an item: "Actually, remove the fries"
4. Agent should call `remove_item_from_order` tool

## Critical Files

| File | Lines | Changes |
|------|-------|---------|
| `src/drive_thru_agent.py` | 35-66 | Reorder initialization, pass tools to parent |
| `src/drive_thru_agent.py` | 68-91 | Verify instructions reference tool names |
| `src/agent.py` | 65 | Add logging to verify agent has tools |

## Verification Checklist

- [ ] Tools are created before `super().__init__()` call
- [ ] Tools are passed to parent Agent class via `tools` parameter
- [ ] Logging confirms tools are registered
- [ ] Console mode test: agent can add items via typed commands
- [ ] Dev mode test: agent can hear and respond to voice orders
- [ ] Order completion flow works end-to-end
- [ ] Order JSON files are created in `orders/` directory
- [ ] Error handling works for invalid items

## Expected Outcome

After this fix:
1. Agent will greet user as before
2. When user speaks an order, the LLM will have access to ordering tools
3. Agent will call `add_item_to_order` to add items
4. Agent will call `complete_order` to finalize the order
5. Order will be saved as JSON in `orders/{session_id}/`

## Additional Notes

- The turn detection (`MultilingualModel`) and VAD (Silero) configurations appear correct
- STT (AssemblyAI), LLM (GPT-4.1-nano), and TTS (Inworld) configurations are properly set up
- The `DriveThruLLM` wrapper correctly injects menu context into conversations
- No changes needed to session handling or audio pipeline—the core issue is tool registration

## Success Criteria

1. Agent can successfully process voice orders in dev mode
2. Tools are called correctly (visible in logs and tool execution)
3. Orders are saved to JSON files
4. User receives verbal confirmation after each item is added
5. Complete order flow works from greeting to order completion
