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