import gi
gi.require_version('Gtk', '4.0')
gi.require_version('Adw', '1')
from gi.repository import Gtk, Adw

class MainWindow(Adw.ApplicationWindow):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.set_title("Gemini GUI Orchestrator")
        self.set_default_size(1200, 800)
        
        # Structure de base : Box horizontale contenant Sidebar G, Workspace, Sidebar D
        main_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL)
        
        # Stub Sidebar Gauche
        left_sidebar = Gtk.Box(width_request=250)
        left_sidebar.append(Gtk.Label(label="History & Skills"))
        
        # Stub Workspace Central
        workspace = Gtk.Box(hexpand=True)
        workspace.append(Gtk.Label(label="Terminal Grid Area"))
        
        # Stub Sidebar Droite
        right_sidebar = Gtk.Box(width_request=300)
        right_sidebar.append(Gtk.Label(label="Agent Swarm Monitor"))
        
        main_box.append(left_sidebar)
        main_box.append(Gtk.Separator(orientation=Gtk.Orientation.VERTICAL))
        main_box.append(workspace)
        main_box.append(Gtk.Separator(orientation=Gtk.Orientation.VERTICAL))
        main_box.append(right_sidebar)
        
        self.set_content(main_box)
