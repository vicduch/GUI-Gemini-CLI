import sys
import os

import gi

gi.require_version("Gtk", "4.0")
gi.require_version("Adw", "1")
from gi.repository import Adw, Gio, GLib

from core.config_manager import ConfigManager
from core.ipc_server import IpcServer
from core.logging_utils import configure_logging
from core.process_manager import ProcessManager
from ui.style_utils import apply_theme, load_css
from ui.window import MainWindow


class GeminiGuiApp(Adw.Application):
    def __init__(self):
        super().__init__(
            application_id="org.gemini.GuiOrchestrator", flags=Gio.ApplicationFlags.FLAGS_NONE
        )
        config_dir = os.path.join(GLib.get_user_config_dir(), "gemini-gui")
        self.config = ConfigManager(os.path.join(config_dir, "config.json"))
        self.pm = ProcessManager()
        self.ipc = IpcServer("/tmp/gemini-gui-ipc.sock")

    def do_activate(self):
        self.ipc.start()
        apply_theme(self.config.get("theme", "System"))
        load_css()
        
        win = self.props.active_window
        if not win:
            win = MainWindow(
                application=self, 
                process_manager=self.pm, 
                ipc_server=self.ipc,
                config_manager=self.config
            )
        win.present()


if __name__ == "__main__":
    configure_logging()
    app = GeminiGuiApp()
    sys.exit(app.run(sys.argv))
