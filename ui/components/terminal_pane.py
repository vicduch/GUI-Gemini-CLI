import gi

gi.require_version("Gtk", "4.0")
gi.require_version("Adw", "1")
gi.require_version("Vte", "3.91")
from gi.repository import Adw, Gtk, Vte

from core.models import ErrorContract


class TerminalPane(Gtk.Overlay):
    def __init__(self, terminal_factory=None, **kwargs):
        super().__init__(**kwargs)

        factory = terminal_factory or self._create_default_terminal
        self.terminal = factory()
        self.terminal.set_hexpand(True)
        self.terminal.set_vexpand(True)

        self.set_child(self.terminal)

        # Bannière d'erreur (Overlay)
        self.error_banner = Adw.Banner()
        self.error_banner.set_valign(Gtk.Align.START)
        self.add_overlay(self.error_banner)

        # Bouton Zoom Focus Mode
        self.zoom_button = Gtk.Button(icon_name="view-fullscreen-symbolic")
        self.zoom_button.set_halign(Gtk.Align.END)
        self.zoom_button.set_valign(Gtk.Align.START)
        self.zoom_button.set_margin_top(8)
        self.zoom_button.set_margin_end(8)

        self.add_overlay(self.zoom_button)

    def show_error(self, error: ErrorContract):
        """Affiche une bannière d'erreur au-dessus du terminal."""
        self.error_banner.set_title(f"[{error.code}] {error.message}")
        self.error_banner.set_revealed(True)

    def clear_error(self):
        """Masque la bannière d'erreur."""
        self.error_banner.set_revealed(False)

    @staticmethod
    def _create_default_terminal():
        return Vte.Terminal()
