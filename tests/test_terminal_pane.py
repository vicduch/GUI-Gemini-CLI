import gi
import pytest

gi.require_version('Gtk', '4.0')
from gi.repository import Gtk

from ui.components.terminal_pane import TerminalPane

pytestmark = pytest.mark.usefixtures("require_gtk_display")

def test_terminal_pane_instantiation():
    pane = TerminalPane(terminal_factory=lambda: Gtk.TextView())
    assert isinstance(pane, Gtk.Overlay)
    assert isinstance(pane.terminal, Gtk.TextView)
