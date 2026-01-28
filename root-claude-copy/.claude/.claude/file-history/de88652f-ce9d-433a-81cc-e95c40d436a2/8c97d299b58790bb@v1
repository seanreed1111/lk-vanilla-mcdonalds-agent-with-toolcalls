# Changelog

## Combined changelog for commits c6ae5c1 to db75b2e (January 21, 2026)

### Features

#### Hybrid LLM System
- **Keyword intercept LLM** - Added intelligent keyword detection for faster responses
  - Intercepts common keywords/phrases and provides immediate responses
  - Falls back to full LLM when keywords don't match
  - Significantly reduces latency for common interactions
- **Mock LLM implementation** - Complete mock LLM for testing and development
  - Supports offline development without API calls
  - Configurable responses for testing scenarios
  - Integration with existing factory pattern

#### Architecture Improvements
- **Simplified architecture** - Removed protocol layer for more direct LiveKit integration
  - Eliminated custom protocol abstractions in favor of concrete LiveKit components
  - Direct use of `livekit.agents.inference.STT/LLM/TTS`
  - Cleaner dependency injection through factories
- **Agent renamed to app** - Refactored `agent.py` to `app.py` for clarity
- **Enhanced configuration** - Extended config support for keyword intercept and mock LLM options

### Testing
- **Keyword intercept tests** - Comprehensive test suite for keyword detection and fallback behavior
  - 250+ lines of test coverage for keyword intercept functionality
  - Tests for exact matches, partial matches, and LLM fallback scenarios
- **Mock LLM examples** - Added `examples/basic_agent_with_mock_llm.py` demonstrating usage

### Build & Development
- **Makefile updates** - Streamlined build commands and targets
- **Audio samples organization** - Moved demo audio files to `audio-samples/` directory
- **Dependency updates** - Updated `uv.lock` with new dependencies

### Refactoring & Cleanup
- **Removed protocol abstractions** - Eliminated `src/protocols.py` and protocol-based adapters
- **Removed mock adapters** - Cleaned up old mock adapter implementations
  - Removed `src/adapters/livekit_adapters.py`
  - Removed `src/adapters/mock_adapters.py`
  - Streamlined `src/adapters/` to focus on utilities only
- **Documentation cleanup** - Removed outdated documentation:
  - Removed `MOCK_ADAPTERS.md` (no longer relevant)
  - Simplified `AGENTS.md` (removed 393 lines of outdated content)
  - Removed refactoring examples from `past-plans/`
- **Test cleanup** - Removed obsolete test files:
  - Removed `tests/test_mock_tts_audio.py`
  - Updated `tests/test_agent.py` for simplified architecture

### Files Modified

#### Core Application
- `src/app.py` (renamed from `src/agent.py`) - Refactored for hybrid LLM support
- `src/factories.py` - Updated to create mock LLM and keyword intercept LLM instances
- `src/config.py` - Added configuration for new LLM options
- `src/session_handler.py` - Simplified for direct LiveKit integration

#### New Modules
- `src/mock_llm.py` - Mock LLM implementation for testing (116 lines)
- `src/keyword_intercept_llm.py` - Keyword intercept LLM wrapper (219 lines)

#### Testing
- `tests/test_keyword_intercept.py` - New comprehensive test suite (250 lines)
- `tests/test_agent.py` - Updated for new architecture

#### Examples
- `examples/basic_agent_with_mock_llm.py` - Demo of mock LLM usage (141 lines)

### Migration Notes

This version represents a significant architectural shift:
- **No more protocol layer**: Direct use of LiveKit components instead of custom abstractions
- **Hybrid LLM approach**: Keyword intercept for common phrases with LLM fallback
- **Cleaner codebase**: Removed ~1,940 lines of unnecessary abstraction code
- **Better performance**: Faster responses through keyword intercept system
- **Simpler testing**: Mock LLM enables offline development and testing

The changes maintain the dependency injection pattern while significantly simplifying the codebase and improving response times.

---

## Combined changelog for commits 420b4cd to 55367d6 (January 18-22, 2026)

## Features

### Agent Core Functionality
- **Initial LiveKit voice agent implementation** with OpenAI, Cartesia, and AssemblyAI integration
- **Initial agent greeting** - Agent now greets users when the session starts
- **Conversation context** - Agent maintains multi-turn conversation context

### Testing & Quality
- **BDD test scenarios** - Added comprehensive Gherkin feature files for:
  - Agent personality and tone
  - Multi-turn conversation context
  - Safety and harmful request handling
  - Voice processing and interruption handling
- **Test suite** with pytest integration

### Mock Adapters for Development
- **Mock TTS adapter with tone generation** - Generate audio tones for testing without API calls
- **Mock STT and LLM adapters** - Complete mock implementation for offline development
- **Audio utilities** - Tone generation, beep creation, and WAV file handling
- **Demo scripts** - `demo_mock_tts_audio.py` for testing mock audio output

## Refactoring & Architecture

### Dependency Injection & Inversion
- **Configuration management** - Centralized Pydantic-based config in `src/config.py`
- **Factory pattern** - Dependency injection through `src/factories.py`
- **Protocol-based abstractions** - Defined protocols in `src/protocols.py` for STT, LLM, and TTS
- **Session handler** - Separated session orchestration into `src/session_handler.py`
- **Adapter pattern** - Organized adapters in `src/adapters/` package:
  - LiveKit concrete implementations
  - Mock implementations for testing
  - Audio utilities

### Code Quality Improvements
- **Removed global variables** - Refactored agent to eliminate global state
- **Sharp boundaries** - Clear separation of concerns between components
- **Model optimization** - Switched to more cost-effective models

## Documentation

### Project Documentation
- **AGENTS.md** - Comprehensive guide for working with LiveKit Agents:
  - Project structure and uv package manager usage
  - Data models with Pydantic v2 best practices
  - Testing guidelines with pytest and BDD
  - Architecture patterns and dependency injection
  - Implementation tracking system
- **MOCK_ADAPTERS.md** - Detailed documentation for mock adapter development and usage
- **Python reference** - Added `PYTHON_MATCH_REFERENCE.md` for pattern matching examples
- **Future bugfixes** - Documented turn detector language warning issue
- **README updates** - Enhanced setup instructions and project overview

## Build & Development

### Build Tools
- **Makefile** - Added comprehensive Make targets for:
  - Running agent (console, dev, start modes)
  - Testing and code quality (test, format, lint)
  - Utilities (download-files, clean)
- **Development examples** - Created refactoring comparison examples in `past-plans/`

### Project Setup
- **Docker support** - Dockerfile for production deployment
- **Environment configuration** - `.env.example` and `.gitignore` setup
- **uv lock file** - Complete dependency lock for reproducible builds
- **CI/CD cleanup** - Removed unnecessary workflow files

## Dependencies

### Added
- **pydantic** - For configuration and data validation
- **pytest-bdd** - For behavior-driven development testing
- **numpy** - For audio processing utilities

## Files Modified

### Core Application
- `src/agent.py` - Major refactoring for dependency injection and clean architecture
- `src/config.py` - New configuration module
- `src/factories.py` - Factory functions for component creation
- `src/protocols.py` - Protocol definitions for type safety
- `src/session_handler.py` - Session lifecycle management

### Adapters
- `src/adapters/__init__.py` - Package initialization
- `src/adapters/livekit_adapters.py` - LiveKit concrete implementations
- `src/adapters/mock_adapters.py` - Mock implementations with greeting and tone support
- `src/adapters/audio_utils.py` - Audio generation utilities

### Testing
- `tests/test_agent.py` - Updated tests for refactored architecture
- `tests/test_mock_tts_audio.py` - New tests for mock TTS audio generation
- `tests/features/*.feature` - BDD scenario files

### Configuration & Build
- `pyproject.toml` - Updated dependencies and project metadata
- `Makefile` - Enhanced build and development commands
- `.gitignore` - Additional patterns for generated files

### Documentation
- `README.md` - Enhanced project overview and setup instructions
- `AGENTS.md` - Comprehensive agent development guide
- `MOCK_ADAPTERS.md` - Mock adapter documentation

## Migration Notes

This version represents a significant architectural improvement with:
- Clear separation between configuration, factories, and runtime logic
- Protocol-based dependency injection for better testability
- Comprehensive mock adapters for offline development
- Enhanced documentation for AI-assisted development

The refactoring maintains backward compatibility while providing a more maintainable and testable codebase.
