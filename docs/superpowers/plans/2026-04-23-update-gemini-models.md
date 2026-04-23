# 2026 Gemini Model Selection Update Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Update the model selection to use April 2026 Gemini models and externalize the list into `ConfigManager`.

**Architecture:** Centralize model definitions in `ConfigManager` to decouple UI from model lists. Update `MainWindow` to dynamically populate its dropdown from this configuration.

**Tech Stack:** Python, GTK4, Libadwaita.

---

### Task 1: Update ConfigManager with 2026 Models

**Files:**
- Modify: `core/config_manager.py`
- Test: `tests/test_config_manager.py`

- [ ] **Step 1: Write failing test for default models**
```python
def test_get_default_models(tmp_path):
    path = str(tmp_path / "config.json")
    cm = ConfigManager(path)
    models = cm.get("available_models")
    assert "gemini-3.1-pro" in models
    assert "gemini-3-flash" in models
```

- [ ] **Step 2: Run test to verify it fails**
Run: `pytest tests/test_config_manager.py -v`

- [ ] **Step 3: Implement default models in ConfigManager**
Modify `core/config_manager.py`:
```python
DEFAULT_MODELS = ["gemini-3.1-pro", "gemini-3-flash", "gemini-3.1-flash-lite"]

class ConfigManager:
    def __init__(self, config_path: str):
        # ... existing init ...
        if "available_models" not in self.config:
            self.config["available_models"] = DEFAULT_MODELS
```

- [ ] **Step 4: Run test to verify it passes**
Run: `pytest tests/test_config_manager.py -v`

- [ ] **Step 5: Commit**
```bash
git add core/config_manager.py tests/test_config_manager.py
git commit -m "feat: add 2026 gemini models to config defaults"
```

### Task 2: Dynamic Model Loading in MainWindow

**Files:**
- Modify: `ui/window.py`
- Test: `tests/test_window.py`

- [ ] **Step 1: Update MainWindow to use ConfigManager for models**
Modify `ui/window.py`:
```python
        # Model Selection DropDown
        models = self.config_manager.get("available_models", ["gemini-3.1-pro"])
        self.model_dropdown = Gtk.DropDown.new_from_strings(models)
```

- [ ] **Step 2: Update existing tests to reflect new model names**
Modify `tests/test_window.py` to use `gemini-3-flash` instead of `gemini-1.5-flash`.

- [ ] **Step 3: Run UI tests**
Run: `pytest tests/test_window.py -v`

- [ ] **Step 4: Commit**
```bash
git add ui/window.py tests/test_window.py
git commit -m "ui: populate model dropdown from config"
```

### Task 3: (Optional/Cleanup) Remove Hardcoded References in Tests

**Files:**
- Modify: `tests/test_hot_reload.py`, `tests/test_models.py`

- [ ] **Step 1: Update model names in other test files to match 2026 specs**
Replace `gemini-2.0` or `gemini-1.5` with `gemini-3.1-pro` in remaining tests.

- [ ] **Step 2: Run all tests**
Run: `pytest -v`

- [ ] **Step 3: Commit**
```bash
git add tests/
git commit -m "test: sync model names with 2026 defaults"
```
