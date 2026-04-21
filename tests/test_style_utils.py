import pytest
from gi.repository import Adw
from ui.style_utils import apply_theme

def test_apply_theme_mapping():
    # Use mocks for Adw components if possible, or just test return value if we refactor
    # But Adw.StyleManager is a singleton.
    # Let's test a helper that returns the correct Adw.ColorScheme
    from ui.style_utils import get_color_scheme_for_name
    
    assert get_color_scheme_for_name("System") == Adw.ColorScheme.DEFAULT
    assert get_color_scheme_for_name("Light") == Adw.ColorScheme.FORCE_LIGHT
    assert get_color_scheme_for_name("Dark") == Adw.ColorScheme.FORCE_DARK
    assert get_color_scheme_for_name("Unknown") == Adw.ColorScheme.DEFAULT
