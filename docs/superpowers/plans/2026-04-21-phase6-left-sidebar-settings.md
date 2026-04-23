# Phase 6: Left Sidebar, Settings & Theming Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Implement the Left Sidebar (History & Skills), dynamic model selection (Hot-Reload), Settings panel, and Libadwaita theme synchronization.

**Architecture:** Use `Adw.NavigationView` for the left sidebar to switch between History and Skills. Introduce `ConfigManager` for persistence. Integrate model selection into the UI for dynamic CLI process restarts.

**Tech Stack:** Python, GTK4, Libadwaita, PyGObject.

---

### Task 1: Core Configuration Manager

**Files:**
- Create: `core/config_manager.py`
- Test: `tests/test_config_manager.py`

- [ ] **Step 1: Write the failing test for ConfigManager**
- [ ] **Step 2: Implement ConfigManager (JSON-based persistence)**
- [ ] **Step 3: Verify tests pass**
- [ ] **Step 4: Commit**

### Task 2: Left Sidebar Component (Adw.NavigationView)

**Files:**
- Create: `ui/views/left_sidebar.py`
- Modify: `ui/window.py`
- Test: `tests/test_left_sidebar.py`

- [ ] **Step 1: Implement `LeftSidebar` using `Adw.NavigationView` with pages for "History" and "Skills"**
- [ ] **Step 2: Replace stub in `MainWindow` with `LeftSidebar`**
- [ ] **Step 3: Write tests for navigation switching**
- [ ] **Step 4: Commit**

### Task 3: History & Skills List Views

**Files:**
- Modify: `ui/views/left_sidebar.py`
- Modify: `core/models.py`

- [ ] **Step 1: Add `HistoryEntry` and `Skill` models to `core/models.py`**
- [ ] **Step 2: Implement `Gtk.ListView` for History with session items**
- [ ] **Step 3: Implement `Gtk.ListView` for Skills**
- [ ] **Step 4: Commit**

### Task 4: Dynamic Model Selection (Hot-Reload)

**Files:**
- Modify: `core/process_manager.py`
- Modify: `ui/window.py`
- Modify: `ui/views/left_sidebar.py`

- [ ] **Step 1: Add `restart_with_model(model_name)` to `ProcessManager`**
- [ ] **Step 2: Add Model Selection dropdown to the UI**
- [ ] **Step 3: Connect UI selection to `ProcessManager` restart logic**
- [ ] **Step 4: Verify hot-reload behavior with tests**
- [ ] **Step 5: Commit**

### Task 5: Settings Panel & Theme Synchronization

**Files:**
- Create: `ui/components/settings_dialog.py`
- Modify: `ui/window.py`

- [ ] **Step 1: Create `SettingsDialog` (Adw.PreferencesWindow)**
- [ ] **Step 2: Add theme toggle (Light/Dark/System) and sync with `Adw.StyleManager`**
- [ ] **Step 3: Add API Key / Model preferences to settings**
- [ ] **Step 4: Persist settings via `ConfigManager`**
- [ ] **Step 5: Commit**
