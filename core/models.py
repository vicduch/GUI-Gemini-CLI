from dataclasses import asdict, dataclass


@dataclass
class ErrorContract:
    code: str
    message: str
    severity: str
    correlation_id: str

    def to_dict(self) -> dict:
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
