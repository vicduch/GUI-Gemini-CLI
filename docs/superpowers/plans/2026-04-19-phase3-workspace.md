# Phase 3 Workspace Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Implement a dynamic multi-terminal workspace with grid layout and a 90% zoom focus mode.

**Architecture:** A `Gtk.Stack` acts as the root workspace container. It has two pages:
1. `grid_page`: A `Gtk.Grid` containing multiple `TerminalPane` instances.
2. `focus_page`: An `Adw.Bin` or `Gtk.Overlay` taking up 100% of the screen but displaying the focused terminal at 90% size, centered. Clicking the background in focus mode returns the terminal to the grid.

**Tech Stack:** Python, GTK4, Libadwaita

---

### Task 1: Create the Workspace class and basic layout

**Files:**
- Create: `ui/views/workspace.py`
- Create: `tests/test_workspace.py`

- [ ] **Step 1: Write the failing test**

```python
import pytest
import gi
gi.require_version('Gtk', '4.0')
from gi.repository import Gtk
from ui.views.workspace import Workspace
from ui.components.terminal_pane import TerminalPane

def test_workspace_initialization():
    workspace = Workspace()
    assert isinstance(workspace, Gtk.Stack)
    
    pages = [page.get_name() for page in workspace.get_pages()]
    assert "grid_page" in pages
    assert "focus_page" in pages

def test_workspace_add_pane():
    workspace = Workspace()
    pane = TerminalPane()
    workspace.add_pane(pane)
    assert pane in workspace.panes
    assert workspace.grid.get_child_at(0, 0) == pane
```

- [ ] **Step 2: Run test to verify it fails**

Run: `pytest tests/test_workspace.py -v`
Expected: FAIL with ModuleNotFoundError or AssertionError

- [ ] **Step 3: Write minimal implementation**

```python
import gi
gi.require_version('Gtk', '4.0')
from gi.repository import Gtk
from ui.components.terminal_pane import TerminalPane

class Workspace(Gtk.Stack):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.set_transition_type(Gtk.StackTransitionType.CROSSFADE)
        
        self.panes = []
        
        # Grid Page
        self.grid = Gtk.Grid()
        self.grid.set_column_spacing(8)
        self.grid.set_row_spacing(8)
        self.grid.set_margin_top(8)
        self.grid.set_margin_bottom(8)
        self.grid.set_margin_start(8)
        self.grid.set_margin_end(8)
        self.add_titled(self.grid, "grid_page", "Grid")
        
        # Focus Page
        self.focus_overlay = Gtk.Overlay()
        self.focus_background = Gtk.Button() # Clickable background
        self.focus_background.set_has_frame(False)
        self.focus_background.connect("clicked", self._on_background_clicked)
        self.focus_overlay.set_child(self.focus_background)
        
        self.focus_bin = Gtk.Box()
        self.focus_bin.set_halign(Gtk.Align.CENTER)
        self.focus_bin.set_valign(Gtk.Align.CENTER)
        self.focus_bin.set_hexpand(True)
        self.focus_bin.set_vexpand(True)
        # Margin simulates the 90% size
        self.focus_bin.set_margin_start(40)
        self.focus_bin.set_margin_end(40)
        self.focus_bin.set_margin_top(40)
        self.focus_bin.set_margin_bottom(40)
        
        self.focus_overlay.add_overlay(self.focus_bin)
        self.add_titled(self.focus_overlay, "focus_page", "Focus")
        
        self.focused_pane = None
        self._next_row = 0
        self._next_col = 0

    def add_pane(self, pane: TerminalPane):
        self.panes.append(pane)
        self.grid.attach(pane, self._next_col, self._next_row, 1, 1)
        self._next_col += 1
        if self._next_col > 1: # Basic 2-column layout
            self._next_col = 0
            self._next_row += 1
        pane.zoom_button.connect("clicked", lambda btn: self.focus_pane(pane))
        
    def _on_background_clicked(self, btn):
        if self.focused_pane:
            self.unfocus_pane()

    def focus_pane(self, pane: TerminalPane):
        pass # To be implemented in next task

    def unfocus_pane(self):
        pass # To be implemented in next task
```

- [ ] **Step 4: Run test to verify it passes**

Run: `pytest tests/test_workspace.py -v`
Expected: PASS

- [ ] **Step 5: Commit**

```bash
git add tests/test_workspace.py ui/views/workspace.py
git commit -m "feat: init workspace stack with grid and focus pages"
```

### Task 2: Implement Focus/Unfocus Logic

**Files:**
- Modify: `ui/views/workspace.py`
- Modify: `tests/test_workspace.py`

- [ ] **Step 1: Write the failing test**

```python
def test_workspace_focus_unfocus():
    workspace = Workspace()
    pane = TerminalPane()
    workspace.add_pane(pane)
    
    # Grid should contain the pane initially
    assert pane.get_parent() == workspace.grid
    
    # Focus the pane
    workspace.focus_pane(pane)
    assert workspace.focused_pane == pane
    assert workspace.get_visible_child_name() == "focus_page"
    assert pane.get_parent() == workspace.focus_bin
    
    # Unfocus the pane
    workspace.unfocus_pane()
    assert workspace.focused_pane is None
    assert workspace.get_visible_child_name() == "grid_page"
    assert pane.get_parent() == workspace.grid
```

- [ ] **Step 2: Run test to verify it fails**

Run: `pytest tests/test_workspace.py::test_workspace_focus_unfocus -v`
Expected: FAIL 

- [ ] **Step 3: Write minimal implementation**

```python
    # Add these implementations to Workspace in ui/views/workspace.py
    def focus_pane(self, pane: TerminalPane):
        if self.focused_pane:
            self.unfocus_pane()
            
        self.focused_pane = pane
        self.grid.remove(pane)
        self.focus_bin.append(pane)
        self.set_visible_child_name("focus_page")

    def unfocus_pane(self):
        if not self.focused_pane:
            return
            
        pane = self.focused_pane
        self.focus_bin.remove(pane)
        self.grid.attach(pane, pane._grid_col, pane._grid_row, 1, 1)
        
        self.focused_pane = None
        self.set_visible_child_name("grid_page")

    # Modify add_pane in Workspace to store grid coordinates:
    def add_pane(self, pane: TerminalPane):
        self.panes.append(pane)
        pane._grid_col = self._next_col
        pane._grid_row = self._next_row
        self.grid.attach(pane, self._next_col, self._next_row, 1, 1)
        self._next_col += 1
        if self._next_col > 1:
            self._next_col = 0
            self._next_row += 1
        pane.zoom_button.connect("clicked", lambda btn: self.focus_pane(pane))
```

- [ ] **Step 4: Run test to verify it passes**

Run: `pytest tests/test_workspace.py::test_workspace_focus_unfocus -v`
Expected: PASS

- [ ] **Step 5: Commit**

```bash
git add tests/test_workspace.py ui/views/workspace.py
git commit -m "feat: implement terminal focus mode transitions"
```

### Task 3: Integrate Workspace into Window

**Files:**
- Modify: `ui/window.py`
- Modify: `tests/test_window.py`

- [ ] **Step 1: Write the failing test**

```python
# Add to tests/test_window.py
from ui.views.workspace import Workspace

def test_window_has_workspace():
    window = MainWindow()
    assert hasattr(window, "workspace")
    assert isinstance(window.workspace, Workspace)
```

- [ ] **Step 2: Run test to verify it fails**

Run: `pytest tests/test_window.py::test_window_has_workspace -v`
Expected: FAIL

- [ ] **Step 3: Write minimal implementation**

```python
# In ui/window.py, import Workspace and add it
import gi
gi.require_version('Gtk', '4.0')
from gi.repository import Gtk
from ui.views.workspace import Workspace
from ui.components.terminal_pane import TerminalPane

class MainWindow(Gtk.ApplicationWindow):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.set_title("Gemini GUI Orchestrator")
        self.set_default_size(1024, 768)

        # Note: adjust this depending on the existing MainWindow layout structure
        self.main_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL)
        self.set_child(self.main_box)
        
        self.workspace = Workspace()
        self.workspace.set_hexpand(True)
        self.workspace.set_vexpand(True)
        
        self.main_box.append(self.workspace)
        self.workspace.add_pane(TerminalPane())
```

- [ ] **Step 4: Run test to verify it passes**

Run: `pytest tests/test_window.py -v`
Expected: PASS

- [ ] **Step 5: Commit**

```bash
git add tests/test_window.py ui/window.py
git commit -m "feat: integrate Workspace into MainWindow"
```
