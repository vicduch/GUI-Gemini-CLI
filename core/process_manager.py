from __future__ import annotations

import os
import signal
from collections.abc import Callable
from dataclasses import dataclass
from enum import StrEnum
from typing import Any

from gi.repository import GLib

from core.logging_utils import get_logger

logger = get_logger(__name__)


class ProcessState(StrEnum):
    STARTING = "starting"
    RUNNING = "running"
    STOPPING = "stopping"
    STOPPED = "stopped"
    FAILED = "failed"


@dataclass(slots=True)
class ProcessInfo:
    session_id: str
    command: tuple[str, ...]
    correlation_id: str = ""
    state: ProcessState = ProcessState.STARTING
    pid: int | None = None
    stdin_fd: int | None = None
    stdout_fd: int | None = None
    stderr_fd: int | None = None
    watch_id: int | None = None
    stop_timeout_id: int | None = None
    pending_command: tuple[str, ...] | None = None
    last_exit_status: int | None = None
    last_error: str | None = None


@dataclass(frozen=True, slots=True)
class ProcessEvent:
    session_id: str
    event: str
    state: ProcessState
    pid: int | None
    correlation_id: str = ""
    message: str | None = None
    exit_status: int | None = None
    error_contract: dict[str, Any] | None = None


class ProcessManager:
    def __init__(self, stop_timeout_ms: int = 3000) -> None:
        self.stop_timeout_ms = stop_timeout_ms
        self.processes: dict[str, ProcessInfo] = {}
        self._event_callback: Callable[[ProcessEvent], None] | None = None
        self._spawn_flags = int(GLib.SpawnFlags.SEARCH_PATH | GLib.SpawnFlags.DO_NOT_REAP_CHILD)

    def set_event_callback(self, callback: Callable[[ProcessEvent], None] | None) -> None:
        self._event_callback = callback

    def spawn(self, session_id: str, command: list[str]) -> ProcessInfo:
        if not command:
            raise ValueError("command cannot be empty")

        existing = self.processes.get(session_id)
        if existing and existing.state in (
            ProcessState.STARTING,
            ProcessState.RUNNING,
            ProcessState.STOPPING,
        ):
            raise RuntimeError(f"session {session_id!r} is already active")

        process = existing or ProcessInfo(session_id=session_id, command=tuple(command))
        process.command = tuple(command)
        process.state = ProcessState.STARTING
        process.last_error = None
        process.pending_command = None
        self.processes[session_id] = process
        self._emit_event(process, "starting")

        try:
            pid, stdin_fd, stdout_fd, stderr_fd = GLib.spawn_async(  # type: ignore[no-untyped-call]
                argv=list(command),
                flags=self._spawn_flags,
                standard_input=True,
                standard_output=True,
                standard_error=True,
            )
        except Exception as exc:
            process.state = ProcessState.FAILED
            process.last_error = str(exc)
            self._emit_event(process, "spawn_failed", message=process.last_error)
            raise

        process.pid = pid
        process.stdin_fd = stdin_fd
        process.stdout_fd = stdout_fd
        process.stderr_fd = stderr_fd
        self._set_non_blocking(stdin_fd, stdout_fd, stderr_fd)
        process.watch_id = GLib.child_watch_add(  # type: ignore[no-untyped-call]
            GLib.PRIORITY_DEFAULT,
            pid,
            self._on_child_exit,
            session_id,
        )
        process.state = ProcessState.RUNNING
        self._emit_event(process, "running")
        return process

    def stop(self, session_id: str, timeout_ms: int | None = None) -> bool:
        process = self.processes.get(session_id)
        if process is None:
            return False
        if process.state in (ProcessState.STOPPED, ProcessState.FAILED):
            return False
        if process.state is ProcessState.STOPPING:
            return True

        process.state = ProcessState.STOPPING
        self._emit_event(process, "stopping")

        if process.pid is None:
            process.state = ProcessState.STOPPED
            self._emit_event(process, "stopped")
            return True

        try:
            os.kill(process.pid, signal.SIGTERM)
        except ProcessLookupError:
            self._close_spawn_pid(process.pid)
            self._remove_child_watch(process)
            self._finalize_exit(process, 0, was_stopping=True)
            self._restart_if_pending(session_id)
            return True
        except OSError as exc:
            process.state = ProcessState.FAILED
            process.last_error = str(exc)
            self._emit_event(process, "stop_failed", message=process.last_error)
            return False

        timeout = timeout_ms if timeout_ms is not None else self.stop_timeout_ms
        process.stop_timeout_id = GLib.timeout_add(timeout, self._on_stop_timeout, session_id)
        return True

    def hot_reload(
        self,
        session_id: str,
        command: list[str],
        timeout_ms: int | None = None,
    ) -> bool:
        if not command:
            raise ValueError("command cannot be empty")

        process = self.processes.get(session_id)
        if process is None:
            self.spawn(session_id, command)
            return True

        process.pending_command = tuple(command)
        if process.state in (ProcessState.STOPPED, ProcessState.FAILED) or process.pid is None:
            self._restart_if_pending(session_id)
            return True

        return self.stop(session_id, timeout_ms=timeout_ms)

    def restart_with_model(self, session_id: str, model_name: str) -> bool:
        """Helper to hot-reload a session with a different model."""
        process = self.processes.get(session_id)
        if not process:
            return False
            
        # Reconstruct command with new model
        # Assuming command[0] is the executable and we want to replace or add --model
        new_command = list(process.command)
        
        # Simple heuristic: if --model exists, replace its next arg. Else append.
        try:
            idx = new_command.index("--model")
            if idx + 1 < len(new_command):
                new_command[idx + 1] = model_name
            else:
                new_command.append(model_name)
        except ValueError:
            new_command.extend(["--model", model_name])
            
        return self.hot_reload(session_id, new_command)

    def stop_all(self) -> None:
        for session_id in list(self.processes):
            self.stop(session_id)

    def _on_stop_timeout(self, session_id: str) -> bool:
        process = self.processes.get(session_id)
        if process is None:
            return False
        process.stop_timeout_id = None

        if process.state is not ProcessState.STOPPING or process.pid is None:
            return False

        try:
            os.kill(process.pid, signal.SIGKILL)
            self._emit_event(process, "force_kill")
        except ProcessLookupError:
            logger.debug("pid %s already gone during force kill", process.pid)
        except OSError as exc:
            process.state = ProcessState.FAILED
            process.last_error = str(exc)
            self._emit_event(process, "kill_failed", message=process.last_error)
        return False

    def _on_child_exit(self, pid: int, status: int, session_id: str) -> None:
        process = self.processes.get(session_id)
        GLib.spawn_close_pid(pid)
        if process is None:
            return
        if process.pid is None:
            return
        if process.pid != pid:
            return

        was_stopping = process.state is ProcessState.STOPPING
        self._finalize_exit(process, status, was_stopping=was_stopping)
        self._restart_if_pending(session_id)

    def _restart_if_pending(self, session_id: str) -> None:
        process = self.processes.get(session_id)
        if process is None or process.pending_command is None:
            return

        pending = list(process.pending_command)
        process.pending_command = None
        self._emit_event(process, "restarting")
        self.spawn(session_id, pending)

    def _finalize_exit(self, process: ProcessInfo, status: int, *, was_stopping: bool) -> None:
        process.last_exit_status = status
        self._cancel_timeout(process)
        self._close_stream_fds(process)
        process.pid = None
        process.watch_id = None

        if was_stopping:
            process.state = ProcessState.STOPPED
            self._emit_event(process, "stopped", exit_status=status)
        else:
            process.state = ProcessState.FAILED
            self._emit_event(process, "failed", exit_status=status)

    def _cancel_timeout(self, process: ProcessInfo) -> None:
        if process.stop_timeout_id is None:
            return
        GLib.source_remove(process.stop_timeout_id)
        process.stop_timeout_id = None

    def _remove_child_watch(self, process: ProcessInfo) -> None:
        if process.watch_id is None:
            return
        try:
            GLib.source_remove(process.watch_id)
        except Exception:
            logger.debug("failed to remove child watch source_id=%s", process.watch_id)
        process.watch_id = None

    def _close_stream_fds(self, process: ProcessInfo) -> None:
        for attr in ("stdin_fd", "stdout_fd", "stderr_fd"):
            fd = getattr(process, attr)
            if fd is None:
                continue
            try:
                os.close(fd)
            except OSError:
                pass
            setattr(process, attr, None)

    def _close_spawn_pid(self, pid: int | None) -> None:
        if pid is None:
            return
        try:
            GLib.spawn_close_pid(pid)
        except Exception:
            logger.debug("failed to close spawn pid=%s", pid)

    def _set_non_blocking(self, stdin_fd: int, stdout_fd: int, stderr_fd: int) -> None:
        for fd in (stdin_fd, stdout_fd, stderr_fd):
            if fd is None or fd < 0:
                continue
            try:
                os.set_blocking(fd, False)
            except OSError:
                logger.debug("failed to set non-blocking fd=%s", fd)

    def _emit_event(
        self,
        process: ProcessInfo,
        event: str,
        *,
        message: str | None = None,
        exit_status: int | None = None,
        error_contract: dict[str, Any] | None = None,
    ) -> None:
        if self._event_callback is None:
            return
        payload = ProcessEvent(
            session_id=process.session_id,
            event=event,
            state=process.state,
            pid=process.pid,
            correlation_id=process.correlation_id,
            message=message,
            exit_status=exit_status,
            error_contract=error_contract,
        )
        try:
            self._event_callback(payload)
        except Exception:
            logger.exception("process manager event callback failed")
