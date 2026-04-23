import gi
import pytest
from unittest.mock import MagicMock
from gi.repository import Gtk, Vte, GLib

gi.require_version("Vte", "3.91")

from ui.components.terminal_pane import TerminalPane
from ui.window import MainWindow
from core.process_manager import ProcessManager

pytestmark = pytest.mark.usefixtures("require_gtk_display")

@pytest.fixture
def adw_app():
    import uuid
    gi.require_version("Adw", "1")
    from gi.repository import Adw
    app = Adw.Application(application_id=f"org.gemini.test_race_{uuid.uuid4().hex[:8]}")
    app.register()
    return app

def test_terminal_pane_buffers_commands_until_ready():
    # Use a real Vte.Terminal to avoid TypeError: argument child: Expected Gtk.Widget
    # But mock its feed_child and spawn_async methods
    terminal = Vte.Terminal()
    terminal.feed_child = MagicMock()
    terminal.spawn_async = MagicMock()
    
    pane = TerminalPane(terminal_factory=lambda: terminal)
    
    # Simulate feeding command before spawn
    pane.inject_command("/test command\r")
    
    # Should NOT have called terminal.feed_child yet
    terminal.feed_child.assert_not_called()
    
    # Now spawn and simulate success
    pane.spawn_process(["gemini"])
    
    # Find the callback passed to spawn_async
    # args: (pty_flags, working_directory, argv, envv, spawn_flags, child_setup, child_setup_data, timeout, cancellable, callback, user_data)
    args, kwargs = terminal.spawn_async.call_args
    callback = args[9] # index 9 is _spawn_cb
    
    # Call the callback to simulate successful spawn
    callback(terminal, 1234, None, None)
    
    # Now it should have flushed the buffer
    terminal.feed_child.assert_called_with(b"/test command\r")

def test_race_condition_model_change_before_spawn(adw_app):
    terminal = Vte.Terminal()
    terminal.feed_child = MagicMock()
    terminal.spawn_async = MagicMock()
    
    pm = MagicMock(spec=ProcessManager)
    win = MainWindow(application=adw_app, process_manager=pm, terminal_factory=lambda: terminal)
    pane = win.workspace.panes[0]
    
    # Trigger model change IMMEDIATELY (before spawn finishes)
    pane.model_dropdown.set_selected(1)
    selected_model = pane.available_models[1]
    
    # feed_child should NOT be called yet
    terminal.feed_child.assert_not_called()
    
    # Simulate spawn completion
    pane.spawn_process(["gemini"])
    args, kwargs = terminal.spawn_async.call_args
    callback = args[9]
    callback(terminal, 1234, None, None)
    
    # Now it should have been called
    expected_cmd = f"/model set {selected_model}\r".encode("utf-8")
    terminal.feed_child.assert_called_with(expected_cmd)
