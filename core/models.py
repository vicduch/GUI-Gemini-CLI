from dataclasses import dataclass


@dataclass
class Session:
    id: str
    model: str
    workspace: str


@dataclass
class Agent:
    id: str
    status: str
    role: str
