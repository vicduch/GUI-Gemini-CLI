from dataclasses import asdict, dataclass
from typing import Any


@dataclass
class ErrorContract:
    code: str
    message: str
    severity: str
    correlation_id: str

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


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
