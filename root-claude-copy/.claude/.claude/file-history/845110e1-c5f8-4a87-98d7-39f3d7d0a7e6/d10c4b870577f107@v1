# Analyze Git Contributions Skill

Intelligently analyzes git contributions and groups them by functional components using AI.

## Quick Start

```bash
# From within a git repository
/analyze-git-contributions

# From outside, specify path
/analyze-git-contributions /path/to/repo
```

## What It Does

1. **Collects** all commits for a specified author from a git repository
2. **Analyzes** commits using AI to identify functional components and patterns
3. **Groups** commits semantically by functionality (not just directory structure)
4. **Generates** a comprehensive markdown report with statistics

## Output Example

The skill produces a markdown report with:
- Summary of contribution themes
- Functional component groups (e.g., "Authentication System", "API Endpoints")
- Detailed commit information with file changes
- Statistics (files changed, additions/deletions, most active areas)

## Scripts

### collect-user-commits.sh
Collects all commits for an author with structured output.

```bash
./scripts/collect-user-commits.sh <repo_path> <author_pattern>
# Output: hash|author_name|author_email|date|subject (one per line)
# Exit codes: 0=success, 1=invalid repo, 2=no commits
```

### extract-commit-details.sh
Extracts detailed information for a single commit.

```bash
./scripts/extract-commit-details.sh <repo_path> <commit_hash>
# Output: commit message and file changes with statistics
# Exit codes: 0=success, 1=invalid commit
```

## Features

- **Auto-detection**: Automatically detects repository and author from git config
- **Semantic grouping**: AI analyzes commit patterns to group by functionality
- **Comprehensive**: Includes commit messages, file changes, and statistics
- **Reusable**: Works across different repositories and authors
- **Error handling**: Gracefully handles invalid repos, no commits, large repos

## Testing

Scripts tested successfully with:
- Valid repository: ✅ (1,379 commits analyzed)
- Invalid repository: ✅ (proper error: exit code 1)
- No commits for author: ✅ (proper error: exit code 2)
- Invalid commit hash: ✅ (proper error: exit code 1)
- Multi-file commits: ✅
- Binary files: ✅

## Installation

Already installed at: `~/.claude/skills/analyze-git-contributions/`

The skill will be auto-discovered by Claude Code and available via `/analyze-git-contributions`.
