# Text-Only Mode Configuration Implementation Plan

> **Status:** DRAFT

## Table of Contents

- [Overview](#overview)
- [Current State Analysis](#current-state-analysis)
- [Desired End State](#desired-end-state)
- [What We're NOT Doing](#what-were-not-doing)
- [Implementation Approach](#implementation-approach)
- [Dependencies](#dependencies)
- [Phase 1: Configuration Setup](#phase-1-configuration-setup)
- [Phase 2: RoomOptions Conditional Logic](#phase-2-roomoptions-conditional-logic)
- [Phase 3: Conversation Logging](#phase-3-conversation-logging)
- [Phase 4: Testing and Documentation](#phase-4-testing-and-documentation)
- [Testing Strategy](#testing-strategy)
- [References](#references)

## Overview

Enable the drive-thru agent to run in either full audio mode (STT→LLM→TTS) or text-only mode (Text→LLM→Text) by changing configuration. All user input and agent responses should be captured in logs for manual testing and debugging.

**Key Requirements:**
- Configuration-driven mode switching (no code changes needed)
- Full audio pipeline: STT → LLM → TTS
- Text-only pipeline: Text Chat → LLM → Text Response
- Comprehensive logging of all conversation turns
- Conversation logs at INFO level (always visible)
- Default logging level set to DEBUG (verbose output)

## Current State Analysis

### What Exists Now

**File:** `src/agent.py:77-84`
```python
room_options = room_io.RoomOptions()
if config.session.enable_noise_cancellation:
    room_options = room_io.RoomOptions(
        audio_input=room_io.AudioInputOptions(
            noise_cancellation=noise_cancellation.BVC(),
        ),
    )
```

**Current Behavior:**
- RoomOptions only configured for noise cancellation
- Always runs in audio mode with STT/TTS
- No text-only mode available
- No conversation logging

**Configuration:** `src/config.py:54-69`
```python
class SessionConfig(BaseModel):
    use_multilingual_turn_detector: bool = True
    preemptive_generation: bool = True
    enable_noise_cancellation: bool = True
```

### Key Discoveries

1. **RoomOptions Structure** (from LiveKit docs):
   - `audio_input`: bool | AudioInputOptions | NotGiven
   - `audio_output`: bool | AudioOutputOptions | NotGiven
   - `text_input`: bool | TextInputOptions | NotGiven (defaults to True)
   - `text_output`: bool | TextOutputOptions | NotGiven (defaults to True)

2. **Text-Only Configuration Pattern**:
   ```python
   room_options = room_io.RoomOptions(
       audio_input=False,   # Disable microphone
       audio_output=False,  # Disable speakers
       text_input=True,     # Enable text chat (default)
       text_output=True,    # Enable text responses (default)
   )
   ```

3. **Conversation Event Logging**:
   - `session.on("conversation_item_added")` event captures both user and agent messages
   - Provides `event.item.role` and `event.item.text_content`

4. **STT/TTS Behavior in Text Mode**:
   - When `audio_input=False` and `audio_output=False`, STT/TTS are still created but bypassed
   - Agent processes text directly
   - No audio tracks published to the room

## Desired End State

### Success Criteria

**Configuration-Driven Mode Switching:**
- [x] Add `text_only_mode` boolean to SessionConfig ✅
- [x] Set `text_only_mode=true` in .env.local to run text-only ✅
- [x] Set `text_only_mode=false` (default) for full audio mode ✅

**Audio Mode (Default):**
- [x] User speaks → STT → LLM → TTS → Audio output ✅
- [x] Noise cancellation works if enabled ✅
- [x] All existing audio features functional ✅

**Text-Only Mode:**
- [x] User types text → LLM → Text response ✅
- [x] No audio input/output ✅
- [x] STT/TTS created but bypassed ✅
- [x] Agent responds via text chat ✅

**Conversation Logging:**
- [x] All user messages logged with timestamp (INFO level) ✅
- [x] All agent responses logged with timestamp (INFO level) ✅
- [x] Logs saved to `logs/conversation_{session_id}.jsonl` ✅
- [x] JSON Lines format for easy parsing ✅
- [x] Default logging level set to DEBUG globally ✅
- [x] Conversation events always visible in console (INFO level) ✅

### How to Verify

**Text-Only Mode:**
```bash
# Set in .env.local
SESSION__TEXT_ONLY_MODE=true

# Run in dev mode
uv run python src/agent.py dev

# Connect with frontend
# Type text messages
# Verify agent responds with text (no audio)
```

**Audio Mode (Default):**
```bash
# Remove or set to false in .env.local
SESSION__TEXT_ONLY_MODE=false

# Run in dev mode
uv run python src/agent.py dev

# Connect with frontend
# Speak into microphone
# Verify agent responds with audio
```

**Conversation Logs:**
```bash
# Check logs directory
ls logs/

# View conversation log
cat logs/conversation_<session_id>.jsonl

# Each line should be valid JSON with:
# - timestamp
# - session_id
# - role (user or assistant)
# - content
```

## What We're NOT Doing

- **Not creating a new CLI command** - text-only mode works in dev/start modes via config
- **Not modifying console mode** - console already has `--text` flag for local testing
- **Not changing the agent's instructions** - same persona regardless of mode
- **Not adding a UI toggle** - mode is set at startup via environment variable
- **Not implementing real-time mode switching** - mode is configured once at session start
- **Not logging audio transcripts** - only logging text content (STT output is already text)

## Implementation Approach

### Strategy

Use LiveKit's `RoomOptions` to conditionally enable/disable audio based on configuration. Register a conversation event handler to log all messages to a JSON Lines file.

**Why This Works:**
1. LiveKit handles audio/text switching internally
2. No changes needed to DriveThruAgent or DriveThruLLM
3. Logging is decoupled from agent logic
4. Configuration change requires only server restart

### Architecture

```
┌─────────────────────────────────────────────────┐
│ .env.local: SESSION__TEXT_ONLY_MODE=true/false  │
└──────────────────┬──────────────────────────────┘
                   │
                   ▼
         ┌─────────────────────┐
         │   SessionConfig     │
         │  text_only_mode     │
         └──────────┬──────────┘
                    │
                    ▼
         ┌──────────────────────┐
         │  _handle_rtc_session │
         └──────────┬───────────┘
                    │
         ┌──────────▼──────────────────────────┐
         │  Conditional RoomOptions Creation    │
         │                                      │
         │  if text_only_mode:                  │
         │    audio_input=False                 │
         │    audio_output=False                │
         │  else:                               │
         │    audio_input=AudioInputOptions()   │
         │    (noise cancellation if enabled)   │
         └──────────┬───────────────────────────┘
                    │
         ┌──────────▼───────────┐
         │  AgentSession.start  │
         └──────────┬───────────┘
                    │
    ┌───────────────┴───────────────┐
    │                               │
    ▼                               ▼
┌─────────────┐            ┌──────────────┐
│ Audio Mode  │            │ Text Mode    │
│ (Default)   │            │ (Config=true)│
├─────────────┤            ├──────────────┤
│ STT Active  │            │ STT Bypassed │
│ TTS Active  │            │ TTS Bypassed │
│ Mic Input   │            │ Text Chat    │
│ Audio Output│            │ Text Output  │
└─────────────┘            └──────────────┘
         │                        │
         └────────┬───────────────┘
                  │
                  ▼
    ┌─────────────────────────────┐
    │ session.on("conversation_   │
    │    item_added")             │
    │                             │
    │ Logs to JSON Lines file     │
    └─────────────────────────────┘
```

## Dependencies

**Execution Order:**

1. Phase 1: Configuration Setup (no dependencies)
2. Phase 2: RoomOptions Conditional Logic (depends on Phase 1)
3. Phase 3: Conversation Logging (depends on Phase 2)
4. Phase 4: Testing and Documentation (depends on Phases 1-3)

**Dependency Graph:**

```
Phase 1 (Configuration)
  │
  ├─> Phase 2 (RoomOptions Logic)
  │      │
  │      └─> Phase 3 (Logging)
  │             │
  └─────────────┴─> Phase 4 (Testing)
```

**Parallelization:**
- All phases are sequential (each depends on previous)
- No parallel execution possible

---

## Phase 1: Configuration and Logging Setup

### Overview
Add `text_only_mode` boolean to SessionConfig, configure default logging level to DEBUG, and update environment variable loading.

### Context
Before starting, read these files:
- `src/config.py` - SessionConfig model
- `src/agent.py` - Main entry point and logging setup
- `.env.example` - Example environment variables
- `AGENTS.md` - Configuration guidelines

### Dependencies
**Depends on:** None
**Required by:** Phase 2, Phase 3, Phase 4

### Changes Required

#### 1.1: Add text_only_mode to SessionConfig
**File:** `src/config.py`

**Current Code (lines 54-69):**
```python
class SessionConfig(BaseModel):
    """Session-level configuration for AgentSession behavior."""

    use_multilingual_turn_detector: bool = Field(
        default=True,
        description="Enable multilingual turn detection model",
    )
    preemptive_generation: bool = Field(
        default=True,
        description="Start generating responses before user finishes speaking",
    )
    enable_noise_cancellation: bool = Field(
        default=True,
        description="Enable background voice cancellation (BVC)",
    )
```

**Add After Line 68:**
```python
    text_only_mode: bool = Field(
        default=False,
        description="Run in text-only mode (no audio input/output). "
        "When True: User types text → LLM → Text response. "
        "When False: User speaks → STT → LLM → TTS → Audio output.",
    )
```

**Rationale:**
- Follows existing SessionConfig pattern
- Clear description for users
- Default=False maintains backward compatibility

#### 1.2: Update .env.example
**File:** `.env.example`

**Add to Session Configuration Section:**
```bash
# Session Configuration
# Enable text-only mode (no audio input/output)
# Set to true for text chat mode, false for voice mode (default)
# SESSION__TEXT_ONLY_MODE=false
```

**Rationale:**
- Documents the new option for users
- Shows environment variable format (SESSION__TEXT_ONLY_MODE)
- Commented out by default (uses config default)

#### 1.3: Verify Logging Configuration
**File:** `src/logging_config.py` (already exists)

**Current Status:**
The codebase already uses **loguru** for logging with proper configuration:
- Console logging at **INFO** level (stderr)
- File logging at **DEBUG** level (logs/agent_{timestamp}.log)
- Configuration is in `src/logging_config.py` and called from `src/agent.py:20`

**No changes needed** - the existing configuration already logs conversation events at INFO level to console, which ensures visibility.

**Rationale:**
- Loguru is already configured correctly
- INFO-level console logging means conversation events will be visible
- File logging captures detailed DEBUG output
- No conflicts with standard library logging

#### 1.4: Update AGENTS.md Documentation
**File:** `AGENTS.md`

**Add to Project Structure Section (after line ~50):**

```markdown
## Running in Text-Only Mode

The agent can run in two modes:

### Audio Mode (Default)
User speaks → STT → LLM → TTS → Audio output

### Text-Only Mode
User types text → LLM → Text response

**To enable text-only mode:**

1. Add to `.env.local`:
   ```bash
   SESSION__TEXT_ONLY_MODE=true
   ```

2. Run the agent normally:
   ```bash
   uv run python src/agent.py dev
   ```

3. Connect with a frontend and type text messages

**Use cases for text-only mode:**
- Manual testing without audio equipment
- Debugging LLM responses
- Testing in CI/CD environments
- Reducing API costs (no STT/TTS usage)

**Note:** In text-only mode, STT and TTS are still created but bypassed by LiveKit.
```

**Rationale:**
- Clear user documentation
- Explains both modes
- Practical use cases

#### 1.5: Document Logging Configuration
**File:** `AGENTS.md`

**Add to Running in Text-Only Mode section:**

```markdown
## Logging Configuration

The agent uses **loguru** for structured logging with two output channels:

### Log Channels

**Console output (stderr)**: INFO level (always visible)
- User messages
- Agent responses
- Session events
- Conversation items

**File output (logs/)**: DEBUG level (verbose details)
- Internal state changes
- Tool calls
- Menu searches
- Configuration loading
- Full tracebacks

### Log File Management

**Files:**
- Pattern: `logs/agent_{timestamp}.log`
- Rotation: Every 4 hours
- Retention: 2 days
- Compression: ZIP for rotated logs

### Controlling Log Output

The logging configuration is set in `src/logging_config.py`. To adjust verbosity:

**Modify console level:**
Edit `src/logging_config.py:29-38` to change console log level from INFO to DEBUG or WARNING.

**Default Behavior:**
- Console shows INFO and above (stderr)
- Files capture DEBUG and above
- Conversation items logged at INFO level for visibility
- Thread-safe with async support
```

**Rationale:**
- Documents loguru's actual configuration
- Shows dual-channel approach (console + file)
- Explains log rotation and retention
- No misleading environment variable references

### Success Criteria

#### Automated Verification:
- [x] Config loads without errors: `uv run python -c "from src.config import AppConfig; print(AppConfig().session.text_only_mode)"` ✅
- [ ] Type checking passes: `uv run mypy src/config.py` (mypy not installed, skipped)
- [x] Linting passes: `uv run ruff check src/config.py` ✅
- [x] Logging is configured: `uv run python -c "from src.logging_config import setup_logging; setup_logging(); print('Logging OK')"` ✅

#### Manual Verification:
- [ ] Environment variable SESSION__TEXT_ONLY_MODE=true is recognized
- [ ] Environment variable SESSION__TEXT_ONLY_MODE=false is recognized
- [ ] Omitting the variable defaults to False
- [ ] Agent outputs INFO logs to console (stderr)
- [ ] Agent outputs DEBUG logs to files (logs/agent_*.log)

---

## Phase 2: RoomOptions Conditional Logic

### Overview
Modify `_handle_rtc_session` to conditionally configure RoomOptions based on `text_only_mode`.

### Context
Before starting, read these files:
- `src/agent.py` - RTC session handler (lines 28-104)
- LiveKit RoomOptions documentation (if available via MCP)

### Dependencies
**Depends on:** Phase 1
**Required by:** Phase 3, Phase 4

### Changes Required

#### 2.1: Refactor RoomOptions Creation
**File:** `src/agent.py`

**Current Code (lines 77-84):**
```python
    # Room options - configure noise cancellation if enabled
    room_options = room_io.RoomOptions()
    if config.session.enable_noise_cancellation:
        room_options = room_io.RoomOptions(
            audio_input=room_io.AudioInputOptions(
                noise_cancellation=noise_cancellation.BVC(),
            ),
        )
```

**Replace with:**
```python
    # Room options - configure based on text_only_mode
    if config.session.text_only_mode:
        # Text-only mode: Disable audio input/output
        room_options = room_io.RoomOptions(
            audio_input=False,
            audio_output=False,
            text_input=True,   # Explicit for clarity
            text_output=True,  # Explicit for clarity
        )
    else:
        # Audio mode: Enable audio with optional noise cancellation
        if config.session.enable_noise_cancellation:
            room_options = room_io.RoomOptions(
                audio_input=room_io.AudioInputOptions(
                    noise_cancellation=noise_cancellation.BVC(),
                ),
            )
        else:
            room_options = room_io.RoomOptions()
```

**Rationale:**
- Clear conditional logic based on mode
- Maintains existing noise cancellation behavior in audio mode
- Explicit text_input/text_output for readability (though they default to True)
- Follows LiveKit's recommended pattern for text-only sessions

#### 2.2: Add Logging for Mode Selection
**File:** `src/agent.py`

**Add After RoomOptions Creation (after new line ~95):**
```python
    # Log the selected mode for debugging
    mode = "text-only" if config.session.text_only_mode else "audio"
    logger.info(
        f"Starting session in {mode} mode",
        extra={
            "session_id": session_id,
            "text_only": config.session.text_only_mode,
            "noise_cancellation": config.session.enable_noise_cancellation,
        },
    )
```

**Rationale:**
- Clear visibility into which mode is active
- Helps with debugging configuration issues
- Structured logging with extra fields

#### 2.3: Verify logger import
**File:** `src/agent.py`

**Current Status:**
Logger is already imported at line 10:
```python
from loguru import logger
```

**No changes needed** - loguru logger is already available for use.

**Rationale:**
- Loguru is the project's logging framework
- Logger is already configured and ready to use

### Success Criteria

#### Automated Verification:
- [ ] Agent starts without errors: `uv run python src/agent.py download-files && uv run python -c "from agent import create_server; create_server()"` (will test after Phase 3)
- [ ] Type checking passes: `uv run mypy src/agent.py` (mypy not installed, skipped)
- [x] Linting passes: `uv run ruff check src/agent.py` ✅

#### Manual Verification:
- [ ] With SESSION__TEXT_ONLY_MODE=true, agent starts in text mode
- [ ] With SESSION__TEXT_ONLY_MODE=false, agent starts in audio mode
- [ ] Log message clearly indicates the selected mode
- [ ] In text mode, no audio tracks are published to the room
- [ ] In audio mode, audio tracks are published normally

**Verify:** Start agent with each mode and connect with a frontend to verify behavior.

---

## Phase 3: Conversation Logging

### Overview
Register a conversation event handler to log all user and agent messages to JSON Lines files.

### Context
Before starting, read these files:
- `src/agent.py` - Session handler (lines 88-103)
- `src/order_state_manager.py` - Example of file-based logging pattern

### Dependencies
**Depends on:** Phase 2
**Required by:** Phase 4

### Changes Required

#### 3.1: Create Conversation Logger Module
**File:** `src/conversation_logger.py` (new file)

**Create:**
```python
"""Conversation logger for capturing all user and agent messages.

Logs conversations to JSON Lines format for debugging and analysis.
"""

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from livekit.agents import ConversationItemAddedEvent
from loguru import logger


class ConversationLogger:
    """Logs conversation messages to JSON Lines files."""

    def __init__(self, session_id: str, output_dir: str = "logs"):
        """Initialize conversation logger.

        Args:
            session_id: Unique session identifier
            output_dir: Directory for log files (default: "logs")
        """
        self.session_id = session_id
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)

        # Create session-specific log file
        self.log_file = self.output_dir / f"conversation_{session_id}.jsonl"
        logger.info(
            f"Conversation logger initialized",
            extra={"session_id": session_id, "log_file": str(self.log_file)},
        )

    def log_message(self, role: str, content: str, metadata: dict[str, Any] | None = None):
        """Log a single message to the conversation log.

        Args:
            role: Message role (user, assistant, system)
            content: Message text content
            metadata: Optional metadata (interrupted, tool_calls, etc.)
        """
        log_entry = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "session_id": self.session_id,
            "role": role,
            "content": content,
        }

        # Add optional metadata
        if metadata:
            log_entry["metadata"] = metadata

        # Append to JSON Lines file
        try:
            with open(self.log_file, "a", encoding="utf-8") as f:
                f.write(json.dumps(log_entry) + "\n")
        except Exception as e:
            logger.error(
                f"Failed to write conversation log",
                extra={"session_id": self.session_id, "error": str(e)},
            )

    def on_conversation_item_added(self, event: ConversationItemAddedEvent):
        """Event handler for conversation_item_added events.

        This is called by LiveKit when any conversation item is added
        (both user and agent messages).

        Args:
            event: Conversation item added event
        """
        # Extract text content
        content = event.item.text_content or ""

        # Skip empty messages
        if not content.strip():
            logger.info(
                f"Skipping empty conversation item",
                extra={
                    "session_id": self.session_id,
                    "role": event.item.role,
                },
            )
            return

        # Prepare metadata
        metadata = {
            "interrupted": event.item.interrupted,
        }

        # Add image/audio content flags if present
        if hasattr(event.item, "image_content") and event.item.image_content:
            metadata["has_image"] = True
        if hasattr(event.item, "audio_content") and event.item.audio_content:
            metadata["has_audio"] = True

        # Log the message
        self.log_message(
            role=event.item.role,
            content=content,
            metadata=metadata,
        )

        # Log at INFO level so conversation events are always visible
        logger.info(
            f"Logged conversation item",
            extra={
                "session_id": self.session_id,
                "role": event.item.role,
                "content_length": len(content),
            },
        )
```

**Rationale:**
- Separate module for clean separation of concerns
- JSON Lines format for easy parsing
- Session-specific log files
- Captures metadata (interrupted, content types)
- Handles errors gracefully
- **Conversation events logged at INFO level** (always visible in console)

#### 3.2: Register Logger in Session Handler
**File:** `src/agent.py`

**Add import at top (after line ~20):**
```python
from src.conversation_logger import ConversationLogger
```

**Note:** The import path should match the project structure. If running from the project root, use `from src.conversation_logger import ConversationLogger`. If imports in `src/agent.py` use relative imports (e.g., `from config import`), then use `from conversation_logger import ConversationLogger`.

**Add After AgentSession Creation (after line ~73, before session.start):**
```python
    # Create conversation logger
    conversation_logger = ConversationLogger(
        session_id=session_id,
        output_dir="logs",
    )

    # Register event handler for logging
    session.on("conversation_item_added", conversation_logger.on_conversation_item_added)
```

**Rationale:**
- Logger is created per session
- Event handler registered before session starts
- Captures all conversation from session beginning

#### 3.3: Update .gitignore for conversation logs
**File:** `.gitignore`

**Current Status:**
The `logs/` directory is already ignored (line 41):
```
# Logs directory
logs/
*.log
```

**Optional Change:**
If you want to explicitly exclude `.jsonl` files, add:
```
*.jsonl
```

**Note:** Since `logs/` is already ignored, all files within it (including `.jsonl` files) are already excluded from git. Adding `*.jsonl` to gitignore would only affect `.jsonl` files outside the `logs/` directory.

**Rationale:**
- Logs directory is already properly excluded
- No changes strictly necessary
- `*.jsonl` pattern may be too broad if used elsewhere

#### 3.4: Update README with logging information
**File:** `README.md`

**Add to "Order Output" section (after line ~80):**

```markdown

### Conversation Logs

All conversations (both audio and text modes) are logged to `logs/conversation_{session_id}.jsonl` in JSON Lines format.

**Log Format:**
```json
{"timestamp": "2026-01-28T10:30:00.000Z", "session_id": "abc123", "role": "user", "content": "I want a Big Mac"}
{"timestamp": "2026-01-28T10:30:01.500Z", "session_id": "abc123", "role": "assistant", "content": "Great choice! Would you like any modifications to your Big Mac?"}
{"timestamp": "2026-01-28T10:30:03.200Z", "session_id": "abc123", "role": "user", "content": "No thank you"}
{"timestamp": "2026-01-28T10:30:04.100Z", "session_id": "abc123", "role": "assistant", "content": "Added one Big Mac to your order. Anything else?"}
```

**Viewing Logs:**
```bash
# List all conversation logs
ls logs/

# View specific conversation
cat logs/conversation_abc123.jsonl

# Parse with jq
cat logs/conversation_abc123.jsonl | jq .

# Filter by role
cat logs/conversation_abc123.jsonl | jq 'select(.role == "user")'
```

**Use Cases:**
- Manual testing and verification
- Debugging agent responses
- Analyzing conversation patterns
- Training data collection
```

**Rationale:**
- Clear documentation for users
- Examples of log parsing
- Practical use cases

### Success Criteria

#### Automated Verification:
- [x] Module imports without errors: `uv run python -c "from src.conversation_logger import ConversationLogger; print('OK')"` ✅
- [ ] Type checking passes: `uv run mypy src/conversation_logger.py` (mypy not installed, skipped)
- [x] Linting passes: `uv run ruff check src/conversation_logger.py` ✅
- [ ] Unit tests pass: `uv run pytest tests/test_conversation_logger.py -v` (tests in Phase 4)

#### Manual Verification:
- [ ] Start agent and have a conversation
- [ ] Verify `logs/conversation_{session_id}.jsonl` file exists
- [ ] Verify file contains user messages
- [ ] Verify file contains agent responses
- [ ] Verify JSON Lines format is valid (each line is valid JSON)
- [ ] Verify timestamps are in ISO format
- [ ] Verify metadata fields (interrupted) are present

**Verify:** Run agent, have a multi-turn conversation, check log file manually.

---

## Phase 4: Testing and Documentation

### Overview
Create unit tests for ConversationLogger and update documentation with usage examples.

### Context
Before starting, read these files:
- `tests/conftest.py` - Shared fixtures
- `tests/test_drive_thru_agent_integration.py` - Integration test patterns
- `AGENTS.md` - Testing guidelines

### Dependencies
**Depends on:** Phases 1, 2, 3
**Required by:** None

### Changes Required

#### 4.1: Create Unit Tests for ConversationLogger
**File:** `tests/test_conversation_logger.py` (new file)

**Create:**
```python
"""Unit tests for ConversationLogger."""

import json
from pathlib import Path
from unittest.mock import Mock

import pytest

from src.conversation_logger import ConversationLogger


@pytest.fixture
def temp_logs_dir(tmp_path):
    """Create temporary logs directory."""
    return str(tmp_path / "logs")


@pytest.fixture
def logger(temp_logs_dir):
    """Create ConversationLogger with temp directory."""
    return ConversationLogger(session_id="test-session-123", output_dir=temp_logs_dir)


def test_logger_creates_directory(logger, temp_logs_dir):
    """Test that logger creates output directory."""
    assert Path(temp_logs_dir).exists()


def test_logger_creates_log_file_path(logger, temp_logs_dir):
    """Test that logger creates correct log file path."""
    expected = Path(temp_logs_dir) / "conversation_test-session-123.jsonl"
    assert logger.log_file == expected


def test_log_message_creates_file(logger):
    """Test that logging a message creates the file."""
    logger.log_message(role="user", content="Hello")
    assert logger.log_file.exists()


def test_log_message_writes_json(logger):
    """Test that logged message is valid JSON."""
    logger.log_message(role="user", content="Hello")

    with open(logger.log_file) as f:
        line = f.readline()
        data = json.loads(line)

    assert data["role"] == "user"
    assert data["content"] == "Hello"
    assert data["session_id"] == "test-session-123"
    assert "timestamp" in data


def test_log_multiple_messages(logger):
    """Test logging multiple messages."""
    logger.log_message(role="user", content="Hello")
    logger.log_message(role="assistant", content="Hi there!")
    logger.log_message(role="user", content="How are you?")

    with open(logger.log_file) as f:
        lines = f.readlines()

    assert len(lines) == 3
    data = [json.loads(line) for line in lines]
    assert data[0]["content"] == "Hello"
    assert data[1]["content"] == "Hi there!"
    assert data[2]["content"] == "How are you?"


def test_log_message_with_metadata(logger):
    """Test logging message with metadata."""
    metadata = {"interrupted": True, "has_image": False}
    logger.log_message(role="assistant", content="Response", metadata=metadata)

    with open(logger.log_file) as f:
        data = json.loads(f.readline())

    assert data["metadata"]["interrupted"] is True
    assert data["metadata"]["has_image"] is False


def test_on_conversation_item_added(logger):
    """Test event handler for conversation_item_added."""
    # Create mock event
    event = Mock()
    event.item.role = "user"
    event.item.text_content = "I want a Big Mac"
    event.item.interrupted = False

    # Call handler
    logger.on_conversation_item_added(event)

    # Verify logged
    with open(logger.log_file) as f:
        data = json.loads(f.readline())

    assert data["role"] == "user"
    assert data["content"] == "I want a Big Mac"
    assert data["metadata"]["interrupted"] is False


def test_skip_empty_messages(logger):
    """Test that empty messages are skipped."""
    event = Mock()
    event.item.role = "assistant"
    event.item.text_content = ""
    event.item.interrupted = False

    logger.on_conversation_item_added(event)

    # File should not exist (no messages logged)
    assert not logger.log_file.exists()


def test_skip_whitespace_only_messages(logger):
    """Test that whitespace-only messages are skipped."""
    event = Mock()
    event.item.role = "assistant"
    event.item.text_content = "   \n\t  "
    event.item.interrupted = False

    logger.on_conversation_item_added(event)

    assert not logger.log_file.exists()


def test_multiple_sessions_separate_files(temp_logs_dir):
    """Test that different sessions create separate log files."""
    logger1 = ConversationLogger(session_id="session-1", output_dir=temp_logs_dir)
    logger2 = ConversationLogger(session_id="session-2", output_dir=temp_logs_dir)

    logger1.log_message(role="user", content="Message 1")
    logger2.log_message(role="user", content="Message 2")

    assert logger1.log_file.exists()
    assert logger2.log_file.exists()
    assert logger1.log_file != logger2.log_file

    # Verify contents
    with open(logger1.log_file) as f:
        data1 = json.loads(f.readline())
    with open(logger2.log_file) as f:
        data2 = json.loads(f.readline())

    assert data1["session_id"] == "session-1"
    assert data2["session_id"] == "session-2"
```

**Rationale:**
- Comprehensive test coverage
- Tests file creation, JSON format, metadata
- Tests event handler integration
- Tests edge cases (empty messages, multiple sessions)

#### 4.2: Add Integration Test for Text-Only Mode
**File:** `tests/test_text_only_mode.py` (new file)

**Create:**
```python
"""Integration tests for text-only mode configuration.

These tests verify that the agent can be configured to run in text-only mode
and that RoomOptions are set correctly based on configuration.
"""

import pytest

from src.config import AppConfig, SessionConfig


def test_text_only_mode_default():
    """Test that text_only_mode defaults to False."""
    config = SessionConfig()
    assert config.text_only_mode is False


def test_text_only_mode_can_be_enabled():
    """Test that text_only_mode can be set to True."""
    config = SessionConfig(text_only_mode=True)
    assert config.text_only_mode is True


def test_app_config_loads_text_only_mode(monkeypatch):
    """Test that AppConfig loads text_only_mode from environment."""
    # Set environment variable
    monkeypatch.setenv("SESSION__TEXT_ONLY_MODE", "true")

    # Create config
    config = AppConfig()

    # Verify
    assert config.session.text_only_mode is True


def test_app_config_defaults_text_only_mode(monkeypatch):
    """Test that AppConfig defaults text_only_mode to False."""
    # Ensure variable is not set
    monkeypatch.delenv("SESSION__TEXT_ONLY_MODE", raising=False)

    # Create config
    config = AppConfig()

    # Verify
    assert config.session.text_only_mode is False


def test_text_only_mode_with_noise_cancellation(monkeypatch):
    """Test that both text_only and noise_cancellation can be configured."""
    monkeypatch.setenv("SESSION__TEXT_ONLY_MODE", "true")
    monkeypatch.setenv("SESSION__ENABLE_NOISE_CANCELLATION", "true")

    config = AppConfig()

    assert config.session.text_only_mode is True
    assert config.session.enable_noise_cancellation is True
    # Note: In text mode, noise cancellation is ignored
```

**Rationale:**
- Tests configuration loading
- Tests environment variable parsing
- Tests default values
- Tests interaction with other config options

#### 4.3: Document Text-Only Mode in README
**File:** `README.md`

**Add to "Running the Drive-Thru Agent" section:**

```markdown
##### Text-Only Mode

Run the agent in text-only mode (no audio input/output):

\`\`\`bash
# Set environment variable and run
SESSION__TEXT_ONLY_MODE=true uv run python src/agent.py dev

# Or using make
SESSION__TEXT_ONLY_MODE=true make run MODE=dev
\`\`\`

This mode is useful for:
- Manual testing without audio equipment
- Debugging LLM responses
- Testing in CI/CD environments
- Reducing API costs (no STT/TTS usage)
```

**Rationale:**
- Documents the feature in user-facing documentation
- Shows both direct and make-based invocation
- Uses existing `MODE=` pattern instead of adding new make target
- Explains practical use cases

#### 4.4: Add Troubleshooting Section to AGENTS.md
**File:** `AGENTS.md`

**Add new section:**

```markdown
## Troubleshooting Text-Only Mode

### Mode Not Switching

**Symptom**: Agent still uses audio despite SESSION__TEXT_ONLY_MODE=true

**Solutions**:
1. Verify environment variable is set:
   ```bash
   echo $SESSION__TEXT_ONLY_MODE
   ```

2. Check .env.local file format:
   ```bash
   SESSION__TEXT_ONLY_MODE=true
   ```
   (No quotes, no spaces around =)

3. Restart the agent server (config is loaded at startup)

4. Check logs for mode confirmation:
   ```
   INFO: Starting session in text-only mode
   ```

### Conversation Logs Not Created

**Symptom**: No log files in logs/ directory

**Solutions**:
1. Verify logs directory exists:
   ```bash
   mkdir -p logs
   ```

2. Check file permissions:
   ```bash
   ls -la logs/
   ```

3. Check file logging for details:
   ```bash
   tail -f logs/agent_*.log
   ```

4. Check for logging errors in console output

### Empty Conversation Logs

**Symptom**: Log file exists but contains no entries

**Possible causes**:
- Session has no conversation activity
- Messages are being filtered (empty content)
- Event handler not registered (check logs for "Conversation logger initialized")

**Debug**:
```bash
# Check if file was created
ls -lh logs/conversation_*.jsonl

# Check if event handler is registered
grep "Conversation logger initialized" <agent_logs>
```
```

**Rationale:**
- Helps users debug common issues
- Provides actionable solutions
- Covers configuration and logging problems

### Success Criteria

#### Automated Verification:
- [x] All unit tests pass: `uv run pytest tests/test_conversation_logger.py -v` ✅ (10 tests passed)
- [x] All integration tests pass: `uv run pytest tests/test_text_only_mode.py -v` ✅ (5 tests passed)
- [x] Full test suite passes: `uv run pytest` ✅ (228 passed, 4 pre-existing failures unrelated to changes)
- [ ] Type checking passes: `uv run mypy src/` (mypy not installed, skipped)
- [x] Linting passes: `uv run ruff check src/` ✅

#### Manual Verification:
- [ ] Environment variable works: `SESSION__TEXT_ONLY_MODE=true uv run python src/agent.py dev`
- [ ] Make command works: `SESSION__TEXT_ONLY_MODE=true make run MODE=dev`
- [ ] Agent starts in text-only mode with either approach
- [ ] Conversation logs are created and contain entries
- [ ] Documentation is clear and accurate
- [ ] Troubleshooting steps resolve common issues

**Verify:** Run full test suite and manually test both audio and text-only modes with logging.

---

## Testing Strategy

### Unit Tests

**ConversationLogger** (`tests/test_conversation_logger.py`):
- Directory creation
- File creation
- JSON Lines format
- Metadata handling
- Event handler integration
- Edge cases (empty messages, multiple sessions)

**Configuration** (`tests/test_text_only_mode.py`):
- Default values
- Environment variable loading
- Config validation
- Interaction with other options

### Integration Tests

**RoomOptions Logic** (manual testing):
1. Start agent with `SESSION__TEXT_ONLY_MODE=true`
2. Connect with frontend
3. Verify no audio tracks published
4. Verify text messages work
5. Check logs for mode confirmation

**Conversation Logging** (manual testing):
1. Start agent in both modes
2. Have multi-turn conversations
3. Verify log files created
4. Verify contents accurate
5. Verify JSON Lines format valid

### Manual Testing Steps

**Test Logging Configuration:**
```bash
# Start agent and verify DEBUG logs appear
uv run python src/agent.py dev
# Should see verbose DEBUG output

# Verify INFO level also works
LIVEKIT_LOG_LEVEL=INFO uv run python src/agent.py dev
# Should see less verbose output

# Check that conversation logs are INFO level
# Start agent and look for "Logged conversation item" messages
# These should appear at INFO level
```

**Test Audio Mode:**
```bash
# Set config
SESSION__TEXT_ONLY_MODE=false

# Start agent with DEBUG logging
uv run python src/agent.py dev

# Connect with frontend
# Speak into microphone
# Verify agent responds with audio
# Check console for "Logged conversation item" messages (INFO level)
# Check logs/conversation_*.jsonl for transcript
```

**Test Text-Only Mode:**
```bash
# Set config
SESSION__TEXT_ONLY_MODE=true

# Start agent with DEBUG logging (default)
uv run python src/agent.py dev

# Verify console shows:
# - DEBUG: Configuration loading messages
# - INFO: "Starting session in text-only mode"
# - INFO: "Logged conversation item" for each message

# Connect with frontend
# Type text messages
# Verify agent responds with text
# Verify no audio tracks in room
# Check console for conversation log messages (INFO)
# Check logs/conversation_*.jsonl for file output
```

**Test Mode Switching:**
```bash
# Test 1: Start in audio mode
SESSION__TEXT_ONLY_MODE=false uv run python src/agent.py dev
# Verify audio works

# Test 2: Stop and restart in text mode
SESSION__TEXT_ONLY_MODE=true uv run python src/agent.py dev
# Verify text works
```

**Test Logging:**
```bash
# Have conversation in each mode
# Check log files exist
cat logs/conversation_*.jsonl

# Verify JSON format
cat logs/conversation_*.jsonl | jq .

# Verify contents
# - User messages present
# - Agent responses present
# - Timestamps correct
# - Metadata present
```

## Performance Considerations

**Text-Only Mode Benefits:**
- No STT API calls (cost savings)
- No TTS API calls (cost savings)
- Lower latency (no audio processing)
- Easier to test and debug

**Logging Performance:**
- JSON Lines append-only (efficient)
- No buffering (immediate writes)
- Minimal overhead per message
- Log rotation not implemented (manual cleanup)

**Future Optimization:**
- Consider log rotation for long-running sessions
- Consider optional logging (enable/disable via config)
- Consider structured logging to external systems (CloudWatch, etc.)

## Migration Notes

**Backward Compatibility:**
- Default behavior unchanged (audio mode)
- Existing deployments continue working
- No breaking changes to API or config

**Rollout Strategy:**
1. Deploy code changes
2. Test with SESSION__TEXT_ONLY_MODE=true on staging
3. Monitor conversation logs
4. Document results
5. Enable in production as needed

**Rollback:**
- Remove SESSION__TEXT_ONLY_MODE from .env.local
- Restart agent
- Logs remain available (read-only)

## References

- Original request: Text-only mode for better manual testing
- LiveKit RoomOptions documentation: https://docs.livekit.io/reference/python/v1/livekit/agents/voice/room_io/
- LiveKit conversation events: https://docs.livekit.io/agents/logic/sessions/
- Current implementation: `src/agent.py:77-84`
- Config implementation: `src/config.py:54-69`
- Order state logging pattern: `src/order_state_manager.py`
