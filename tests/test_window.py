import pytest
import gi
gi.require_version('Gtk', '4.0')
gi.require_version('Adw', '1')
from gi.repository import Gtk, Adw
from ui.window import MainWindow
from ui.views.workspace import Workspace

pytestmark = pytest.mark.usefixtures("require_gtk_display")

@pytest.fixture
def adw_app():
    import uuid
    app = Adw.Application(application_id=f"org.gemini.test_{uuid.uuid4().hex[:8]}")
    app.register()
    return app

@pytest.fixture
def fake_terminal_factory():
    return lambda: Gtk.TextView()

def test_main_window_instantiation(adw_app, fake_terminal_factory):
    window = MainWindow(application=adw_app, terminal_factory=fake_terminal_factory)

    assert window.get_title() == "Gemini GUI Orchestrator"
    assert isinstance(window, Adw.ApplicationWindow)

def test_window_has_workspace(adw_app, fake_terminal_factory):
    window = MainWindow(application=adw_app, terminal_factory=fake_terminal_factory)
    assert hasattr(window, "workspace")
    assert isinstance(window.workspace, Workspace)
