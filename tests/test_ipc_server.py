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