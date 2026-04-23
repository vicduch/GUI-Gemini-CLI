# Per-Terminal Model Selection Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Allow users to select a specific Gemini model for each terminal independently via a header bar.

**Architecture:** Refactor `TerminalPane` to include a header bar with a model selection `Gtk.DropDown` (or `Gtk.MenuButton`) and a zoom button. Use `GObject` signals to communicate changes to the `MainWindow`.

**Tech Stack:** Python, GTK4, Libadwaita, PyGObject.

---

### Task 1: Refactor `TerminalPane` UI Structure

**Files:**
- Modify: `ui/components/terminal_pane.py`

- [ ] **Step 1: Update imports and inheritance**
Change `TerminalPane` to inherit from `Gtk.Box(orientation=Gtk.Orientation.VERTICAL)`. Add `GObject` signals.

- [ ] **Step 2: Implement the Header Bar**
Create a compact header bar using `Gtk.CenterBox` or a horizontal `Gtk.Box`.
Add a `Gtk.Label` for the session ID (or model name).
Add a `Gtk.DropDown` for model selection.
Add the `zoom_button` to the header.

- [ ] **Step 3: Update `__init__` to handle model list**
Pass `available_models` to the constructor.

- [ ] **Step 4: Update internal layout**
The terminal and error banner remain in a `Gtk.Overlay`, which is then added to the `Gtk.Box`.

### Task 2: Implement Model Change Signaling

**Files:**
- Modify: `ui/components/terminal_pane.py`

- [ ] **Step 1: Connect DropDown signal**
Connect to `notify::selected` on the DropDown and emit `model-changed`.

- [ ] **Step 2: Connect Zoom button signal**
Connect to `clicked` on `zoom_button` and emit `zoom-clicked`.

### Task 3: Update `Workspace` to use new signals

**Files:**
- Modify: `ui/views/workspace.py`

- [ ] **Step 1: Update `add_pane`**
Connect to `zoom-clicked` instead of `pane.zoom_button.clicked`.

- [ ] **Step 2: Update `remove_pane`**
Disconnect from `zoom-clicked`.

### Task 4: Update `MainWindow` to handle per-terminal models

**Files:**
- Modify: `ui/window.py`

- [ ] **Step 1: Update `_on_slot_requested` and `__init__`**
Pass `available_models` to `TerminalPane` creation.
Connect to `model-changed` signal.

- [ ] **Step 2: Implement `_on_pane_model_changed`**
Call `process_manager.restart_with_model(pane.session_id, new_model)`.

- [ ] **Step 3: Remove global model selection**
Remove the `model_dropdown` from the main header bar if deemed redundant.

### Task 5: Verification & Cleanup

- [ ] **Step 1: Run existing tests**
Ensure no regressions in workspace or terminal functionality.

- [ ] **Step 2: Add new test case**
Add a test in `tests/test_terminal_pane.py` to verify model selection signaling.

- [ ] **Step 3: Manual verification**
Launch the app and verify each terminal can have a different model.
