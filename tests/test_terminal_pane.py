import pytest
import gi
gi.require_version('Gtk', '4.0')
gi.require_version('Adw', '1')
gi.require_version('Vte', '3.91') # Note: VTE4 uses 3.91 API in GTK4
from gi.repository import Gtk, Adw, Vte
from ui.components.terminal_pane import TerminalPane

@pytest.fixture(autouse=True)
def init_adw():
    Adw.init()

def test_terminal_pane_instantiation():
    pane = TerminalPane()
    assert isinstance(pane, Gtk.Overlay)
    
    # Vérifier que le composant a un Vte.Terminal enfant
    terminal_found = False
    child = pane.get_first_child()
    while child is not None:
        if isinstance(child, Vte.Terminal):
            terminal_found = True
            break
        child = child.get_next_sibling()
        
    assert terminal_found, "Vte.Terminal should be embedded inside TerminalPane"
