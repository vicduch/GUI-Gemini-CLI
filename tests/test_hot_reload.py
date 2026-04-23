import os
import signal
import time
from unittest.mock import MagicMock
import pytest
from core.process_manager import ProcessManager, ProcessState

def test_process_manager_restart_with_model():
    pm = ProcessManager()
    session_id = "test_restart"
    # Using 'cat' as a dummy process that stays open
    pm.spawn(session_id, ["cat"])
    
    proc = pm.processes[session_id]
    assert proc.state == ProcessState.RUNNING
    old_pid = proc.pid
    
    # Restart with different model
    pm.restart_with_model(session_id, "gemini-3.1-pro-preview")
    
    # It should be in STOPPING or already RESTARTING
    # Since 'cat' won't exit on SIGTERM immediately (it waits for input), 
    # but ProcessManager sends SIGTERM.
    
    # Let's wait a bit for the transition
    # In a real test we'd use GLib main loop, but here we check state
    assert pm.processes[session_id].state in (ProcessState.STOPPING, ProcessState.RUNNING)
    assert pm.processes[session_id].pending_command == ("cat", "--model", "gemini-3.1-pro-preview")
    
    pm.stop_all()
