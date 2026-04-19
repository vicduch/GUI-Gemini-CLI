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