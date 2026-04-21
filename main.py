import sys

import gi

gi.require_version('Gtk', '4.0')
gi.require_version('Adw', '1')
from gi.repository import Adw, Gio

from core.ipc_server import IpcServer
from core.logging_utils import configure_logging
from core.process_manager import ProcessManager
from ui.window import MainWindow


class GeminiGuiApp(Adw.Application):
    def __init__(self):
        super().__init__(application_id="org.gemini.GuiOrchestrator",
                         flags=Gio.ApplicationFlags.FLAGS_NONE)
        self.pm = ProcessManager()
        self.ipc = IpcServer("/tmp/gemini-gui-ipc.sock")

    def do_activate(self):
        self.ipc.start()
        win = self.props.active_window
        if not win:
            win = MainWindow(application=self, process_manager=self.pm, ipc_server=self.ipc)
        win.present()

if __name__ == '__main__':
    configure_logging()
    app = GeminiGuiApp()
    sys.exit(app.run(sys.argv))
