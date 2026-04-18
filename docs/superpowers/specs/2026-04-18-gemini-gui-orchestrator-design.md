# Gemini CLI GUI Orchestrator - Design Document
**Date:** 2026-04-18

## 1. Contexte et Objectif
Développer une application graphique GTK4 (Libadwaita) pour Linux GNOME 50+ / Wayland. Elle sert de "Tour de contrôle" pour `gemini-cli`, permettant la gestion des historiques de session, l'orchestration dynamique des modèles (Hot-Reload), le monitoring des sous-agents via IPC, et le multiplexage de terminaux embarqués avec un mode Focus.

## 2. Architecture Globale
L'application suit une structure modulaire, séparant clairement la logique de gestion des processus/IPC (Core) et l'interface utilisateur (UI).

```text
gemini-gui-orchestrator/
│
├── main.py                   # Point d'entrée (Adw.Application)
├── core/
│   ├── config_manager.py     # Gestion des préférences, clés API (Settings)
│   ├── process_manager.py    # Cycle de vie gemini-cli (spawn, kill, hot-reload) via GLib
│   ├── ipc_server.py         # Serveur Unix Socket intégré à GLib (io_add_watch)
│   └── models.py             # Dataclasses (Session, Agent)
│
├── ui/
│   ├── window.py             # Adw.ApplicationWindow principale
│   ├── components/           # Composants réutilisables (TerminalPane, etc.)
│   │   └── terminal_pane.py  # Gtk.Overlay + Vte.Terminal + Zoom button
│   └── views/
│       ├── sidebar.py        # Adw.NavigationView (Historiques / Hub Skills)
│       ├── right_sidebar.py  # Adw.OverlaySplitView (Moniteur d'agents)
│       └── workspace.py      # TerminalGrid (Gtk.Grid) + Gtk.Stack (Focus Mode)
│
├── assets/
│   └── style.css             # Libadwaita custom overrides
└── requirements.txt          # Dépendances Python (PyGObject, pytest)
```

## 3. Composants et Flux de Données (Data Flow)

### 3.1 UI Layout
- **Sidebar Gauche (History & Skills):** Une liste (`Gtk.ListView` via `Gio.ListStore`) affiche l'historique des sessions. Les badges de modèles permettent le Hot-Reload via un `Gtk.DropDown`.
- **Zone Centrale (Workspace):** Un multiplexeur de terminaux (`Gtk.Grid`). Un terminal peut passer en plein écran (Focus Mode) via un `Gtk.Stack` qui masque la grille et affiche le terminal seul.
- **Sidebar Droite (Agent Monitor):** Un `Gtk.TreeView` affiche l'état en temps réel des sous-agents de la session active (Master Agent, Sub-agents).

### 3.2 Core Logic (Process & IPC)
- **Process Management:** `core/process_manager.py` utilise `GLib.spawn_async_with_pipes` pour instancier les processus `gemini-cli`. Pour le Hot-Reload, il envoie un signal SIGTERM au processus, attend la fermeture gracieuse (timeout 3s suivi d'un SIGKILL), modifie la commande de lancement (ex: `--model gemini-3.1-pro`) et relance le processus avec l'ID de session.
- **IPC Server (Agent Swarm):** `core/ipc_server.py` crée un socket Unix (`/tmp/gemini-gui-<pid>.sock`). Le serveur utilise `GLib.io_add_watch` pour lire les trames JSON (ex: `{"event": "spawn", "agent_id": "alpha"}`) de façon asynchrone dans la boucle d'événements GTK. Ces événements sont dispatchés vers `ui/views/right_sidebar.py` pour mettre à jour l'arbre des agents.

## 4. Gestion des Erreurs
- **Crash du Processus CLI:** Si un processus `gemini-cli` quitte de façon inattendue, le `TerminalPane` affiche un `Adw.Toast` ("Process exited with code X") et un bouton de redémarrage.
- **Timeout IPC:** Si un sous-agent déclaré dans l'IPC ne donne plus de nouvelles dans le délai défini par le CLI, la Sidebar Droite met à jour l'icône de l'agent (Warning).
- **Hot-Reload Failsafe:** Le Hot-Reload garantit la fermeture des terminaux existants. Si le processus est zombie, le `ProcessManager` force le SIGKILL après un timeout de 3 secondes avant de relancer.

## 5. Tests et Validation
- **Unit Testing (Core):** `pytest` est utilisé pour tester `process_manager.py` et `ipc_server.py`. Un script fantôme (`mock_cli.py`) simulera l'envoi de messages JSON dans le socket Unix.
- **UI Testing:** Vérification de l'instanciation correcte des fenêtres (`Adw.ApplicationWindow`) et du Focus Mode dans un environnement Wayland headless (ou via `xvfb-run`).

## 6. Dépendances
- Python 3.12+
- `PyGObject` (bindings GTK4, Libadwaita, Vte-2.91)
- `pytest` (pour l'environnement de test)