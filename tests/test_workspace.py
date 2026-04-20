from __future__ import annotations

import gi
import pytest

gi.require_version("Gtk", "4.0")
from gi.repository import Gtk

from ui.components.terminal_pane import TerminalPane
from ui.views.workspace import Workspace

pytestmark = pytest.mark.usefixtures("require_gtk_display")


def _make_pane() -> TerminalPane:
    return TerminalPane(terminal_factory=lambda: Gtk.TextView())


def test_workspace_initialization() -> None:
    workspace = Workspace()
    assert isinstance(workspace, Gtk.Stack)

    pages = [page.get_name() for page in workspace.get_pages()]
    assert "grid_page" in pages
    assert "focus_page" in pages


def test_workspace_focus_unfocus_restores_position() -> None:
    workspace = Workspace()
    pane = _make_pane()
    workspace.add_pane(pane)

    assert workspace.pane_positions[pane] == (0, 0)
    assert pane.get_parent() == workspace.grid

    workspace.focus_pane(pane)
    assert workspace.focused_pane == pane
    assert pane.get_parent() == workspace.focus_bin
    assert workspace.get_visible_child_name() == "focus_page"

    workspace.unfocus_pane()
    assert workspace.focused_pane is None
    assert workspace.pane_positions[pane] == (0, 0)
    assert pane.get_parent() == workspace.grid
    assert workspace.get_visible_child_name() == "grid_page"


def test_workspace_refocus_same_pane_is_idempotent() -> None:
    workspace = Workspace()
    pane = _make_pane()
    workspace.add_pane(pane)

    workspace.focus_pane(pane)
    first_parent = pane.get_parent()
    workspace.focus_pane(pane)

    assert workspace.focused_pane == pane
    assert pane.get_parent() == first_parent
    assert workspace.get_visible_child_name() == "focus_page"


def test_workspace_remove_focused_pane_returns_to_grid() -> None:
    workspace = Workspace()
    pane = _make_pane()
    other = _make_pane()
    workspace.add_pane(pane)
    workspace.add_pane(other)
    workspace.focus_pane(pane)

    removed = workspace.remove_pane(pane)
    assert removed is True
    assert workspace.focused_pane is None
    assert workspace.get_visible_child_name() == "grid_page"
    assert pane not in workspace.panes
    assert other in workspace.panes


def test_workspace_rapid_focus_unfocus_loop() -> None:
    workspace = Workspace()
    pane_a = _make_pane()
    pane_b = _make_pane()
    workspace.add_pane(pane_a)
    workspace.add_pane(pane_b)

    for _ in range(25):
        workspace.focus_pane(pane_a)
        workspace.unfocus_pane()
        workspace.focus_pane(pane_b)
        workspace.unfocus_pane()

    assert pane_a.get_parent() == workspace.grid
    assert pane_b.get_parent() == workspace.grid
    assert workspace.focused_pane is None
    assert len(workspace.panes) == 2


def test_workspace_focus_margins_follow_90_percent_rule() -> None:
    workspace = Workspace()
    workspace._update_focus_margins(width=1000, height=800)

    assert workspace.focus_bin.get_margin_start() == 50
    assert workspace.focus_bin.get_margin_end() == 50
    assert workspace.focus_bin.get_margin_top() == 40
    assert workspace.focus_bin.get_margin_bottom() == 40


def test_workspace_does_not_use_dynamic_grid_attributes() -> None:
    workspace = Workspace()
    pane = _make_pane()
    workspace.add_pane(pane)

    assert not hasattr(pane, "_grid_col")
    assert not hasattr(pane, "_grid_row")


def test_workspace_transition_flag_resets_if_focus_transition_fails(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    workspace = Workspace()
    pane = _make_pane()
    workspace.add_pane(pane)

    def _raise(_name: str) -> None:
        raise RuntimeError("transition failed")

    monkeypatch.setattr(workspace, "set_visible_child_name", _raise)

    with pytest.raises(RuntimeError):
        workspace.focus_pane(pane)

    assert workspace._is_transitioning is False
