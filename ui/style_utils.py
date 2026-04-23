import gi

gi.require_version("Adw", "1")
gi.require_version("Gtk", "4.0")
from gi.repository import Adw, Gtk, Gdk


def get_color_scheme_for_name(theme_name: str) -> Adw.ColorScheme:
    if theme_name == "Light":
        return Adw.ColorScheme.FORCE_LIGHT
    elif theme_name == "Dark":
        return Adw.ColorScheme.FORCE_DARK
    else:
        return Adw.ColorScheme.DEFAULT


def apply_theme(theme_name: str) -> None:
    style_manager = Adw.StyleManager.get_default()
    style_manager.set_color_scheme(get_color_scheme_for_name(theme_name))


def load_css() -> None:
    css_provider = Gtk.CssProvider()
    css_provider.load_from_data(b"""
        .empty-slot {
            border: 2px dashed alpha(@theme_fg_color, 0.2);
            border-radius: 12px;
            background-color: alpha(@theme_bg_color, 0.5);
        }
        .empty-slot:hover {
            border-color: alpha(@theme_fg_color, 0.4);
            background-color: alpha(@theme_bg_color, 0.8);
        }
        .terminal-header {
            min-height: 24px;
            padding: 0;
            background-color: alpha(@theme_fg_color, 0.05);
            border-bottom: 1px solid alpha(@theme_fg_color, 0.1);
        }
        .terminal-header button, .terminal-header dropdown {
            padding: 2px 6px;
            min-height: 20px;
        }
        .terminal-header label {
            font-size: 0.8rem;
        }
    """)
    Gtk.StyleContext.add_provider_for_display(
        Gdk.Display.get_default(),
        css_provider,
        Gtk.STYLE_PROVIDER_PRIORITY_APPLICATION,
    )
