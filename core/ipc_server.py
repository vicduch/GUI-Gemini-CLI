from __future__ import annotations

import json
import os
import socket
from collections.abc import Callable
from dataclasses import dataclass
from typing import Any

from gi.repository import GLib

from core.logging_utils import get_logger

logger = get_logger(__name__)


_CLIENT_WATCH_MASK = GLib.IO_IN | GLib.IO_HUP | GLib.IO_ERR | GLib.IO_NVAL
_SERVER_WATCH_MASK = GLib.IO_IN | GLib.IO_HUP | GLib.IO_ERR | GLib.IO_NVAL


@dataclass(slots=True)
class _ClientInfo:
    sock: socket.socket
    watch_id: int
    buffer: bytearray


class IpcServer:
    """
    GLib-integrated UNIX socket server using newline-delimited JSON payloads.
    """

    def __init__(self, socket_path: str, max_buffer_bytes: int = 1024 * 1024) -> None:
        self.socket_path = socket_path
        self.max_buffer_bytes = max_buffer_bytes
        self.server_socket: socket.socket | None = None
        self.server_watch_id: int | None = None
        self.clients: dict[int, _ClientInfo] = {}
        self.callback: Callable[[dict[str, Any]], None] | None = None

    def set_callback(self, callback: Callable[[dict[str, Any]], None]) -> None:
        self.callback = callback

    def start(self) -> None:
        if self.server_socket is not None:
            self.stop()

        if os.path.exists(self.socket_path):
            os.remove(self.socket_path)

        server_socket = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
        server_socket.bind(self.socket_path)
        server_socket.listen(16)
        server_socket.setblocking(False)
        self.server_socket = server_socket

        self.server_watch_id = GLib.io_add_watch(
            server_socket.fileno(),
            GLib.PRIORITY_DEFAULT,
            _SERVER_WATCH_MASK,
            self._on_accept,
        )

    def _on_accept(self, _fd: int, condition: GLib.IOCondition) -> bool:
        if condition & (GLib.IO_HUP | GLib.IO_ERR | GLib.IO_NVAL):
            logger.warning("ipc server watch received terminal condition=%s", int(condition))
            self.stop()
            return False

        if self.server_socket is None:
            return False

        while True:
            try:
                client_sock, _ = self.server_socket.accept()
            except BlockingIOError:
                return True
            except OSError:
                logger.exception("ipc accept failed")
                return True

            client_sock.setblocking(False)
            client_fd = client_sock.fileno()
            watch_id = GLib.io_add_watch(
                client_fd,
                GLib.PRIORITY_DEFAULT,
                _CLIENT_WATCH_MASK,
                self._on_read,
                client_fd,
            )
            self.clients[client_fd] = _ClientInfo(
                sock=client_sock,
                watch_id=watch_id,
                buffer=bytearray(),
            )

    def _on_read(self, _fd: int, condition: GLib.IOCondition, client_fd: int) -> bool:
        if condition & (GLib.IO_HUP | GLib.IO_ERR | GLib.IO_NVAL):
            self._cleanup_client(client_fd, remove_watch=False)
            return False

        client_info = self.clients.get(client_fd)
        if client_info is None:
            return False

        try:
            data = client_info.sock.recv(4096)
        except BlockingIOError:
            return True
        except (ConnectionResetError, OSError):
            self._cleanup_client(client_fd, remove_watch=False)
            return False

        if not data:
            self._cleanup_client(client_fd, remove_watch=False)
            return False

        client_info.buffer.extend(data)
        if len(client_info.buffer) > self.max_buffer_bytes:
            logger.warning("ipc buffer overflow client_fd=%s", client_fd)
            self._cleanup_client(client_fd, remove_watch=False)
            return False

        while True:
            newline_index = client_info.buffer.find(b"\n")
            if newline_index < 0:
                break

            line_bytes = bytes(client_info.buffer[:newline_index]).strip()
            del client_info.buffer[: newline_index + 1]
            if not line_bytes:
                continue

            try:
                line = line_bytes.decode("utf-8")
            except UnicodeDecodeError:
                logger.warning("ipc invalid utf-8 payload dropped")
                continue

            try:
                message = json.loads(line)
            except json.JSONDecodeError:
                logger.warning("ipc invalid json payload dropped")
                continue

            if not isinstance(message, dict):
                logger.warning("ipc non-object json payload dropped")
                continue

            if self.callback is None:
                continue

            try:
                self.callback(message)
            except Exception:
                logger.exception("ipc callback failed")

        return True

    def _cleanup_client(self, client_fd: int, *, remove_watch: bool) -> None:
        client_info = self.clients.pop(client_fd, None)
        if client_info is None:
            return

        if remove_watch:
            self._safe_source_remove(client_info.watch_id)

        try:
            client_info.sock.close()
        except OSError:
            logger.debug("client socket close failed fd=%s", client_fd)

    def _safe_source_remove(self, source_id: int | None) -> None:
        if source_id is None:
            return
        try:
            GLib.source_remove(source_id)
        except Exception:
            logger.debug("source removal failed source_id=%s", source_id)

    def stop(self) -> None:
        if self.server_watch_id is not None:
            self._safe_source_remove(self.server_watch_id)
            self.server_watch_id = None

        for client_fd in list(self.clients):
            self._cleanup_client(client_fd, remove_watch=True)

        if self.server_socket is not None:
            try:
                self.server_socket.close()
            finally:
                self.server_socket = None

        if os.path.exists(self.socket_path):
            try:
                os.remove(self.socket_path)
            except OSError:
                logger.debug("failed to remove socket path=%s", self.socket_path)
