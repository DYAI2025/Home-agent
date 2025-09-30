"""Async MongoDB helper using Motor."""

from __future__ import annotations

import logging
import os
from typing import Any, Dict, Optional

try:
    from motor.motor_asyncio import AsyncIOMotorClient
except Exception:  # pragma: no cover - dependency missing at runtime
    AsyncIOMotorClient = None  # type: ignore


class MongoDBHandler:
    """Lazily connects to MongoDB when credentials are provided."""

    def __init__(self) -> None:
        self.logger = logging.getLogger(self.__class__.__name__)
        self._uri = os.getenv("MONGODB_URI")
        self._client: Optional[AsyncIOMotorClient] = None
        self._db = None
        self._connected = False

    async def connect(self) -> None:
        if self._connected or not self._uri or AsyncIOMotorClient is None:
            if not self._uri:
                self.logger.info("No MONGODB_URI provided; using in-memory storage")
            return
        try:
            self._client = AsyncIOMotorClient(self._uri)
            self._db = self._client.get_default_database()
            self._connected = True
            self.logger.info("Connected to MongoDB database %s", self._db.name)
        except Exception as exc:  # pragma: no cover - connection failures
            self.logger.warning("MongoDB connection failed: %s", exc)
            self._client = None
            self._db = None
            self._connected = False

    async def ensure_connection(self) -> None:
        if not self._connected:
            await self.connect()

    async def get_user_data(self, user_id: str) -> Dict[str, Any]:
        if not self._connected or not self._db:
            return {}
        doc = await self._db.user_profiles.find_one({"user_id": user_id})
        return doc or {}

    async def store_user_preferences(self, user_id: str, preferences: Dict[str, Any]) -> None:
        if not self._connected or not self._db:
            return
        await self._db.user_profiles.update_one(
            {"user_id": user_id},
            {"$set": {"preferences": preferences}},
            upsert=True,
        )
