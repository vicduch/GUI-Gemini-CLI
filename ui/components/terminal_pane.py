import gi
gi.require_version('Gtk', '4.0')
gi.require_version('Vte', '3.91')
from gi.repository import Gtk, Vte

class TerminalPane(Gtk.Overlay):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        
        # Initialisation du VTE Terminal
        self.terminal = Vte.Terminal()
        self.terminal.set_hexpand(True)
        self.terminal.set_vexpand(True)
        
        self.set_child(self.terminal)
        
        # Bouton Zoom Focus Mode (stub pour la logique de focus)
        self.zoom_button = Gtk.Button(icon_name="view-fullscreen-symbolic")
        self.zoom_button.set_halign(Gtk.Align.END)
        self.zoom_button.set_valign(Gtk.Align.START)
        self.zoom_button.set_margin_top(8)
        self.zoom_button.set_margin_end(8)
        
        self.add_overlay(self.zoom_button)
