"""Tracks conversation episodes."""

from __future__ import annotations

import asyncio
from collections import defaultdict
from datetime import datetime, timedelta
from typing import Dict, List


class EpisodicMemory:
    """Maintain chronological conversation entries."""

    def __init__(self) -> None:
        self._interactions: Dict[str, List[Dict[str, str]]] = defaultdict(list)
        self._lock = asyncio.Lock()

    async def store_interaction(self, user_id: str, text: str, *, is_response: bool = False) -> None:
        async with self._lock:
            self._interactions[user_id].append(
                {
                    "timestamp": datetime.utcnow().isoformat(),
                    "text": text,
                    "role": "agent" if is_response else "user",
                }
            )

    async def summarize_session(self, user_id: str, start: datetime, end: datetime) -> Dict[str, str]:
        async with self._lock:
            entries = [entry for entry in self._interactions[user_id] if start.isoformat() <= entry["timestamp"] <= end.isoformat()]
        summary = f"Session between {start.isoformat()} and {end.isoformat()} with {len(entries)} turns."
        return {"summary": summary}

    async def clear_old_interactions(self, user_id: str, days_to_keep: int = 30) -> None:
        cutoff = datetime.utcnow() - timedelta(days=days_to_keep)
        async with self._lock:
            self._interactions[user_id] = [
                entry for entry in self._interactions[user_id]
                if datetime.fromisoformat(entry["timestamp"]) >= cutoff
            ]
