import gi

gi.require_version("Gtk", "4.0")
gi.require_version("Adw", "1")
from gi.repository import Adw, Gtk


class SettingsDialog(Adw.PreferencesWindow):
    def __init__(self, config_manager, **kwargs):
        super().__init__(**kwargs)
        self.config_manager = config_manager
        self.set_title("Settings")

        # Page Appearance
        page = Adw.PreferencesPage(title="Appearance", icon_name="display-brightness-symbolic")
        self.add(page)

        group = Adw.PreferencesGroup(title="Theme")
        page.add(group)

        # Theme selection
        self.theme_row = Adw.ComboRow(title="Color Scheme")
        self.theme_row.set_model(Gtk.StringList.new(["System", "Light", "Dark"]))
        
        # Initial value
        current_theme = self.config_manager.get("theme", "System")
        themes = ["System", "Light", "Dark"]
        if current_theme in themes:
            self.theme_row.set_selected(themes.index(current_theme))
            
        self.theme_row.connect("notify::selected", self._on_theme_changed)
        group.add(self.theme_row)

        # Page API
        api_page = Adw.PreferencesPage(title="API", icon_name="network-server-symbolic")
        self.add(api_page)
        
        api_group = Adw.PreferencesGroup(title="Gemini API")
        api_page.add(api_group)
        
        self.api_key_row = Adw.EntryRow(title="API Key")
        self.api_key_row.set_text(self.config_manager.get("api_key", ""))
        self.api_key_row.connect("notify::text", self._on_api_key_changed)
        api_group.add(self.api_key_row)

    def _on_theme_changed(self, row, pspec):
        selected = row.get_selected_item().get_string()
        self.config_manager.set("theme", selected)
        self.config_manager.save()
        self._apply_theme(selected)

    def _apply_theme(self, theme_name):
        style_manager = Adw.StyleManager.get_default()
        if theme_name == "Light":
            style_manager.set_color_scheme(Adw.ColorScheme.FORCE_LIGHT)
        elif theme_name == "Dark":
            style_manager.set_color_scheme(Adw.ColorScheme.FORCE_DARK)
        else:
            style_manager.set_color_scheme(Adw.ColorScheme.PREFER_LIGHT)

    def _on_api_key_changed(self, row, pspec):
        self.config_manager.set("api_key", row.get_text())
        self.config_manager.save()
