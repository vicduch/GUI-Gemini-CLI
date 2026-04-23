from __future__ import annotations

import gi
gi.require_version("Gtk", "4.0")
gi.require_version("GObject", "2.0")
from gi.repository import Gtk, GObject

class EmptySlot(Gtk.Widget):
    """An empty slot in the workspace grid. Features a dashed border and a '+' button."""

    __gsignals__ = {
        "slot-clicked": (GObject.SignalFlags.RUN_FIRST, None, ()),
    }

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        
        self.add_css_class("empty-slot")
        self.set_hexpand(True)
        self.set_vexpand(True)

        self._layout_manager = Gtk.BinLayout()
        self.set_layout_manager(self._layout_manager)

        self.button = Gtk.Button(icon_name="list-add-symbolic")
        self.button.add_css_class("circular")
        self.button.add_css_class("suggested-action")
        self.button.set_halign(Gtk.Align.CENTER)
        self.button.set_valign(Gtk.Align.CENTER)
        self.button.set_size_request(64, 64)

        self.button.connect("clicked", self._on_button_clicked)
        
        self.button.set_parent(self)

    def dispose(self):
        if self.button:
            self.button.unparent()
            self.button = None
        super().dispose()

    def _on_button_clicked(self, _button: Gtk.Button) -> None:
        self.emit("slot-clicked")
