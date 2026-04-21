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
