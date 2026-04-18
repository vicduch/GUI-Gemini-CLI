import pytest
from core.process_manager import ProcessManager

def test_process_manager_initialization():
    pm = ProcessManager()
    assert pm.processes == {}

def test_spawn_process():
    pm = ProcessManager()
    # We just test the method signature and dictionary update for now
    pm.spawn("session-123", ["echo", "hello"])
    assert "session-123" in pm.processes
