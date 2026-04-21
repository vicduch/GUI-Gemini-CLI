import gi

gi.require_version("Gtk", "4.0")
gi.require_version("Adw", "1")
from gi.repository import Adw, Gtk


class LeftSidebar(Gtk.Box):
    def __init__(self, **kwargs):
        super().__init__(orientation=Gtk.Orientation.VERTICAL, **kwargs)
        self.set_size_request(250, -1)

        self.nav_view = Adw.NavigationView()
        self.append(self.nav_view)

        # Pages
        self.history_page = self._create_history_page()
        self.skills_page = self._create_skills_page()

        self.nav_view.add(self.history_page)
        self.nav_view.add(self.skills_page)

    def push_by_tag(self, tag: str) -> None:
        self.nav_view.push_by_tag(tag)

    def pop(self) -> None:
        self.nav_view.pop()

    def get_visible_page(self) -> Adw.NavigationPage:
        return self.nav_view.get_visible_page()

    def _create_history_page(self) -> Adw.NavigationPage:
        box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)
        
        header = Adw.HeaderBar()
        # Bouton pour aller aux Skills
        skills_btn = Gtk.Button(icon_name="builder-blocks-symbolic")
        skills_btn.set_tooltip_text("Skills Hub")
        skills_btn.connect("clicked", lambda _: self.push_by_tag("skills"))
        header.pack_end(skills_btn)
        
        box.append(header)
        
        # History List Placeholder
        list_box = Gtk.ListBox()
        list_box.set_selection_mode(Gtk.SelectionMode.SINGLE)
        list_box.append(Gtk.Label(label="History Item 1", xalign=0))
        list_box.append(Gtk.Label(label="History Item 2", xalign=0))
        
        scrolled = Gtk.ScrolledWindow()
        scrolled.set_child(list_box)
        scrolled.set_vexpand(True)
        box.append(scrolled)

        return Adw.NavigationPage(child=box, title="History", tag="history")

    def _create_skills_page(self) -> Adw.NavigationPage:
        box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)
        
        header = Adw.HeaderBar()
        box.append(header)
        
        # Skills Hub Placeholder
        label = Gtk.Label(label="Skills Hub\n(Coming Soon)", vexpand=True)
        box.append(label)

        return Adw.NavigationPage(child=box, title="Skills", tag="skills")
