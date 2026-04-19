import pytest
import gi
gi.require_version('Gtk', '4.0')
gi.require_version('Adw', '1')
from gi.repository import Gtk, Adw
from ui.window import MainWindow

@pytest.fixture(scope="session", autouse=True)
def init_adw():
    Adw.init()

@pytest.fixture
def adw_app():
    # Use a unique ID for each test to avoid "already exported" error in shared process
    import uuid
    app_id = f"org.gemini.test_{uuid.uuid4().hex[:8]}"
    app = Adw.Application(application_id=app_id)
    app.register()
    return app

def test_main_window_instantiation(adw_app):
    window = MainWindow(application=adw_app)
    assert window.get_title() == "Gemini GUI Orchestrator"
    assert isinstance(window, Adw.ApplicationWindow)

def test_window_has_workspace(adw_app):
    window = MainWindow(application=adw_app)
    from ui.views.workspace import Workspace
    assert hasattr(window, "workspace")
    assert isinstance(window.workspace, Workspace)
