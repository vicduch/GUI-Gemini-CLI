from gi.repository import GObject
from dataclasses import dataclass

class GHistoryEntry(GObject.Object):
    def __init__(self, entry_id, title, timestamp, model):
        super().__init__()
        self.id = entry_id
        self.title = title
        self.timestamp = timestamp
        self.model = model

class GSkill(GObject.Object):
    def __init__(self, skill_id, name, description, icon):
        super().__init__()
        self.id = skill_id
        self.name = name
        self.description = description
        self.icon = icon
