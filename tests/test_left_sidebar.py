import gi

gi.require_version("Gtk", "4.0")
gi.require_version("Adw", "1")
from gi.repository import Adw, Gtk
from ui.views.left_sidebar import LeftSidebar


def test_left_sidebar_navigation(require_gtk_display):
    sidebar = LeftSidebar()
    
    # Check initial page is history
    assert sidebar.get_visible_page().get_tag() == "history"
    
    # Trigger navigation to skills
    # We can't easily click the button in headless test, but we can call push_by_tag
    sidebar.push_by_tag("skills")
    assert sidebar.get_visible_page().get_tag() == "skills"
    
    # Pop back to history
    sidebar.pop()
    assert sidebar.get_visible_page().get_tag() == "history"
