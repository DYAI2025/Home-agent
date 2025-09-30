"""Calendar style helper for the cockpit."""

from __future__ import annotations

import asyncio
from datetime import datetime, timedelta
from typing import Any, Dict, List


class Scheduler:
    """Keeps a minimal list of upcoming events per user."""

    def __init__(self) -> None:
        self._events: Dict[str, List[Dict[str, Any]]] = {}
        self._lock = asyncio.Lock()

    async def add_event(self, user_id: str, title: str, when: datetime) -> None:
        async with self._lock:
            self._events.setdefault(user_id, []).append({
                "title": title,
                "time": when.isoformat(),
            })

    async def get_event_summary(self, user_id: str) -> Dict[str, Any]:
        async with self._lock:
            events = list(self._events.get(user_id, []))
        if not events:
            # Provide a friendly default so the UI always has data.
            next_event = {
                "title": "No upcoming events",
                "time": (datetime.utcnow() + timedelta(hours=4)).isoformat(),
            }
            events = [next_event]
        return {
            "upcoming": events[:5],
        }
