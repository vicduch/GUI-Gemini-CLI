import pytest
import gi
gi.require_version('Gtk', '4.0')
gi.require_version('Adw', '1')
from gi.repository import Gtk, Adw
from ui.window import MainWindow

@pytest.fixture(autouse=True)
def init_adw():
    Adw.init()

def test_main_window_instantiation():
    app = Adw.Application(application_id="org.gemini.GuiOrchestrator")
    app.register()
    
    window = MainWindow(application=app)
    
    assert window.get_title() == "Gemini GUI Orchestrator"
    assert isinstance(window, Adw.ApplicationWindow)
