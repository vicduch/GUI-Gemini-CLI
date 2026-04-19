import socket
import json
import os
from typing import Callable, Any, Dict, Optional
from gi.repository import GLib

class IpcServer:
    """
    Inter-Process Communication (IPC) Server using Unix Domain Sockets.
    
    This server listens for incoming connections and processes JSON-encoded
    messages separated by newlines. It uses GLib's event loop to handle
    I/O asynchronously.
    """
    
    def __init__(self, socket_path: str):
        """
        Initialize the IPC server.

        Args:
            socket_path: The filesystem path where the Unix socket will be created.
        """
        self.socket_path: str = socket_path
        self.server_socket: Optional[socket.socket] = None
        self.callback: Optional[Callable[[Dict[str, Any]], None]] = None
        self.server_watch_id: Optional[int] = None
        self.clients: Dict[int, Dict[str, Any]] = {}  # Map fd to {"sock": socket, "buffer": "", "watch_id": int}

    def set_callback(self, callback: Callable[[Dict[str, Any]], None]):
        """
        Set the callback function to be invoked when a valid message is received.

        Args:
            callback: A function that takes a parsed JSON dictionary as its argument.
        """
        self.callback = callback

    def start(self):
        """
        Start the IPC server. 
        Creates the socket, binds it, and starts listening for connections
        within the GLib event loop.
        """
        if os.path.exists(self.socket_path):
            os.remove(self.socket_path)
            
        self.server_socket = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
        self.server_socket.bind(self.socket_path)
        self.server_socket.listen(5)
        self.server_socket.setblocking(False)
        
        self.server_watch_id = GLib.io_add_watch(
            self.server_socket.fileno(), 
            GLib.IO_IN, 
            self._on_accept
        )

    def _on_accept(self, fd: int, condition: GLib.IOCondition) -> bool:
        """
        Callback for accepting new client connections.
        
        Args:
            fd: The file descriptor of the server socket.
            condition: The GLib IO condition.
            
        Returns:
            bool: True to keep listening for new connections.
        """
        try:
            if not self.server_socket:
                return False

            client_sock, _ = self.server_socket.accept()
            client_sock.setblocking(False)
            client_fd = client_sock.fileno()
            
            watch_id = GLib.io_add_watch(client_fd, GLib.IO_IN, self._on_read, client_fd)
            self.clients[client_fd] = {"sock": client_sock, "buffer": "", "watch_id": watch_id}
        except BlockingIOError:
            pass
        return True # Keep listening

    def _on_read(self, fd: int, condition: GLib.IOCondition, client_fd: int) -> bool:
        """
        Callback for reading data from a connected client.
        Handles message fragmentation and delegates complete JSON messages
        to the registered callback.
        
        Args:
            fd: The file descriptor of the client socket.
            condition: The GLib IO condition.
            client_fd: The original file descriptor associated with this client.
            
        Returns:
            bool: True to keep the connection alive, False to close it.
        """
        client_info = self.clients.get(client_fd)
        if not client_info:
            return False
            
        client_sock = client_info["sock"]
        
        try:
            data = client_sock.recv(4096)
            if not data:
                self._cleanup_client(client_fd)
                return False
                
            client_info["buffer"] += data.decode("utf-8")
            
            # Process complete messages only
            while "\n" in client_info["buffer"]:
                line, client_info["buffer"] = client_info["buffer"].split("\n", 1)
                line = line.strip()
                if line and self.callback:
                    try:
                        msg = json.loads(line)
                        self.callback(msg)
                    except json.JSONDecodeError as e:
                        print(f"IPC JSON Decode Error: {e} - Payload: {line}")
                        
        except BlockingIOError:
            return True
        except ConnectionResetError:
            self._cleanup_client(client_fd)
            return False
            
        return True # Keep connection alive

    def _cleanup_client(self, client_fd: int):
        """
        Clean up resources associated with a specific client.
        
        Args:
            client_fd: The file descriptor of the client to clean up.
        """
        if client_fd in self.clients:
            self.clients[client_fd]["sock"].close()
            del self.clients[client_fd]

    def stop(self):
        """
        Stop the IPC server and clean up all resources, including client connections
        and the socket file.
        """
        if self.server_watch_id is not None:
            GLib.source_remove(self.server_watch_id)
            self.server_watch_id = None
            
        for client_info in self.clients.values():
            GLib.source_remove(client_info["watch_id"])
            client_info["sock"].close()
        self.clients.clear()
        
        if self.server_socket:
            self.server_socket.close()
            self.server_socket = None
            
        if os.path.exists(self.socket_path):
            os.remove(self.socket_path)
