import gi

gi.require_version('Gtk', '4.0')
gi.require_version('Adw', '1')
from gi.repository import Adw, Gtk

from ui.components.terminal_pane import TerminalPane
from ui.views.workspace import Workspace
from ui.views.right_sidebar import AgentMonitorSidebar
from core.process_manager import ProcessState
from core.models import ErrorContract, Agent


class MainWindow(Adw.ApplicationWindow):
    def __init__(self, process_manager=None, ipc_server=None, terminal_factory=None, **kwargs):
        super().__init__(**kwargs)
        self.process_manager = process_manager
        self.ipc_server = ipc_server

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

        if self.process_manager:
            self.process_manager.set_event_callback(self._on_process_event)
        
        if self.ipc_server:
            self.ipc_server.set_callback(self._on_ipc_message)

        # Lancement d'un processus test
        if self.process_manager:
            # On utilise python3 pour envoyer les messages IPC car socat n'est pas garanti
            cmd = [
                "python3", "-c",
                "import socket, time; "
                "s = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM); "
                "s.connect('/tmp/gemini-gui-ipc.sock'); "
                "s.sendall(b'{\"agent_id\": \"master\", \"status\": \"running\", \"role\": \"orchestrator\"}\\n'); "
                "time.sleep(2); "
                "s.sendall(b'{\"agent_id\": \"master\", \"status\": \"finished\", \"role\": \"orchestrator\"}\\n'); "
                "time.sleep(100)"
            ]
            self.process_manager.spawn("test_session", cmd)

    def _on_process_event(self, event):
        if event.state == ProcessState.FAILED:
            err = ErrorContract(
                code="PROC_FAIL", 
                message=event.message or "Process died", 
                severity="error", 
                correlation_id=event.correlation_id
            )
            # Dispatch au premier pane du workspace pour test
            if self.workspace.panes:
                self.workspace.panes[0].show_error(err)

    def _on_ipc_message(self, message: dict):
        # Route to right sidebar
        if "agent_id" in message:
            agent = Agent(
                id=message["agent_id"], 
                status=message.get("status", "unknown"), 
                role=message.get("role", "agent")
            )
            self.right_sidebar.update_agent(agent)
