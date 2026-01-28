# Plan: Create BDD Scenario Writing Agent

## Overview
Create a specialized agent that writes high-quality Behavior-Driven Development (BDD) scenarios in Gherkin format. The agent will focus on behavior over implementation, following established best practices from industry sources.

## User Requirements
- Test behavior of the system under test, not implementation details
- Focus on what users can do with the system
- Prioritize maintainability (resilient to implementation changes)
- Prioritize readability (serves as documentation)
- User-centric approach (external client perspective)
- Only write good scenarios based on comprehensive guidelines

## Research Findings

### Agent Structure Pattern
All agents in `.claude/agents/` follow this structure:
1. YAML frontmatter with: name, description, tools, model
2. Opening role statement + critical constraint section
3. Core responsibilities (2-4 numbered items)
4. Strategy/process section with sequential steps
5. Output format template with examples
6. Important guidelines (DO's and DON'Ts)
7. "What NOT to Do" comprehensive list
8. Closing philosophy statement

### BDD Best Practices Extracted
From researched sources:
- **Golden Rule**: Write so people unfamiliar with the feature understand it
- **Cardinal Rule**: One scenario = one behavior
- **Declarative over Imperative**: Focus on WHAT, not HOW
- **Concrete over Abstract**: Use specific examples, not placeholders
- **Domain Language**: Business terms, not technical implementation
- **Consistent Perspective**: Third person or first person throughout
- **Present Tense**: Across all step types
- **Short Scenarios**: Fewer than 10 steps
- **No Multiple When-Then Pairs**: Each represents separate behavior

### Key Anti-Patterns to Prevent
- Procedure-driven testing (translating test cases directly)
- Technical implementation details (XPath, URLs, database keys)
- Scripty language ("fill in", "click", multiple When steps)
- Tautological scenarios (vague assertions)
- Excessive detail (unnecessary data points)
- Incomplete step phrases (missing subjects/predicates)
- Mixed tenses or perspectives

## Implementation Plan

### File to Create
**Location**: `/Users/seanreed/PythonProjects/lk-agent-1/.claude/agents/bdd-scenario-writer.md`

### Agent Definition Structure

#### 1. YAML Frontmatter
```yaml
---
name: bdd-scenario-writer
description: Writes behavior-driven development scenarios in Gherkin format focused on system behavior from user perspective
tools: Read, Grep, Glob, LS, Write, Edit
model: sonnet
---
```

**Rationale for tools**:
- Read: Examine code to understand behavior
- Grep/Glob: Search for patterns and similar scenarios
- LS: Explore directory structure
- Write/Edit: Create and update .feature files with scenarios

#### 2. Opening Statement
Role: Specialist in writing BDD scenarios
Critical constraint: ONLY write behavior-focused scenarios, not implementation tests

#### 3. Core Responsibilities
1. **Analyze System Behavior** - Understand what users can do
2. **Write Gherkin Scenarios** - Following best practices
3. **Focus on User Perspective** - External client view
4. **Ensure Maintainability** - Implementation-agnostic scenarios

#### 4. Strategy Section
Step 1: Understand the feature/behavior to test
Step 2: Identify user-facing behaviors (not implementation)
Step 3: Write concrete, domain-language scenarios
Step 4: Review against anti-patterns

#### 5. Output Format
Template showing:
- Feature structure
- Scenario organization
- Given/When/Then formatting
- Good vs Bad examples side-by-side

#### 6. Guidelines Section

**DO:**
- Use concrete examples with specific data
- Write in domain/business language
- Focus on one behavior per scenario
- Use present tense consistently
- Keep scenarios under 10 steps
- Write complete subject-predicate phrases
- Make scenarios understandable to non-technical stakeholders

**DON'T:**
- Include technical implementation details (URLs, selectors, database IDs)
- Use procedural step-by-step UI instructions
- Test internal system mechanics
- Write abstract/generic placeholders
- Use multiple When-Then pairs in one scenario
- Mix tenses or perspectives
- Include unnecessary data points

#### 7. Comprehensive Examples Section
Include multiple good vs bad scenario pairs demonstrating:
- Declarative vs imperative
- Behavior vs implementation
- Concrete vs abstract
- Domain language vs technical language
- Single behavior vs multiple behaviors

#### 8. Closing Philosophy
"You are a behavior documentarian, not an implementation tester."

### Integration with AGENTS.md

The file already contains a BDD section (lines 58-62):
```markdown
### BDD and Gherkin
- When asked to write BDD scenarios or feature files, they should be written in Gherkin language
- Only implement steps corresponding to the scenarios when explicitly told to do so
- When writing authorization/authentication scenarios, write only a minimal set of five or less unless explicitly told otherwise
```

**Action**: No changes needed to AGENTS.md - these guidelines are complementary

## Detailed Content Plan

### Section 1: Introduction (After frontmatter)
- Role as BDD scenario specialist
- Critical directive: Focus on behavior, not implementation
- Reference to user-centric testing philosophy

### Section 2: Core Responsibilities
1. **Analyze User-Facing Behavior**
   - Identify what users can do with the system
   - Understand feature from external perspective
   - Focus on outcomes, not mechanics

2. **Write Declarative Scenarios**
   - Use high-level domain language
   - Describe WHAT happens, not HOW
   - Keep scenarios concrete with specific examples

3. **Ensure Quality Standards**
   - One behavior per scenario
   - Present tense, consistent perspective
   - Short, readable, maintainable

4. **Validate Against Anti-Patterns**
   - Check for implementation leakage
   - Ensure domain language usage
   - Verify behavior focus

### Section 3: Scenario Writing Strategy

**Step 1: Understand the Feature**
- Read relevant code files
- Identify user-facing capabilities
- Map features to user behaviors

**Step 2: Identify Distinct Behaviors**
- Each behavior gets one scenario
- Separate multiple When-Then pairs
- Focus on one outcome per scenario

**Step 3: Write in Domain Language**
- Use business terminology
- Avoid technical implementation
- Make understandable to stakeholders

**Step 4: Apply Gherkin Best Practices**
- Given: Present perfect or state ("a patron has checked out a book")
- When: Present tense action ("the patron searches for a book")
- Then: Conditional passive describing outcome ("the book should be shown")

**Step 5: Review and Refine**
- Check against anti-patterns
- Verify concreteness and clarity
- Ensure maintainability

**Step 6: Write to Feature Files**
- Create .feature files in appropriate location (tests/, features/, or spec/)
- Follow Gherkin file structure and formatting
- Use descriptive file names matching feature name

### Section 4: Output Format Template

```gherkin
Feature: [Business capability name]
  As a [role]
  I want to [action]
  So that [business value]

  Scenario: [What's unique about this behavior]
    Given [concrete initial state in domain language]
    And [additional context if needed]
    When [single user action in present tense]
    Then [expected outcome in domain language]
    And [additional assertions if needed]
```

Include comparison examples:
- Good scenario example
- Bad scenario example (with explanation of problems)

### Section 5: Important Guidelines

**Behavior vs Implementation:**
- ✅ "When a patron searches for 'Tale of Two Cities'"
- ❌ "When a patron enters text in search field #searchBox and clicks button"

**Concrete vs Abstract:**
- ✅ "Given a book 'Pride and Prejudice' by Jane Austen"
- ❌ "Given a book with valid data"

**Domain Language vs Technical:**
- ✅ "Then the book's status should be 'Available'"
- ❌ "Then the database field book_status should equal 1"

**Single Behavior:**
- ✅ One scenario for search, one for selecting result
- ❌ One scenario covering search + select + navigate

### Section 6: File Writing Guidelines

**Location Convention:**
- Check for existing feature file directories: `features/`, `tests/features/`, `spec/`, `tests/`
- If unclear, ask user where to place .feature files
- Default to `features/` if creating new structure

**File Naming:**
- Use lowercase with hyphens: `book-search.feature`
- Match feature name: Feature "Book Search" → `book-search.feature`
- One feature per file

**File Structure:**
```gherkin
# language: en
Feature: [Name]
  [Feature description]

  Background:
    [Common setup if needed]

  Scenario: [First behavior]
    ...

  Scenario: [Second behavior]
    ...
```

**When to Write:**
- User explicitly asks for scenarios to be written
- After generating and reviewing scenarios
- Always show the scenarios before writing to get implicit approval

### Section 7: Comprehensive Anti-Patterns List

DO NOT:
- Write procedural step-by-step UI interactions
- Include technical details (URLs, XPath, CSS selectors, database keys)
- Use scripty language ("fill in", "click on", "navigate to")
- Create multiple When-Then pairs in single scenario
- Write tautological assertions ("correct results are shown")
- Include data irrelevant to the behavior being tested
- Use past tense or future tense
- Mix first and third person perspectives
- Translate test cases directly into Gherkin
- Test internal system mechanics
- Write abstract/generic placeholder data
- Create incomplete step phrases
- Specify HOW system achieves behavior

### Section 8: Example Gallery

Include 3-5 complete scenario pairs showing:
1. Search feature (good vs bad)
2. Authentication (good vs bad)
3. Data validation (good vs bad)
4. Multi-step workflow (good vs bad)

Each pair should highlight specific issues and fixes.

### Section 9: Closing Statement

"## REMEMBER: You are a behavior documentarian, not an implementation tester

Your purpose is to specify WHAT the system does from the user's perspective, creating maintainable documentation that survives implementation changes. Think like a user describing what they can accomplish, not a developer describing how code works."

## Verification Plan

After creating the agent:

1. **Test with LiveKit Agent Codebase**
   - Ask agent to write scenarios for the voice assistant behavior
   - Scenarios should focus on user interactions (e.g., "user asks a question, assistant responds")
   - Should NOT test implementation (e.g., "STT converts speech to text")

2. **Test with Authentication Flow**
   - Ask agent to write auth scenarios
   - Should produce 5 or fewer scenarios (per AGENTS.md:61)
   - Should focus on user capabilities (login, logout, access control)
   - Should NOT test technical details (JWT tokens, session storage)

3. **Review Generated Scenarios**
   - Check for domain language usage
   - Verify no technical implementation details
   - Confirm one behavior per scenario
   - Validate concrete examples with specific data
   - Ensure present tense throughout
   - Check for consistent perspective

4. **Negative Test**
   - Give agent a complex feature and ask for scenarios
   - Verify it doesn't create procedure-driven test cases
   - Confirm it separates multiple behaviors into distinct scenarios

## Success Criteria

- Agent definition file follows established pattern structure
- Contains comprehensive good/bad examples
- Enforces behavior-over-implementation philosophy
- Includes all anti-patterns from research
- Provides clear output templates
- Works on any codebase without modification
- Generates scenarios that are:
  - Maintainable (survive refactoring)
  - Readable (non-technical stakeholders understand)
  - User-centric (external perspective)
  - Concrete (specific examples)
  - Focused (one behavior each)

## Files Involved

**New file**:
- `/Users/seanreed/PythonProjects/lk-agent-1/.claude/agents/bdd-scenario-writer.md`

**Reference files** (no changes):
- `/Users/seanreed/PythonProjects/lk-agent-1/AGENTS.md` (lines 58-62 already have BDD guidance)
- `/Users/seanreed/PythonProjects/lk-agent-1/.claude/agents/codebase-analyzer.md` (structure reference)
- `/Users/seanreed/PythonProjects/lk-agent-1/.claude/agents/codebase-locator.md` (structure reference)

## Implementation Notes

- Agent can write .feature files directly to codebase
- Shows scenarios before writing for user review
- Focuses on generating scenarios, not implementing step definitions (unless explicitly requested)
- Aligns with existing AGENTS.md guidance about not implementing steps unless told
- Can be used on any codebase by invoking: "Write BDD scenarios for [feature]"
- Will ask about file location if not obvious from project structure
