# Phase 1: Core Backend & IPC Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Establish the foundational Python project structure, dependency management, and the `ProcessManager` to orchestrate `gemini-cli` subprocesses.
**Architecture:** A native GTK/GLib backend (`process_manager.py`) using `GLib.spawn_async_with_pipes` integrated into tests without UI logic.
**Tech Stack:** Python 3.12+, PyGObject (GLib/Gio), pytest.

---

### Task 1: Project Setup & Dependencies

**Files:**
- Create: `requirements.txt`
- Create: `pytest.ini`
- Create: `core/__init__.py`

- [ ] **Step 1: Write requirements.txt**

```text
PyGObject>=3.48.0
pytest>=8.0.0
pytest-asyncio>=0.23.0
```

- [ ] **Step 2: Write pytest.ini**

```ini
[pytest]
testpaths = tests
python_files = test_*.py
```

- [ ] **Step 3: Create core package**

```bash
mkdir -p core tests
touch core/__init__.py tests/__init__.py
```

- [ ] **Step 4: Commit project setup**

```bash
git add requirements.txt pytest.ini core/ tests/
git commit -m "chore: setup project structure and dependencies"
```

### Task 2: Data Models

**Files:**
- Create: `core/models.py`
- Create: `tests/test_models.py`

- [ ] **Step 1: Write failing test for Session model**

```python
# tests/test_models.py
from core.models import Session, Agent

def test_session_creation():
    session = Session(id="sess-1", model="gemini-3.1-pro", workspace="/tmp")
    assert session.id == "sess-1"
    assert session.model == "gemini-3.1-pro"

def test_agent_creation():
    agent = Agent(id="agt-1", status="running", role="master")
    assert agent.id == "agt-1"
    assert agent.status == "running"
```

- [ ] **Step 2: Run test to verify it fails**

Run: `pytest tests/test_models.py -v`
Expected: FAIL (ModuleNotFoundError)

- [ ] **Step 3: Implement data models**

```python
# core/models.py
from dataclasses import dataclass

@dataclass
class Session:
    id: str
    model: str
    workspace: str

@dataclass
class Agent:
    id: str
    status: str
    role: str
```

- [ ] **Step 4: Run test to verify it passes**

Run: `pytest tests/test_models.py -v`
Expected: PASS

- [ ] **Step 5: Commit models**

```bash
git add core/models.py tests/test_models.py
git commit -m "feat: implement Session and Agent data models"
```

### Task 3: Process Manager (Stub & Test)

**Files:**
- Create: `core/process_manager.py`
- Create: `tests/test_process_manager.py`

- [ ] **Step 1: Write the failing test**

```python
# tests/test_process_manager.py
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
```

- [ ] **Step 2: Run test to verify it fails**

Run: `pytest tests/test_process_manager.py -v`
Expected: FAIL (ModuleNotFoundError)

- [ ] **Step 3: Write minimal implementation**

```python
# core/process_manager.py
class ProcessManager:
    def __init__(self):
        self.processes = {}
        
    def spawn(self, session_id: str, command: list[str]):
        # Stub implementation
        self.processes[session_id] = {"command": command}
```

- [ ] **Step 4: Run test to verify it passes**

Run: `pytest tests/test_process_manager.py -v`
Expected: PASS

- [ ] **Step 5: Commit Process Manager stub**

```bash
git add core/process_manager.py tests/test_process_manager.py
git commit -m "feat: add ProcessManager stub and tests"
```