# Plan: Fix Console Mode Implementation

**Date:** 2026-01-27
**Status:** ✅ Implemented - Option 1 Complete
**Priority:** High - Blocking console testing

---

## Problem Summary

The console mode in `src/agent.py` is using an outdated LiveKit Agents API that has changed significantly. The current implementation has three critical errors:

### Error 1: Incorrect `AgentsConsole` API Usage
```python
# Current (BROKEN):
console = AgentsConsole(session)  # ❌ TypeError: takes 1 positional argument but 2 were given
await console.arun()              # ❌ AttributeError: no 'arun' method exists
```

### Error 2: Missing HTTP Session Context
```
RuntimeError: Attempted to use an http session outside of a job context.
You may need to create your own aiohttp.ClientSession, pass it into
the plugin constructor as a kwarg, and manage its lifecycle.
```

### Error 3: Cascading AttributeError
```
AttributeError: 'SpeechStream' object has no attribute '_session'
```

---

## Root Cause Analysis

The LiveKit Agents SDK has fundamentally changed how console mode works:

### Old API (What our code attempts):
```python
console = AgentsConsole(session)
await console.arun()
```

### New API (Current LiveKit SDK):
```python
# AgentsConsole is now a singleton with no constructor arguments
console = AgentsConsole.get_instance()
console.enabled = True
console.console_mode = "audio"  # or "text"

# The console automatically integrates with AgentSession.start()
# via the acquire_io() method - no manual wiring needed
```

### How Console Mode Actually Works Now

1. **Singleton Pattern**: `AgentsConsole.get_instance()` returns a shared instance
2. **Property-based Configuration**: Set `enabled`, `console_mode`, `record` properties
3. **Automatic Integration**: When `AgentSession.start()` is called, it checks:
   ```python
   c = cli.AgentsConsole.get_instance()
   if c.enabled and not c.io_acquired:
       c.acquire_io(loop=self._loop, session=self)
   ```
4. **CLI Framework Handles Lifecycle**: The LiveKit CLI runs event loops for audio/text modes

---

## Solution Options

### Option 1: Use LiveKit CLI Framework (Recommended)

**Approach**: Remove custom console implementation and use the built-in CLI command.

**Changes Required**:

#### 1.1 Remove Custom Console Command

**File**: `src/agent.py`

**Current Code (lines 115-160):**
```python
@agent_cli.command()
def console():
    """Run drive-thru agent in console mode for testing."""

    async def run_console():
        # Load configuration
        config = AppConfig()

        # Create session handler
        handler = DriveThruSessionHandler(config)

        # Create agent for console session
        session_id = str(uuid4())
        logger.info(f"Starting console session: {session_id}")

        drive_thru_agent = await handler.create_agent(session_id)

        # Verify agent has tools registered
        logger.info(f"Agent has {len(drive_thru_agent.tools)} tools available")

        # Create voice pipeline components
        stt = create_stt(config.pipeline)
        tts = create_tts(config.pipeline)

        # Create AgentSession with drive-thru LLM
        # Console mode doesn't support MultilingualModel (requires job context)
        turn_detection = NOT_GIVEN

        session = AgentSession(
            stt=stt,
            llm=drive_thru_agent.llm,  # Use the DriveThruLLM
            tts=tts,
            turn_detection=turn_detection,
            preemptive_generation=config.session.preemptive_generation,
        )

        # Start session with the agent
        await session.start(agent=drive_thru_agent)

        # Run console
        logger.info("Console ready. Start speaking to the agent.")
        console = AgentsConsole(session)  # ❌ BROKEN
        await console.arun()              # ❌ BROKEN

    # Run the async console
    asyncio.run(run_console())
```

**New Code:**
```python
# REMOVE the @agent_cli.command() console function entirely
# Users will use: uv run python src/agent.py console (via LiveKit CLI integration)
```

#### 1.2 Update Makefile

**File**: `Makefile`

**Current:**
```makefile
console:
	@echo "$(BLUE)Starting drive-thru agent in console mode...$(RESET)"
	uv run python src/agent.py console
```

**New:**
```makefile
console:
	@echo "$(BLUE)Starting drive-thru agent in console mode...$(RESET)"
	uv run lk agent console
```

**Pros**:
- Uses official, maintained API
- Gets all LiveKit console features (frequency visualizer, text/audio toggle, recording)
- No need to manage HTTP sessions manually
- Automatic device selection and management

**Cons**:
- Requires understanding of LiveKit CLI architecture
- Less control over console behavior
- May need to adjust server setup

---

### Option 2: Fix Custom Implementation (Not Recommended)

**Approach**: Keep custom console but fix the API usage and add HTTP session management.

**Changes Required**:

#### 2.1 Add HTTP Session Management

**File**: `src/agent.py`

**Current Code (lines 136-137):**
```python
stt = create_stt(config.pipeline)
tts = create_tts(config.pipeline)
```

**New Code:**
```python
import aiohttp

# Create HTTP session for plugins
http_session = aiohttp.ClientSession()

try:
    # Pass http_session to factories
    stt = create_stt(config.pipeline, http_session=http_session)
    tts = create_tts(config.pipeline, http_session=http_session)

    # ... rest of console code ...

finally:
    await http_session.close()
```

#### 2.2 Update Factory Functions

**File**: `src/factories.py`

**Current Code:**
```python
def create_stt(config: PipelineConfig) -> assemblyai.STT:
    logger.info(f"Creating STT with model: {config.stt_model}, lang: {config.stt_lang}")
    return assemblyai.STT(
        model=config.stt_model,
        language=config.stt_lang,
    )

def create_tts(config: PipelineConfig) -> inference.TTS:
    logger.info(
        f"Creating TTS with model: {config.tts_model}, voice: {config.tts_voice}"
    )
    return inference.TTS(
        model=config.tts_model,
        voice=config.tts_voice,
    )
```

**New Code:**
```python
from typing import Optional
import aiohttp

def create_stt(
    config: PipelineConfig,
    http_session: Optional[aiohttp.ClientSession] = None
) -> assemblyai.STT:
    logger.info(f"Creating STT with model: {config.stt_model}, lang: {config.stt_lang}")
    kwargs = {
        "model": config.stt_model,
        "language": config.stt_lang,
    }
    if http_session is not None:
        kwargs["http_session"] = http_session
    return assemblyai.STT(**kwargs)

def create_tts(
    config: PipelineConfig,
    http_session: Optional[aiohttp.ClientSession] = None
) -> inference.TTS:
    logger.info(
        f"Creating TTS with model: {config.tts_model}, voice: {config.tts_voice}"
    )
    kwargs = {
        "model": config.tts_model,
        "voice": config.tts_voice,
    }
    if http_session is not None:
        kwargs["http_session"] = http_session
    return inference.TTS(**kwargs)
```

#### 2.3 Fix AgentsConsole Usage

**File**: `src/agent.py`

**Current Code (lines 155-157):**
```python
logger.info("Console ready. Start speaking to the agent.")
console = AgentsConsole(session)  # ❌ BROKEN
await console.arun()              # ❌ BROKEN
```

**New Code:**
```python
# Enable console mode
console = AgentsConsole.get_instance()
console.enabled = True
console.console_mode = "audio"

logger.info("Console ready. Start speaking to the agent.")

# Start session - console will automatically attach via acquire_io()
await session.start(agent=drive_thru_agent)

# Keep session running until interrupted
try:
    while True:
        await asyncio.sleep(1.0)
except KeyboardInterrupt:
    logger.info("Console session interrupted by user")
```

**Pros**:
- More control over console behavior
- Can customize the experience

**Cons**:
- Requires maintaining custom code as LiveKit SDK evolves
- Need to manually handle HTTP sessions
- Miss out on LiveKit's built-in console features (visualizer, device management, etc.)
- More complex error handling

---

## Recommendation

**Use Option 1 (LiveKit CLI Framework)** because:

1. **Official Support**: Uses the maintained LiveKit CLI infrastructure
2. **Feature Complete**: Gets frequency visualizer, device selection, recording, text/audio toggle
3. **Less Maintenance**: No need to track SDK changes
4. **HTTP Session Handled**: No manual lifecycle management needed
5. **Simpler Code**: Less code to maintain

## Implementation Steps (Option 1 - Recommended)

### Step 1: Verify LiveKit CLI Integration

Check if the existing `start()` command properly integrates with LiveKit's CLI framework:

**File**: `src/agent.py` (lines 163-169)

```python
@agent_cli.command()
def dev():
    """Run drive-thru agent in dev mode with LiveKit connection."""
    # Create server
    server = create_server()

    # Use LiveKit CLI - this should provide 'console' command automatically
    cli = server.cli
    cli()
```

The `server.cli` should already provide the `console` command. Test with:
```bash
uv run python src/agent.py --help
```

### Step 2: Remove Custom Console Function

Delete lines 115-160 in `src/agent.py`:
```python
# DELETE THIS ENTIRE FUNCTION:
@agent_cli.command()
def console():
    ...
```

### Step 3: Update Documentation

**File**: `README.md`

Update console mode instructions:

**Current:**
```markdown
#### Console Mode (Testing)

Test the agent directly in your terminal:

```bash
uv run python src/agent.py console
```

**New:**
```markdown
#### Console Mode (Testing)

Test the agent directly in your terminal using LiveKit's built-in console:

```bash
uv run python src/agent.py console
```

Options:
- `--text`: Start in text mode instead of audio mode
- `--input-device DEVICE`: Select input audio device
- `--output-device DEVICE`: Select output audio device
- `--list-devices`: Show available audio devices
- `--record`: Record the session to disk

Example with text mode:
```bash
uv run python src/agent.py console --text
```

To toggle between text and audio mode during a session, press `Ctrl+T`.
```

### Step 4: Update Makefile

**File**: `Makefile`

**Current:**
```makefile
console:
	@echo "$(BLUE)Starting drive-thru agent in console mode...$(RESET)"
	uv run python src/agent.py console
```

**Keep as-is** (the command should work once we use LiveKit's CLI)

### Step 5: Test the Integration

```bash
# List available commands
uv run python src/agent.py --help

# Test console mode
uv run python src/agent.py console

# Test with text mode
uv run python src/agent.py console --text
```

---

## Alternative: If LiveKit CLI Not Integrated

If `server.cli` doesn't automatically provide the console command, we need to explicitly integrate it:

**File**: `src/agent.py`

**Current (lines 163-171):**
```python
@agent_cli.command()
def dev():
    """Run drive-thru agent in dev mode with LiveKit connection."""
    # Create server
    server = create_server()

    # Use LiveKit CLI
    cli = server.cli
    cli()
```

**New:**
```python
# Remove all custom Click commands and use LiveKit CLI exclusively
if __name__ == "__main__":
    # Create server
    server = create_server()

    # Use LiveKit's built-in CLI (includes console, start, dev commands)
    server.cli()
```

This would mean removing all custom `@agent_cli.command()` decorators and using LiveKit's CLI directly.

---

## Testing Plan

1. **Verify CLI Help**:
   ```bash
   uv run python src/agent.py --help
   ```
   Expected: See `console`, `start`, `dev` commands

2. **Test Audio Console**:
   ```bash
   uv run python src/agent.py console
   ```
   Expected: Microphone/speaker selection, audio input visualization

3. **Test Text Console**:
   ```bash
   uv run python src/agent.py console --text
   ```
   Expected: Text-based chat interface

4. **Test Device Listing**:
   ```bash
   uv run python src/agent.py console --list-devices
   ```
   Expected: List of available audio input/output devices

5. **Test Mode Toggle**:
   - Start in audio mode
   - Press `Ctrl+T`
   - Expected: Switch to text mode

6. **Test Order Flow**:
   - Start console
   - Say "I'd like a Big Mac"
   - Expected: Agent responds with confirmation and menu search

---

## Files Modified

- `src/agent.py` - Removed custom Click CLI commands, switched to LiveKit's `cli.run_app(server)`
- `README.md` - Updated console mode documentation with LiveKit CLI options
- `AGENTS.md` - Added comprehensive CLI Framework section documenting required pattern
- `Makefile` - No changes needed (command stays the same)

---

## Risks & Mitigations

| Risk | Impact | Mitigation |
|------|--------|------------|
| LiveKit CLI not integrated properly | High - Console won't work | Verify `server.cli` provides console command before removing custom code |
| HTTP session errors persist | Medium - STT/TTS may fail | LiveKit CLI should handle this automatically, but verify |
| Loss of custom console features | Low - May lose specific customizations | Document any custom features before removing |

---

## Success Criteria

- [x] `uv run python src/agent.py console` launches successfully
- [ ] Audio input/output devices are selectable (manual test required)
- [ ] Frequency visualizer displays microphone input (manual test required)
- [ ] Agent responds to spoken commands (manual test required)
- [ ] Order tracking works in console mode (manual test required)
- [ ] `Ctrl+T` toggles between audio and text modes (manual test required)
- [x] No HTTP session errors in logs

---

## Rollback Plan

If Option 1 doesn't work:
1. Revert changes to `src/agent.py`
2. Implement Option 2 (custom implementation with fixes)
3. Add HTTP session management to factory functions
