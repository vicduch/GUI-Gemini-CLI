from __future__ import annotations

import json
import os
import socket
import uuid
from collections.abc import Callable
from pathlib import Path
from typing import Any

import pytest
from gi.repository import GLib

from core.ipc_server import IpcServer


def _run_loop_until(predicate: Callable[[], bool], timeout_ms: int = 1200) -> None:
    loop = GLib.MainLoop()
    timed_out = {"value": False}

    def _poll() -> bool:
        if predicate():
            loop.quit()
            return False
        return True

    def _timeout() -> bool:
        timed_out["value"] = True
        loop.quit()
        return False

    GLib.timeout_add(10, _poll)
    GLib.timeout_add(timeout_ms, _timeout)
    loop.run()
    assert not timed_out["value"], "main loop timed out"


@pytest.fixture
def socket_path(tmp_path: Path) -> str:
    # Use tmp_path to ensure a shorter path and automatic cleanup
    return str(tmp_path / f"t_{uuid.uuid4().hex[:8]}.sock")


@pytest.fixture
def server(socket_path: str) -> IpcServer:
    srv = IpcServer(socket_path)
    srv.start()
    try:
        yield srv
    finally:
        srv.stop()


def _connect(socket_path: str) -> socket.socket:
    client = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
    client.connect(socket_path)
    return client


def _send_json(client: socket.socket, payload: dict[str, Any]) -> None:
    client.sendall((json.dumps(payload, ensure_ascii=False) + "\n").encode("utf-8"))


def test_ipc_server_receives_message(server: IpcServer, socket_path: str) -> None:
    received: list[dict[str, Any]] = []
    server.set_callback(received.append)

    client = _connect(socket_path)
    _send_json(client, {"event": "spawn", "agent_id": "alpha"})
    _run_loop_until(lambda: len(received) == 1)
    client.close()

    assert received == [{"event": "spawn", "agent_id": "alpha"}]


def test_ipc_server_handles_callback_exception_and_keeps_running(
    server: IpcServer, socket_path: str
) -> None:
    callback_count = 0
    received: list[dict[str, Any]] = []

    def _callback(msg: dict[str, Any]) -> None:
        nonlocal callback_count
        callback_count += 1
        received.append(msg)
        if callback_count == 1:
            raise RuntimeError("boom")

    server.set_callback(_callback)
    client = _connect(socket_path)

    _send_json(client, {"event": "first"})
    _send_json(client, {"event": "second"})
    _run_loop_until(lambda: callback_count == 2)
    client.close()

    assert received == [{"event": "first"}, {"event": "second"}]


def test_ipc_server_handles_utf8_chunk_boundaries(server: IpcServer, socket_path: str) -> None:
    received: list[dict[str, Any]] = []
    server.set_callback(received.append)

    client = _connect(socket_path)
    payload = json.dumps({"event": "spawn", "agent_id": "alpha 🌟"}, ensure_ascii=False) + "\n"
    payload_bytes = payload.encode("utf-8")
    split_point = payload_bytes.find(b"\xf0\x9f\x8c\x9f") + 2

    client.sendall(payload_bytes[:split_point])
    client.sendall(payload_bytes[split_point:])
    _run_loop_until(lambda: len(received) == 1)
    client.close()

    assert received == [{"event": "spawn", "agent_id": "alpha 🌟"}]


def test_ipc_server_survives_invalid_utf8_and_json(server: IpcServer, socket_path: str) -> None:
    received: list[dict[str, Any]] = []
    server.set_callback(received.append)

    client = _connect(socket_path)
    client.sendall(b"\xff\xff\xff\n")
    client.sendall(b"{bad-json}\n")
    _send_json(client, {"event": "healthy"})
    _run_loop_until(lambda: len(received) == 1)
    client.close()

    assert received == [{"event": "healthy"}]


def test_ipc_server_cleans_up_hup_and_err_conditions(server: IpcServer, socket_path: str) -> None:
    server.set_callback(lambda _: None)
    client = _connect(socket_path)
    _run_loop_until(lambda: len(server.clients) == 1)

    client_fd = next(iter(server.clients))
    assert server._on_read(client_fd, GLib.IO_HUP, client_fd) is False
    assert client_fd not in server.clients

    client2 = _connect(socket_path)
    _run_loop_until(lambda: len(server.clients) == 1)
    client_fd2 = next(iter(server.clients))
    assert server._on_read(client_fd2, GLib.IO_ERR, client_fd2) is False
    assert client_fd2 not in server.clients

    client.close()
    client2.close()


def test_ipc_server_stop_is_idempotent(socket_path: str) -> None:
    srv = IpcServer(socket_path)
    srv.start()

    client = _connect(socket_path)
    _run_loop_until(lambda: len(srv.clients) == 1)

    srv.stop()
    srv.stop()
    client.close()

    assert srv.server_socket is None
    assert srv.server_watch_id is None
    assert srv.clients == {}
    assert not os.path.exists(socket_path)


def test_ipc_server_multi_clients_fragmentation(server: IpcServer, socket_path: str) -> None:
    received: list[dict[str, Any]] = []
    server.set_callback(received.append)

    client_a = _connect(socket_path)
    client_b = _connect(socket_path)

    payload_a1 = (json.dumps({"agent_id": "a1"}) + "\n").encode("utf-8")
    payload_a2 = (json.dumps({"agent_id": "a2"}) + "\n").encode("utf-8")
    payload_b1 = (json.dumps({"agent_id": "b1"}) + "\n").encode("utf-8")
    payload_b2 = (json.dumps({"agent_id": "b2"}) + "\n").encode("utf-8")

    client_a.sendall(payload_a1[:5])
    client_b.sendall(payload_b1[:7])
    client_a.sendall(payload_a1[5:] + payload_a2)
    client_b.sendall(payload_b1[7:] + payload_b2)

    _run_loop_until(lambda: len(received) == 4, timeout_ms=1500)
    client_a.close()
    client_b.close()

    ids = sorted(msg["agent_id"] for msg in received)
    assert ids == ["a1", "a2", "b1", "b2"]


def test_ipc_server_abrupt_client_close_is_cleaned(server: IpcServer, socket_path: str) -> None:
    server.set_callback(lambda _: None)
    client = _connect(socket_path)
    _run_loop_until(lambda: len(server.clients) == 1)

    client.close()
    _run_loop_until(lambda: len(server.clients) == 0)

    assert server.clients == {}


def test_ipc_server_accept_terminal_condition_stops_server(socket_path: str) -> None:
    srv = IpcServer(socket_path)
    srv.start()

    assert srv.server_socket is not None
    server_fd = srv.server_socket.fileno()
    assert srv._on_accept(server_fd, GLib.IO_NVAL) is False

    assert srv.server_socket is None
    assert srv.server_watch_id is None
