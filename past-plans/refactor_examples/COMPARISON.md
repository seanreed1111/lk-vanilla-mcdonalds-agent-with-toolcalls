# Refactoring Options Comparison

## Current Issues
- Global `server` instance makes testing difficult
- Tight coupling between server setup and session handlers
- Harder to reuse components in different contexts

## Option 1: Application Class ✅ **RECOMMENDED**

**File:** `option1_app_class.py`

### Pros
- Zero globals - everything is encapsulated
- Easy to test (can instantiate multiple apps)
- Clear initialization flow
- Methods can access shared state via `self`
- Easy to extend with additional configuration
- Follows object-oriented best practices

### Cons
- More boilerplate code
- Slight paradigm shift from functional style

### When to use
- **Best for:** Production applications, complex agents, testing
- **Use if:** You want the cleanest architecture and easiest testing

---

## Option 2: Separate Configuration Module

**Files:** `option2_server_config.py` + `option2_agent.py`

### Pros
- Separates concerns (config vs business logic)
- No module-level globals (created in `__main__`)
- Reusable `create_server()` factory
- Good for sharing configuration across multiple agents

### Cons
- Requires an additional file
- Still uses decorator pattern which can be harder to test
- `setup_agent_handlers` function must receive server parameter

### When to use
- **Best for:** Multiple agents sharing configuration
- **Use if:** You want to centralize server config but keep functional style

---

## Option 3: Minimal Change

**File:** `option3_minimal.py`

### Pros
- Minimal refactoring required
- No globals at module level
- Keeps all logic in one file
- Simple and straightforward

### Cons
- Everything still in `__main__` block
- Harder to import for testing
- Less reusable

### When to use
- **Best for:** Quick fix, simple agents
- **Use if:** You want the smallest change possible

---

## Testing Comparison

### Option 1 (App Class)
```python
# Super easy to test
def test_agent():
    app = VoiceAgentApp()
    # Test app.server, mock methods, etc.
    assert app.server is not None
```

### Option 2 (Config Module)
```python
# Easy to test components
def test_server_creation():
    server = create_server()
    assert server.setup_fnc is not None
```

### Option 3 (Minimal)
```python
# Harder - need to import from __main__
# or copy initialization logic
```

---

## Recommendation

**Use Option 1 (Application Class)** for the best long-term maintainability, testability, and adherence to clean code principles. It eliminates all globals while providing a clear, extensible structure.

If you need absolute minimal changes, use Option 3, but plan to migrate to Option 1 as the project grows.
