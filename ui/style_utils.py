import gi

gi.require_version("Adw", "1")
from gi.repository import Adw


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
