from __future__ import annotations

import gi
import pytest

gi.require_version("Gtk", "4.0")
from gi.repository import Gtk

from ui.components.empty_slot import EmptySlot

pytestmark = pytest.mark.usefixtures("require_gtk_display")

def test_empty_slot_initialization() -> None:
    slot = EmptySlot()
    assert isinstance(slot, Gtk.Widget)
    assert slot.get_css_classes() == ["empty-slot"]

def test_empty_slot_button_clicked() -> None:
    clicked = False
    def on_click(slot: EmptySlot) -> None:
        nonlocal clicked
        clicked = True

    slot = EmptySlot()
    slot.connect("slot-clicked", on_click)
    
    # simulate click
    slot.button.emit("clicked")
    
    assert clicked is True
