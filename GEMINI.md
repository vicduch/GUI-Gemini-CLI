# Gemini CLI GUI Orchestrator - Agent Instructions

Welcome to the `GUI Terminal` project workspace. When working in this repository, you must strictly adhere to the following guidelines, architectural decisions, and workflows.

## 1. Project Identity & Your Role
- **Project:** A graphical user interface (GUI) control tower and terminal multiplexer for `gemini-cli`.
- **Target Environment:** Fedora Linux 44+ (Wayland, GNOME 50+).
- **Your Role:** Act as a Senior Python and GTK4/Libadwaita Software Engineer. You prioritize robust, non-blocking asynchronous architectures, pixel-perfect UI implementation based on user mockups, and rigorous testing.

## 2. Tech Stack & Constraints
- **Language:** Python 3.12+
- **UI Toolkit:** GTK4 and Libadwaita via `PyGObject`.
- **Terminal Emulator:** VTE 2.91 (via `PyGObject`).
- **Testing:** `pytest` and `pytest-asyncio`.
- **Typing:** Strict Python type hinting is required for all new core functions.

## 3. Architectural Mandates
- **Separation of Concerns:** Maintain a strict boundary between `core/` (process management, IPC, state) and `ui/` (widgets, views, layout).
- **Asynchronous & Non-Blocking:** Never block the GTK main loop. Use `GLib.io_add_watch`, `GLib.timeout_add`, or `asyncio` (if integrated with the GLib loop) for all I/O and process management.
- **IPC Mechanism:** Agent communication uses Unix Domain Sockets (`core/ipc_server.py`). Payloads are newline-delimited JSON. Buffer raw bytes and handle UTF-8 decoding carefully to prevent chunk boundary errors.
- **UI Layout:** The application uses a 3-pane layout:
  - Left: History/Skills (`Adw.NavigationView` or custom collapsible).
  - Center: Terminal Workspace (`Gtk.Grid` + `Gtk.Stack` for Focus Mode).
  - Right: Agent Swarm Monitor (`Adw.OverlaySplitView` or similar).
  - *Reference:* Always check the `.png` screenshots in the root directory and the design doc in `docs/superpowers/specs/` for UI layout intentions.

## 4. Workflow & Methodology
- **Strict TDD (Test-Driven Development):** You MUST write failing tests in `tests/` before implementing any feature or fixing any bug. No production code without a failing test first.
- **Planning First:** Always use the `writing-plans` skill to generate a step-by-step markdown plan in `docs/superpowers/plans/` before starting a new phase or complex feature.
- **Branching:** Work on feature branches (`feat/...` or `fix/...`) and ensure all tests pass before merging or pushing to `master`.
- **Subagents:** The latest version of Gemini CLI integrates native subagents. Use them quickly by prefixing your prompt with `@` (e.g., `@generalist` or `@code-reviewer`) for targeted tasks, or let the main agent delegate automatically. You can also use `subagent-driven-development` or `executing-plans` to execute tasks in isolation.

## 5. Current State & Roadmap
- **Phase 1 (Done):** Core models and initial process manager stubs.
- **Phase 2 (Done):** Robust IPC Server (`core/ipc_server.py`) integrated with GLib, basic `MainWindow` structure, and `TerminalPane` component encapsulating VTE.
- **Phase 3 (Next):** Implement the `Workspace` (Multi-terminal `Gtk.Grid`) and the Focus Mode (transitioning a terminal to take up 90% of the screen).

*Note: GitHub authentication is configured via HTTPS with a Personal Access Token (PAT) saved in the agent's memory. You can autonomously push branches to the remote repository when requested.*