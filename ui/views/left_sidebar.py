import gi

gi.require_version("Gtk", "4.0")
gi.require_version("Adw", "1")
from gi.repository import Adw, Gtk, Gio, GObject
from ui.views.left_sidebar_models import GHistoryEntry, GSkill


class LeftSidebar(Gtk.Box):
    def __init__(self, **kwargs):
        super().__init__(orientation=Gtk.Orientation.VERTICAL, **kwargs)
        self.set_size_request(250, -1)

        self.nav_view = Adw.NavigationView()
        self.append(self.nav_view)

        # Stores
        self.history_store = Gio.ListStore.new(GHistoryEntry)
        self.skills_store = Gio.ListStore.new(GSkill)

        # Pages
        self.history_page = self._create_history_page()
        self.skills_page = self._create_skills_page()

        self.nav_view.add(self.history_page)
        self.nav_view.add(self.skills_page)
        
        # Populate with dummy data
        self.history_store.append(GHistoryEntry("1", "Session 1", "2026-04-21", "gemini-1.5-pro"))
        self.history_store.append(GHistoryEntry("2", "Session 2", "2026-04-20", "gemini-1.5-flash"))
        
        self.skills_store.append(GSkill("1", "Skill Creator", "Create new skills", "builder-blocks-symbolic"))

    def push_by_tag(self, tag: str) -> None:
        self.nav_view.push_by_tag(tag)

    def pop(self) -> None:
        self.nav_view.pop()

    def get_visible_page(self) -> Adw.NavigationPage:
        return self.nav_view.get_visible_page()

    def _create_history_page(self) -> Adw.NavigationPage:
        box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)
        
        header = Adw.HeaderBar()
        skills_btn = Gtk.Button(icon_name="builder-blocks-symbolic")
        skills_btn.set_tooltip_text("Skills Hub")
        skills_btn.connect("clicked", lambda _: self.push_by_tag("skills"))
        header.pack_end(skills_btn)
        box.append(header)
        
        # History ListView
        factory = Gtk.SignalListItemFactory()
        factory.connect("setup", self._on_history_setup)
        factory.connect("bind", self._on_history_bind)
        
        selection = Gtk.SingleSelection(model=self.history_store)
        list_view = Gtk.ListView(model=selection, factory=factory)
        list_view.add_css_class("navigation-sidebar")
        
        scrolled = Gtk.ScrolledWindow()
        scrolled.set_child(list_view)
        scrolled.set_vexpand(True)
        box.append(scrolled)

        return Adw.NavigationPage(child=box, title="History", tag="history")

    def _on_history_setup(self, factory, list_item):
        label = Gtk.Label(xalign=0)
        label.set_margin_start(12)
        label.set_margin_end(12)
        label.set_margin_top(6)
        label.set_margin_bottom(6)
        list_item.set_child(label)

    def _on_history_bind(self, factory, list_item):
        item = list_item.get_item()
        label = list_item.get_child()
        label.set_text(item.title)

    def _create_skills_page(self) -> Adw.NavigationPage:
        box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)
        
        header = Adw.HeaderBar()
        box.append(header)
        
        # Skills ListView
        factory = Gtk.SignalListItemFactory()
        factory.connect("setup", self._on_skill_setup)
        factory.connect("bind", self._on_skill_bind)
        
        selection = Gtk.SingleSelection(model=self.skills_store)
        list_view = Gtk.ListView(model=selection, factory=factory)
        list_view.add_css_class("navigation-sidebar")
        
        scrolled = Gtk.ScrolledWindow()
        scrolled.set_child(list_view)
        scrolled.set_vexpand(True)
        box.append(scrolled)

        return Adw.NavigationPage(child=box, title="Skills", tag="skills")

    def _on_skill_setup(self, factory, list_item):
        box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=12)
        box.set_margin_start(12)
        box.set_margin_end(12)
        box.set_margin_top(6)
        box.set_margin_bottom(6)
        
        icon = Gtk.Image()
        label = Gtk.Label(xalign=0)
        
        box.append(icon)
        box.append(label)
        list_item.set_child(box)

    def _on_skill_bind(self, factory, list_item):
        item = list_item.get_item()
        box = list_item.get_child()
        icon = box.get_first_child()
        label = icon.get_next_sibling()
        
        icon.set_from_icon_name(item.icon)
        label.set_text(item.name)
