class ProcessManager:
    def __init__(self):
        self.processes = {}
        
    def spawn(self, session_id: str, command: list[str]):
        # Stub implementation
        self.processes[session_id] = {"command": command}
