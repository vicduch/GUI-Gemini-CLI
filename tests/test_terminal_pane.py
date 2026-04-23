import gi
import pytest

gi.require_version("Gtk", "4.0")
from gi.repository import Gtk

from core.models import ErrorContract
from ui.components.terminal_pane import TerminalPane

pytestmark = pytest.mark.usefixtures("require_gtk_display")


def test_terminal_pane_instantiation():
    pane = TerminalPane(terminal_factory=lambda: Gtk.TextView())
    assert isinstance(pane, Gtk.Overlay)
    assert isinstance(pane.terminal, Gtk.TextView)


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
    
    # On vérifie que spawn_async a été appelé
    assert spawn_called is True
    assert spawn_argv is not None
    assert "gemini-cli" in spawn_argv[0] or "gemini" in spawn_argv[0]

