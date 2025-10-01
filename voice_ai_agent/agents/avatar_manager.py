"""Utility helpers for managing Ready Player Me avatars."""

from __future__ import annotations

import logging
from dataclasses import dataclass, asdict
from typing import Dict, Any


@dataclass
class AvatarProfile:
    """Simple avatar configuration returned to the frontend."""

    ready_player_me_url: str
    pose: str = "wave"
    background: str = "gradient"
    accessories: Dict[str, Any] | None = None

    def as_dict(self) -> Dict[str, Any]:
        data = asdict(self)
        data.setdefault("accessories", {})
        return data


class AvatarManager:
    """Stores avatar presets for the cockpit UI."""

    def __init__(self) -> None:
        self.logger = logging.getLogger(self.__class__.__name__)
        self._default_profile = AvatarProfile(
            ready_player_me_url=(
                "https://readyplayerme-avatars.s3.amazonaws.com/benchmark.glb?pose=standing"
            ),
            pose="standing",
            background="#1e1e2f",
            accessories={"glasses": "cyber", "outfit": "casual"},
        )

    async def get_avatar_config(self) -> Dict[str, Any]:
        self.logger.debug("Providing default avatar configuration")
        return self._default_profile.as_dict()
