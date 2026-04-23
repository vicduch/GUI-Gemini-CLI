from __future__ import annotations

import gi

gi.require_version("Gtk", "4.0")
gi.require_version("Adw", "1")
from gi.repository import Gtk, GObject, Adw

from ui.components.empty_slot import EmptySlot
from ui.components.terminal_pane import TerminalPane


class Workspace(Gtk.Stack):
    __gsignals__ = {
        "slot-requested": (GObject.SignalFlags.RUN_FIRST, None, (object,)),
    }

    def __init__(self, columns: int = 2, rows: int = 2, **kwargs):
        super().__init__(**kwargs)
        self.set_transition_type(Gtk.StackTransitionType.NONE)

        self._columns = max(columns, 1)
        self._rows = max(rows, 1)
        self._is_transitioning = False

        self.panes: list[TerminalPane] = []
        self.pane_positions: dict[TerminalPane, tuple[int, int]] = {}
        self.empty_slots: list[EmptySlot] = []
        self.empty_slot_positions: dict[EmptySlot, tuple[int, int]] = {}
        
        self._zoom_handler_ids: dict[TerminalPane, int] = {}
        self._slot_clicked_handler_ids: dict[EmptySlot, int] = {}
        self.focused_pane: TerminalPane | None = None
        
        self._animation: Adw.TimedAnimation | None = None
        self._start_geometry = (0, 0, 0, 0)
        self._target_margins = (0, 0, 0, 0)

        self.grid = Gtk.Grid()
        self.grid.set_column_spacing(8)
        self.grid.set_row_spacing(8)
        self.grid.set_margin_top(8)
        self.grid.set_margin_bottom(8)
        self.grid.set_margin_start(8)
        self.grid.set_margin_end(8)
        self.add_titled(self.grid, "grid_page", "Grid")

        self.focus_overlay = Gtk.Overlay()
        self.focus_background = Gtk.Button()
        self.focus_background.set_has_frame(False)
        self.focus_background.set_hexpand(True)
        self.focus_background.set_vexpand(True)
        self.focus_background.connect("clicked", self._on_background_clicked)
        self.focus_overlay.set_child(self.focus_background)

        self.focus_bin = Gtk.Box()
        self.focus_bin.set_halign(Gtk.Align.FILL)
        self.focus_bin.set_valign(Gtk.Align.FILL)
        self.focus_bin.set_hexpand(True)
        self.focus_bin.set_vexpand(True)
        self.focus_overlay.add_overlay(self.focus_bin)
        self.add_titled(self.focus_overlay, "focus_page", "Focus")

        self.set_visible_child_name("grid_page")
        self.connect("notify::visible-child-name", self._on_visible_page_changed)

        self._init_empty_slots()

    def _init_empty_slots(self) -> None:
        for row in range(self._rows):
            for col in range(self._columns):
                slot = EmptySlot()
                self.empty_slots.append(slot)
                self.empty_slot_positions[slot] = (col, row)
                self.grid.attach(slot, col, row, 1, 1)
                handler_id = slot.connect("slot-clicked", self._on_slot_clicked, slot)
                self._slot_clicked_handler_ids[slot] = handler_id

    def _on_slot_clicked(self, _widget: EmptySlot, slot: EmptySlot) -> None:
        self.emit("slot-requested", slot)

    def add_pane(self, pane: TerminalPane, replace_slot: EmptySlot | None = None) -> bool:
        if pane in self.panes:
            return False

        if replace_slot and replace_slot in self.empty_slots:
            col, row = self.empty_slot_positions[replace_slot]
            self._remove_empty_slot(replace_slot)
        elif self.empty_slots:
            # Replaces the first available empty slot
            slot = self.empty_slots[0]
            col, row = self.empty_slot_positions[slot]
            self._remove_empty_slot(slot)
        else:
            # Grid is full (all slots taken)
            return False

        self.panes.append(pane)
        self.pane_positions[pane] = (col, row)
        self.grid.attach(pane, col, row, 1, 1)

        handler_id = pane.connect("zoom-clicked", self._on_zoom_clicked, pane)
        self._zoom_handler_ids[pane] = handler_id
        return True

    def _remove_empty_slot(self, slot: EmptySlot) -> None:
        self.grid.remove(slot)
        handler_id = self._slot_clicked_handler_ids.pop(slot, None)
        if handler_id is not None:
            slot.disconnect(handler_id)
        self.empty_slots.remove(slot)
        self.empty_slot_positions.pop(slot, None)

    def remove_pane(self, pane: TerminalPane) -> bool:
        if pane not in self.panes:
            return False

        if pane is self.focused_pane:
            if pane.get_parent() is self.focus_bin:
                self.focus_bin.remove(pane)
            self.focused_pane = None
            self.set_visible_child_name("grid_page")
        elif pane.get_parent() is self.grid:
            self.grid.remove(pane)

        handler_id = self._zoom_handler_ids.pop(pane, None)
        if handler_id is not None:
            pane.disconnect(handler_id)

        self.panes.remove(pane)
        col, row = self.pane_positions.pop(pane)
        
        # Add back the empty slot
        slot = EmptySlot()
        self.empty_slots.append(slot)
        self.empty_slot_positions[slot] = (col, row)
        self.grid.attach(slot, col, row, 1, 1)
        handler_id = slot.connect("slot-clicked", self._on_slot_clicked, slot)
        self._slot_clicked_handler_ids[slot] = handler_id

        return True

    def focus_pane(self, pane: TerminalPane) -> None:
        if pane not in self.panes or self._is_transitioning:
            return
        if pane is self.focused_pane:
            return

        if self.focused_pane is not None:
            self.unfocus_pane()

        self._is_transitioning = True
        
        # Get start geometry relative to workspace
        coords = pane.translate_coordinates(self, 0, 0)
        if coords:
            x, y = coords
        else:
            x, y = 0, 0
        w, h = pane.get_width(), pane.get_height()
        tw, th = self.get_width(), self.get_height()
        
        start_margins = (x, tw - (x + w), y, th - (y + h))
        
        # Target margins (5%)
        target_hm = max(int(tw * 0.05), 8)
        target_vm = max(int(th * 0.05), 8)
        end_margins = (target_hm, target_hm, target_vm, target_vm)

        try:
            self.focused_pane = pane

            if pane.get_parent() is self.grid:
                self.grid.remove(pane)
            if pane.get_parent() is not self.focus_bin:
                self.focus_bin.append(pane)

            # Set initial position for animation
            self.focus_bin.set_margin_start(start_margins[0])
            self.focus_bin.set_margin_end(start_margins[1])
            self.focus_bin.set_margin_top(start_margins[2])
            self.focus_bin.set_margin_bottom(start_margins[3])
            
            self.set_visible_child_name("focus_page")
            
            self._animate_margins(start_margins, end_margins)
        finally:
            self._is_transitioning = False

    def unfocus_pane(self) -> None:
        if self.focused_pane is None or self._is_transitioning:
            return

        self._is_transitioning = True
        pane = self.focused_pane
        
        # Current margins
        tw, th = self.get_width(), self.get_height()
        start_margins = (
            self.focus_bin.get_margin_start(),
            self.focus_bin.get_margin_end(),
            self.focus_bin.get_margin_top(),
            self.focus_bin.get_margin_bottom()
        )
        
        # Calculate target margins in the grid
        col, row = self.pane_positions[pane]

        # The grid fills the workspace with 8px margins
        cell_w = (tw - 16 - (self._columns - 1) * 8) / self._columns
        cell_h = (th - 16 - (self._rows - 1) * 8) / self._rows

        gx = 8 + col * (cell_w + 8)
        gy = 8 + row * (cell_h + 8)
        # Adjust for stack margins/padding if any (the grid has 8px margins)
        end_margins = (int(gx), int(tw - (gx + cell_w)), int(gy), int(th - (gy + cell_h)))

        def on_done():
            self._is_transitioning = True
            try:
                if pane.get_parent() is self.focus_bin:
                    self.focus_bin.remove(pane)

                col, row = self.pane_positions[pane]
                self.grid.attach(pane, col, row, 1, 1)

                self.focused_pane = None
                self.set_visible_child_name("grid_page")
            finally:
                self._is_transitioning = False

        self._animate_margins(start_margins, end_margins, on_done)

    def _animate_margins(self, start: tuple[int, int, int, int], end: tuple[int, int, int, int], callback=None) -> None:
        if self._animation:
            self._animation.skip()

        def update_cb(value: float) -> None:
            ms = start[0] + (end[0] - start[0]) * value
            me = start[1] + (end[1] - start[1]) * value
            mt = start[2] + (end[2] - start[2]) * value
            mb = start[3] + (end[3] - start[3]) * value
            self.focus_bin.set_margin_start(int(ms))
            self.focus_bin.set_margin_end(int(me))
            self.focus_bin.set_margin_top(int(mt))
            self.focus_bin.set_margin_bottom(int(mb))

        target = Adw.CallbackAnimationTarget.new(update_cb)
        self._animation = Adw.TimedAnimation.new(self, 0, 1, 400, target)
        self._animation.set_easing(Adw.Easing.EASE_OUT_QUINT)
        
        if callback:
            self._animation.connect("done", lambda _: callback())
            
        self._animation.play()

    def _on_zoom_clicked(self, _button: Gtk.Button, pane: TerminalPane) -> None:
        self.focus_pane(pane)

    def _on_background_clicked(self, _button: Gtk.Button) -> None:
        self.unfocus_pane()

    def _on_visible_page_changed(self, *_args) -> None:
        self._update_focus_margins()

    def do_size_allocate(self, width: int, height: int, baseline: int) -> None:
        Gtk.Stack.do_size_allocate(self, width, height, baseline)
        self._update_focus_margins(width=width, height=height)

    def _update_focus_margins(self, width: int | None = None, height: int | None = None) -> None:
        if self._is_transitioning or (self._animation and self._animation.get_state() == Adw.AnimationState.PLAYING):
            return

        if width is None:
            width = max(self.get_width(), 0)
        if height is None:
            height = max(self.get_height(), 0)

        horizontal_margin = max(int(width * 0.05), 8)
        vertical_margin = max(int(height * 0.05), 8)
        self.focus_bin.set_margin_start(horizontal_margin)
        self.focus_bin.set_margin_end(horizontal_margin)
        self.focus_bin.set_margin_top(vertical_margin)
        self.focus_bin.set_margin_bottom(vertical_margin)

    def get_active_session_id(self) -> str | None:
        """Returns the session_id of the active terminal."""
        if self.focused_pane:
            return self.focused_pane.session_id
        if self.panes:
            return self.panes[0].session_id
        return None
