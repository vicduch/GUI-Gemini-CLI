import sys
import gi
gi.require_version('Gtk', '4.0')
gi.require_version('Adw', '1')
from gi.repository import Gtk, Adw, Gio
from core.logging_utils import configure_logging
from ui.window import MainWindow

class GeminiGuiApp(Adw.Application):
    def __init__(self):
        super().__init__(application_id="org.gemini.GuiOrchestrator",
                         flags=Gio.ApplicationFlags.FLAGS_NONE)

    def do_activate(self):
        win = self.props.active_window
        if not win:
            win = MainWindow(application=self)
        win.present()

if __name__ == '__main__':
    configure_logging()
    app = GeminiGuiApp()
    sys.exit(app.run(sys.argv))
