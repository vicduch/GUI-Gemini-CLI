import gi

gi.require_version("Gtk", "4.0")
gi.require_version("Adw", "1")
from gi.repository import Adw, Gtk, GObject

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
        self.terminal_factory = terminal_factory

        self.set_title("Gemini GUI Orchestrator")
        self.set_default_size(1200, 800)

        # ToolbarView pour HeaderBar + Contenu
        toolbar_view = Adw.ToolbarView()
        
        header = Adw.HeaderBar()
        
        # Sidebar Toggles
        self.toggle_left = Gtk.ToggleButton(icon_name="sidebar-show-symbolic")
        self.toggle_left.set_active(True)
        self.toggle_left.set_tooltip_text("Toggle Left Sidebar")
        header.pack_start(self.toggle_left)

        # Model Selection DropDown
        if self.config_manager:
            models = self.config_manager.get("available_models", ["gemini-3.1-pro"])
        else:
            models = ["gemini-3.1-pro", "gemini-3-flash", "gemini-3.1-flash-lite"]
        
        self.model_dropdown = Gtk.DropDown.new_from_strings(models)
        self.model_dropdown.set_valign(Gtk.Align.CENTER)
        self.model_dropdown.connect("notify::selected", self._on_model_changed)
        header.pack_start(self.model_dropdown)
        
        # Right Sidebar Toggle
        self.toggle_right = Gtk.ToggleButton(icon_name="sidebar-show-right-symbolic")
        self.toggle_right.set_active(True)
        self.toggle_right.set_tooltip_text("Toggle Right Sidebar")
        header.pack_end(self.toggle_right)

        # Settings Button
        settings_btn = Gtk.Button(icon_name="emblem-system-symbolic")
        settings_btn.set_tooltip_text("Settings")
        settings_btn.connect("clicked", self._on_settings_clicked)
        header.pack_end(settings_btn)
        
        toolbar_view.add_top_bar(header)

        # Sidebar Gauche (History & Skills)
        self.left_sidebar = LeftSidebar()

        # Workspace central (grid + focus)
        self.workspace = Workspace()
        self.workspace.set_hexpand(True)
        self.workspace.set_vexpand(True)
        self.workspace.connect("slot-requested", self._on_slot_requested)

        # Sidebar Droite (Agent Monitor)
        self.right_sidebar = AgentMonitorSidebar()

        # Imbrication des SplitViews pour les barres latérales
        self.left_split_view = Adw.OverlaySplitView()
        self.left_split_view.set_sidebar(self.left_sidebar)
        self.left_split_view.set_content(self.workspace)
        self.left_split_view.set_min_sidebar_width(250)
        self.left_split_view.bind_property("show-sidebar", self.toggle_left, "active", GObject.BindingFlags.BIDIRECTIONAL | GObject.BindingFlags.SYNC_CREATE)

        self.right_split_view = Adw.OverlaySplitView()
        self.right_split_view.set_sidebar_position(Gtk.PackType.END)
        self.right_split_view.set_sidebar(self.right_sidebar)
        self.right_split_view.set_content(self.left_split_view)
        self.right_split_view.set_min_sidebar_width(300)
        self.right_split_view.bind_property("show-sidebar", self.toggle_right, "active", GObject.BindingFlags.BIDIRECTIONAL | GObject.BindingFlags.SYNC_CREATE)

        toolbar_view.set_content(self.right_split_view)
        self.set_content(toolbar_view)

        self.workspace.add_pane(TerminalPane(terminal_factory=terminal_factory))

        if self.process_manager:
            self.process_manager.set_event_callback(self._on_process_event)

        if self.ipc_server:
            self.ipc_server.set_callback(self._on_ipc_message)

    def _on_slot_requested(self, _workspace, slot):
        pane = TerminalPane(terminal_factory=self.terminal_factory)
        self.workspace.add_pane(pane, replace_slot=slot)

    def _on_process_event(self, event):
        if event.state == ProcessState.FAILED:
            err = ErrorContract(
                code="PROC_FAIL",
                message=event.message or "Process died",
                severity="error",
                correlation_id=event.correlation_id,
            )
            for pane in self.workspace.panes:
                if pane.session_id == event.session_id:
                    pane.show_error(err)
                    return

            if len(self.workspace.panes) == 1:
                self.workspace.panes[0].show_error(err)
            else:
                logger.warning("No terminal pane found for failed session_id=%s", event.session_id)

    def _on_model_changed(self, dropdown, pspec):
        selected_item = dropdown.get_selected_item()
        if not selected_item:
            return
        
        model_name = selected_item.get_string()
        logger.info(f"Model changed to: {model_name}")
        
        if self.process_manager:
            session_id = self.workspace.get_active_session_id()
            if session_id:
                logger.info(f"Restarting session '{session_id}' with model {model_name}")
                self.process_manager.restart_with_model(session_id, model_name)
            else:
                logger.warning("No active session found for hot-reload")

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
