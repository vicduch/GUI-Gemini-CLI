import gi
gi.require_version("Gtk", "4.0")
from gi.repository import Gtk
from ui.views.right_sidebar import AgentMonitorSidebar

def test_agent_monitor_adds_agent():
    sidebar = AgentMonitorSidebar()
    sidebar.update_agent({"agent_id": "agent-1", "status": "running", "role": "subagent"})
    assert sidebar.store.get_n_items() == 1

def test_agent_monitor_updates_status():
    sidebar = AgentMonitorSidebar()
    sidebar.update_agent({"agent_id": "agent-1", "status": "running", "role": "subagent"})
    sidebar.update_agent({"agent_id": "agent-1", "status": "completed"})
    
    item = sidebar.store.get_item(0)
    assert item.status == "completed"

