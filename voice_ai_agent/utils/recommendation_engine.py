"""Simple recommendation engine using in-memory preferences."""

from __future__ import annotations

import asyncio
from collections import defaultdict
from dataclasses import dataclass
from typing import Any, Dict, List


@dataclass
class Recommendation:
    content: str


class RecommendationEngine:
    """Generate task suggestions and personalised hints."""

    def __init__(self) -> None:
        self._preferences: Dict[str, Dict[str, Any]] = defaultdict(dict)
        self._history: Dict[str, List[str]] = defaultdict(list)
        self._lock = asyncio.Lock()

    async def generate_recommendations(self, user_id: str, context: str = "") -> List[Recommendation]:
        async with self._lock:
            prefs = self._preferences[user_id]
            history = self._history[user_id]

            suggestions = []
            if prefs.get("focus") == "productivity":
                suggestions.append("Block 25 minutes for focused work.")
            if "call" in context.lower():
                suggestions.append("Prepare a quick agenda for your call.")
            if not suggestions:
                suggestions.append("Review your daily dashboard for new insights.")

            history.extend(suggestions)

        return [Recommendation(content=s) for s in suggestions]

    async def update_user_preferences(self, user_id: str, preferences: Dict[str, Any]) -> None:
        async with self._lock:
            self._preferences[user_id].update(preferences)

    async def personalization_summary(self, user_id: str) -> Dict[str, Any]:
        async with self._lock:
            prefs = dict(self._preferences[user_id])
            history = list(self._history[user_id][-5:])
        return {"preferences": prefs, "recent_suggestions": history}
