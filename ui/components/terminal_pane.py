import gi

gi.require_version("Gtk", "4.0")
gi.require_version("Adw", "1")
gi.require_version("Vte", "3.91")
from gi.repository import Adw, Gtk, Vte, GLib, GObject

from core.models import ErrorContract


class TerminalPane(Gtk.Box):
    __gsignals__ = {
        "model-changed": (GObject.SignalFlags.RUN_FIRST, None, (str,)),
        "zoom-clicked": (GObject.SignalFlags.RUN_FIRST, None, ()),
    }

    def __init__(self, terminal_factory=None, session_id="default", available_models=None, **kwargs):
        super().__init__(orientation=Gtk.Orientation.VERTICAL, **kwargs)
        self.session_id = session_id
        self.available_models = available_models or [
            "gemini-3.1-pro-preview",
            "gemini-3-flash-preview",
        ]

        # 1. Header Bar
        self.header_bar = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=4)
        self.header_bar.add_css_class("terminal-header")
        self.header_bar.set_margin_start(4)
        self.header_bar.set_margin_end(4)
        self.header_bar.set_margin_top(2)
        self.header_bar.set_margin_bottom(2)

        # Label Session/Model
        self.title_label = Gtk.Label(label=f"Session: {session_id}")
        self.title_label.add_css_class("caption")
        self.title_label.add_css_class("dim-label")
        self.header_bar.append(self.title_label)

        # Spacer
        spacer = Gtk.Box()
        spacer.set_hexpand(True)
        self.header_bar.append(spacer)

        # Model Selection DropDown
        self.model_dropdown = Gtk.DropDown.new_from_strings(self.available_models)
        self.model_dropdown.set_valign(Gtk.Align.CENTER)
        self.model_dropdown.add_css_class("flat")
        self.model_dropdown.connect("notify::selected", self._on_model_selected)
        self.header_bar.append(self.model_dropdown)

        # Zoom Button
        self.zoom_button = Gtk.Button(icon_name="view-fullscreen-symbolic")
        self.zoom_button.set_tooltip_text("Focus Mode")
        self.zoom_button.add_css_class("flat")
        self.zoom_button.connect("clicked", lambda _: self.emit("zoom-clicked"))
        self.header_bar.append(self.zoom_button)

        self.append(self.header_bar)

        # 2. Terminal Area (Overlay)
        self.terminal_overlay = Gtk.Overlay()
        self.terminal_overlay.set_vexpand(True)
        self.terminal_overlay.set_hexpand(True)

        factory = terminal_factory or self._create_default_terminal
        self.terminal = factory()
        self.terminal.set_hexpand(True)
        self.terminal.set_vexpand(True)

        self.terminal_overlay.set_child(self.terminal)

        # Bannière d'erreur (Overlay)
        self.error_banner = Adw.Banner()
        self.error_banner.set_valign(Gtk.Align.START)
        self.terminal_overlay.add_overlay(self.error_banner)

        self.append(self.terminal_overlay)

    def _on_model_selected(self, dropdown, pspec):
        selected_item = dropdown.get_selected_item()
        if selected_item:
            model_name = selected_item.get_string()
            self.emit("model-changed", model_name)

    def spawn_process(self, command: list[str], on_spawned=None, on_exited=None):
        """Spawns the gemini-cli process inside the VTE terminal."""
        if not isinstance(self.terminal, Vte.Terminal):
            return

        def _spawn_cb(terminal, pid, error, _user_data):
            if error:
                err = ErrorContract(code="SPAWN_FAIL", message=error.message, severity="error", correlation_id="")
                self.show_error(err)
            elif on_spawned:
                on_spawned(pid)

        def _exit_cb(terminal, status):
            if on_exited:
                on_exited(status)

        # Clear previous signal if any
        if hasattr(self, "_exit_handler_id"):
            self.terminal.disconnect(self._exit_handler_id)
        self._exit_handler_id = self.terminal.connect("child-exited", _exit_cb)

        self.terminal.spawn_async(
            Vte.PtyFlags.DEFAULT,
            None,  # working directory
            command,
            None,  # envv
            GLib.SpawnFlags.SEARCH_PATH,
            None,  # child_setup
            None,  # child_setup_data
            -1,    # timeout
            None,  # cancellable
            _spawn_cb,
            None   # user_data
        )

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
