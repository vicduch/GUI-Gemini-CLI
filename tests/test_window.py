import gi
import pytest

gi.require_version("Gtk", "4.0")
gi.require_version("Adw", "1")
from gi.repository import Adw, Gtk

from unittest.mock import MagicMock
from ui.views.workspace import Workspace
from ui.window import MainWindow
from core.process_manager import ProcessManager

pytestmark = pytest.mark.usefixtures("require_gtk_display")


@pytest.fixture
def adw_app():
    import uuid

    app = Adw.Application(application_id=f"org.gemini.test_{uuid.uuid4().hex[:8]}")
    app.register()
    return app


@pytest.fixture
def fake_terminal_factory():
    return lambda: Gtk.TextView()


def test_main_window_instantiation(adw_app, fake_terminal_factory):
    window = MainWindow(application=adw_app, terminal_factory=fake_terminal_factory)

    assert window.get_title() == "Gemini GUI Orchestrator"
    assert isinstance(window, Adw.ApplicationWindow)


def test_window_has_workspace(adw_app, fake_terminal_factory):
    window = MainWindow(application=adw_app, terminal_factory=fake_terminal_factory)
    assert hasattr(window, "workspace")
    assert isinstance(window.workspace, Workspace)


def test_model_change_triggers_hot_reload_with_real_session(adw_app, fake_terminal_factory):
    pm = MagicMock(spec=ProcessManager)
    win = MainWindow(application=adw_app, process_manager=pm, terminal_factory=fake_terminal_factory)
    
    # Simulate a terminal pane with a specific session ID
    pane = win.workspace.panes[0]
    pane.session_id = "real-session-123"
    
    # Trigger model change
    # Note: notify::selected is emitted when selection changes.
    # Initially 0 (gemini-1.5-pro). Change to 1 (gemini-1.5-flash).
    win.model_dropdown.set_selected(1)
    
    # Verify pm.restart_with_model was called with real-session-123
    pm.restart_with_model.assert_called_with("real-session-123", "gemini-1.5-flash")


def test_model_change_no_session_active(adw_app, fake_terminal_factory):
    pm = MagicMock(spec=ProcessManager)
    win = MainWindow(application=adw_app, process_manager=pm, terminal_factory=fake_terminal_factory)
    
    # Remove all panes to simulate no session
    for pane in list(win.workspace.panes):
        win.workspace.remove_pane(pane)
    
    # Trigger model change
    win.model_dropdown.set_selected(1)
    
    # Verify pm.restart_with_model was NOT called
    pm.restart_with_model.assert_not_called()
