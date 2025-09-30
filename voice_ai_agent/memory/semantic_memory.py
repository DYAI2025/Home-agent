"""Semantic memory placeholder storing facts per user."""

from __future__ import annotations

import asyncio
from typing import Any, Dict, List


class SemanticMemory:
    """Persist key-value knowledge for a user."""

    def __init__(self) -> None:
        self._knowledge: Dict[str, Dict[str, Any]] = {}
        self._lock = asyncio.Lock()

    async def store_fact(self, user_id: str, key: str, value: Any) -> None:
        async with self._lock:
            self._knowledge.setdefault(user_id, {})[key] = value

    async def retrieve_facts(self, user_id: str) -> Dict[str, Any]:
        async with self._lock:
            return dict(self._knowledge.get(user_id, {}))
