from __future__ import annotations

import os
import signal
from dataclasses import dataclass
from enum import IntFlag
from typing import Any

import pytest

import core.process_manager as process_manager_module
from core.process_manager import ProcessManager, ProcessState


class _FakeSpawnFlags(IntFlag):
    SEARCH_PATH = 1
    DO_NOT_REAP_CHILD = 2


@dataclass(slots=True)
class _RegisteredWatch:
    pid: int
    callback: Any
    data: tuple[Any, ...]


@dataclass(slots=True)
class _RegisteredTimeout:
    callback: Any
    data: tuple[Any, ...]


class _FakeGLib:
    PRIORITY_DEFAULT = 0
    SpawnFlags = _FakeSpawnFlags

    def __init__(self) -> None:
        self._next_pid = 1000
        self._next_source_id = 1
        self.watches: dict[int, _RegisteredWatch] = {}
        self.timeouts: dict[int, _RegisteredTimeout] = {}
        self.closed_pids: list[int] = []
        self.removed_sources: list[int] = []

    def spawn_async(
        self,
        argv: list[str],
        envp: list[str] | None = None,
        working_directory: str | None = None,
        flags: int = 0,
        child_setup: Any = None,
        user_data: Any = None,
        standard_input: bool | int | None = None,
        standard_output: bool | int | None = None,
        standard_error: bool | int | None = None,
    ) -> tuple[int, int, int, int]:
        del envp, working_directory, flags, child_setup, user_data
        del standard_input, standard_output, standard_error
        if not argv:
            raise RuntimeError("argv cannot be empty")
        pid = self._next_pid
        self._next_pid += 1
        return pid, -1, -1, -1

    def child_watch_add(self, priority: int, pid: int, function: Any, *data: Any) -> int:
        del priority
        source_id = self._next_source_id
        self._next_source_id += 1
        self.watches[source_id] = _RegisteredWatch(pid=pid, callback=function, data=data)
        return source_id

    def timeout_add(self, interval_ms: int, function: Any, *data: Any) -> int:
        del interval_ms
        source_id = self._next_source_id
        self._next_source_id += 1
        self.timeouts[source_id] = _RegisteredTimeout(callback=function, data=data)
        return source_id

    def source_remove(self, source_id: int) -> bool:
        removed = False
        if source_id in self.timeouts:
            self.timeouts.pop(source_id)
            removed = True
        if source_id in self.watches:
            self.watches.pop(source_id)
            removed = True
        self.removed_sources.append(source_id)
        return removed

    def spawn_close_pid(self, pid: int) -> None:
        self.closed_pids.append(pid)

    def trigger_exit(self, pid: int, status: int) -> None:
        for source_id, watch in list(self.watches.items()):
            if watch.pid == pid:
                watch.callback(pid, status, *watch.data)
                self.watches.pop(source_id, None)
                return
        raise AssertionError(f"No child watch found for pid={pid}")

    def trigger_timeout(self, source_id: int) -> None:
        timeout = self.timeouts.pop(source_id)
        timeout.callback(*timeout.data)


@pytest.fixture
def fake_glib(monkeypatch: pytest.MonkeyPatch) -> _FakeGLib:
    fake = _FakeGLib()
    monkeypatch.setattr(process_manager_module, "GLib", fake)
    return fake


@pytest.fixture
def recorded_signals(monkeypatch: pytest.MonkeyPatch) -> list[tuple[int, int]]:
    emitted: list[tuple[int, int]] = []

    def _fake_kill(pid: int, sig: int) -> None:
        emitted.append((pid, sig))

    monkeypatch.setattr(os, "kill", _fake_kill)
    monkeypatch.setattr(os, "set_blocking", lambda fd, flag: None)
    return emitted


def test_spawn_sets_running_state(fake_glib: _FakeGLib) -> None:
    manager = ProcessManager()
    process = manager.spawn("session-1", ["gemini", "--model", "pro"])

    assert process.session_id == "session-1"
    assert process.state is ProcessState.RUNNING
    assert process.pid == 1000
    assert process.watch_id is not None
    assert manager.processes["session-1"].state is ProcessState.RUNNING


def test_stop_graceful_before_timeout(
    fake_glib: _FakeGLib, recorded_signals: list[tuple[int, int]]
) -> None:
    manager = ProcessManager(stop_timeout_ms=50)
    process = manager.spawn("session-1", ["gemini"])
    pid = process.pid

    manager.stop("session-1")
    fake_glib.trigger_exit(process.pid or 0, 0)

    assert recorded_signals[0] == (pid, signal.SIGTERM)
    assert manager.processes["session-1"].state is ProcessState.STOPPED
    assert manager.processes["session-1"].stop_timeout_id is None


def test_stop_forces_sigkill_after_timeout(
    fake_glib: _FakeGLib, recorded_signals: list[tuple[int, int]]
) -> None:
    manager = ProcessManager(stop_timeout_ms=50)
    process = manager.spawn("session-2", ["gemini"])
    pid = process.pid

    manager.stop("session-2")
    timeout_id = manager.processes["session-2"].stop_timeout_id
    assert timeout_id is not None
    fake_glib.trigger_timeout(timeout_id)
    fake_glib.trigger_exit(process.pid or 0, 9)

    assert recorded_signals[0] == (pid, signal.SIGTERM)
    assert recorded_signals[1] == (pid, signal.SIGKILL)
    assert manager.processes["session-2"].state is ProcessState.STOPPED


def test_hot_reload_preserves_session_identity(
    fake_glib: _FakeGLib, recorded_signals: list[tuple[int, int]]
) -> None:
    manager = ProcessManager(stop_timeout_ms=50)
    first = manager.spawn("session-3", ["gemini", "--model", "a"])
    first_pid = first.pid

    manager.hot_reload("session-3", ["gemini", "--model", "b"])
    fake_glib.trigger_exit(first.pid or 0, 0)

    second = manager.processes["session-3"]
    assert second.session_id == "session-3"
    assert second.command == ("gemini", "--model", "b")
    assert second.state is ProcessState.RUNNING
    assert second.pid != first_pid
    assert recorded_signals[0] == (first_pid, signal.SIGTERM)


def test_process_crash_marks_failed(fake_glib: _FakeGLib) -> None:
    manager = ProcessManager()
    process = manager.spawn("session-4", ["gemini"])

    fake_glib.trigger_exit(process.pid or 0, 1)

    assert manager.processes["session-4"].state is ProcessState.FAILED
