import gi

gi.require_version("Gtk", "4.0")
from gi.repository import Gio, GObject, Gtk

from core.models import Agent


class AgentItem(GObject.Object):
    __gtype_name__ = "AgentItem"
    agent_id = GObject.Property(type=str)
    status = GObject.Property(type=str)
    role = GObject.Property(type=str)

    def __init__(self, agent_id, status, role):
        super().__init__()
        self.agent_id = agent_id
        self.status = status
        self.role = role


class AgentMonitorSidebar(Gtk.Box):
    def __init__(self, **kwargs):
        super().__init__(orientation=Gtk.Orientation.VERTICAL, **kwargs)
        self.store = Gio.ListStore(item_type=AgentItem)
        self._agent_cache: dict[str, AgentItem] = {}

        factory = Gtk.SignalListItemFactory()
        factory.connect("setup", self._setup_list_item)
        factory.connect("bind", self._bind_list_item)
        factory.connect("unbind", self._unbind_list_item)

        selection = Gtk.SingleSelection(model=self.store)
        list_view = Gtk.ListView(model=selection, factory=factory)

        scroll = Gtk.ScrolledWindow()
        scroll.set_child(list_view)
        scroll.set_vexpand(True)

        self.append(Gtk.Label(label="Agent Swarm Monitor", margin_top=10, margin_bottom=10))
        self.append(scroll)

    def _setup_list_item(self, factory, list_item):
        label = Gtk.Label(halign=Gtk.Align.START, margin_start=10)
        list_item.set_child(label)

    def _bind_list_item(self, factory, list_item):
        item = list_item.get_item()
        label = list_item.get_child()

        def update_label(*args):
            label.set_text(f"{item.role}: {item.agent_id} [{item.status}]")

        update_label()  # Initial set
        handler_id = item.connect("notify::status", update_label)
        list_item._handler_id = handler_id

    def _unbind_list_item(self, factory, list_item):
        item = list_item.get_item()
        handler_id = getattr(list_item, "_handler_id", None)
        if handler_id and item:
            item.disconnect(handler_id)
            list_item._handler_id = None

    def update_agent(self, agent: Agent):
        if agent.id in self._agent_cache:
            item = self._agent_cache[agent.id]
            if item.status != agent.status:
                item.status = agent.status
        else:
            new_item = AgentItem(agent_id=agent.id, status=agent.status, role=agent.role)
            self._agent_cache[agent.id] = new_item
            self.store.append(new_item)
