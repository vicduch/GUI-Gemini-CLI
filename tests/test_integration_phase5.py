import gi
import pytest

gi.require_version("Gtk", "4.0")
gi.require_version("Adw", "1")

from core.process_manager import ProcessEvent, ProcessState
from ui.window import MainWindow

pytestmark = pytest.mark.usefixtures("require_gtk_display")


def test_mainwindow_routes_ipc_to_sidebar():
    win = MainWindow()
    # Simulate IPC message
    msg = {"agent_id": "master-agent", "status": "active", "role": "orchestrator"}
    win._on_ipc_message(msg)

    # Check if agent is in sidebar
    assert win.right_sidebar.store.get_n_items() == 1
    item = win.right_sidebar.store.get_item(0)
    assert item.agent_id == "master-agent"
    assert item.status == "active"


def test_mainwindow_handles_invalid_ipc_payload():
    win = MainWindow()
    # Missing agent_id should be ignored gracefully
    win._on_ipc_message({"status": "ghost"})
    assert win.right_sidebar.store.get_n_items() == 0


def test_mainwindow_crash_recovery_ux():
    win = MainWindow()
    # Simulate process failure event
    event = ProcessEvent(
        session_id="sess-1",
        event="failed",
        state=ProcessState.FAILED,
        pid=1234,
        correlation_id="corr-1",
        message="Critical failure",
    )
    win._on_process_event(event)

    # Check if first pane shows error
    pane = win.workspace.panes[0]
    assert pane.error_banner.get_revealed() is True
    assert "PROC_FAIL" in pane.error_banner.get_title()
    assert "Critical failure" in pane.error_banner.get_title()
