import gi
import pytest

gi.require_version("Gtk", "4.0")
from core.models import Agent
from ui.views.right_sidebar import AgentMonitorSidebar

pytestmark = pytest.mark.usefixtures("require_gtk_display")


def test_agent_monitor_adds_agent():
    sidebar = AgentMonitorSidebar()
    sidebar.update_agent(Agent(id="agent-1", status="running", role="subagent"))
    assert sidebar.store.get_n_items() == 1


def test_agent_monitor_updates_status():
    sidebar = AgentMonitorSidebar()
    sidebar.update_agent(Agent(id="agent-1", status="running", role="subagent"))
    sidebar.update_agent(Agent(id="agent-1", status="completed", role="subagent"))

    item = sidebar.store.get_item(0)
    assert item.status == "completed"


def test_agent_monitor_handles_partial_data():
    sidebar = AgentMonitorSidebar()
    # Initial add
    sidebar.update_agent(Agent(id="agent-1", status="running", role="subagent"))
    # Update with Agent object (partial updates are handled by the controller logic usually,
    # but here we test the sidebar's robustness to the Agent object it receives)
    sidebar.update_agent(Agent(id="agent-1", status="failed", role="subagent"))
    item = sidebar.store.get_item(0)
    assert item.status == "failed"
