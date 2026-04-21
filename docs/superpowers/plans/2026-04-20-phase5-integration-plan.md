# Phase 5: Real Integration & Observability Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Transformer le socle Phase 4 en un orchestrateur capable de piloter de vraies instances de gemini-cli avec monitoring UI (IPC) et gestion de crash.

**Architecture:** Câblage de `ProcessManager` et `IpcServer` dans un contrôleur central ou `MainWindow`. Routage des événements IPC vers un nouveau composant `AgentMonitorSidebar`. Enrichissement du modèle d'erreurs (contrat JSON) et ajout de `correlation_id` pour la traçabilité complète.

**Tech Stack:** Python 3.12+, GTK4, Libadwaita, GLib.

---

### Task 1: Contrat d'Erreurs et Observabilité (Core)

**Files:**
- Modify: `core/models.py:1`
- Modify: `core/logging_utils.py:1`
- Modify: `core/process_manager.py:1`
- Test: `tests/test_models.py`

- [ ] **Step 1: Écrire le test du contrat d'erreur**

```python
# tests/test_models.py
from core.models import ErrorContract

def test_error_contract_serialization():
    err = ErrorContract(code="SPAWN_FAIL", message="Friendly message", severity="error", correlation_id="123")
    assert err.to_dict() == {"code": "SPAWN_FAIL", "message": "Friendly message", "severity": "error", "correlation_id": "123"}
```

- [ ] **Step 2: Vérifier l'échec**
Run: `pytest tests/test_models.py -v`
Expected: FAIL (ErrorContract non défini)

- [ ] **Step 3: Implémenter ErrorContract et MAJ des modèles**

```python
# core/models.py
from dataclasses import dataclass, asdict

@dataclass
class ErrorContract:
    code: str
    message: str
    severity: str
    correlation_id: str

    def to_dict(self) -> dict:
        return asdict(self)

@dataclass
class Session:
    id: str
    model: str
    workspace: str

@dataclass
class Agent:
    id: str
    status: str
    role: str
```

- [ ] **Step 4: Ajouter `correlation_id` à ProcessInfo et ProcessEvent**

```python
# core/process_manager.py
# (Dans les imports et dataclasses)
@dataclass(slots=True)
class ProcessInfo:
    session_id: str
    command: tuple[str, ...]
    correlation_id: str = ""
    # ... reste inchangé ...

@dataclass(frozen=True, slots=True)
class ProcessEvent:
    session_id: str
    event: str
    state: ProcessState
    pid: int | None
    correlation_id: str = ""
    message: str | None = None
    exit_status: int | None = None
    error_contract: dict | None = None
```
*(Mettre à jour `_emit_event` pour passer ces champs).*

- [ ] **Step 5: Run tests**
Run: `pytest tests/test_models.py tests/test_process_manager.py -v`
Expected: PASS

- [ ] **Step 6: Commit**
```bash
git add core/models.py core/process_manager.py tests/
git commit -m "feat: contrat erreur et correlation_id"
```

### Task 2: IPC Routing & Agent Monitor Sidebar (UI)

**Files:**
- Create: `ui/views/right_sidebar.py`
- Modify: `ui/window.py:1`
- Test: `tests/test_right_sidebar.py`

- [ ] **Step 1: Test Right Sidebar update**

```python
# tests/test_right_sidebar.py
import gi
gi.require_version("Gtk", "4.0")
from gi.repository import Gtk
from ui.views.right_sidebar import AgentMonitorSidebar

def test_agent_monitor_adds_agent():
    sidebar = AgentMonitorSidebar()
    sidebar.update_agent({"agent_id": "agent-1", "status": "running", "role": "subagent"})
    assert sidebar.store.get_n_items() == 1
```

- [ ] **Step 2: Vérifier l'échec**
Run: `pytest tests/test_right_sidebar.py -v`

- [ ] **Step 3: Implémenter AgentMonitorSidebar**

```python
# ui/views/right_sidebar.py
import gi
gi.require_version('Gtk', '4.0')
from gi.repository import Gtk, Gio, GObject

class AgentItem(GObject.Object):
    __gtype_name__ = 'AgentItem'
    agent_id = GObject.Property(type=str)
    status = GObject.Property(type=str)
    role = GObject.Property(type=str)
    
    def __init__(self, agent_id, status, role):
        super().__init__()
        self.agent_id = agent_id
        self.status = status
        self.role = role

class AgentMonitorSidebar(Gtk.Box):
    def __init__(self, **kwargs):
        super().__init__(orientation=Gtk.Orientation.VERTICAL, **kwargs)
        self.set_width_request(300)
        self.store = Gio.ListStore(item_type=AgentItem)
        
        factory = Gtk.SignalListItemFactory()
        factory.connect("setup", self._setup_list_item)
        factory.connect("bind", self._bind_list_item)
        
        selection = Gtk.SingleSelection(model=self.store)
        list_view = Gtk.ListView(model=selection, factory=factory)
        
        scroll = Gtk.ScrolledWindow()
        scroll.set_child(list_view)
        scroll.set_vexpand(True)
        
        self.append(Gtk.Label(label="Agent Swarm Monitor", margin_top=10, margin_bottom=10))
        self.append(scroll)
        
    def _setup_list_item(self, factory, list_item):
        label = Gtk.Label(halign=Gtk.Align.START, margin_start=10)
        list_item.set_child(label)
        
    def _bind_list_item(self, factory, list_item):
        item = list_item.get_item()
        label = list_item.get_child()
        label.set_text(f"{item.role}: {item.agent_id} [{item.status}]")

    def update_agent(self, data: dict):
        # Update existing or add new
        agent_id = data.get("agent_id")
        for i in range(self.store.get_n_items()):
            item = self.store.get_item(i)
            if item.agent_id == agent_id:
                item.status = data.get("status", item.status)
                return
        
        new_item = AgentItem(agent_id=agent_id, status=data.get("status", "unknown"), role=data.get("role", "agent"))
        self.store.append(new_item)
```

- [ ] **Step 4: Run tests**
Run: `xvfb-run -a pytest tests/test_right_sidebar.py -v`
Expected: PASS

- [ ] **Step 5: Intégrer dans MainWindow**
*(Remplacer le stub Right Sidebar dans `ui/window.py` par l'instanciation de `AgentMonitorSidebar`)*

- [ ] **Step 6: Commit**
```bash
git add ui/views/right_sidebar.py ui/window.py tests/
git commit -m "feat: agent monitor sidebar via Gio.ListStore"
```

### Task 3: UI Crash Recovery (UX)

**Files:**
- Modify: `ui/components/terminal_pane.py:1`
- Test: `tests/test_terminal_pane.py`

- [ ] **Step 1: Test affichage erreur**

```python
# tests/test_terminal_pane.py
from ui.components.terminal_pane import TerminalPane
from core.models import ErrorContract

def test_terminal_pane_shows_error():
    pane = TerminalPane()
    err = ErrorContract(code="FAIL", message="Crash", severity="error", correlation_id="1")
    pane.show_error(err)
    # Check if error overlay/toast is created
    assert pane.error_overlay is not None
```

- [ ] **Step 2: Vérifier l'échec**
Run: `xvfb-run -a pytest tests/test_terminal_pane.py -v`

- [ ] **Step 3: Implémenter show_error dans TerminalPane**

```python
# ui/components/terminal_pane.py
# (Ajouter show_error et clear_error)
from core.models import ErrorContract
import gi
gi.require_version('Adw', '1')
from gi.repository import Adw, Gtk

# Dans la classe TerminalPane (__init__):
# self.error_banner = Adw.Banner()
# self.error_overlay = Gtk.Overlay()
# self.error_overlay.set_child(vte_terminal)
# self.error_overlay.add_overlay(self.error_banner)
# (Il faut adapter la hiérarchie pour placer la bannière au-dessus du terminal)

# def show_error(self, error: ErrorContract):
#     self.error_banner.set_title(f"[{error.code}] {error.message}")
#     self.error_banner.set_revealed(True)

# def clear_error(self):
#     self.error_banner.set_revealed(False)
```

- [ ] **Step 4: Run tests**
Run: `xvfb-run -a pytest tests/test_terminal_pane.py -v`
Expected: PASS

- [ ] **Step 5: Commit**
```bash
git add ui/components/terminal_pane.py tests/test_terminal_pane.py
git commit -m "feat: error recovery banner in terminal pane"
```

### Task 4: Pilotage Réel (Câblage Core -> UI)

**Files:**
- Modify: `main.py:1`
- Modify: `ui/window.py:1`

- [ ] **Step 1: Initialiser ProcessManager et IpcServer dans main.py / MainWindow**

```python
# main.py
# Ajouter l'initialisation du PM et IPC et les passer à MainWindow
from core.process_manager import ProcessManager
from core.ipc_server import IpcServer

class GeminiGuiApp(Adw.Application):
    def __init__(self):
        super().__init__(application_id="org.gemini.GuiOrchestrator")
        self.pm = ProcessManager()
        self.ipc = IpcServer("/tmp/gemini-gui-ipc.sock")
        
    def do_activate(self):
        self.ipc.start()
        win = self.props.active_window
        if not win:
            win = MainWindow(application=self, process_manager=self.pm, ipc_server=self.ipc)
        win.present()
```

- [ ] **Step 2: Connecter les événements**

```python
# ui/window.py
# Dans MainWindow.__init__ :
# self.process_manager.set_event_callback(self._on_process_event)
# self.ipc_server.set_callback(self._on_ipc_message)

# def _on_process_event(self, event):
#     if event.state == ProcessState.FAILED:
#         err = ErrorContract(code="PROC_FAIL", message=event.message or "Process died", severity="error", correlation_id=event.correlation_id)
#         # dispatch to the right terminal pane ...

# def _on_ipc_message(self, message: dict):
#     # Route to right sidebar
#     if "agent_id" in message:
#         self.right_sidebar.update_agent(message)
```

- [ ] **Step 3: Lancer un processus test**
Ajouter un bouton temporaire ou lancer automatiquement un `ProcessManager.spawn("test_session", ["bash", "-c", "echo '{\"agent_id\": \"master\", \"status\": \"running\"}' > /tmp/gemini-gui-ipc.sock; sleep 100"])` pour valider de bout en bout l'intégration de la Phase 5.

- [ ] **Step 4: Valider**
Run: `xvfb-run -a pytest -q`
Expected: PASS

- [ ] **Step 5: Commit**
```bash
git add main.py ui/window.py
git commit -m "feat: pilotage complet et routage IPC vers UI"
```
