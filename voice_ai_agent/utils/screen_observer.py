"""Very light-weight placeholder for screen observation hooks."""

from __future__ import annotations

import logging
from datetime import datetime
from typing import Any, Dict


class ScreenObserver:
    """Collects timestamps of screen observations for analytics."""

    def __init__(self) -> None:
        self.logger = logging.getLogger(self.__class__.__name__)
        self._events: list[Dict[str, Any]] = []

    async def record_event(self, payload: Dict[str, Any]) -> None:
        event = {"timestamp": datetime.utcnow().isoformat(), **payload}
        self._events.append(event)
        self.logger.debug("Screen observation stored: %s", event)

    def recent_events(self, limit: int = 20) -> list[Dict[str, Any]]:
        return self._events[-limit:]
