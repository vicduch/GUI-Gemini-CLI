import gi

gi.require_version('Gtk', '4.0')
gi.require_version('Adw', '1')
from gi.repository import Adw, Gtk

from ui.components.terminal_pane import TerminalPane
from ui.views.workspace import Workspace
from ui.views.right_sidebar import AgentMonitorSidebar


class MainWindow(Adw.ApplicationWindow):
    def __init__(self, terminal_factory=None, **kwargs):
        super().__init__(**kwargs)
        self.set_title("Gemini GUI Orchestrator")
        self.set_default_size(1200, 800)
        
        # Structure de base : Box horizontale contenant Sidebar G, Workspace, Sidebar D
        main_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL)
        
        # Stub Sidebar Gauche
        left_sidebar = Gtk.Box(width_request=250)
        left_sidebar.append(Gtk.Label(label="History & Skills"))

        # Workspace central (grid + focus)
        self.workspace = Workspace()
        self.workspace.set_hexpand(True)
        self.workspace.set_vexpand(True)

        # Sidebar Droite (Agent Monitor)
        self.right_sidebar = AgentMonitorSidebar()
        
        main_box.append(left_sidebar)
        main_box.append(Gtk.Separator(orientation=Gtk.Orientation.VERTICAL))
        main_box.append(self.workspace)
        main_box.append(Gtk.Separator(orientation=Gtk.Orientation.VERTICAL))
        main_box.append(self.right_sidebar)

        self.set_content(main_box)

        self.workspace.add_pane(TerminalPane(terminal_factory=terminal_factory))
