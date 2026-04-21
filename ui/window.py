import gi

gi.require_version("Gtk", "4.0")
gi.require_version("Adw", "1")
from gi.repository import Adw, Gtk

from core.logging_utils import get_logger
from core.models import Agent, ErrorContract
from core.process_manager import ProcessState
from ui.components.terminal_pane import TerminalPane
from ui.components.settings_dialog import SettingsDialog
from ui.views.left_sidebar import LeftSidebar
from ui.views.right_sidebar import AgentMonitorSidebar
from ui.views.workspace import Workspace

logger = get_logger(__name__)


class MainWindow(Adw.ApplicationWindow):
    def __init__(self, process_manager=None, ipc_server=None, terminal_factory=None, config_manager=None, **kwargs):
        super().__init__(**kwargs)
        self.process_manager = process_manager
        self.ipc_server = ipc_server
        self.config_manager = config_manager

        self.set_title("Gemini GUI Orchestrator")
        self.set_default_size(1200, 800)

        # ToolbarView pour HeaderBar + Contenu
        toolbar_view = Adw.ToolbarView()
        
        header = Adw.HeaderBar()
        
        # Model Selection DropDown
        models = ["gemini-1.5-pro", "gemini-1.5-flash", "gemini-2.0-flash-exp"]
        self.model_dropdown = Gtk.DropDown.new_from_strings(models)
        self.model_dropdown.set_valign(Gtk.Align.CENTER)
        self.model_dropdown.connect("notify::selected", self._on_model_changed)
        header.pack_start(self.model_dropdown)
        
        # Settings Button
        settings_btn = Gtk.Button(icon_name="emblem-system-symbolic")
        settings_btn.set_tooltip_text("Settings")
        settings_btn.connect("clicked", self._on_settings_clicked)
        header.pack_end(settings_btn)
        
        toolbar_view.add_top_bar(header)

        # Structure de base : Box horizontale contenant Sidebar G, Workspace, Sidebar D
        main_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL)

        # Sidebar Gauche (History & Skills)
        self.left_sidebar = LeftSidebar()

        # Workspace central (grid + focus)
        self.workspace = Workspace()
        self.workspace.set_hexpand(True)
        self.workspace.set_vexpand(True)

        # Sidebar Droite (Agent Monitor)
        self.right_sidebar = AgentMonitorSidebar()

        main_box.append(self.left_sidebar)
        main_box.append(Gtk.Separator(orientation=Gtk.Orientation.VERTICAL))
        main_box.append(self.workspace)
        main_box.append(Gtk.Separator(orientation=Gtk.Orientation.VERTICAL))
        main_box.append(self.right_sidebar)

        toolbar_view.set_content(main_box)
        self.set_content(toolbar_view)

        self.workspace.add_pane(TerminalPane(terminal_factory=terminal_factory))

        if self.process_manager:
            self.process_manager.set_event_callback(self._on_process_event)

        if self.ipc_server:
            self.ipc_server.set_callback(self._on_ipc_message)

    def _on_process_event(self, event):
        if event.state == ProcessState.FAILED:
            err = ErrorContract(
                code="PROC_FAIL",
                message=event.message or "Process died",
                severity="error",
                correlation_id=event.correlation_id,
            )
            # Dispatch au premier pane du workspace pour test
            if self.workspace.panes:
                self.workspace.panes[0].show_error(err)

    def _on_model_changed(self, dropdown, pspec):
        selected_item = dropdown.get_selected_item()
        if not selected_item:
            return
        
        model_name = selected_item.get_string()
        logger.info(f"Model changed to: {model_name}")
        
        if self.process_manager and self.workspace.panes:
            # Pour le prototype, on redémarre la session du premier terminal visible
            # Dans une version finale, chaque terminal pourrait avoir sa session/modèle
            session_id = "default" # TODO: Get from terminal pane
            self.process_manager.restart_with_model(session_id, model_name)

    def _on_settings_clicked(self, button):
        if not self.config_manager:
            return
        dialog = SettingsDialog(self.config_manager, transient_for=self)
        dialog.present()

    def _on_ipc_message(self, message: dict):
        # Route to right sidebar
        if "agent_id" in message:
            agent = Agent(
                id=message["agent_id"],
                status=message.get("status", "unknown"),
                role=message.get("role", "agent"),
            )
            self.right_sidebar.update_agent(agent)
