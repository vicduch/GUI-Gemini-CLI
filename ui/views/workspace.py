import gi
gi.require_version('Gtk', '4.0')
from gi.repository import Gtk
from ui.components.terminal_pane import TerminalPane

class Workspace(Gtk.Stack):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.set_transition_type(Gtk.StackTransitionType.CROSSFADE)
        
        self.panes = []
        
        # Grid Page
        self.grid = Gtk.Grid()
        self.grid.set_column_spacing(8)
        self.grid.set_row_spacing(8)
        self.grid.set_margin_top(8)
        self.grid.set_margin_bottom(8)
        self.grid.set_margin_start(8)
        self.grid.set_margin_end(8)
        self.add_titled(self.grid, "grid_page", "Grid")
        
        # Focus Page
        self.focus_overlay = Gtk.Overlay()
        self.focus_background = Gtk.Button() # Clickable background
        self.focus_background.set_has_frame(False)
        self.focus_background.connect("clicked", self._on_background_clicked)
        self.focus_overlay.set_child(self.focus_background)
        
        self.focus_bin = Gtk.Box()
        self.focus_bin.set_halign(Gtk.Align.CENTER)
        self.focus_bin.set_valign(Gtk.Align.CENTER)
        self.focus_bin.set_hexpand(True)
        self.focus_bin.set_vexpand(True)
        # Margin simulates the 90% size
        self.focus_bin.set_margin_start(40)
        self.focus_bin.set_margin_end(40)
        self.focus_bin.set_margin_top(40)
        self.focus_bin.set_margin_bottom(40)
        
        self.focus_overlay.add_overlay(self.focus_bin)
        self.add_titled(self.focus_overlay, "focus_page", "Focus")
        
        self.focused_pane = None
        self._next_row = 0
        self._next_col = 0

    def add_pane(self, pane: TerminalPane):
        self.panes.append(pane)
        pane._grid_col = self._next_col
        pane._grid_row = self._next_row
        self.grid.attach(pane, self._next_col, self._next_row, 1, 1)
        self._next_col += 1
        if self._next_col > 1: # Basic 2-column layout
            self._next_col = 0
            self._next_row += 1
        pane.zoom_button.connect("clicked", lambda btn: self.focus_pane(pane))
        
    def _on_background_clicked(self, btn):
        if self.focused_pane:
            self.unfocus_pane()

    def focus_pane(self, pane: TerminalPane):
        if self.focused_pane:
            self.unfocus_pane()
            
        self.focused_pane = pane
        self.grid.remove(pane)
        self.focus_bin.append(pane)
        self.set_visible_child_name("focus_page")

    def unfocus_pane(self):
        if not self.focused_pane:
            return
            
        pane = self.focused_pane
        self.focus_bin.remove(pane)
        self.grid.attach(pane, pane._grid_col, pane._grid_row, 1, 1)
        
        self.focused_pane = None
        self.set_visible_child_name("grid_page")