import sys
import os

import gi

gi.require_version("Gtk", "4.0")
gi.require_version("Adw", "1")
from gi.repository import Adw, Gio

from core.config_manager import ConfigManager
from core.ipc_server import IpcServer
from core.logging_utils import configure_logging
from core.process_manager import ProcessManager
from ui.window import MainWindow


class GeminiGuiApp(Adw.Application):
    def __init__(self):
        super().__init__(
            application_id="org.gemini.GuiOrchestrator", flags=Gio.ApplicationFlags.FLAGS_NONE
        )
        self.config = ConfigManager(os.path.expanduser("~/.config/gemini-gui/config.json"))
        self.pm = ProcessManager()
        self.ipc = IpcServer("/tmp/gemini-gui-ipc.sock")

    def do_activate(self):
        self.ipc.start()
        self._apply_theme()
        
        win = self.props.active_window
        if not win:
            win = MainWindow(
                application=self, 
                process_manager=self.pm, 
                ipc_server=self.ipc,
                config_manager=self.config
            )
        win.present()

    def _apply_theme(self):
        theme = self.config.get("theme", "System")
        style_manager = Adw.StyleManager.get_default()
        if theme == "Light":
            style_manager.set_color_scheme(Adw.ColorScheme.FORCE_LIGHT)
        elif theme == "Dark":
            style_manager.set_color_scheme(Adw.ColorScheme.FORCE_DARK)
        else:
            style_manager.set_color_scheme(Adw.ColorScheme.PREFER_LIGHT)


if __name__ == "__main__":
    configure_logging()
    app = GeminiGuiApp()
    sys.exit(app.run(sys.argv))
