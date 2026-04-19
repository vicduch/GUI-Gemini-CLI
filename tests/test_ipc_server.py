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