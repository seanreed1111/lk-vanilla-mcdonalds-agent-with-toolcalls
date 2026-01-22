---
name: writing-plans
description: Create implementation plans with tasks grouped by subsystem. Related tasks share agent context; groups parallelize across subsystems.
---

# Writing Plans

Write step-by-step implementation plans for agentic execution. Each task should be a **complete unit of work** that one agent handles entirely.

**Save to:** `**/plans/YYYY-MM-DD-<feature-name>.md`

## Plan Template

````markdown
# [Feature Name] Implementation Plan

> **Status:** DRAFT | APPROVED | IN_PROGRESS | COMPLETED

## Table of Contents

- [Specification](#specification)
- [Dependencies](#dependencies)
- [Context Loading](#context-loading)
- [Tasks](#tasks)
  - [Task 1: Complete Feature Unit](#task-1-complete-feature-unit)
  - [Task 2: Another Complete Unit](#task-2-another-complete-unit)

## Specification

**Goal:** [What we're building and why]

**Success Criteria:**

- [ ] Criterion 1
- [ ] Criterion 2

## Dependencies

**Execution Order:**

1. Task 1 (no dependencies)
2. Task 2 (depends on Task 1)

**Dependency Graph:**

```
Task 1 (Authentication)
  └─> Task 2 (Billing - needs auth)
      └─> Task 3 (Integration - needs both)
```

**Parallelization:**
- Tasks 1 and 4 can run in parallel (independent subsystems)
- Task 2 must wait for Task 1
- Task 3 must wait for Tasks 1 and 2

## Context Loading

_Run before starting:_

```bash
read src/relevant/file.ts
glob src/feature/**/*.ts
```

## Tasks

### Task 1: [Complete Feature Unit]

**Context:** `src/auth/`, `tests/auth/`

**Dependencies:** None

**Steps:**

1. [ ] Create `src/auth/login.ts` with authentication logic
2. [ ] Add tests in `tests/auth/login.test.ts`
3. [ ] Export from `src/auth/index.ts`

**Verify:** `npm test -- tests/auth/`

---

### Task 2: [Another Complete Unit]

**Context:** `src/billing/`

**Dependencies:** Task 1 (requires authentication)

**Steps:**

1. [ ] ...

**Verify:** `npm test -- tests/billing/`
````

## Task Sizing

A task includes **everything** to complete one logical unit:

- Implementation + tests + types + exports
- All steps a single agent should do together

**Right-sized:** "Add user authentication" - one agent does model, service, tests, types
**Wrong:** Separate tasks for model, service, tests - these should be one task

**Bundle trivial items:** Group small related changes (add export, update config, rename) into one task.

## Parallelization & Grouping

During execution, tasks are **grouped by subsystem** to share agent context. Structure your plan to make grouping clear:

```markdown
## Authentication Tasks          ← These will run in one agent
### Task 1: Add login
### Task 2: Add logout

## Billing Tasks                 ← These will run in another agent (parallel)
### Task 3: Add billing API
### Task 4: Add webhooks

## Integration Tasks             ← Sequential (depends on above)
### Task 5: Wire auth + billing
```

**Execution model:**
- Tasks under same `##` heading → grouped into one agent
- Groups touching different subsystems → run in parallel
- Max 3-4 tasks per group (split larger sections)

Tasks in the **same subsystem** should be sequential or combined into one task.

## Rules

1. **Table of contents required:** Every plan must start with a linked table of contents
2. **Document dependencies:** Every plan must have a Dependencies section showing:
   - Execution order (which tasks must run first)
   - Dependency graph (which tasks depend on which other tasks)
   - Parallelization opportunities (which tasks can run simultaneously)
3. **Task dependencies:** Each task must specify what it depends on and what depends on it
4. **Explicit paths:** Say "create `src/utils/helpers.ts`" not "create a utility"
5. **Context per task:** List files the agent should read first
6. **Verify every task:** End with a command that proves it works
7. **One agent per task:** All steps in a task are handled by the same agent
8. **Split large plans:** Plans over 400-500 lines must be split into numbered task files (01-name.md, 02-name.md) with bidirectional links

## Large Plans

For plans over 400-500 lines, split into separate files in a folder:

```
**/plans/YYYY-MM-DD-feature/
├── README.md                    # Overview, table of contents, checklist
├── 01-authentication.md         # First task group
├── 02-billing.md                # Second task group
└── 03-integration.md            # Third task group
```

### Main README.md Structure

```markdown
# [Feature Name] Implementation Plan

> **Status:** DRAFT | APPROVED | IN_PROGRESS | COMPLETED

## Table of Contents

- [Overview](#overview)
- [Dependencies](#dependencies)
- [Task Checklist](#task-checklist)
- [Task Files](#task-files)

## Overview

Brief 2-3 paragraph summary of what we're building and why.

## Dependencies

**Execution Order:**

1. [Authentication](./01-authentication.md) (no dependencies)
2. [Billing](./02-billing.md) (depends on Authentication)
3. [Integration](./03-integration.md) (depends on Authentication + Billing)

**Dependency Graph:**

```
01-authentication.md
  ├─> 02-billing.md
  └─> 03-integration.md
```

## Task Checklist

- [ ] [01: Authentication](./01-authentication.md)
- [ ] [02: Billing](./02-billing.md)
- [ ] [03: Integration](./03-integration.md)

## Task Files

1. [Authentication Tasks](./01-authentication.md)
2. [Billing Tasks](./02-billing.md)
3. [Integration Tasks](./03-integration.md)
```

### Individual Task File Structure (e.g., 01-authentication.md)

```markdown
# 01: Authentication Tasks

← [Back to Main Plan](./README.md)

## Table of Contents

- [Overview](#overview)
- [Dependencies](#dependencies)
- [Tasks](#tasks)

## Overview

Brief description of this task group.

## Dependencies

**Depends on:** None

**Required by:**
- [02: Billing](./02-billing.md)
- [03: Integration](./03-integration.md)

## Tasks

### Task 1.1: Add Login

**Context:** `src/auth/`

**Steps:**
1. [ ] Create login logic
2. [ ] Add tests

**Verify:** `npm test -- tests/auth/`

---

← [Back to Main Plan](./README.md)
```

**Bidirectional Links:**
- Each task file includes "← Back to Main Plan" links at top and bottom
- README.md links to all task files
- Task files link to their dependencies and dependents
