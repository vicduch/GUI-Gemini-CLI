from __future__ import annotations

import os
from pathlib import Path

import gi
import pytest

gi.require_version("Gtk", "4.0")
gi.require_version("Adw", "1")
from gi.repository import Adw, Gdk, Gtk


_runtime_dir = Path("/tmp/gui-terminal-runtime")
_runtime_dir.mkdir(parents=True, exist_ok=True)
_runtime_dir.chmod(0o700)

os.environ.setdefault("XDG_RUNTIME_DIR", str(_runtime_dir))
os.environ.setdefault("GSETTINGS_BACKEND", "memory")
os.environ.setdefault("GDK_BACKEND", "x11")


def _has_usable_display() -> bool:
    candidates = [os.environ.get("DISPLAY"), os.environ.get("WAYLAND_DISPLAY")]
    for display_name in candidates:
        if not display_name:
            continue
        try:
            display = Gdk.Display.open(display_name)
        except Exception:
            continue
        if display is not None:
            display.close()
            return True
    return False


@pytest.fixture(scope="session")
def gtk_display_available() -> bool:
    return _has_usable_display()


@pytest.fixture
def require_gtk_display(gtk_display_available: bool) -> None:
    if not gtk_display_available:
        pytest.skip("No usable GTK display in this environment")
    Gtk.init()
    Adw.init()
