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

def test_ipc_server_handles_fragmentation(socket_path):
    received_messages = []
    
    def on_message(msg):
        received_messages.append(msg)
        if len(received_messages) == 2:
            loop.quit()

    server = IpcServer(socket_path)
    server.set_callback(on_message)
    server.start()

    # Client simulation
    client = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
    client.connect(socket_path)
    
    payload1 = json.dumps({"event": "spawn", "agent_id": "alpha"}) + "\n"
    payload2 = json.dumps({"event": "kill", "agent_id": "beta"}) + "\n"
    
    loop = GLib.MainLoop()
    
    def send_fragment_1():
        client.sendall(payload1[:10].encode("utf-8"))
        return False  # Run once
        
    def send_fragment_2():
        client.sendall(payload1[10:].encode("utf-8"))
        return False
        
    def send_payload_2():
        client.sendall(payload2.encode("utf-8"))
        return False

    # Schedule sends
    GLib.timeout_add(10, send_fragment_1)
    GLib.timeout_add(50, send_fragment_2)
    GLib.timeout_add(100, send_payload_2)
    
    # Timeout failsafe
    GLib.timeout_add(1000, loop.quit)
    loop.run()
    
    server.stop()
    client.close()

    assert len(received_messages) == 2
    assert received_messages[0] == {"event": "spawn", "agent_id": "alpha"}
    assert received_messages[1] == {"event": "kill", "agent_id": "beta"}

def test_ipc_server_handles_utf8_chunk_boundaries(socket_path):
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

    # 🌟 is \\xf0\\x9f\\x8c\\x9f (4 bytes)
    payload = json.dumps({"event": "spawn", "agent_id": "alpha 🌟"}, ensure_ascii=False) + "\n"
    payload_bytes = payload.encode("utf-8")
    # split inside the star
    star_idx = payload_bytes.find(b'\xf0\x9f\x8c\x9f')
    split_point = star_idx + 2

    loop = GLib.MainLoop()

    def send_fragment_1():
        client.sendall(payload_bytes[:split_point])
        return False

    def send_fragment_2():
        client.sendall(payload_bytes[split_point:])
        return False

    # Schedule sends
    GLib.timeout_add(10, send_fragment_1)
    GLib.timeout_add(50, send_fragment_2)

    # Timeout failsafe
    GLib.timeout_add(1000, loop.quit)
    loop.run()

    server.stop()
    client.close()

    assert len(received_messages) == 1
    assert received_messages[0] == {"event": "spawn", "agent_id": "alpha 🌟"}

def test_ipc_server_drops_connection_on_buffer_overflow(socket_path):
    received_messages = []

    def on_message(msg):
        received_messages.append(msg)

    server = IpcServer(socket_path)
    server.set_callback(on_message)
    server.start()

    client = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
    client.connect(socket_path)
    client.setblocking(False)

    loop = GLib.MainLoop()

    payload_chunk = b"A" * 65536
    bytes_sent = [0]

    def send_large_payload():
        try:
            sent = client.send(payload_chunk)
            bytes_sent[0] += sent
            if bytes_sent[0] > 1024 * 1024 + 10:
                return False # Stop sending
        except BlockingIOError:
            pass
        except (BrokenPipeError, ConnectionResetError):
            return False
        return True # Keep sending

    def check_connection_dropped():
        if len(server.clients) == 0:
            loop.quit()
            return False
        return True # check again later
    # Schedule sends
    GLib.timeout_add(10, send_large_payload)
    GLib.timeout_add(50, check_connection_dropped)

    # Timeout failsafe
    GLib.timeout_add(2000, loop.quit)
    loop.run()

    clients_count = len(server.clients)

    server.stop()
    client.close()

    assert len(received_messages) == 0
    assert clients_count == 0