# Fix ModuleNotFoundError: No module named 'menus'

## Problem Summary

The application fails with `ModuleNotFoundError: No module named 'menus'` when running `make console`. The error occurs in `src/menu_provider.py:9` when trying to import `from menus.mcdonalds.models import Item, Menu`.

**Root Cause**: Python requires `__init__.py` files in directories to treat them as packages. The `menus/` and `menus/mcdonalds/` directories are missing these files, preventing Python from recognizing them as importable packages.

## Current State

```
Project Root/
├── src/                    # Application code
├── menus/                  # Menu data (NOT in src/)
│   └── mcdonalds/
│       ├── (missing __init__.py) ❌
│       ├── models.py ✓
│       └── transformed-data/
│           └── menu-structure-2026-01-21.json ✓
└── tests/
```

## Affected Files

The following files import from the `menus` package:

1. `src/menu_provider.py:9` - `from menus.mcdonalds.models import Item, Menu`
2. `src/menu_validation.py:12` - `from menus.mcdonalds.models import Item, Menu`
3. `src/drive_thru_llm.py:12` - `from menus.mcdonalds.models import Item`
4. `tests/conftest.py:12` - `from menus.mcdonalds.models import Item, Menu, Modifier`
5. `tests/test_menu_models.py:17` - `from menus.mcdonalds.models import Item, Menu, Modifier`

**Total: 5 files with imports**

Files with hardcoded string paths to menu data:
1. `src/config.py:88` - `menu_file_path: str = Field(default="menus/mcdonalds/...")`
2. `tests/conftest.py:155` - `menu_path = "menus/mcdonalds/..."`
3. `tests/conftest.py:168-172` - Path construction using `Path(__file__).parent.parent / "menus"`
4. `tests/conftest.py:203` - `menu_path = "menus/mcdonalds/..."`

## Two Approaches to Fix

### Approach A: Simple Fix (Add __init__.py files)
**Effort**: Minimal | **Risk**: Low | **Time**: 2 minutes

Keep `menus/` at project root, add missing package files.

**Changes Required:**
- Create `menus/__init__.py`
- Create `menus/mcdonalds/__init__.py`
- No other changes needed

**Pros:**
- Minimal changes (2 files)
- No import changes
- No path changes
- Low risk

**Cons:**
- `menus/` remains outside `src/` package structure
- Not fully integrated with uv package management

### Approach B: Structural Fix (Move menus to src/)
**Effort**: Moderate | **Risk**: Low | **Time**: 10 minutes

Move `menus/` into `src/menus/` to consolidate all runtime code.

**Changes Required:**
- Move `menus/` directory to `src/menus/`
- Create `src/menus/__init__.py`
- Create `src/menus/mcdonalds/__init__.py`
- Update 4 hardcoded file paths in 2 files:
  - `src/config.py:88` - Change default path
  - `tests/conftest.py:155, 168-172, 203` - Update 3 path references

**Pros:**
- Cleaner package structure
- All runtime code in `src/`
- Better alignment with `pyproject.toml` configuration
- Standard Python package layout

**Cons:**
- Requires path updates in 2 files
- More comprehensive change

## Recommended Approach: B (Move to src/)

**Rationale**: The `pyproject.toml` is already configured for `src/`-based packages. Moving `menus/` to `src/menus/` creates a cleaner, more maintainable structure where all application code is properly packaged together.

## Implementation Plan (Approach B)

### Step 1: Move Directory Structure

Move `menus/` to `src/menus/`:

```bash
mv menus/ src/menus/
```

**Result:**
```
src/
├── menus/              # Newly moved
│   └── mcdonalds/
│       ├── models.py
│       ├── raw-data/
│       └── transformed-data/
│           └── menu-structure-2026-01-21.json
├── agent.py
├── config.py
└── ... (other files)
```

### Step 2: Create Package Initializers

Create two `__init__.py` files:

**File: `src/menus/__init__.py`**
```python
"""McDonald's menu data package.

This package contains menu models and data files for various restaurant chains.
Currently includes: McDonald's
"""
```

**File: `src/menus/mcdonalds/__init__.py`**
```python
"""McDonald's menu models and data.

This module provides Pydantic v2 models for representing McDonald's menu items,
modifiers, and complete menu structure.
"""

from menus.mcdonalds.models import Item, Menu, Modifier

__all__ = ["Item", "Menu", "Modifier"]
```

### Step 3: Update File Path References

Update hardcoded string paths in 2 files:

**File: `src/config.py` (line 88)**

Change:
```python
menu_file_path: str = Field(
    default="menus/mcdonalds/transformed-data/menu-structure-2026-01-21.json",
    description="Path to menu JSON file",
)
```

To:
```python
menu_file_path: str = Field(
    default="src/menus/mcdonalds/transformed-data/menu-structure-2026-01-21.json",
    description="Path to menu JSON file",
)
```

**File: `tests/conftest.py` (line 155)**

Change:
```python
menu_path = "menus/mcdonalds/transformed-data/menu-structure-2026-01-21.json"
```

To:
```python
menu_path = "src/menus/mcdonalds/transformed-data/menu-structure-2026-01-21.json"
```

**File: `tests/conftest.py` (lines 168-172)**

Change:
```python
return (
    Path(__file__).parent.parent
    / "menus"
    / "mcdonalds"
    / "transformed-data"
    / "menu-structure-2026-01-21.json"
)
```

To:
```python
return (
    Path(__file__).parent.parent
    / "src"
    / "menus"
    / "mcdonalds"
    / "transformed-data"
    / "menu-structure-2026-01-21.json"
)
```

**File: `tests/conftest.py` (line 203)**

Change:
```python
menu_path = "menus/mcdonalds/transformed-data/menu-structure-2026-01-21.json"
```

To:
```python
menu_path = "src/menus/mcdonalds/transformed-data/menu-structure-2026-01-21.json"
```

### Step 4: Python Imports (No Changes Needed!)

**Important**: All 5 Python import statements remain unchanged:
- `from menus.mcdonalds.models import Item, Menu`
- `from menus.mcdonalds.models import Modifier`

This works because `pyproject.toml` configures `src/` as the package root:
```toml
[tool.setuptools.packages.find]
where = ["src"]
```

When `uv run` executes, it adds `src/` to `sys.path`, so `menus` is found directly.

## Critical Files to Modify

**Directory Move:**
- `menus/` → `src/menus/` (entire directory)

**New Files:**
- `src/menus/__init__.py` (to be created)
- `src/menus/mcdonalds/__init__.py` (to be created)

**Path Updates:**
- `src/config.py` (1 line change)
- `tests/conftest.py` (3 path changes)

**Unchanged (imports work automatically):**
- `src/menu_provider.py`
- `src/menu_validation.py`
- `src/drive_thru_llm.py`
- `tests/test_menu_models.py`
- All other source files

## Verification Steps

After implementing the changes, verify everything works:

### 1. Verify Import in Python
```bash
uv run python -c "from menus.mcdonalds.models import Item, Menu, Modifier; print('✓ Imports successful')"
```
**Expected**: Prints "✓ Imports successful" without errors

### 2. Run Console Mode
```bash
make console
```
**Expected**: Agent starts successfully without `ModuleNotFoundError`

### 3. Run All Tests
```bash
uv run pytest -v
```
**Expected**: All tests pass, including:
- `tests/test_menu_models.py` - Menu model tests
- `tests/test_menu_provider.py` - MenuProvider tests
- `tests/test_drive_thru_agent.py` - Agent tests

### 4. Run Dev Mode
```bash
make dev
```
**Expected**: Agent connects to LiveKit without errors

### 5. Verify Menu File Path
```bash
uv run python -c "from pathlib import Path; print('Menu exists:', Path('src/menus/mcdonalds/transformed-data/menu-structure-2026-01-21.json').exists())"
```
**Expected**: Prints "Menu exists: True"

## Summary of Changes

| Change Type | Files Affected | Effort |
|-------------|----------------|--------|
| Directory move | 1 directory | `mv menus/ src/menus/` |
| Create `__init__.py` | 2 new files | Simple (docstrings only) |
| Update file paths | 2 files (4 locations) | Find & replace |
| Update imports | 0 files | No changes needed ✓ |
| Update `pyproject.toml` | 0 files | No changes needed ✓ |

**Total Lines Changed**: ~8 lines across 2 files + 2 new files

## Why This Approach Is Better

1. **Proper Package Structure**: All application code in `src/` aligns with `pyproject.toml` configuration
2. **Better Integration**: Menu data becomes part of the uv-managed package
3. **Standard Layout**: Follows Python packaging best practices
4. **Future-Proof**: Easier to add more menu data (e.g., `src/menus/burger_king/`)
5. **Clear Boundaries**: Separates source code (`src/`) from project metadata (root level)
