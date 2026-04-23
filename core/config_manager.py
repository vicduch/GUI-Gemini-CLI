import json
import os
from typing import Any

DEFAULT_MODELS = [
    "gemini-3.1-pro-preview",
    "gemini-3-flash-preview",
    "gemini-3.1-flash-lite-preview",
    "gemini-2.5-pro",
    "gemini-2.5-flash",
]


class ConfigManager:
    def __init__(self, config_path: str):
        self.config_path = config_path
        self.config: dict[str, Any] = {}
        self.load()
        if "available_models" not in self.config:
            self.config["available_models"] = DEFAULT_MODELS

    def load(self) -> None:
        if os.path.exists(self.config_path):
            try:
                with open(self.config_path, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    self.config = data if isinstance(data, dict) else {}
            except (json.JSONDecodeError, OSError):
                self.config = {}
        else:
            self.config = {}

    def save(self) -> None:
        parent_dir = os.path.dirname(self.config_path)
        if parent_dir:
            os.makedirs(parent_dir, exist_ok=True)
        with open(self.config_path, "w", encoding="utf-8") as f:
            json.dump(self.config, f, indent=4)

    def get(self, key: str, default: Any = None) -> Any:
        return self.config.get(key, default)

    def set(self, key: str, value: Any) -> None:
        self.config[key] = value
