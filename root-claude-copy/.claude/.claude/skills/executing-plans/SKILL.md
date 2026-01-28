---
name: executing-plans
description: Executes implementation plans with smart task grouping. Groups related tasks to share context, parallelizes across independent subsystems.
---

# Executing Plans

**Core principle:** Group related tasks to share agent context. One agent per subsystem, groups run in parallel.

## Why Grouping Matters

Without grouping:
```
Task 1 (auth/login)  → Agent 1 [explores codebase, reads auth/]
Task 2 (auth/logout) → Agent 2 [explores codebase, reads auth/ again]
```

With grouping:
```
Tasks 1-2 (auth/*)   → Agent 1 [explores once, executes both]
```

## Execution Flow

```
- [ ] Load plan file
- [ ] Group tasks by subsystem
- [ ] Dispatch agents for independent groups in parallel
- [ ] Update plan file (mark IN_PROGRESS)
- [ ] Wait, dispatch dependent groups
- [ ] Run verification (tests, build, lint)
- [ ] Dispatch code-reviewer agent
- [ ] Mark plan COMPLETED
```

## Grouping Rules

| Signal | Group together |
|--------|----------------|
| Same directory prefix | `src/auth/*` tasks |
| Same domain/feature | Auth tasks, billing tasks |
| Plan sections | Tasks under same `##` heading |

**Limits:** 3-4 tasks max per group. Split if larger.

## Parallel vs Sequential

**Parallel:** Groups touch different subsystems
```
Group A: src/auth/*    ─┬─ parallel
Group B: src/billing/* ─┘
```

**Sequential:** Groups have dependencies
```
Group A: Create shared types → Group B: Use those types
```

## Group Dispatch

```
Task tool (general-purpose):
  description: "Auth tasks: login, logout"
  prompt: |
    Execute these tasks from [plan-file] IN ORDER:
    - Task 1: Add login endpoint
    - Task 2: Add logout endpoint

    Use skills: <relevant skills>
    Commit after each task. Report: files changed, test results
```

## Progress Tracking

1. Set plan status to IN_PROGRESS when starting
2. Check off `[x]` each task as completed
3. Set status to COMPLETED when all pass verification

## Auto-Recovery

1. Agent attempts to fix failures (has context)
2. If can't fix, report failure
3. Dispatch fix agent with error output
4. Same error twice → stop and ask user

## Final Verification

1. Run full test suite
2. Run build
3. Dispatch `ce:code-reviewer`
4. Fix issues found
5. Mark COMPLETED
