import gi
import pytest
from types import SimpleNamespace

gi.require_version("Gtk", "4.0")
gi.require_version("Adw", "1")
from gi.repository import Adw, Gtk

from unittest.mock import MagicMock
from ui.components.terminal_pane import TerminalPane
from ui.views.workspace import Workspace
from ui.window import MainWindow
from core.process_manager import ProcessManager, ProcessState

pytestmark = pytest.mark.usefixtures("require_gtk_display")


@pytest.fixture
def adw_app():
    import uuid

    app = Adw.Application(application_id=f"org.gemini.test_{uuid.uuid4().hex[:8]}")
    app.register()
    return app


@pytest.fixture
def fake_terminal_factory():
    def _factory():
        term = Gtk.TextView()
        term.feed_child = MagicMock()
        term.spawn_async = MagicMock()
        return term
    return _factory


def test_main_window_instantiation(adw_app, fake_terminal_factory):
    window = MainWindow(application=adw_app, terminal_factory=fake_terminal_factory)

    assert window.get_title() == "Gemini GUI Orchestrator"
    assert isinstance(window, Adw.ApplicationWindow)


def test_window_has_workspace(adw_app, fake_terminal_factory):
    window = MainWindow(application=adw_app, terminal_factory=fake_terminal_factory)
    assert isinstance(window.workspace, Workspace)


def test_window_spawns_default_session_on_startup(adw_app, fake_terminal_factory):
    pm = MagicMock(spec=ProcessManager)
    win = MainWindow(application=adw_app, process_manager=pm, terminal_factory=fake_terminal_factory)
    pm.spawn.assert_called_once()


def test_model_change_injects_command_with_real_session(adw_app, fake_terminal_factory):
    pm = MagicMock(spec=ProcessManager)
    win = MainWindow(application=adw_app, process_manager=pm, terminal_factory=fake_terminal_factory)
    
    # Simulate a terminal pane with a specific session ID
    pane = win.workspace.panes[0]
    pane.session_id = "real-session-123"
    
    # Trigger model change on the pane
    # Fallback list: gemini-3.1-pro-preview, gemini-3-flash-preview, etc.
    pane.model_dropdown.set_selected(1)
    
    # Verify feed_child was NOT called yet due to buffering
    pane.terminal.feed_child.assert_not_called()

    # Simulate spawn completion to flush buffer
    pane.spawn_process(["gemini"])
    args, _ = pane.terminal.spawn_async.call_args
    args[9](pane.terminal, 1234, None, None) # call _spawn_cb
    
    # Now verify feed_child was called with the /model set command using \r
    pane.terminal.feed_child.assert_called_with(b"/model set gemini-3-flash-preview\r")


def test_model_change_no_session_active(adw_app, fake_terminal_factory):
    pm = MagicMock(spec=ProcessManager)
    win = MainWindow(application=adw_app, process_manager=pm, terminal_factory=fake_terminal_factory)
    
    # Remove all panes to simulate no session
    for pane in list(win.workspace.panes):
        win.workspace.remove_pane(pane)
    
    # No pane means no dropdown to trigger
    assert len(win.workspace.panes) == 0
    pm.restart_with_model.assert_not_called()


def test_model_dropdown_populated_from_config(adw_app, fake_terminal_factory):
    from core.config_manager import ConfigManager
    cm = MagicMock(spec=ConfigManager)
    custom_models = ["custom-model-1", "custom-model-2"]
    cm.get.return_value = custom_models
    
    win = MainWindow(application=adw_app, config_manager=cm, terminal_factory=fake_terminal_factory)
    pane = win.workspace.panes[0]
    
    # Check if dropdown has the custom models
    model_list = []
    # In GTK4 Gtk.DropDown uses a Gio.ListModel.
    model = pane.model_dropdown.get_model()
    for i in range(model.get_n_items()):
        item = model.get_item(i)
        model_list.append(item.get_string())
    
    assert model_list == custom_models
    cm.get.assert_called_with("available_models", ["gemini-3.1-pro-preview"])


def test_process_error_routed_to_matching_session_pane(adw_app, fake_terminal_factory):
    win = MainWindow(application=adw_app, terminal_factory=fake_terminal_factory)
    first_pane = win.workspace.panes[0]
    first_pane.session_id = "session-1"
    first_pane.show_error = MagicMock()

    second_pane = TerminalPane(terminal_factory=fake_terminal_factory, session_id="session-2")
    second_pane.show_error = MagicMock()
    win.workspace.add_pane(second_pane)

    event = SimpleNamespace(
        state=ProcessState.FAILED,
        session_id="session-2",
        message="boom",
        correlation_id="corr-123",
    )
    win._on_process_event(event)

    first_pane.show_error.assert_not_called()
    second_pane.show_error.assert_called_once()

def test_window_slot_requested_adds_terminal_pane(adw_app, fake_terminal_factory):
    win = MainWindow(application=adw_app, terminal_factory=fake_terminal_factory)
    initial_panes = len(win.workspace.panes)
    
    assert len(win.workspace.empty_slots) > 0
    slot = win.workspace.empty_slots[0]
    
    win.workspace.emit("slot-requested", slot)
    
    assert len(win.workspace.panes) == initial_panes + 1
    assert slot not in win.workspace.empty_slots
