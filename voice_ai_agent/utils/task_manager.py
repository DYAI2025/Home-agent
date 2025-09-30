"""Track simple user tasks for the cockpit."""

from __future__ import annotations

import asyncio
from typing import Any, Dict, List


class TaskManager:
    """Minimal async task list implementation."""

    def __init__(self) -> None:
        self._tasks: Dict[str, List[Dict[str, Any]]] = {}
        self._lock = asyncio.Lock()

    async def add_task(self, user_id: str, task: Dict[str, Any]) -> None:
        async with self._lock:
            self._tasks.setdefault(user_id, []).append(task)

    async def get_task_summary(self, user_id: str) -> Dict[str, Any]:
        async with self._lock:
            tasks = list(self._tasks.get(user_id, []))
        return {
            "total": len(tasks),
            "pending": [task for task in tasks if not task.get("done")],
            "completed": [task for task in tasks if task.get("done")],
        }
