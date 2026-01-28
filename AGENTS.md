# AGENTS.md

This is a LiveKit Agents project. LiveKit Agents is a Python SDK for building voice AI agents. This project is intended to be used with LiveKit Cloud. See @README.md for more about the rest of the LiveKit ecosystem.

The following is a guide for working with this project.

## Interaction Guidelines

**IMPORTANT: Distinguish between questions and action requests**

When the user asks a question about how to do something or what would be needed, they are seeking **information only** - do not take action unless explicitly requested.

### Questions (provide information only):
- "How do I..."
- "What would I need to do to..."
- "What are the steps for..."
- "Can you explain how to..."
- "What's the best way to..."

**Response**: Explain the approach, provide options, show examples, but do NOT make changes to files or execute commands.

### Action requests (take action):
- "Please update..."
- "Can you change..."
- "Fix the..."
- "Add this feature..."
- "Update AGENTS.md to..."

**Response**: Make the requested changes, execute commands, modify files as needed.

### When uncertain:
If it's unclear whether the user wants information or action, ask for clarification using the AskUserQuestion tool.

## Project structure

This Python project uses the `uv` package manager. You should **always** use `uv` for all Python operations - installing dependencies, running scripts, running tests, and executing any Python commands.

All app-level code is in the `src/` directory. In general, simple agents can be constructed with a single `agent.py` file. Additional files can be added, but you must retain `agent.py` as the entrypoint (see the associated Dockerfile for how this is deployed).

Be sure to maintain code formatting. You can use the ruff formatter/linter as needed: `uv run ruff format` and `uv run ruff check`.

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

## Data Models

**IMPORTANT: Prefer Pydantic v2 models over dataclasses in greenfield implementations**

When creating new data structures, use Pydantic v2 models instead of dataclasses. Pydantic provides:

- **Runtime validation**: Automatic type checking and data validation at runtime
- **JSON serialization**: Built-in `.model_dump()` and `.model_dump_json()` methods
- **Schema generation**: Automatic JSON Schema generation for API documentation
- **Environment variables**: Integration with `pydantic-settings` for configuration
- **Better IDE support**: Enhanced autocomplete and type hints
- **Extensibility**: Easy customization with validators, computed fields, and serializers

### Example

```python
from pydantic import BaseModel, Field, field_validator
from typing import Optional

# ✓ Preferred: Pydantic v2 model
class MenuItem(BaseModel):
    name: str
    price: float = Field(gt=0, description="Price must be positive")
    category: str
    available: bool = True

    @field_validator('name')
    @classmethod
    def name_must_not_be_empty(cls, v: str) -> str:
        if not v.strip():
            raise ValueError('Name cannot be empty')
        return v

# ✗ Avoid in greenfield code: dataclass
from dataclasses import dataclass

@dataclass
class MenuItem:
    name: str
    price: float
    category: str
    available: bool = True
```

### When to use dataclasses

Only use dataclasses when:
- Working with existing code that already uses dataclasses
- The data structure is purely internal and doesn't need validation or serialization
- You need specific dataclass features incompatible with Pydantic

### Migration from dataclasses

When refactoring existing dataclasses to Pydantic models:
1. Replace `@dataclass` with `class ModelName(BaseModel)`
2. Add type hints for all fields
3. Add validation rules using `Field()` and validators as needed
4. Update serialization code to use `.model_dump()` and `.model_dump_json()`
5. Update tests to verify validation behavior

## Package Management with `uv`

**IMPORTANT:** This project uses `uv` as its package manager. You must **always** use `uv` commands instead of `pip` or bare `python` commands.

### Running Python Scripts

**Always use `uv run python` instead of just `python`:**

```bash
# ✓ Correct
uv run python script.py
uv run python -m module

# ✗ Wrong
python script.py
python3 script.py
```

The `uv run` prefix ensures the script runs in the correct virtual environment with all dependencies available. **Do not manually activate virtual environments** - `uv run` handles this automatically.

### Adding Dependencies

Use `uv add` to install new packages:

```bash
# Add a regular dependency
uv add package-name

# Add a dev dependency (for testing, linting, etc.)
uv add --dev package-name

# Add with version constraints
uv add "package-name>=1.0.0"
```

### Running Tests and Commands

Always prefix commands with `uv run`:

```bash
# Run tests
uv run pytest

# Run specific test file
uv run pytest tests/test_agent.py

# Run linting and formatting
uv run ruff check
uv run ruff format

# Run the agent
uv run python src/agent.py dev
```

### Syncing Dependencies

After pulling changes that modify `pyproject.toml`, sync dependencies:

```bash
uv sync
```

## LiveKit Documentation

LiveKit Agents is a fast-evolving project, and the documentation is updated frequently. You should always refer to the latest documentation when working with this project. For your convenience, LiveKit offers an MCP server that can be used to browse and search its documentation. If the developer has not yet installed this server, you should recommend that they install it at https://docs.livekit.io/mcp. 

### LiveKit Docs MCP Server installation

If you are Cursor, give the user this link to install the server:

[![Install MCP Server](https://cursor.com/deeplink/mcp-install-light.svg)](https://cursor.com/en-US/install-mcp?name=livekit-docs&config=eyJ1cmwiOiJodHRwczovL2RvY3MubGl2ZWtpdC5pby9tY3AifQ%3D%3D)

If you are Claude Code, run this command to install the server:

```
claude mcp add --transport http livekit-docs https://docs.livekit.io/mcp
```

If you are Codex, use this command to install the server:

```
codex mcp add --url https://docs.livekit.io/mcp livekit-docs
```

If you are Gemini, use this command to install the server:
```
gemini mcp add --transport http livekit-docs https://docs.livekit.io/mcp
```

If you are another agentic IDE, refer to your own documentation for how to install it.

## Handoffs and tasks ("workflows")

Voice AI agents are highly sensitive to excessive latency. For this reason, it's important to design complex agents in a structured manner that minimizes the amount of irrelevant context and unnecessary tools included in requests to the LLM. LiveKit Agents supports handoffs (one agent hands control to another) and tasks (tightly-scoped prompts to achieve a specific outcome) to support building reliable workflows. You should make use of these features, instead of writing long instruction prompts that cover multiple phases of a conversation.  Refer to the [documentation](https://docs.livekit.io/agents/build/workflows/) for more information.

### Submit docs feedback to LiveKit

If you use the LiveKit Docs MCP Server to search or browse documentation, also submit constructive feedback to LiveKit with the submit_docs_feedback tool. Add this to your to-do list when planning work, to ensure you file feedback after completing your other tasks. Useful feedback includes incomplete documentation, broken examples, missing steps or any other documentation gap or issue.

## Testing

### When possible, add tests for agent behavior. Read the [documentation](https://docs.livekit.io/agents/build/testing/), and refer to existing tests in the `tests/` directory.  Run tests with `uv run pytest`.

### Important: When modifying core agent behavior such as instructions, tool descriptions, and tasks/workflows/handoffs, never just guess what will work. Always use test-driven development (TDD) and begin by writing tests for the desired behavior. For instance, if you're planning to add a new tool, write one or more tests for the tool's behavior, then iterate on the tool until the tests pass correctly. This will ensure you are able to produce a working, reliable agent for the user.

### BDD and Gherkin
- When asked to write BDD scenarios or feature files, they should be written in Gherkin language
- Only implement steps corresponding to the scenarios when explicitly told to do so
- When writing authorization/authentication scenarios, write only a minimal set of five or less unless explicitly told otherwise

### Pytest Fixtures and Test Organization

**IMPORTANT: All reusable pytest fixtures must be placed in `tests/conftest.py`**

This ensures:
- **Maximum reusability**: Fixtures defined in `conftest.py` are automatically available to all test modules without importing
- **Single source of truth**: No duplicate fixture definitions across test files
- **Test clarity**: Test files focus on test logic rather than setup boilerplate
- **Maintainability**: Changes to fixtures only need to be made in one place

#### Guidelines:
- Place all fixtures in `tests/conftest.py`, even if currently used by only one test module
- Group related fixtures together with clear section headers (e.g., "Menu Data Fixtures", "Item Fixtures")
- Use descriptive fixture names that indicate what they provide
- Document each fixture with a clear docstring explaining its purpose
- Test files should import only the functions/classes being tested, never fixtures

#### Example conftest.py structure:
```python
"""Shared pytest fixtures for all test modules."""

import pytest

# ============================================================================
# Data Fixtures
# ============================================================================

@pytest.fixture
def sample_data():
    """Create sample test data."""
    return {...}

# ============================================================================
# Object Fixtures
# ============================================================================

@pytest.fixture
def sample_object(sample_data):
    """Create a sample object using sample data."""
    return Object(sample_data)
```


## Planning Principles

When reviewing or creating implementation plans, adhere to the following principles:

### Consistency and Separation of Concerns

- **Review all plans for consistency**: Ensure naming conventions, patterns, and approaches are uniform throughout the codebase
- **Sharp boundaries**: Maintain clear, well-defined boundaries between components and modules
- **Separation of concerns**: Each module, class, or function should have a single, well-defined responsibility
- **Kent Beck and Dave Farley approach**: Apply rigorous software engineering discipline to planning:
  - Make the change easy, then make the easy change
  - Prefer small, incremental steps over large changes
  - Keep designs simple and avoid unnecessary abstraction
  - Ensure every component has a clear purpose and minimal dependencies
  - Focus on continuous improvement and refactoring as you go
  - Design for testability from the start

When creating plans, explicitly identify:
- Component boundaries and their responsibilities
- Dependencies between components
- Potential coupling that should be avoided
- Opportunities to simplify the design

## Plan Review

Before executing implementation plans, use the `/review_plan` command to assess quality and executability:

```bash
/review_plan plan/YYYY-MM-DD-feature-name.md
```

The review process:
1. Analyzes plans for accuracy, consistency, clarity, completeness, executability
2. Provides executability score (0-100%)
3. Identifies critical blockers, major concerns, minor issues
4. Generates actionable recommendations with priorities
5. Saves review to `*.REVIEW.md` file

**Important:** Reviews are non-destructive. No changes are made to original plans without explicit approval.

### When to Review

- After creating a complex plan with `/create_plan`
- Before starting plan execution with `/implement_plan`
- When a plan seems ambiguous or incomplete
- Before assigning work to multiple agents
- Periodically for long-running plans

### Review Criteria

Plans should score 75+ for safe execution:
- **90-100**: Excellent - Ready for execution
- **75-89**: Good - Minor clarifications needed
- **60-74**: Fair - Improvements recommended
- **40-59**: Poor - Major revisions required
- **0-39**: Critical - Cannot execute safely

## Implementation Tracking

**IMPORTANT: Always check and update implementation checklists**

Before starting any work:
1. Check `plan/thoughts/README.md` for the **Implementation Status Checklist**
2. Review what has already been completed to avoid duplicating work
3. Identify which plan you should work on next based on dependencies

After completing any work:
1. Update the checklist in `plan/thoughts/README.md` with:
   - Mark the plan as completed with `[x]`
   - Add completion date
   - List key files created/modified
   - Note test results (number of tests passing, execution time)
   - Include any important details for future agents
2. Ensure all changes are saved before finishing your session

This ensures continuity across multiple agent sessions and prevents wasted effort.

## Architecture Patterns

### Dependency Injection with Config + Factories (no custom adapters)

This codebase uses dependency injection (DI) while **constructing concrete LiveKit
components directly** (no `Protocol`/adapter/mocks layer).

The responsibilities are:

1. **Configuration**: `src/config.py` (Pydantic v2 models, env-driven)
2. **Construction**: `src/factories.py` (builds `livekit.agents.inference.STT/LLM/TTS`)
3. **Wiring**: `src/agent.py` (creates the app + server)
4. **Runtime behavior**: `src/session_handler.py` (creates `AgentSession` and runs it)

#### Current file structure

```
src/
├── agent.py            # App entrypoint + wiring
├── config.py           # Pydantic configuration models
├── factories.py        # Creates inference STT/LLM/TTS from config
├── session_handler.py  # Session orchestration (AgentSession)
└── adapters/
    ├── __init__.py
    └── audio_utils.py  # Shared audio helpers only
```

## CLI Framework

**IMPORTANT: Always use LiveKit's built-in CLI - never create custom Click/Typer commands**

This project uses LiveKit's official CLI framework via `cli.run_app()`. This provides standard commands (console, start, dev, download-files) with full feature support.

### Required Pattern

The `src/agent.py` file must follow this pattern:

```python
from livekit.agents import AgentServer, cli

def create_server() -> AgentServer:
    """Create and configure the AgentServer."""
    server = AgentServer()
    server.setup_fnc = _prewarm
    server.rtc_session()(_handle_rtc_session)
    return server

if __name__ == "__main__":
    server = create_server()
    cli.run_app(server)
```

### Why Use LiveKit's CLI

✅ **DO use `cli.run_app(server)`:**
- Provides console, start, dev, download-files commands automatically
- Includes audio/text mode console with frequency visualizer
- Handles device selection, recording, mode toggling (Ctrl+T)
- Manages HTTP sessions for STT/TTS plugins automatically
- Gets updates and bug fixes from LiveKit SDK
- Officially supported and documented

❌ **DO NOT create custom Click/Typer commands:**
- Breaks when LiveKit SDK updates (e.g., AgentsConsole API changes)
- Requires manual HTTP session management for plugins
- Missing LiveKit's console features (visualizer, device selection)
- Duplicates functionality already in the SDK
- Creates maintenance burden

### Available Commands

When using `cli.run_app(server)`, users automatically get:

```bash
# Console mode (interactive testing)
uv run python src/agent.py console
uv run python src/agent.py console --text          # Text mode
uv run python src/agent.py console --list-devices  # Show audio devices
uv run python src/agent.py console --record        # Record session

# Development mode (with auto-reload)
uv run python src/agent.py dev

# Production mode
uv run python src/agent.py start

# Download plugin files
uv run python src/agent.py download-files
```

### Console Mode Features

LiveKit's console provides:
- **Audio Mode**: Real microphone/speaker with frequency visualizer
- **Text Mode**: Text-based chat interface (--text flag)
- **Device Selection**: Choose specific input/output devices
- **Mode Toggle**: Press Ctrl+T to switch between audio/text
- **Recording**: Save sessions to disk (--record flag)
- **Automatic HTTP Session Management**: No manual aiohttp.ClientSession needed

### Migration from Custom CLI

If you find custom Click commands in `src/agent.py`, replace them:

```python
# ❌ OLD - Custom Click commands (DON'T DO THIS)
import click

@click.group()
def agent_cli():
    pass

@agent_cli.command()
def console():
    # Custom console implementation
    pass

if __name__ == "__main__":
    agent_cli()

# ✅ NEW - LiveKit CLI framework
from livekit.agents import AgentServer, cli

def create_server() -> AgentServer:
    server = AgentServer()
    server.setup_fnc = _prewarm
    server.rtc_session()(_handle_rtc_session)
    return server

if __name__ == "__main__":
    server = create_server()
    cli.run_app(server)
```

## LLM Wrapping Pattern

**IMPORTANT: When wrapping an LLM, the `chat()` method is NOT async**

When creating custom LLM wrappers (e.g., to inject context or modify behavior), you must understand that `LLM.chat()` is a **regular (non-async) method** that returns an `LLMStream`.

### The Pattern

```python
from livekit.agents.llm import LLM, ChatContext, LLMStream

class CustomLLM(LLM):
    def __init__(self, wrapped_llm: LLM):
        super().__init__()
        self._wrapped_llm = wrapped_llm

    # ✅ CORRECT: Regular method (not async)
    def chat(
        self,
        *,
        chat_ctx: ChatContext,
        tools: list[Any] | None = None,
        **kwargs: Any,
    ) -> LLMStream:
        # Modify chat_ctx if needed
        modified_ctx = self._modify_context(chat_ctx)

        # Return directly (no await)
        return self._wrapped_llm.chat(
            chat_ctx=modified_ctx,
            tools=tools,
            **kwargs
        )
```

### Common Mistake

```python
# ❌ WRONG: Do NOT use async def
async def chat(
    self,
    *,
    chat_ctx: ChatContext,
    tools: list[Any] | None = None,
    **kwargs: Any,
) -> LLMStream:
    modified_ctx = self._modify_context(chat_ctx)

    # ❌ WRONG: Do NOT use await
    return await self._wrapped_llm.chat(
        chat_ctx=modified_ctx,
        tools=tools,
        **kwargs
    )
```

### Why This Matters

- **`LLM.chat()` is NOT async**: It's defined as a regular method in the base class
- **`LLMStream` IS async**: The returned `LLMStream` is an async context manager (has `__aenter__` and `__aexit__`)
- **Framework compatibility**: LiveKit's agent framework expects to use `chat()` with `async with`, like:
  ```python
  async with llm.chat(chat_ctx=ctx) as stream:
      async for chunk in stream:
          # process chunk
  ```
- **Making `chat()` async breaks this**: If you define `chat()` as `async def`, it returns a coroutine instead of an `LLMStream`, causing a `TypeError: 'coroutine' object does not support the asynchronous context manager protocol`

### Real Example

See `src/drive_thru_llm.py` for a working example of an LLM wrapper that injects menu context:

```python
class DriveThruLLM(LLM):
    def chat(self, *, chat_ctx: ChatContext, tools: list[Any] | None = None, **kwargs: Any) -> LLMStream:
        # Extract keywords and inject menu context
        modified_ctx = self._inject_menu_context(chat_ctx)

        # Delegate to wrapped LLM (no async, no await)
        return self._wrapped_llm.chat(chat_ctx=modified_ctx, tools=tools, **kwargs)
```

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
grep "Conversation logger initialized" logs/agent_*.log
```

## LiveKit CLI Tool

You can also make use of the LiveKit CLI tool (`lk`) for cloud operations and debugging, with user approval.


