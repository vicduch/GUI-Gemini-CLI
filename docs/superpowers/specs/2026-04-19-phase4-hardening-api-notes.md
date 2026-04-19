# Phase 4 Hardening - API Notes

Date: 2026-04-19

## Core

### `core.process_manager`

- Added explicit process state machine via `ProcessState`:
  - `starting`, `running`, `stopping`, `stopped`, `failed`.
- Added typed payloads:
  - `ProcessInfo`
  - `ProcessEvent`
- `ProcessManager` is now production-ready:
  - `spawn(session_id, command)`
  - `stop(session_id, timeout_ms=None)` with SIGTERM then SIGKILL timeout fallback.
  - `hot_reload(session_id, command, timeout_ms=None)` preserving `session_id`.
  - `stop_all()`
  - `set_event_callback(callback)`
- Lifecycle is non-blocking and GLib-driven (`spawn_async`, `child_watch_add`, `timeout_add`).

### `core.ipc_server`

- Hardened callback execution (`try/except`) so callback failures no longer break reads.
- Added explicit IO condition handling:
  - `GLib.IO_HUP`
  - `GLib.IO_ERR`
  - `GLib.IO_NVAL`
- Added cleanup guarantees for all error/stop paths.
- `stop()` is idempotent.
- Added typed client metadata and structured logging.

### `core.logging_utils`

- New centralized logging helpers:
  - `configure_logging(level=...)`
  - `get_logger(name, **context)`
- Added context adapter for `session_id`, `process_pid`, `agent_id`.

## UI

### `ui.views.workspace`

- Added robust `Workspace` (`Gtk.Stack`) with explicit APIs:
  - `add_pane(pane)`
  - `remove_pane(pane)`
  - `focus_pane(pane)`
  - `unfocus_pane()`
- Focus/Grid lifecycle hardened:
  - typed `pane_positions` mapping
  - transition guards
  - idempotent focus/unfocus
  - pane signal cleanup
- Focus size margins now computed proportionally (target ~90% visible pane area).

### `ui.components.terminal_pane`

- Added injectable `terminal_factory` for safer headless testing and test isolation.

### `ui.window`

- Integrates `Workspace` directly.
- Supports `terminal_factory` injection to build deterministic test windows without VTE dependency.
