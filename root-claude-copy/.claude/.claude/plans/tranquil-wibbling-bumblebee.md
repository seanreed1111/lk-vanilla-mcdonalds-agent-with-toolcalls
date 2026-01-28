# Plan: Scale `/analyze-git-contributions` for Large Repositories

## Problem Statement

The `/analyze-git-contributions` skill encounters token limit errors when analyzing repositories with many commits (e.g., 1,379 commits):

**Error Example:**
```
File content (89,049 tokens) exceeds maximum allowed tokens (25,000)
```

**Root Cause:**
- `collect-user-commits.sh` returns all commits (1,379 lines)
- Agent runs `extract-commit-details.sh` for each commit
- Combined output stored in tool result file exceeds Read tool's 25K token limit
- Agent cannot process the results

**Requirements:**
1. Handle repositories with 500-10,000+ commits without hitting token limits
2. Maintain meaningful AI analysis and component grouping
3. Provide user control over scope and sampling strategy
4. Keep skill responsive and usable

## Solution Strategy: Multi-Tier Approach

### Core Principle (from reading-logs skill)
**"Count first, filter/sample, then read"** - Never process all data without checking volume first

### Three Scaling Strategies

1. **Segmented Analysis** (NEW) - Divide timeline into periods, generate multiple reports
   - Analyzes ALL commits without token limits
   - Creates separate report per time segment (3-month periods, quarters, etc.)
   - Each segment stays within token budget (250-400 commits)
   - Best for: Complete analysis, portfolios, year-in-review

2. **Intelligent Sampling** - Analyze representative subset
   - Time-stratified sampling (evenly distributed across timeline)
   - Default: 200 commits from entire history
   - Best for: Quick overview, pattern identification

3. **Date Range Filtering** - Focus on specific time period
   - User specifies --since and/or --until dates
   - Best for: Recent work, specific project phases

### Tier 1: Auto-Process (<500 commits)
- Process all commits with full details
- Current implementation works fine

### Tier 2: User Choice (500-2000 commits)
- Count commits and present all three strategies
- Offer segmented analysis, sampling, date filter, or full analysis
- Recommend segmented analysis for complete coverage

### Tier 3: Require Scoping (>2000 commits)
- Require user to choose strategy (no "process all" option)
- Recommend segmented analysis or date filtering
- Prevent token overflow

## Implementation Approach

### Phase 1: Add Commit Counting Script

**New script:** `scripts/count-user-commits.sh`

```bash
#!/bin/bash
# Fast commit count without fetching details
# Usage: ./count-user-commits.sh <repo_path> <author_pattern>
# Output: Single number (commit count)
# Exit codes: 0=success, 1=invalid repo, 2=no commits

git -C "$REPO_PATH" log --author="$AUTHOR_PATTERN" --all --oneline | wc -l
```

**Why:** Instant feedback on repository size before collecting data

### Phase 2: Add Intelligent Sampling Script

**New script:** `scripts/sample-commits.sh`

```bash
#!/bin/bash
# Samples commits using time-stratified strategy
# Usage: ./sample-commits.sh <repo_path> <author_pattern> <sample_size>
# Strategy: Divide timeline into buckets, sample evenly from each
# Output: Same format as collect-user-commits.sh (subset of commits)

# Algorithm:
# 1. Get date range (first and last commit dates)
# 2. Divide into N time buckets (e.g., 10 buckets for 200 samples)
# 3. Sample ~sample_size/N commits from each bucket
# 4. Ensures coverage across entire contribution timeline
```

**Why:**
- Maintains temporal diversity (captures work from entire timeline)
- More representative than "first N" or "random N" commits
- Useful for portfolios, annual reviews, long-running projects

### Phase 3: Add Date Range Filtering Script

**Enhancement:** Modify `collect-user-commits.sh` to support optional date filters

```bash
# Add optional parameters:
# $3: --since date (optional)
# $4: --until date (optional)

if [ -n "$3" ]; then
    SINCE_FLAG="--since=$3"
fi
if [ -n "$4" ]; then
    UNTIL_FLAG="--until=$4"
fi

git -C "$REPO_PATH" log \
    --author="$AUTHOR_PATTERN" \
    --all \
    $SINCE_FLAG \
    $UNTIL_FLAG \
    --date=iso \
    --format='%H|%an|%ae|%ad|%s'
```

**Why:**
- Most users want recent work analysis (last 6 months, last year)
- Natural way to scope the analysis
- git native filtering (fast)

### Phase 3.5: Add Segmented Analysis Script

**New script:** `scripts/calculate-time-segments.sh`

```bash
#!/bin/bash
# Calculates optimal time segments to keep commits per segment in target range
# Usage: ./calculate-time-segments.sh <repo_path> <author_pattern> <target_commits_per_segment>
# Output: Date ranges, one per line (format: start_date|end_date|commit_count)
# Exit codes: 0=success, 1=invalid repo, 2=no commits

# Algorithm:
# 1. Get first and last commit dates for author
# 2. Get total commit count
# 3. Calculate number of segments needed: total_commits / target_commits
# 4. Calculate segment duration: total_days / num_segments
# 5. Generate date ranges with actual commit counts
# 6. Adjust segment boundaries to balance commit counts (optional refinement)

# Example output (note: variable-length periods based on commit density):
# 2024-01-01|2024-02-28|287    (2 months - busy period)
# 2024-03-01|2024-07-31|312    (5 months - quiet period)
# 2024-08-01|2024-09-30|345    (2 months - busy period)
# 2024-10-01|2025-01-31|335    (4 months - moderate activity)
```

**Why:**
- Analyzes ALL commits without hitting token limits
- Natural chronological organization (quarterly, monthly, etc.)
- Each segment generates a separate, manageable report
- Useful for portfolios, progress tracking, year-in-review

**Algorithm Details:**

1. **Calculate initial segments:**
   ```bash
   total_commits=$(count-user-commits.sh "$REPO" "$AUTHOR")
   target_per_segment=300  # Sweet spot: 250-400
   num_segments=$((total_commits / target_per_segment + 1))
   ```

2. **Get date range:**
   ```bash
   first_date=$(git log --author="$AUTHOR" --reverse --format=%ad --date=short | head -1)
   last_date=$(git log --author="$AUTHOR" --format=%ad --date=short | head -1)
   ```

3. **Create adaptive segments (IMPORTANT):**
   - Start with equal time divisions as initial guess
   - Count commits in each proposed segment
   - **Adaptively adjust segment boundaries:**
     - If segment has >400 commits → split into smaller time period
     - If segment has <100 commits → merge with adjacent or extend period
     - Repeat until all segments are in 250-400 range
   - **Result: Variable-length time periods based on commit density**
     - Busy periods (many commits) → shorter time segments (e.g., 1 month)
     - Quiet periods (few commits) → longer time segments (e.g., 6 months)

4. **Example with variable segments:**
   ```
   2024-01-01 to 2024-02-28 (2 months)  - 287 commits (busy period)
   2024-03-01 to 2024-07-31 (5 months)  - 312 commits (quiet period)
   2024-08-01 to 2024-09-30 (2 months)  - 345 commits (busy period)
   2024-10-01 to 2025-01-31 (4 months)  - 335 commits (moderate period)
   ```
   Note: Segments have different durations to maintain target commit count

**Output Format:**
Each report file includes:
- Filename: `git-contributions-analysis-2024-Q1.md`
- Header note: "Part 1 of 4 - January 2024 to March 2024"
- Standard analysis format for that period
- Link to index file

**Index File:**
- Filename: `git-contributions-analysis-index.md`
- Lists all segments with date ranges
- Shows commit count per segment
- Brief summary of each period (if needed)
- Links to individual segment files

### Phase 4: Update SKILL.md Workflow

**New Phase 2 Logic (Data Collection):**

```markdown
### Phase 2: Data Collection

#### Step 1: Count commits
1. Run `scripts/count-user-commits.sh` to get total commit count
2. Store count for decision logic

#### Step 2: Decide strategy based on count

**If count < 500:**
- Proceed with full analysis (existing workflow)
- Run `collect-user-commits.sh` to gather all commits
- For each commit, run `extract-commit-details.sh`

**If count 500-2000:**
- Present user with options using AskUserQuestion:
  1. **Segmented analysis** - Create multiple reports, one per time period (e.g., quarterly)
  2. Intelligent sampling - Analyze 200 representative commits
  3. Date range filter - Specify a time period (e.g., last 6 months)
  4. Full analysis - Process all commits (may take longer)

**If count > 2000:**
- Inform user: "Found 3,450 commits. Please narrow the scope:"
- Options:
  1. **Segmented analysis (Recommended)** - Multiple reports by time period
  2. Date range filter - Specify a time period
  3. Intelligent sampling - 200 commits across entire timeline
- Do not offer "full analysis" option (would hit token limits)

#### Step 3: Collect based on strategy

**For full analysis:**
- Use existing `collect-user-commits.sh`
- Process all commit details

**For segmented analysis:**
- Run `scripts/calculate-time-segments.sh <repo> <author> <target_commits_per_segment>`
  - Script calculates date range and divides into segments
  - Target: 250-400 commits per segment
  - Returns: List of date ranges (e.g., "2024-01-01|2024-03-31", "2024-04-01|2024-06-30")
- For each segment:
  - Run `collect-user-commits.sh <repo> <author> <segment_start> <segment_end>`
  - Analyze commits for that period
  - Generate separate markdown file: `git-contributions-2024-Q1.md`
- Create index file listing all segments with summaries
- Note in each report: "Part X of Y - Period: YYYY-MM-DD to YYYY-MM-DD"

**For intelligent sampling:**
- Run `scripts/sample-commits.sh <repo> <author> 200`
- Get evenly distributed sample across timeline
- Process sampled commit details
- Note in report: "Analysis based on 200 representative commits"

**For date range filter:**
- Run `collect-user-commits.sh <repo> <author> <since> <until>`
- Process filtered commits
- Note in report: "Analysis for period: YYYY-MM-DD to YYYY-MM-DD"

#### Step 4: Token budget check (safety)
- Before processing commit details, estimate token usage
- Rule of thumb: ~65 tokens per commit on average
- If estimated tokens > 20,000, reduce sample size or warn user
- This prevents edge cases (commits with huge diffs)
```

### Phase 5: Enhance Report Metadata

**Add analysis scope information:**

```markdown
# Git Contributions Analysis
**Repository:** /path/to/repo
**Author:** Sean Reed
**Analysis Scope:** 200 sampled commits (out of 1,379 total)
**Sampling Strategy:** Time-stratified (evenly distributed across contribution timeline)
**Date Range:** 2024-01-15 to 2026-01-25
**Total Commits Analyzed:** 200
```

**For date-filtered:**
```markdown
**Analysis Scope:** Commits from 2025-06-01 to 2026-01-25
**Total Commits in Period:** 342
**Total Commits (All Time):** 1,379
```

## Token Budget Analysis

### Current State (Broken)
- 1,379 commits × ~65 tokens/commit = ~89,600 tokens
- Exceeds 25,000 token Read limit

### With Sampling (200 commits)
- 200 commits × 65 tokens/commit = ~13,000 tokens
- Well under 25,000 token limit
- Leaves ~12,000 tokens for AI analysis and context

### With Date Filter (6 months, ~300 commits)
- 300 commits × 65 tokens/commit = ~19,500 tokens
- Under 25,000 token limit
- Leaves ~5,500 tokens for analysis

### Safety Margin
- Target: Keep commit details under 15,000 tokens
- Maximum sample size: ~230 commits
- Recommended default: 200 commits

## Sampling Strategy Details

### Time-Stratified Sampling

**Algorithm:**
1. Get first and last commit dates
2. Divide timeline into 10 equal buckets
3. Sample 20 commits from each bucket (20 × 10 = 200 total)
4. If bucket has <20 commits, take all
5. Within each bucket, sample evenly distributed commits

**Example (1,379 commits over 2 years):**
```
Bucket 1: 2024-01 to 2024-03 (20 commits sampled from 150 total)
Bucket 2: 2024-04 to 2024-06 (20 commits sampled from 140 total)
...
Bucket 10: 2025-11 to 2026-01 (20 commits sampled from 130 total)
```

**Benefits:**
- Captures early work (project setup, initial features)
- Captures middle period (main development)
- Captures recent work (current focus)
- Representative of entire contribution arc
- Better than "most recent N" for portfolio/review purposes

### Alternative: Recent-Weighted Sampling

**For ongoing projects where recent work is more important:**
- 50% of samples from last 6 months
- 30% from 6-12 months ago
- 20% from >12 months ago

**When to use:** User indicates they want to focus on recent work

## User Experience Flow

### Scenario 1: Small Repo (<500 commits)
```
User: /analyze-git-contributions /path/to/repo
Agent: Found 342 commits for Sean Reed. Analyzing all commits...
[Generates full analysis]
```

### Scenario 2: Medium Repo (500-2000 commits)
```
User: /analyze-git-contributions /path/to/repo
Agent: Found 1,379 commits for Sean Reed (spanning 2024-01-15 to 2026-01-25).

       How would you like to proceed?

       1. Segmented analysis - Create 4 reports, one per time period
          (~345 commits each, organized chronologically)

       2. Intelligent sampling - Analyze 200 representative commits
          evenly distributed across your contribution timeline

       3. Date range filter - Specify a time period
          (e.g., last 6 months: --since='2025-07-01')

       4. Full analysis - Process all 1,379 commits
          (may take longer)

User: [Selects option 1 - Segmented analysis]
Agent: Creating 4 time-segmented reports...

       Analyzing 2024-Q1 (Jan-Mar 2024): 312 commits...
       ✓ Generated: git-contributions-analysis-2024-Q1.md

       Analyzing 2024-Q2 (Apr-Jun 2024): 298 commits...
       ✓ Generated: git-contributions-analysis-2024-Q2.md

       Analyzing 2024-Q3 (Jul-Sep 2024): 387 commits...
       ✓ Generated: git-contributions-analysis-2024-Q3.md

       Analyzing 2024-Q4 (Oct-Dec 2024): 382 commits...
       ✓ Generated: git-contributions-analysis-2024-Q4.md

       ✓ Generated index: git-contributions-analysis-index.md

       Analysis complete! 4 reports covering all 1,379 commits.
```

### Scenario 3: Large Repo (>2000 commits)
```
User: /analyze-git-contributions /path/to/repo
Agent: Found 3,450 commits for Sean Reed (spanning 2020-03-10 to 2026-01-25).

       To provide focused analysis, please narrow the scope:

       1. Segmented analysis (Recommended) - Create 11 reports, one per
          time period (~314 commits each)

       2. Recent work - Last 6 months

       3. Recent work - Last year

       4. Custom date range - Specify dates

       5. Intelligent sampling - 200 commits across entire timeline

User: [Selects option]
Agent: [Proceeds with selected strategy]
```

## Files to Modify/Create

### New Files
1. `~/.claude/skills/analyze-git-contributions/scripts/count-user-commits.sh`
   - Fast commit counting
   - ~10 lines of bash

2. `~/.claude/skills/analyze-git-contributions/scripts/sample-commits.sh`
   - Time-stratified sampling implementation
   - ~80-100 lines of bash
   - Uses git log with date filtering and head/tail

3. `~/.claude/skills/analyze-git-contributions/scripts/calculate-time-segments.sh`
   - Calculates optimal time segments for commit analysis
   - Divides timeline to keep commits per segment in 250-400 range
   - ~60-80 lines of bash
   - Uses date arithmetic and git log counting

### Modified Files
1. `~/.claude/skills/analyze-git-contributions/scripts/collect-user-commits.sh`
   - Add optional `--since` and `--until` parameters
   - ~5 line change

2. `~/.claude/skills/analyze-git-contributions/SKILL.md`
   - Update Phase 2 (Data Collection) with new logic
   - Add token budget awareness
   - Add sampling strategy documentation
   - Update example outputs to show scope metadata
   - ~100 lines of changes/additions

## Implementation Steps

### Step 1: Create count-user-commits.sh
- Simple wrapper around `git log --oneline | wc -l`
- Test with target repo (should return 1379)

### Step 2: Create sample-commits.sh
- Implement time-stratified sampling algorithm
- Test with various sample sizes (50, 100, 200)
- Verify even distribution across timeline

### Step 2.5: Create calculate-time-segments.sh
- Implement time segment calculation algorithm
- Get first/last commit dates, calculate optimal segment boundaries
- Target 250-400 commits per segment
- Test with target repo (1,379 commits → should suggest ~4 segments)
- Verify segment boundaries are reasonable (don't split awkwardly)

### Step 3: Enhance collect-user-commits.sh
- Add optional date range parameters
- Maintain backward compatibility (existing usage still works)
- Test with date filters

### Step 4: Update SKILL.md
- Rewrite Phase 2 with new decision logic
- Add user interaction patterns for each scenario
- Update examples with scope metadata
- Add token budget guidelines

### Step 5: Test end-to-end
- Test with small repo (<500 commits) - should work as before
- Test with medium repo (1,379 commits) - should offer options including segmented analysis
- Test with segmented analysis - verify multiple reports generated, each under token limit
- Test with sampling - verify token usage stays under limit
- Test with date filtering - verify correct commits selected
- Verify index file created correctly for segmented analysis

## Testing Plan

### Test Case 1: Small Repo
- Repository: Any with <500 commits
- Expected: Full analysis without prompting
- Verify: All commits processed

### Test Case 2: Medium Repo (Target)
- Repository: `/Users/seanreed/PythonProjects/audivi/other/realtime_experiment`
- Commits: 1,379
- Expected: Prompt user for strategy (including segmented analysis option)
- Test sampling: Should return 200 commits, evenly distributed
- Verify: Token count < 25,000

### Test Case 2.5: Segmented Analysis
- Repository: `/Users/seanreed/PythonProjects/audivi/other/realtime_experiment`
- Commits: 1,379
- Expected: Calculate 4-5 segments (~275-345 commits each)
- Verify: Each segment stays under token limit
- Verify: All segment files created with correct naming
- Verify: Index file lists all segments with summaries
- Verify: No commits are missed or duplicated across segments
- Verify: Date boundaries are reasonable (don't split mid-month awkwardly)

### Test Case 3: Date Range Filter
- Repository: Same as above
- Filter: Last 6 months
- Expected: ~300-400 commits
- Verify: All commits within date range

### Test Case 4: Token Safety
- Create artificial test with commits having large diffs
- Verify: Token estimation catches overflow before Read tool fails
- Expected: Agent reduces sample size or warns user

## Success Criteria

- ✅ Handles repositories with 500-10,000+ commits without token errors
- ✅ Provides user control over analysis scope (sampling, filtering, segmentation)
- ✅ Segmented analysis covers ALL commits across multiple manageable reports
- ✅ Maintains meaningful AI analysis quality
- ✅ Backward compatible (small repos work as before)
- ✅ Clear user communication about what was analyzed
- ✅ Sampling provides representative coverage across timeline
- ✅ Token usage stays under 20,000 for commit details (per segment/analysis)
- ✅ Multiple output files properly organized with index for navigation

## Edge Cases

### Very Recent Author (Few Commits)
- <50 commits: Always do full analysis
- Don't offer sampling for small datasets

### Sparse Contributions
- Author has 500 commits over 5 years but very sparse
- Sampling still works (may get 1-2 commits per bucket)
- Report notes sparse contribution pattern

### Bursty Contributions
- Author made 1000 commits in 1 month, then nothing
- Time stratification handles this (samples from active period)
- Better than pure random sampling

### Merge Commits
- Some commits may be merges with huge diffs
- Token estimation accounts for this (conservative estimate)
- If single commit exceeds budget, skip details for that commit

## Future Enhancements (Out of Scope)

### Progressive Summarization
- For very large repos, do two-tier analysis
- First: Group commits using lightweight metadata only
- Second: Fetch full details only for representative commits from each group

### Interactive Refinement
- Generate initial analysis from sample
- Offer to "drill into" specific components with more commits
- User-guided iterative exploration

### Caching
- Cache commit details locally
- Speed up re-analysis with different scopes
- Useful for experimentation

## Critical Files

### To Create
- `~/.claude/skills/analyze-git-contributions/scripts/count-user-commits.sh`
- `~/.claude/skills/analyze-git-contributions/scripts/sample-commits.sh`
- `~/.claude/skills/analyze-git-contributions/scripts/calculate-time-segments.sh`

### To Modify
- `~/.claude/skills/analyze-git-contributions/scripts/collect-user-commits.sh`
- `~/.claude/skills/analyze-git-contributions/SKILL.md`

### Reference
- `~/.claude/skills/reading-logs/SKILL.md` - "Filter first" principle
- Current implementation handles token limits similarly to log file analysis
