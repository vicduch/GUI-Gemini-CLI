import gi
gi.require_version('Gtk', '4.0')
from gi.repository import Gtk, Gio, GObject

class AgentItem(GObject.Object):
    __gtype_name__ = 'AgentItem'
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
        self.set_size_request(300, -1)
        self.store = Gio.ListStore(item_type=AgentItem)
        
        factory = Gtk.SignalListItemFactory()
        factory.connect("setup", self._setup_list_item)
        factory.connect("bind", self._bind_list_item)
        
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
        label.set_text(f"{item.role}: {item.agent_id} [{item.status}]")

    def update_agent(self, data: dict):
        # Update existing or add new
        agent_id = data.get("agent_id")
        for i in range(self.store.get_n_items()):
            item = self.store.get_item(i)
            if item.agent_id == agent_id:
                new_status = data.get("status", item.status)
                if new_status != item.status:
                    new_item = AgentItem(agent_id=item.agent_id, status=new_status, role=item.role)
                    self.store.splice(i, 1, [new_item])
                return
        
        new_item = AgentItem(agent_id=agent_id, status=data.get("status", "unknown"), role=data.get("role", "agent"))
        self.store.append(new_item)
