from __future__ import annotations

import os
from pathlib import Path


_runtime_dir = Path("/tmp/gui-terminal-runtime")
_runtime_dir.mkdir(parents=True, exist_ok=True)
_runtime_dir.chmod(0o700)

os.environ.setdefault("XDG_RUNTIME_DIR", str(_runtime_dir))
os.environ.setdefault("GSETTINGS_BACKEND", "memory")
