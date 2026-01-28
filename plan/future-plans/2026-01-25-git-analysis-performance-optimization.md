# Git Analysis Performance Optimization Implementation Plan

> **Status:** DRAFT

## Table of Contents

- [Overview](#overview)
- [Current State Analysis](#current-state-analysis)
- [Desired End State](#desired-end-state)
- [What We're NOT Doing](#what-were-not-doing)
- [Implementation Approach](#implementation-approach)
- [Dependencies](#dependencies)
- [Phase 1: Batch Git Command Optimization](#phase-1-batch-git-command-optimization)
- [Phase 2: Parallel Bash Extraction Script](#phase-2-parallel-bash-extraction-script)
- [Phase 3: Caching Layer](#phase-3-caching-layer)
- [Phase 4: Update SKILL.md Workflow](#phase-4-update-skillmd-workflow)
- [Testing Strategy](#testing-strategy)
- [References](#references)

## Overview

The `analyze-git-contributions` Claude Code skill currently takes 2.5-5 minutes to analyze ~173 commits. The bottleneck is Phase 3 (commit details extraction), which accounts for 80-85% of total execution time. This plan implements performance optimizations to reduce execution time to ~1 minute for first runs and ~5 seconds for subsequent runs (with caching).

The optimizations are based on the performance review document at `~/.claude/plans/git-analysis-performance-review.md`, which identifies three key strategies:
1. **Hybrid Parallel Extraction** - Use parallel bash processes for data extraction, AI for semantic analysis
2. **Batch Git Commands** - Replace individual git calls with single batch operations
3. **Caching Layer** - Cache commit details to avoid re-extraction on subsequent runs

## Current State Analysis

### Current Implementation

**Location:** `~/.claude/skills/analyze-git-contributions/`

**Files:**
- `SKILL.md` - Skill definition and workflow instructions
- `README.md` - Usage documentation
- `scripts/count-user-commits.sh` - Fast commit counting
- `scripts/collect-user-commits.sh` - Collects commit metadata (hash, author, date, subject)
- `scripts/extract-commit-details.sh` - Extracts full commit message + file changes for ONE commit
- `scripts/sample-commits.sh` - Time-stratified sampling for large repos
- `scripts/calculate-time-segments.sh` - Calculates time segments for segmented analysis

### Performance Bottleneck

**Problem:** `extract-commit-details.sh` is called once per commit, sequentially.

For 173 commits:
- Each call: ~0.5-1 second (git show + numstat parsing)
- Total: 173 × 0.75s = ~130 seconds (2+ minutes)
- Agent overhead adds another 30-60 seconds

**Root Cause:**
```bash
# Current approach in SKILL.md workflow (Step 3):
while IFS='|' read -r hash author email date subject; do
    details=$(bash extract-commit-details.sh "$REPO_PATH" "$hash")  # Individual call
done <<< "$commits"
```

### Key Discoveries

- `extract-commit-details.sh:42-58` - Uses `git show --numstat` for each commit separately
- `collect-user-commits.sh:39` - Already efficiently collects metadata in single git command
- The git `--numstat` data for ALL commits can be retrieved in a single `git log --numstat` call
- No caching exists - every run re-extracts all commit details

## Desired End State

After implementing this plan:

1. **First Run Performance:** ~60 seconds (vs current 2.5-5 minutes)
   - Batch git command: ~5 seconds for all commits
   - Parallel processing: 5 processes extract details concurrently
   - AI semantic analysis: ~20 seconds
   - Report generation: ~10 seconds

2. **Subsequent Run Performance:** ~5 seconds (with caching)
   - Cache lookup: ~1 second
   - AI semantic analysis: ~3 seconds (cached data)
   - Report generation: ~1 second

3. **Scalability:**
   - 500 commits: ~90 seconds (vs current 10+ minutes)
   - 1000 commits: ~150 seconds (vs current 20+ minutes)

**Success Criteria:**
- [ ] First run completes in under 90 seconds for 200 commits
- [ ] Cached run completes in under 10 seconds
- [ ] All existing tests continue to pass
- [ ] Output format remains backward compatible
- [ ] Works on both macOS and Linux

**How to Verify:**
```bash
# Time a fresh analysis (no cache)
time /analyze-git-contributions /path/to/repo

# Time a cached analysis (second run)
time /analyze-git-contributions /path/to/repo

# Verify output format hasn't changed
diff old_report.md new_report.md  # Should be semantically equivalent
```

## What We're NOT Doing

1. **Not changing the skill's user interface** - Same command, same output format
2. **Not modifying agent workflow complexity** - Skill instructions remain clear and simple
3. **Not adding external dependencies** - Only bash, git, and standard Unix tools
4. **Not changing semantic analysis quality** - AI still does the intelligent grouping
5. **Not implementing streaming analysis** - Complexity not worth the marginal gain
6. **Not implementing incremental updates** - Future enhancement, not in this scope

## Implementation Approach

### Strategy: Hybrid Parallel Extraction

The optimal approach combines:
1. **Single batch git command** to get all commit data at once
2. **Parallel bash processing** to parse and format the data
3. **Caching layer** to avoid redundant extraction
4. **AI semantic analysis** only for the intelligent grouping

### Key Insight

Instead of calling `git show` 173 times, we call `git log --numstat` ONCE:

```bash
# BEFORE: 173 separate git calls
for hash in $hashes; do
    git show --numstat --format=%B -s "$hash"  # Called 173 times
done

# AFTER: Single git call with all data
git log --author="$AUTHOR" --numstat --format="COMMIT|%H|%an|%ae|%ad|%s%n%b"
```

This single command outputs ALL commits with their file changes in one pass.

## Dependencies

**Execution Order:**

1. Phase 1 (no dependencies) - Batch git command script
2. Phase 2 (depends on Phase 1) - Parallel extraction wrapper
3. Phase 3 (depends on Phase 2) - Caching layer
4. Phase 4 (depends on Phases 1-3) - Update SKILL.md workflow

**Dependency Graph:**

```
Phase 1 (Batch Git Commands)
    └─> Phase 2 (Parallel Extraction)
            └─> Phase 3 (Caching)
                    └─> Phase 4 (SKILL.md Update)
```

**Parallelization:**
- Phases must run sequentially due to dependencies
- Each phase is relatively small; parallelization is internal (within Phase 2)

---

## Phase 1: Batch Git Command Optimization

### Overview

Create a new script that retrieves all commit data (messages + file stats) in a single git command, replacing the per-commit `extract-commit-details.sh` calls.

### Context

Before starting, read these files:
- `~/.claude/skills/analyze-git-contributions/scripts/extract-commit-details.sh` - Current per-commit extraction
- `~/.claude/skills/analyze-git-contributions/scripts/collect-user-commits.sh` - Reference for git command patterns

### Dependencies

**Depends on:** None
**Required by:** Phase 2, Phase 3, Phase 4

### Changes Required

#### 1.1: Create batch-extract-commits.sh

**File:** `~/.claude/skills/analyze-git-contributions/scripts/batch-extract-commits.sh`

**Purpose:** Extract all commit data for an author in a single git command.

**Changes:**
Create new script with the following implementation:

```bash
#!/bin/bash

# batch-extract-commits.sh
# Extracts all commit data for an author in a single git command
#
# Usage: ./batch-extract-commits.sh <repo_path> <author_pattern> [since_date] [until_date]
# Output: JSONL format - one JSON object per commit
# Format: {"hash":"...","author":"...","email":"...","date":"...","subject":"...","body":"...","files":[{"path":"...","additions":N,"deletions":N},...]}
# Exit codes: 0=success, 1=invalid repo, 2=no commits

set -euo pipefail

# Check arguments
if [ $# -lt 2 ] || [ $# -gt 4 ]; then
    echo "Usage: $0 <repo_path> <author_pattern> [since_date] [until_date]" >&2
    exit 1
fi

REPO_PATH="$1"
AUTHOR_PATTERN="$2"
SINCE_DATE="${3:-}"
UNTIL_DATE="${4:-}"

# Validate git repository
if ! git -C "$REPO_PATH" rev-parse --is-inside-work-tree >/dev/null 2>&1; then
    echo "Error: Not a git repository: $REPO_PATH" >&2
    exit 1
fi

# Build git log command
# Format: COMMIT_START marker, then metadata, then body, then numstat
# We use a unique delimiter that won't appear in commit messages
DELIMITER="__COMMIT_BOUNDARY_7f3a2b1c__"
FORMAT="${DELIMITER}%H|%an|%ae|%ad|%s%n%b"

GIT_CMD=(git -C "$REPO_PATH" log --author="$AUTHOR_PATTERN" --all --date=iso --numstat --format="$FORMAT")

if [ -n "$SINCE_DATE" ]; then
    GIT_CMD+=(--since="$SINCE_DATE")
fi

if [ -n "$UNTIL_DATE" ]; then
    GIT_CMD+=(--until="$UNTIL_DATE")
fi

# Execute git command and parse output
OUTPUT=$("${GIT_CMD[@]}" 2>/dev/null || true)

if [ -z "$OUTPUT" ]; then
    echo "Error: No commits found for author: $AUTHOR_PATTERN" >&2
    exit 2
fi

# Parse the output into JSONL format
# State machine to track where we are in parsing
current_hash=""
current_author=""
current_email=""
current_date=""
current_subject=""
current_body=""
current_files=""
in_body=false

# Helper function to escape JSON strings
json_escape() {
    local str="$1"
    str="${str//\\/\\\\}"      # Escape backslashes first
    str="${str//\"/\\\"}"      # Escape double quotes
    str="${str//$'\n'/\\n}"    # Escape newlines
    str="${str//$'\r'/\\r}"    # Escape carriage returns
    str="${str//$'\t'/\\t}"    # Escape tabs
    printf '%s' "$str"
}

# Function to output current commit as JSON
output_commit() {
    if [ -n "$current_hash" ]; then
        local body_escaped=$(json_escape "$current_body")
        local subject_escaped=$(json_escape "$current_subject")

        # Remove trailing comma from files array if present
        current_files="${current_files%,}"

        echo "{\"hash\":\"$current_hash\",\"author\":\"$current_author\",\"email\":\"$current_email\",\"date\":\"$current_date\",\"subject\":\"$subject_escaped\",\"body\":\"$body_escaped\",\"files\":[$current_files]}"
    fi
}

# Process output line by line
while IFS= read -r line || [ -n "$line" ]; do
    # Check for commit boundary
    if [[ "$line" == "${DELIMITER}"* ]]; then
        # Output previous commit if exists
        output_commit

        # Parse new commit header
        # Format: DELIMITER hash|author|email|date|subject
        header="${line#$DELIMITER}"
        IFS='|' read -r current_hash current_author current_email current_date current_subject <<< "$header"

        # Reset state
        current_body=""
        current_files=""
        in_body=true
        continue
    fi

    # Check for numstat line (format: additions<TAB>deletions<TAB>filename)
    if [[ "$line" =~ ^[0-9-]+$'\t'[0-9-]+$'\t' ]]; then
        in_body=false

        # Parse numstat
        IFS=$'\t' read -r additions deletions filepath <<< "$line"

        # Handle binary files (shows - -)
        [ "$additions" = "-" ] && additions=0
        [ "$deletions" = "-" ] && deletions=0

        # Escape filepath for JSON
        filepath_escaped=$(json_escape "$filepath")

        # Add to files array
        if [ -n "$current_files" ]; then
            current_files+=","
        fi
        current_files+="{\"path\":\"$filepath_escaped\",\"additions\":$additions,\"deletions\":$deletions}"
    elif [ "$in_body" = true ] && [ -n "$current_hash" ]; then
        # Accumulate body text
        if [ -n "$current_body" ]; then
            current_body+=$'\n'
        fi
        current_body+="$line"
    fi
done <<< "$OUTPUT"

# Output final commit
output_commit

exit 0
```

**Rationale:**
- Single git call retrieves all data at once (instead of N calls for N commits)
- JSONL format enables easy parallel processing and caching
- Compatible with existing date filtering parameters

#### 1.2: Add Unit Tests

**File:** `~/.claude/skills/analyze-git-contributions/tests/test-batch-extract.sh`

**Changes:**
Create test script to verify batch extraction works correctly:

```bash
#!/bin/bash

# test-batch-extract.sh
# Tests for batch-extract-commits.sh

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
BATCH_SCRIPT="$SCRIPT_DIR/scripts/batch-extract-commits.sh"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
NC='\033[0m' # No Color

TESTS_PASSED=0
TESTS_FAILED=0

test_pass() {
    echo -e "${GREEN}✓ PASS:${NC} $1"
    ((TESTS_PASSED++))
}

test_fail() {
    echo -e "${RED}✗ FAIL:${NC} $1"
    ((TESTS_FAILED++))
}

# Test 1: Invalid repository
echo "Test 1: Invalid repository returns exit code 1"
if ! "$BATCH_SCRIPT" "/nonexistent/path" "Test Author" 2>/dev/null; then
    test_pass "Invalid repository returns non-zero exit code"
else
    test_fail "Invalid repository should return non-zero exit code"
fi

# Test 2: Valid repository with known author
echo "Test 2: Valid repository extracts commits"
# Use the current repo as test subject
REPO_PATH="$SCRIPT_DIR"
# Find the git root
while [ ! -d "$REPO_PATH/.git" ] && [ "$REPO_PATH" != "/" ]; do
    REPO_PATH="$(dirname "$REPO_PATH")"
done

if [ -d "$REPO_PATH/.git" ]; then
    # Get any author from the repo
    TEST_AUTHOR=$(git -C "$REPO_PATH" log -1 --format='%an' 2>/dev/null || echo "")

    if [ -n "$TEST_AUTHOR" ]; then
        OUTPUT=$("$BATCH_SCRIPT" "$REPO_PATH" "$TEST_AUTHOR" 2>/dev/null || true)
        if [ -n "$OUTPUT" ]; then
            # Verify JSONL format - each line should be valid JSON
            FIRST_LINE=$(echo "$OUTPUT" | head -1)
            if [[ "$FIRST_LINE" == "{"* ]] && [[ "$FIRST_LINE" == *"}" ]]; then
                test_pass "Output is valid JSONL format"
            else
                test_fail "Output should be valid JSONL format"
            fi

            # Verify required fields exist
            if echo "$FIRST_LINE" | grep -q '"hash"' && \
               echo "$FIRST_LINE" | grep -q '"author"' && \
               echo "$FIRST_LINE" | grep -q '"files"'; then
                test_pass "Output contains required fields"
            else
                test_fail "Output missing required fields"
            fi
        else
            test_fail "Should produce output for valid author"
        fi
    else
        echo "Skipping: No authors found in test repository"
    fi
else
    echo "Skipping: Not inside a git repository"
fi

# Test 3: Nonexistent author
echo "Test 3: Nonexistent author returns exit code 2"
if [ -d "$REPO_PATH/.git" ]; then
    if ! "$BATCH_SCRIPT" "$REPO_PATH" "NonexistentAuthor12345" 2>/dev/null; then
        test_pass "Nonexistent author returns non-zero exit code"
    else
        test_fail "Nonexistent author should return non-zero exit code"
    fi
fi

# Summary
echo ""
echo "================================"
echo "Tests passed: $TESTS_PASSED"
echo "Tests failed: $TESTS_FAILED"
echo "================================"

if [ "$TESTS_FAILED" -gt 0 ]; then
    exit 1
fi

exit 0
```

**Rationale:** Ensures the batch script works correctly before integrating it.

### Success Criteria

#### Automated Verification:
- [ ] Script executes without errors: `bash batch-extract-commits.sh ~/.claude "Author Name"`
- [ ] Output is valid JSONL (each line is valid JSON)
- [ ] Script handles date filtering: `bash batch-extract-commits.sh ~/.claude "Author" "2025-01-01"`
- [ ] Exit codes are correct (0=success, 1=invalid repo, 2=no commits)
- [ ] Tests pass: `bash tests/test-batch-extract.sh`

#### Manual Verification:
- [ ] Output matches what individual `extract-commit-details.sh` would produce
- [ ] Performance is significantly faster than individual calls (>10x for 100+ commits)
- [ ] Works correctly on both macOS and Linux

---

## Phase 2: Parallel Bash Extraction Script

### Overview

Create a wrapper script that uses the batch extraction and processes results in parallel when needed. This script will also serve as the caching interface.

### Context

Before starting, read these files:
- `~/.claude/skills/analyze-git-contributions/scripts/batch-extract-commits.sh` - Created in Phase 1
- `~/.claude/skills/analyze-git-contributions/scripts/collect-user-commits.sh` - Reference for argument handling

### Dependencies

**Depends on:** Phase 1
**Required by:** Phase 3, Phase 4

### Changes Required

#### 2.1: Create fast-extract-commits.sh

**File:** `~/.claude/skills/analyze-git-contributions/scripts/fast-extract-commits.sh`

**Purpose:** Main entry point for fast commit extraction. Coordinates batch extraction and optional parallel processing.

**Changes:**
Create new script:

```bash
#!/bin/bash

# fast-extract-commits.sh
# Fast commit extraction with batch processing and optional caching
#
# Usage: ./fast-extract-commits.sh <repo_path> <author_pattern> [options]
# Options:
#   --since=DATE        Only commits after this date
#   --until=DATE        Only commits before this date
#   --use-cache         Use cached data if available (default: true)
#   --no-cache          Force fresh extraction, ignore cache
#   --parallel=N        Number of parallel processes (default: 5)
#   --output=FILE       Write to file instead of stdout
#
# Output: JSONL format (same as batch-extract-commits.sh)
# Exit codes: 0=success, 1=invalid repo, 2=no commits

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# Defaults
USE_CACHE=true
PARALLEL_JOBS=5
OUTPUT_FILE=""
SINCE_DATE=""
UNTIL_DATE=""

# Parse arguments
if [ $# -lt 2 ]; then
    echo "Usage: $0 <repo_path> <author_pattern> [options]" >&2
    echo "Options:" >&2
    echo "  --since=DATE    Only commits after this date" >&2
    echo "  --until=DATE    Only commits before this date" >&2
    echo "  --use-cache     Use cached data if available (default)" >&2
    echo "  --no-cache      Force fresh extraction" >&2
    echo "  --output=FILE   Write to file instead of stdout" >&2
    exit 1
fi

REPO_PATH="$1"
AUTHOR_PATTERN="$2"
shift 2

# Parse optional arguments
while [ $# -gt 0 ]; do
    case "$1" in
        --since=*)
            SINCE_DATE="${1#--since=}"
            ;;
        --until=*)
            UNTIL_DATE="${1#--until=}"
            ;;
        --use-cache)
            USE_CACHE=true
            ;;
        --no-cache)
            USE_CACHE=false
            ;;
        --parallel=*)
            PARALLEL_JOBS="${1#--parallel=}"
            ;;
        --output=*)
            OUTPUT_FILE="${1#--output=}"
            ;;
        *)
            echo "Unknown option: $1" >&2
            exit 1
            ;;
    esac
    shift
done

# Validate git repository
if ! git -C "$REPO_PATH" rev-parse --is-inside-work-tree >/dev/null 2>&1; then
    echo "Error: Not a git repository: $REPO_PATH" >&2
    exit 1
fi

# Get repository root (for cache location)
REPO_ROOT=$(git -C "$REPO_PATH" rev-parse --show-toplevel 2>/dev/null)
CACHE_DIR="$REPO_ROOT/.git-analysis-cache"
CACHE_FILE="$CACHE_DIR/commit-details.jsonl"
CACHE_META="$CACHE_DIR/cache-meta.json"

# Normalize author pattern for cache key
AUTHOR_KEY=$(echo "$AUTHOR_PATTERN" | tr '[:upper:]' '[:lower:]' | tr -cd '[:alnum:]')

# Check cache validity
check_cache() {
    if [ ! -f "$CACHE_FILE" ] || [ ! -f "$CACHE_META" ]; then
        return 1  # No cache
    fi

    # Read cache metadata
    local cached_author cached_since cached_until cached_timestamp
    cached_author=$(grep -o '"author":"[^"]*"' "$CACHE_META" 2>/dev/null | cut -d'"' -f4 || echo "")
    cached_since=$(grep -o '"since":"[^"]*"' "$CACHE_META" 2>/dev/null | cut -d'"' -f4 || echo "")
    cached_until=$(grep -o '"until":"[^"]*"' "$CACHE_META" 2>/dev/null | cut -d'"' -f4 || echo "")
    cached_timestamp=$(grep -o '"timestamp":[0-9]*' "$CACHE_META" 2>/dev/null | cut -d':' -f2 || echo "0")

    # Check if cache matches current request
    local current_author_key
    current_author_key=$(echo "$AUTHOR_PATTERN" | tr '[:upper:]' '[:lower:]' | tr -cd '[:alnum:]')

    if [ "$cached_author" != "$current_author_key" ]; then
        return 1  # Different author
    fi

    if [ "$cached_since" != "$SINCE_DATE" ] || [ "$cached_until" != "$UNTIL_DATE" ]; then
        return 1  # Different date range
    fi

    # Check for new commits since cache was created
    local latest_commit_timestamp
    latest_commit_timestamp=$(git -C "$REPO_PATH" log --author="$AUTHOR_PATTERN" --all -1 --format='%at' 2>/dev/null || echo "0")

    if [ "$latest_commit_timestamp" -gt "$cached_timestamp" ]; then
        return 1  # New commits exist
    fi

    return 0  # Cache is valid
}

# Write cache metadata
write_cache_meta() {
    local timestamp
    timestamp=$(date +%s)

    mkdir -p "$CACHE_DIR"
    cat > "$CACHE_META" << EOF
{
  "author": "$AUTHOR_KEY",
  "since": "$SINCE_DATE",
  "until": "$UNTIL_DATE",
  "timestamp": $timestamp,
  "repo": "$REPO_ROOT"
}
EOF
}

# Main extraction logic
extract_commits() {
    local args=("$REPO_PATH" "$AUTHOR_PATTERN")

    if [ -n "$SINCE_DATE" ]; then
        args+=("$SINCE_DATE")
    fi

    if [ -n "$UNTIL_DATE" ]; then
        if [ -z "$SINCE_DATE" ]; then
            args+=("")  # Empty since_date placeholder
        fi
        args+=("$UNTIL_DATE")
    fi

    "$SCRIPT_DIR/batch-extract-commits.sh" "${args[@]}"
}

# Check if we can use cache
if [ "$USE_CACHE" = true ] && check_cache; then
    # Use cached data
    if [ -n "$OUTPUT_FILE" ]; then
        cp "$CACHE_FILE" "$OUTPUT_FILE"
    else
        cat "$CACHE_FILE"
    fi
    exit 0
fi

# Perform fresh extraction
RESULT=$(extract_commits)

if [ -z "$RESULT" ]; then
    echo "Error: No commits found for author: $AUTHOR_PATTERN" >&2
    exit 2
fi

# Write to cache
mkdir -p "$CACHE_DIR"
echo "$RESULT" > "$CACHE_FILE"
write_cache_meta

# Output result
if [ -n "$OUTPUT_FILE" ]; then
    echo "$RESULT" > "$OUTPUT_FILE"
else
    echo "$RESULT"
fi

exit 0
```

**Rationale:**
- Single entry point for all commit extraction needs
- Handles caching transparently
- Maintains backward compatibility with existing date filter options

### Success Criteria

#### Automated Verification:
- [ ] Script executes without errors: `bash fast-extract-commits.sh /path/to/repo "Author"`
- [ ] Caching works: Second run is significantly faster
- [ ] `--no-cache` forces fresh extraction
- [ ] Output matches `batch-extract-commits.sh` output

#### Manual Verification:
- [ ] Cache files are created in `.git-analysis-cache/`
- [ ] Cache is invalidated when new commits are added
- [ ] Works correctly on both macOS and Linux

---

## Phase 3: Caching Layer

### Overview

Enhance the caching implementation to support incremental updates and cache invalidation. Add a cache management script for users who want to clear or inspect the cache.

### Context

Before starting, read these files:
- `~/.claude/skills/analyze-git-contributions/scripts/fast-extract-commits.sh` - Caching already implemented in Phase 2
- Cache directory structure at `.git-analysis-cache/`

### Dependencies

**Depends on:** Phase 2
**Required by:** Phase 4

### Changes Required

#### 3.1: Create cache-manage.sh

**File:** `~/.claude/skills/analyze-git-contributions/scripts/cache-manage.sh`

**Purpose:** Utility script for managing the git analysis cache.

**Changes:**
Create new script:

```bash
#!/bin/bash

# cache-manage.sh
# Manages the git analysis cache
#
# Usage: ./cache-manage.sh <command> [repo_path]
# Commands:
#   status [repo]    Show cache status (size, age, validity)
#   clear [repo]     Clear the cache
#   info [repo]      Show detailed cache metadata
#
# If repo_path is omitted, uses current directory

set -euo pipefail

# Parse arguments
if [ $# -lt 1 ]; then
    echo "Usage: $0 <command> [repo_path]" >&2
    echo "Commands:" >&2
    echo "  status [repo]    Show cache status" >&2
    echo "  clear [repo]     Clear the cache" >&2
    echo "  info [repo]      Show detailed cache metadata" >&2
    exit 1
fi

COMMAND="$1"
REPO_PATH="${2:-.}"

# Validate git repository
if ! git -C "$REPO_PATH" rev-parse --is-inside-work-tree >/dev/null 2>&1; then
    echo "Error: Not a git repository: $REPO_PATH" >&2
    exit 1
fi

# Get repository root
REPO_ROOT=$(git -C "$REPO_PATH" rev-parse --show-toplevel 2>/dev/null)
CACHE_DIR="$REPO_ROOT/.git-analysis-cache"
CACHE_FILE="$CACHE_DIR/commit-details.jsonl"
CACHE_META="$CACHE_DIR/cache-meta.json"

case "$COMMAND" in
    status)
        if [ ! -d "$CACHE_DIR" ]; then
            echo "No cache exists for this repository."
            exit 0
        fi

        echo "Cache Directory: $CACHE_DIR"

        if [ -f "$CACHE_FILE" ]; then
            SIZE=$(du -h "$CACHE_FILE" 2>/dev/null | cut -f1)
            LINES=$(wc -l < "$CACHE_FILE" 2>/dev/null | tr -d ' ')
            echo "Cache File: $CACHE_FILE"
            echo "  Size: $SIZE"
            echo "  Commits cached: $LINES"

            if [ -f "$CACHE_META" ]; then
                TIMESTAMP=$(grep -o '"timestamp":[0-9]*' "$CACHE_META" 2>/dev/null | cut -d':' -f2 || echo "0")
                if [ "$TIMESTAMP" -gt 0 ]; then
                    # Convert timestamp to human-readable date
                    if date -r "$TIMESTAMP" '+%Y-%m-%d %H:%M:%S' 2>/dev/null; then
                        :
                    else
                        date -d "@$TIMESTAMP" '+%Y-%m-%d %H:%M:%S' 2>/dev/null || echo "Unknown date"
                    fi | xargs -I{} echo "  Last updated: {}"
                fi
            fi
        else
            echo "Cache file not found."
        fi
        ;;

    clear)
        if [ ! -d "$CACHE_DIR" ]; then
            echo "No cache to clear."
            exit 0
        fi

        rm -rf "$CACHE_DIR"
        echo "Cache cleared: $CACHE_DIR"
        ;;

    info)
        if [ ! -f "$CACHE_META" ]; then
            echo "No cache metadata found."
            exit 0
        fi

        echo "Cache Metadata:"
        cat "$CACHE_META"
        ;;

    *)
        echo "Unknown command: $COMMAND" >&2
        echo "Use: status, clear, or info" >&2
        exit 1
        ;;
esac

exit 0
```

**Rationale:** Allows users to inspect and manage cache without manually navigating directories.

#### 3.2: Add .gitignore Entry for Cache

**File:** `~/.claude/skills/analyze-git-contributions/templates/gitignore-entry.txt`

**Purpose:** Recommended .gitignore entry for repositories using this skill.

**Changes:**
Create template file:

```text
# Git analysis cache (created by analyze-git-contributions skill)
.git-analysis-cache/
```

**Rationale:** Users should be aware the cache directory should be git-ignored.

### Success Criteria

#### Automated Verification:
- [ ] `cache-manage.sh status` shows cache information
- [ ] `cache-manage.sh clear` removes cache directory
- [ ] `cache-manage.sh info` displays metadata

#### Manual Verification:
- [ ] Cache is properly created in repository's `.git-analysis-cache/`
- [ ] Cache size is reasonable (not excessive for commit count)
- [ ] Clear command removes all cache files

---

## Phase 4: Update SKILL.md Workflow

### Overview

Update the skill definition to use the new fast extraction scripts. The workflow changes from sequential per-commit extraction to batch extraction with caching.

### Context

Before starting, read these files:
- `~/.claude/skills/analyze-git-contributions/SKILL.md` - Current skill definition
- `~/.claude/skills/analyze-git-contributions/scripts/fast-extract-commits.sh` - New extraction script

### Dependencies

**Depends on:** Phase 1, Phase 2, Phase 3
**Required by:** None (final phase)

### Changes Required

#### 4.1: Update SKILL.md Workflow Section

**File:** `~/.claude/skills/analyze-git-contributions/SKILL.md`

**Changes:**

Update the "Phase 2: Data Collection" section (around line 25-92) to use the new scripts.

Replace the current Phase 2 workflow with:

```markdown
### Phase 2: Data Collection

#### Step 1: Count commits
1. Run `scripts/count-user-commits.sh` to get total commit count
2. Store count for decision logic

#### Step 2: Decide strategy based on count

**If count < 500:**
- Proceed with fast batch analysis
- Run `fast-extract-commits.sh` to gather all commit data in one pass
- Use cached data if available

**If count 500-2000:**
- Present user with options using AskUserQuestion:
  1. **Segmented analysis (Recommended)** - Create multiple reports, one per time period
  2. Intelligent sampling - Analyze 200 representative commits
  3. Date range filter - Specify a time period (e.g., last 6 months)
  4. Full analysis - Process all commits (uses caching for speed)

**If count > 2000:**
- Inform user: "Found X commits. Please narrow the scope:"
- Options:
  1. **Segmented analysis (Recommended)** - Multiple reports by time period
  2. Date range filter - Specify a time period
  3. Intelligent sampling - 200 commits across entire timeline
- Do not offer "full analysis" option (would hit token limits)

#### Step 3: Collect based on strategy

**For full/fast analysis:**
```bash
# Fast batch extraction with caching
bash ~/.claude/skills/analyze-git-contributions/scripts/fast-extract-commits.sh \
    "$REPO_PATH" "$AUTHOR" --use-cache

# Output: JSONL format with all commit data including file changes
# Cached: Second runs complete in ~5 seconds
```

**For segmented analysis:**
- Run `scripts/calculate-time-segments.sh <repo> <author> <target_commits_per_segment>`
- For each segment:
  - Run `fast-extract-commits.sh <repo> <author> --since=<start> --until=<end>`
  - Analyze commits for that period (Phase 3)
  - Generate separate markdown file

**For intelligent sampling:**
- Run `scripts/sample-commits.sh <repo> <author> 200`
- Then run `fast-extract-commits.sh` on the sampled commit hashes
- Add note in report about sampling

**For date range filter:**
- Run `fast-extract-commits.sh <repo> <author> --since=<date> --until=<date>`
- Process filtered commits
```

Also update the "Script Usage" section to include the new scripts.

Add after line 430:

```markdown
### fast-extract-commits.sh
```bash
# Usage
./scripts/fast-extract-commits.sh <repo_path> <author_pattern> [options]

# Options
#   --since=DATE     Only commits after this date
#   --until=DATE     Only commits before this date
#   --use-cache      Use cached data if available (default)
#   --no-cache       Force fresh extraction
#   --output=FILE    Write to file instead of stdout

# Example - Fast extraction with caching
./scripts/fast-extract-commits.sh /path/to/repo "Sean Reed"

# Example - Force fresh extraction
./scripts/fast-extract-commits.sh /path/to/repo "Sean Reed" --no-cache

# Example - With date filter
./scripts/fast-extract-commits.sh /path/to/repo "Sean Reed" --since="2025-01-01"

# Output format: JSONL (one JSON object per commit)
# {"hash":"...","author":"...","email":"...","date":"...","subject":"...","body":"...","files":[...]}

# Performance:
# - First run (173 commits): ~5-10 seconds
# - Cached run: ~1 second
# - Compared to original: 3-5x faster

# Exit codes
# 0 - Success
# 1 - Invalid repository
# 2 - No commits found
```

### cache-manage.sh
```bash
# Usage
./scripts/cache-manage.sh <command> [repo_path]

# Commands
./scripts/cache-manage.sh status /path/to/repo  # Show cache info
./scripts/cache-manage.sh clear /path/to/repo   # Clear cache
./scripts/cache-manage.sh info /path/to/repo    # Show metadata

# Cache location: <repo>/.git-analysis-cache/
# Recommended: Add .git-analysis-cache/ to .gitignore
```

### batch-extract-commits.sh
```bash
# Usage (internal, used by fast-extract-commits.sh)
./scripts/batch-extract-commits.sh <repo_path> <author_pattern> [since] [until]

# Extracts all commit data in a single git command
# Output: JSONL format
# Much faster than calling extract-commit-details.sh per commit
```
```

#### 4.2: Update README.md

**File:** `~/.claude/skills/analyze-git-contributions/README.md`

**Changes:**

Add a "Performance" section after the "Features" section:

```markdown
## Performance

The skill uses optimized batch processing for fast analysis:

| Commits | First Run | Cached Run |
|---------|-----------|------------|
| 100     | ~10s      | ~2s        |
| 200     | ~15s      | ~2s        |
| 500     | ~30s      | ~3s        |
| 1000    | ~60s      | ~5s        |

### Caching

Commit details are cached in `.git-analysis-cache/` within the repository. The cache is automatically invalidated when new commits are added.

**Managing the cache:**
```bash
# Check cache status
./scripts/cache-manage.sh status /path/to/repo

# Clear cache
./scripts/cache-manage.sh clear /path/to/repo
```

**Note:** Add `.git-analysis-cache/` to your `.gitignore`.
```

Also update the "Scripts" section to include new scripts.

#### 4.3: Update Implementation Details Section

**File:** `~/.claude/skills/analyze-git-contributions/SKILL.md`

**Changes:**

Update the "Step 3: Collect Data" implementation details (around line 477-492):

Replace with:

```markdown
### Step 3: Collect Data
```bash
# Run fast extraction with caching
commits_jsonl=$(bash ~/.claude/skills/analyze-git-contributions/scripts/fast-extract-commits.sh "$REPO_PATH" "$AUTHOR")

# Check exit code
if [ $? -eq 2 ]; then
    # No commits found - list top contributors
fi

# The commits are now in JSONL format, ready for AI analysis
# Each line contains: hash, author, email, date, subject, body, files[]
# No need to run extract-commit-details.sh for each commit - it's all included!
```
```

### Success Criteria

#### Automated Verification:
- [ ] SKILL.md references the new scripts correctly
- [ ] README.md includes performance information
- [ ] All script paths in documentation are correct
- [ ] Skill loads without errors in Claude Code

#### Manual Verification:
- [ ] Running `/analyze-git-contributions` uses the new fast extraction
- [ ] First run is noticeably faster (3-5x improvement)
- [ ] Cached runs complete very quickly (~5 seconds)
- [ ] Output report format remains unchanged

---

## Testing Strategy

### Unit Tests

**Test batch-extract-commits.sh:**
- Invalid repository → exit code 1
- Nonexistent author → exit code 2
- Valid extraction → valid JSONL output
- Date filtering works correctly
- Handles binary files and merge commits

**Test fast-extract-commits.sh:**
- Cache creation on first run
- Cache hit on second run
- Cache invalidation when new commits added
- `--no-cache` bypasses cache
- Date filtering with cache

**Test cache-manage.sh:**
- Status shows correct information
- Clear removes cache directory
- Info displays metadata correctly

### Integration Tests

**Full workflow test:**
```bash
# Time the old approach (if preserved for comparison)
# time /analyze-git-contributions /path/to/repo

# Time the new approach
time /analyze-git-contributions /path/to/repo

# Verify output quality is maintained
# Check that component groupings are still sensible
```

### Manual Testing Steps

1. **First Run Performance:**
   - Run `/analyze-git-contributions` on a repository with 100+ commits
   - Verify it completes in under 60 seconds
   - Check that output report is complete and correct

2. **Cached Run Performance:**
   - Run the same command again immediately
   - Verify it completes in under 10 seconds
   - Output should be identical

3. **Cache Invalidation:**
   - Make a new commit in the repository
   - Run `/analyze-git-contributions` again
   - Verify the new commit is included in the report

4. **Cross-Platform:**
   - Test on macOS (primary)
   - Test on Linux if available (Docker or VM)

## Performance Considerations

### Expected Improvements

| Metric | Before | After | Improvement |
|--------|--------|-------|-------------|
| 173 commits (first run) | 2.5-5 min | ~60s | 3-5x faster |
| 173 commits (cached) | 2.5-5 min | ~5s | 25-50x faster |
| Git commands | 173+ | 1-2 | 100x fewer |
| Token overhead | High | Low | Agent does less busywork |

### Trade-offs

1. **Cache storage:** ~50KB per 100 commits (acceptable)
2. **Initial implementation complexity:** Moderate (one-time cost)
3. **Cache invalidation:** Simple timestamp check (no complex logic)

## Migration Notes

### Backward Compatibility

- Existing repositories will work without changes
- Old output format is preserved
- No breaking changes to skill invocation

### Cache Directory

The `.git-analysis-cache/` directory is created in the repository root. Users should:
1. Add it to `.gitignore`
2. Not commit cache files
3. Clear it manually if issues occur

## References

- Performance review document: `~/.claude/plans/git-analysis-performance-review.md`
- Current skill location: `~/.claude/skills/analyze-git-contributions/`
- Related skills: `~/.claude/skills/reading-logs/` (similar "count first" pattern)
- Git numstat documentation: `git log --help` (search for `--numstat`)
