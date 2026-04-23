import gi
import pytest

gi.require_version("Gtk", "4.0")
from gi.repository import Gtk

from core.models import ErrorContract
from ui.components.terminal_pane import TerminalPane

pytestmark = pytest.mark.usefixtures("require_gtk_display")


def test_terminal_pane_instantiation():
    pane = TerminalPane(terminal_factory=lambda: Gtk.TextView())
    assert isinstance(pane, Gtk.Box)
    assert pane.get_orientation() == Gtk.Orientation.VERTICAL
    assert isinstance(pane.terminal, Gtk.TextView)


def test_terminal_pane_signals():
    pane = TerminalPane(terminal_factory=lambda: Gtk.TextView(), available_models=["m1", "m2"])
    
    model_changed_called = False
    new_model_val = ""

    def on_model_changed(_pane, model_name):
        nonlocal model_changed_called, new_model_val
        model_changed_called = True
        new_model_val = model_name

    pane.connect("model-changed", on_model_changed)
    
    # Simulate selection change
    pane.model_dropdown.set_selected(1)
    assert model_changed_called is True
    assert new_model_val == "m2"


def test_terminal_pane_zoom_signal():
    pane = TerminalPane(terminal_factory=lambda: Gtk.TextView())
    zoom_called = False

    def on_zoom_clicked(_pane):
        nonlocal zoom_called
        zoom_called = True

    pane.connect("zoom-clicked", on_zoom_clicked)
    pane.zoom_button.emit("clicked")
    assert zoom_called is True


def test_terminal_pane_shows_error():
    pane = TerminalPane(terminal_factory=lambda: Gtk.TextView())
    err = ErrorContract(code="FAIL", message="Crash", severity="error", correlation_id="1")
    pane.show_error(err)
    # Check if error banner is available and visible (revealed)
    assert hasattr(pane, "error_banner")
    assert pane.error_banner.get_revealed() is True
    assert "FAIL" in pane.error_banner.get_title()
    assert "Crash" in pane.error_banner.get_title()


def test_terminal_pane_clears_error():
    pane = TerminalPane(terminal_factory=lambda: Gtk.TextView())
    err = ErrorContract(code="FAIL", message="Crash", severity="error", correlation_id="1")
    pane.show_error(err)
    assert pane.error_banner.get_revealed() is True

    pane.clear_error()
    assert pane.error_banner.get_revealed() is False


def test_terminal_pane_spawns_gemini_cli(monkeypatch):
    from gi.repository import Vte, GLib

    spawn_called = False
    spawn_argv = None

    def mock_spawn_async(
        _self, _pty_flags, _working_directory, argv, _envv, _spawn_flags, _child_setup, _child_setup_data, _timeout, _cancellable, _callback, _user_data
    ):
        nonlocal spawn_called, spawn_argv
        spawn_called = True
        spawn_argv = argv

    # On utilise monkeypatch pour intercepter l'appel à spawn_async sur la classe Vte.Terminal
    monkeypatch.setattr(Vte.Terminal, "spawn_async", mock_spawn_async)

    # On utilise le terminal par défaut (Vte.Terminal)
    pane = TerminalPane(session_id="test-session")
    pane.spawn_process(["gemini", "cli"])

    # On vérifie que spawn_async a été appelé
    assert spawn_called is True
    assert spawn_argv == ["gemini", "cli"]
    assert "gemini-cli" in spawn_argv[0] or "gemini" in spawn_argv[0]

