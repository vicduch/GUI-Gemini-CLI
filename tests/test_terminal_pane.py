import pytest
import gi
gi.require_version('Gtk', '4.0')
gi.require_version('Adw', '1')
from gi.repository import Gtk, Adw
from ui.components.terminal_pane import TerminalPane

@pytest.fixture(autouse=True)
def init_adw():
    Adw.init()

def test_terminal_pane_instantiation():
    pane = TerminalPane(terminal_factory=lambda: Gtk.TextView())
    assert isinstance(pane, Gtk.Overlay)
    assert isinstance(pane.terminal, Gtk.TextView)
