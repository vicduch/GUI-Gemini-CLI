from __future__ import annotations

import logging
from collections.abc import MutableMapping
from typing import Any

_DEFAULT_FORMAT = (
    "%(asctime)s %(levelname)s %(name)s "
    "[session=%(session_id)s pid=%(process_pid)s agent=%(agent_id)s corr=%(correlation_id)s] %(message)s"
)


class ContextLoggerAdapter(logging.LoggerAdapter[logging.Logger]):
    def process(
        self,
        msg: str,
        kwargs: MutableMapping[str, Any],
    ) -> tuple[str, MutableMapping[str, Any]]:
        extra_value = kwargs.get("extra", {})
        extra: dict[str, Any] = dict(extra_value) if isinstance(extra_value, dict) else {}
        base_context: dict[str, Any] = dict(self.extra) if isinstance(self.extra, dict) else {}
        merged = {**base_context, **extra}
        merged.setdefault("session_id", "-")
        merged.setdefault("process_pid", "-")
        merged.setdefault("agent_id", "-")
        merged.setdefault("correlation_id", "-")
        kwargs["extra"] = merged
        return msg, kwargs


def configure_logging(level: int = logging.INFO) -> None:
    logging.basicConfig(level=level, format=_DEFAULT_FORMAT)


def get_logger(name: str, **context: Any) -> ContextLoggerAdapter:
    return ContextLoggerAdapter(logging.getLogger(name), context)
