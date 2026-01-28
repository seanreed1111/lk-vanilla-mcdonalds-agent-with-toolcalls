# Remove Generic Voice Agent Implementation Plan

> **Status:** DRAFT
> **Last Updated:** 2026-01-27
> **Review Status:** Reviewed and corrected

## Review Findings and Corrections

**Date Reviewed:** 2026-01-27

**Issues Found and Corrected:**

1. **✓ Fixed: Misleading import verification in Phase 1**
   - **Issue:** Success criteria used `uv run python -c "import agent"` which would fail or be misleading
   - **Correction:** Changed to `uv run python src/agent.py --help` to verify the CLI still works

2. **✓ Fixed: AGENTS.md has no references to app.py**
   - **Issue:** Phase 4.2 claimed AGENTS.md needed updates to remove app.py references
   - **Finding:** AGENTS.md already only references `agent.py` - no changes needed
   - **Correction:** Updated Phase 4.2 to verify AGENTS.md is already correct (no changes needed)

3. **✓ Enhanced: Made Phase 4.1 more specific**
   - **Issue:** Instructions were somewhat vague about what to change in README.md
   - **Correction:** Added specific line numbers and exact wording changes for each update
   - Added detail about changing "two main applications" to singular focus

4. **✓ Updated: Current State Analysis**
   - Corrected documentation to reflect that AGENTS.md needs no changes
   - Updated success criteria to include CLI verification test

**Files Verified:**
- ✓ All source files exist (src/app.py, src/keyword_intercept_llm.py, src/mock_llm.py)
- ✓ All test files exist (tests/test_agent.py, tests/test_keyword_intercept.py)
- ✓ Dockerfile.voice exists
- ✓ Obsolete plan files exist
- ✓ README.md references verified (5 locations: lines 10, 31, 53, 247, 262, 373)
- ✓ AGENTS.md confirmed to have NO references to app.py

**Overall Assessment:** Plan is now accurate and ready for execution. All file references verified, line numbers confirmed, and corrected AGENTS.md misunderstanding.

## Table of Contents

- [Overview](#overview)
- [Current State Analysis](#current-state-analysis)
- [Desired End State](#desired-end-state)
- [What We're NOT Doing](#what-were-not-doing)
- [Dependencies](#dependencies)
- [Phase 1: Delete Source Files](#phase-1-delete-source-files)
- [Phase 2: Delete Test Files](#phase-2-delete-test-files)
- [Phase 3: Delete Container and Plan Files](#phase-3-delete-container-and-plan-files)
- [Phase 4: Update Documentation](#phase-4-update-documentation)
- [Testing Strategy](#testing-strategy)
- [References](#references)

## Overview

Remove the generic voice assistant (`app.py`) and all related code from the repository. This project will focus exclusively on the McDonald's Drive-Thru Agent (`agent.py`).

The generic voice assistant was a general-purpose AI that could answer questions on any topic. Since we're now focused solely on the specialized drive-thru ordering agent, this functionality and its supporting code should be removed to simplify the codebase.

## Current State Analysis

The codebase currently has two entry points:

1. **`src/agent.py`** - McDonald's Drive-Thru Agent (KEEP)
2. **`src/app.py`** - Generic Voice Assistant (REMOVE)

### Files to Remove:

**Source Files:**
- `src/app.py` - Generic voice assistant entry point
- `src/keyword_intercept_llm.py` - LLM wrapper for keyword interception (only used in tests with `app.py`)
- `src/mock_llm.py` - Mock LLM for testing (only used in tests with `app.py`)

**Test Files:**
- `tests/test_agent.py` - Tests the generic `Assistant` class from `app.py`
- `tests/test_keyword_intercept.py` - Tests `KeywordInterceptLLM` using `Assistant`

**Container Files:**
- `Dockerfile.voice` - Docker container for the generic voice assistant

**Plan Files:**
- `plan/future-plans/remove-mcdonalds-voice-agent.md` - Obsolete plan (opposite direction)
- `plan/future-plans/remove-mcdonalds-voice-agent.REVIEW.md` - Review of obsolete plan

### Files to Update:

**Documentation:**
- `README.md` - Remove references to generic voice assistant and `app.py`
- `AGENTS.md` - **No changes needed** (already only references `agent.py`)

### Files to Keep (unchanged):

**Shared Infrastructure:**
- `src/config.py` - Configuration (used by both, keep for agent.py)
- `src/factories.py` - Component factories (used by both, keep for agent.py)
- `src/session_handler.py` - Session orchestration (used by both, keep for agent.py)

**Drive-Thru Agent:**
- `src/agent.py` - Main drive-thru agent entry point
- `src/drive_thru_agent.py` - Drive-thru agent implementation
- `src/drive_thru_llm.py` - Menu-aware LLM wrapper
- `src/menu_provider.py` - Menu search and loading
- `src/order_state_manager.py` - Order tracking
- `src/tools/order_tools.py` - Order management tools

**Tests:**
- `tests/conftest.py` - Shared fixtures
- `tests/test_drive_thru_agent.py` - Drive-thru agent tests
- `tests/test_drive_thru_agent_integration.py` - Integration tests
- `tests/test_drive_thru_llm.py` - Drive-thru LLM tests
- `tests/test_menu_models.py` - Menu model tests
- `tests/test_menu_provider.py` - Menu provider tests
- `tests/test_menu_validation.py` - Menu validation tests
- `tests/test_order_state.py` - Order state tests
- `tests/test_order_tools.py` - Order tools tests

**Other:**
- `Dockerfile` - Docker container for drive-thru agent (uses `agent.py`)
- `Makefile` - Already only references `agent.py`
- `CHANGELOG.md` - Keep unchanged (historical record)

## Desired End State

A simplified codebase with only the McDonald's Drive-Thru Agent:

- Single entry point: `src/agent.py`
- Single Docker container: `Dockerfile`
- All tests pass with `make test`
- Documentation accurately reflects the drive-thru-only focus

**Success Criteria:**
- [x] `src/app.py` no longer exists
- [x] `src/keyword_intercept_llm.py` no longer exists
- [x] `src/mock_llm.py` no longer exists
- [x] `tests/test_agent.py` no longer exists
- [x] `tests/test_keyword_intercept.py` no longer exists
- [x] `Dockerfile.voice` no longer exists
- [x] `plan/future-plans/remove-mcdonalds-voice-agent.md` no longer exists
- [x] `plan/future-plans/remove-mcdonalds-voice-agent.REVIEW.md` no longer exists
- [x] All remaining tests pass: `make test` (188 tests passed)
- [x] Code linting passes: `make lint` (src/ and tests/ clean)
- [x] README.md has no references to `app.py` or "Generic Voice Assistant"
- [x] AGENTS.md still has no references to `app.py` (verify unchanged)
- [x] Drive-thru agent CLI works: `uv run python src/agent.py --help`

**How to Verify:**
```bash
# Verify files are deleted
ls src/app.py src/keyword_intercept_llm.py src/mock_llm.py 2>&1 | grep -c "No such file" | grep -q 3
ls tests/test_agent.py tests/test_keyword_intercept.py 2>&1 | grep -c "No such file" | grep -q 2
ls Dockerfile.voice 2>&1 | grep -q "No such file"

# Verify tests pass
make test

# Verify linting passes
make lint

# Verify no references in docs
grep -r "app.py" README.md AGENTS.md | wc -l  # Should be 0
grep -r "Generic Voice" README.md | wc -l     # Should be 0
```

## What We're NOT Doing

- **NOT** modifying `CHANGELOG.md` - keeping historical record intact
- **NOT** removing shared infrastructure (`config.py`, `factories.py`, `session_handler.py`)
- **NOT** modifying any drive-thru agent code
- **NOT** modifying `Dockerfile` (the main one that uses `agent.py`)
- **NOT** modifying `Makefile` (already only references `agent.py`)

## Dependencies

**Execution Order:**

1. Phase 1: Delete Source Files (no dependencies)
2. Phase 2: Delete Test Files (no dependencies)
3. Phase 3: Delete Container and Plan Files (no dependencies)
4. Phase 4: Update Documentation (no dependencies)

**Dependency Graph:**

```
Phase 1 (Source Files)     ─┐
Phase 2 (Test Files)       ─┼─> Final Verification
Phase 3 (Container/Plans)  ─┤
Phase 4 (Documentation)    ─┘
```

**Parallelization:**
- All four phases can run in parallel (independent deletions and updates)
- Final verification should wait for all phases to complete

---

## Phase 1: Delete Source Files

### Overview
Remove the generic voice assistant source code and its helper modules.

### Context
Before starting, read these files to confirm they exist:
- `src/app.py` - the file to delete
- `src/keyword_intercept_llm.py` - the file to delete
- `src/mock_llm.py` - the file to delete

### Dependencies
**Depends on:** None
**Required by:** Final Verification

### Changes Required

#### 1.1: Delete Generic Voice Assistant
**File:** `src/app.py`

**Action:** Delete the entire file

```bash
rm src/app.py
```

**Rationale:** This is the main entry point for the generic voice assistant that we're removing.

#### 1.2: Delete Keyword Intercept LLM
**File:** `src/keyword_intercept_llm.py`

**Action:** Delete the entire file

```bash
rm src/keyword_intercept_llm.py
```

**Rationale:** This wrapper LLM is only used in tests with the generic Assistant class. It's not used by the drive-thru agent.

#### 1.3: Delete Mock LLM
**File:** `src/mock_llm.py`

**Action:** Delete the entire file

```bash
rm src/mock_llm.py
```

**Rationale:** This mock is only used in tests with the generic Assistant class. The drive-thru agent tests use different mocking approaches.

### Success Criteria

#### Automated Verification:
- [x] File does not exist: `! test -f src/app.py`
- [x] File does not exist: `! test -f src/keyword_intercept_llm.py`
- [x] File does not exist: `! test -f src/mock_llm.py`
- [x] Drive-thru agent CLI still works: `uv run python src/agent.py --help`

---

## Phase 2: Delete Test Files

### Overview
Remove test files that test the generic voice assistant functionality.

### Context
Before starting, read these files to confirm they exist:
- `tests/test_agent.py` - the file to delete
- `tests/test_keyword_intercept.py` - the file to delete

### Dependencies
**Depends on:** None
**Required by:** Final Verification

### Changes Required

#### 2.1: Delete Generic Agent Tests
**File:** `tests/test_agent.py`

**Action:** Delete the entire file

```bash
rm tests/test_agent.py
```

**Rationale:** These tests test the `Assistant` class from `app.py` which we're removing.

#### 2.2: Delete Keyword Intercept Tests
**File:** `tests/test_keyword_intercept.py`

**Action:** Delete the entire file

```bash
rm tests/test_keyword_intercept.py
```

**Rationale:** These tests test `KeywordInterceptLLM` using the `Assistant` class. Both are being removed.

### Success Criteria

#### Automated Verification:
- [x] File does not exist: `! test -f tests/test_agent.py`
- [x] File does not exist: `! test -f tests/test_keyword_intercept.py`
- [x] Remaining tests pass: `make test`

---

## Phase 3: Delete Container and Plan Files

### Overview
Remove the Docker container for the generic voice assistant and the obsolete planning files.

### Context
Before starting, read these files to confirm they exist:
- `Dockerfile.voice` - the file to delete
- `plan/future-plans/remove-mcdonalds-voice-agent.md` - the file to delete
- `plan/future-plans/remove-mcdonalds-voice-agent.REVIEW.md` - the file to delete

### Dependencies
**Depends on:** None
**Required by:** Final Verification

### Changes Required

#### 3.1: Delete Voice Assistant Dockerfile
**File:** `Dockerfile.voice`

**Action:** Delete the entire file

```bash
rm Dockerfile.voice
```

**Rationale:** This Dockerfile runs `app.py` which we're removing. The main `Dockerfile` runs `agent.py` and should remain.

#### 3.2: Delete Obsolete Plan File
**File:** `plan/future-plans/remove-mcdonalds-voice-agent.md`

**Action:** Delete the entire file

```bash
rm plan/future-plans/remove-mcdonalds-voice-agent.md
```

**Rationale:** This plan proposed removing the McDonald's agent (opposite direction). It's now obsolete.

#### 3.3: Delete Obsolete Plan Review
**File:** `plan/future-plans/remove-mcdonalds-voice-agent.REVIEW.md`

**Action:** Delete the entire file

```bash
rm plan/future-plans/remove-mcdonalds-voice-agent.REVIEW.md
```

**Rationale:** Review of the obsolete plan.

### Success Criteria

#### Automated Verification:
- [x] File does not exist: `! test -f Dockerfile.voice`
- [x] File does not exist: `! test -f plan/future-plans/remove-mcdonalds-voice-agent.md`
- [x] File does not exist: `! test -f plan/future-plans/remove-mcdonalds-voice-agent.REVIEW.md`

---

## Phase 4: Update Documentation

### Overview
Update README.md and AGENTS.md to remove references to the generic voice assistant.

### Context
Before starting, read these files:
- `README.md` - to identify sections to update
- `AGENTS.md` - to identify sections to update

### Dependencies
**Depends on:** None
**Required by:** Final Verification

### Changes Required

#### 4.1: Update README.md
**File:** `README.md`

**Changes:**

1. **Update header description** (lines 7-10):
   - Line 7: Change "This repository contains **two main applications**:" to "This repository contains a specialized voice AI agent:"
   - Remove line 10: "2. **Generic Voice Assistant** (`src/app.py`) - A general-purpose voice AI assistant"
   - Keep only the drive-thru agent description

2. **Update Table of Contents** (line 31):
   - Remove: "  - [Generic Voice Assistant](#generic-voice-assistant)"

3. **Remove "Generic Voice Assistant" section** (lines 233-253):
   - Delete the entire section including:
     - "## Generic Voice Assistant"
     - "### What It Does"
     - "### Running the Voice Assistant"
     - The code example `uv run python src/app.py`

4. **Update "Overview" section** (lines 48-53):
   - Line 50: Change "two distinct entry points" to "a specialized entry point"
   - Remove line 53: "- **`src/app.py`** - Generic Voice Assistant (general-purpose AI)"
   - Rephrase to make it singular focus

5. **Update "Project Structure" section** (line 262):
   - Remove: `├── app.py                    # Generic Voice Assistant`

6. **Update "Architecture" section** (line 373):
   - Change "3. **Wiring** - `src/agent.py` or `src/app.py` (creates app + server)" to "3. **Wiring** - `src/agent.py` (creates app + server)"

**Rationale:** Documentation should accurately reflect that this is now a single-purpose drive-thru agent repository.

#### 4.2: Verify AGENTS.md (No Changes Needed)
**File:** `AGENTS.md`

**Action:** Verify that AGENTS.md contains no references to `app.py`

```bash
grep -q "app\.py" AGENTS.md && echo "Found references to app.py" || echo "No references found - AGENTS.md is already correct"
```

**Expected Result:** AGENTS.md already only references `agent.py` (line 343: "Wiring: `src/agent.py` (creates the app + server)"). No changes are needed.

**Rationale:** AGENTS.md is already correct and focused on the drive-thru agent entry point.

### Success Criteria

#### Automated Verification:
- [x] No references to app.py: `! grep -q "app.py" README.md`
- [x] No references to "Generic Voice": `! grep -qi "generic voice" README.md`
- [x] Verify AGENTS.md still has no references to app.py: `! grep -q "app.py" AGENTS.md`
- [x] Linting passes: `make lint` (src/ and tests/ directories clean)

#### Manual Verification:
- [ ] README.md reads coherently after changes
- [ ] No broken links in table of contents
- [ ] Project description accurately reflects drive-thru-only focus
- [ ] Header properly describes single application instead of two

---

## Testing Strategy

### Automated Tests:
After all phases complete:
```bash
# Run all remaining tests
make test

# Verify linting passes
make lint

# Verify the drive-thru agent still runs
uv run python src/agent.py --help
```

### Manual Testing:
1. Run `make console` and verify drive-thru agent works
2. Review README.md to ensure it reads coherently
3. Verify no broken references in documentation

## References

- Original request: Remove generic voice assistant, keep only drive-thru agent
- Files identified via codebase search
- CHANGELOG.md preserved for historical context
