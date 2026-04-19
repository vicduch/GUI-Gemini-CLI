# Phase 2 Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Implémenter le serveur IPC, le point d'entrée de l'application UI (Adw.Application) et sa fenêtre principale, ainsi que le composant de terminal VTE de base.

**Architecture:** 
1. `core/ipc_server.py`: Gère un serveur Unix Socket asynchrone intégré à la boucle d'événements GLib (`GLib.io_add_watch`) pour traiter les événements JSON entrants des agents.
2. `main.py` & `ui/window.py`: Définissent l'application `Adw.Application` et la fenêtre principale (`Adw.ApplicationWindow`) comprenant la structure de base (Sidebar Gauche, Workspace central, Sidebar Droite).
3. `ui/components/terminal_pane.py`: Encapsule un widget `Vte.Terminal` pour affichage dans le workspace.

**Tech Stack:** Python 3.12+, GTK4, Libadwaita, VTE 2.91 (PyGObject), pytest.

---

### Task 1: Implémentation du serveur IPC (`core/ipc_server.py`)

**Files:**
- Create: `core/ipc_server.py`
- Create: `tests/test_ipc_server.py`

- [ ] **Step 1: Write the failing test**

```python
# tests/test_ipc_server.py
import json
import socket
import os
import pytest
from gi.repository import GLib
from core.ipc_server import IpcServer

@pytest.fixture
def socket_path(tmp_path):
    return str(tmp_path / "test_ipc.sock")

def test_ipc_server_receives_message(socket_path):
    received_messages = []
    
    def on_message(msg):
        received_messages.append(msg)
        loop.quit()

    server = IpcServer(socket_path)
    server.set_callback(on_message)
    server.start()

    # Client simulation
    client = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
    client.connect(socket_path)
    payload = json.dumps({"event": "spawn", "agent_id": "alpha"}) + "\n"
    client.sendall(payload.encode("utf-8"))
    
    loop = GLib.MainLoop()
    # Timeout failsafe
    GLib.timeout_add(1000, loop.quit)
    loop.run()
    
    server.stop()
    client.close()

    assert len(received_messages) == 1
    assert received_messages[0] == {"event": "spawn", "agent_id": "alpha"}
```

- [ ] **Step 2: Run test to verify it fails**

Run: `pytest tests/test_ipc_server.py -v`
Expected: FAIL avec `ModuleNotFoundError: No module named 'core.ipc_server'`

- [ ] **Step 3: Write minimal implementation**

```python
# core/ipc_server.py
import socket
import json
import os
from gi.repository import GLib

class IpcServer:
    def __init__(self, socket_path: str):
        self.socket_path = socket_path
        self.server_socket = None
        self.callback = None
        self.watch_ids = []

    def set_callback(self, callback):
        self.callback = callback

    def start(self):
        if os.path.exists(self.socket_path):
            os.remove(self.socket_path)
            
        self.server_socket = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
        self.server_socket.bind(self.socket_path)
        self.server_socket.listen(5)
        self.server_socket.setblocking(False)
        
        watch_id = GLib.io_add_watch(self.server_socket.fileno(), GLib.IO_IN, self._on_accept)
        self.watch_ids.append(watch_id)

    def _on_accept(self, fd, condition):
        try:
            client_sock, _ = self.server_socket.accept()
            client_sock.setblocking(False)
            watch_id = GLib.io_add_watch(client_sock.fileno(), GLib.IO_IN, self._on_read, client_sock)
            self.watch_ids.append(watch_id)
        except BlockingIOError:
            pass
        return True # Keep listening

    def _on_read(self, fd, condition, client_sock):
        try:
            data = client_sock.recv(4096)
            if not data:
                return False # Close connection
            
            if self.callback:
                for line in data.decode("utf-8").strip().split("\n"):
                    if line:
                        try:
                            msg = json.loads(line)
                            self.callback(msg)
                        except json.JSONDecodeError:
                            pass
        except BlockingIOError:
            return True
        except ConnectionResetError:
            return False
            
        return True # Keep connection alive

    def stop(self):
        for watch_id in self.watch_ids:
            GLib.source_remove(watch_id)
        self.watch_ids.clear()
        
        if self.server_socket:
            self.server_socket.close()
            self.server_socket = None
            
        if os.path.exists(self.socket_path):
            os.remove(self.socket_path)
```

- [ ] **Step 4: Run test to verify it passes**

Run: `pytest tests/test_ipc_server.py -v`
Expected: PASS

- [ ] **Step 5: Commit**

```bash
git add tests/test_ipc_server.py core/ipc_server.py
git commit -m "feat: IPC server for JSON messages integrated with GLib"
```

---

### Task 2: Initialisation de la Fenêtre Principale et Point d'Entrée (`ui/window.py`, `main.py`)

**Files:**
- Create: `ui/__init__.py`
- Create: `ui/window.py`
- Create: `main.py`
- Create: `tests/test_window.py`

- [ ] **Step 1: Write the failing test**

```python
# tests/test_window.py
import pytest
import gi
gi.require_version('Gtk', '4.0')
gi.require_version('Adw', '1')
from gi.repository import Gtk, Adw
from ui.window import MainWindow

@pytest.fixture(autouse=True)
def init_adw():
    Adw.init()

def test_main_window_instantiation():
    app = Adw.Application(application_id="org.gemini.GuiOrchestrator")
    app.register()
    
    window = MainWindow(application=app)
    
    assert window.get_title() == "Gemini GUI Orchestrator"
    assert isinstance(window, Adw.ApplicationWindow)
```

- [ ] **Step 2: Run test to verify it fails**

Run: `xvfb-run -a pytest tests/test_window.py -v` (xvfb-run requis pour GTK en CI/headless)
Expected: FAIL avec `ModuleNotFoundError: No module named 'ui'`

- [ ] **Step 3: Write minimal implementation**

```python
# ui/__init__.py
# (Empty file)
```

```python
# ui/window.py
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
```

```python
# main.py
import sys
import gi
gi.require_version('Gtk', '4.0')
gi.require_version('Adw', '1')
from gi.repository import Gtk, Adw, Gio
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
    app = GeminiGuiApp()
    sys.exit(app.run(sys.argv))
```

- [ ] **Step 4: Run test to verify it passes**

Run: `xvfb-run -a pytest tests/test_window.py -v`
Expected: PASS

- [ ] **Step 5: Commit**

```bash
git add ui/ tests/test_window.py main.py
git commit -m "feat: initial Adw.Application entry point and MainWindow structure"
```

---

### Task 3: Composant Terminal Pane (`ui/components/terminal_pane.py`)

**Files:**
- Create: `ui/components/__init__.py`
- Create: `ui/components/terminal_pane.py`
- Create: `tests/test_terminal_pane.py`

- [ ] **Step 1: Write the failing test**

```python
# tests/test_terminal_pane.py
import pytest
import gi
gi.require_version('Gtk', '4.0')
gi.require_version('Adw', '1')
gi.require_version('Vte', '3.91') # Note: VTE4 uses 3.91 API in GTK4
from gi.repository import Gtk, Adw, Vte
from ui.components.terminal_pane import TerminalPane

@pytest.fixture(autouse=True)
def init_adw():
    Adw.init()

def test_terminal_pane_instantiation():
    pane = TerminalPane()
    assert isinstance(pane, Gtk.Overlay)
    
    # Vérifier que le composant a un Vte.Terminal enfant
    terminal_found = False
    child = pane.get_first_child()
    while child is not None:
        if isinstance(child, Vte.Terminal):
            terminal_found = True
            break
        child = child.get_next_sibling()
        
    assert terminal_found, "Vte.Terminal should be embedded inside TerminalPane"
```

- [ ] **Step 2: Run test to verify it fails**

Run: `xvfb-run -a pytest tests/test_terminal_pane.py -v`
Expected: FAIL avec `ModuleNotFoundError: No module named 'ui.components.terminal_pane'`

- [ ] **Step 3: Write minimal implementation**

```python
# ui/components/__init__.py
# (Empty file)
```

```python
# ui/components/terminal_pane.py
import gi
gi.require_version('Gtk', '4.0')
gi.require_version('Vte', '3.91')
from gi.repository import Gtk, Vte

class TerminalPane(Gtk.Overlay):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        
        # Initialisation du VTE Terminal
        self.terminal = Vte.Terminal()
        self.terminal.set_hexpand(True)
        self.terminal.set_vexpand(True)
        
        self.set_child(self.terminal)
        
        # Bouton Zoom Focus Mode (stub pour la logique de focus)
        self.zoom_button = Gtk.Button(icon_name="view-fullscreen-symbolic")
        self.zoom_button.set_halign(Gtk.Align.END)
        self.zoom_button.set_valign(Gtk.Align.START)
        self.zoom_button.set_margin_top(8)
        self.zoom_button.set_margin_end(8)
        
        self.add_overlay(self.zoom_button)
```

- [ ] **Step 4: Run test to verify it passes**

Run: `xvfb-run -a pytest tests/test_terminal_pane.py -v`
Expected: PASS

- [ ] **Step 5: Commit**

```bash
git add ui/components/ tests/test_terminal_pane.py
git commit -m "feat: VTE terminal pane component with overlay zoom button"
```
