"""Utility helpers for managing Ready Player Me avatars."""

from __future__ import annotations

import logging
from dataclasses import dataclass, asdict
from typing import Dict, Any, Optional


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
    """Manages avatar configuration with personalization support."""

    def __init__(self, voice_profile_manager: Optional[Any] = None) -> None:
        """
        Initialize avatar manager.

        Args:
            voice_profile_manager: Optional VoiceProfileManager instance
                                  for loading personalized avatars
        """
        self.logger = logging.getLogger(self.__class__.__name__)
        self.profile_manager = voice_profile_manager

        self._default_profile = AvatarProfile(
            ready_player_me_url=(
                "https://readyplayerme-avatars.s3.amazonaws.com/benchmark.glb?pose=standing"
            ),
            pose="standing",
            background="#1e1e2f",
            accessories={"glasses": "cyber", "outfit": "casual"},
        )

    async def get_avatar_config(self) -> Dict[str, Any]:
        """
        Get avatar configuration, preferring personalized settings.

        Returns:
            Dict with avatar configuration
        """
        # Try to get personalized avatar from profile manager
        if self.profile_manager is not None:
            try:
                avatar_config = self.profile_manager.get_avatar_config()
                self.logger.info(
                    f"Using personalized avatar: {avatar_config.get('avatar_url', 'N/A')[:60]}..."
                )
                return avatar_config
            except Exception as exc:
                self.logger.warning(
                    f"Failed to load personalized avatar: {exc}. Using default."
                )

        # Fall back to default
        self.logger.debug("Providing default avatar configuration")
        return self._default_profile.as_dict()

    def set_custom_avatar(self, avatar_url: str, **kwargs) -> None:
        """
        Set a custom avatar URL and save to profile.

        Args:
            avatar_url: Ready Player Me avatar URL
            **kwargs: Additional avatar settings (pose, background, etc.)
        """
        if self.profile_manager is None:
            self.logger.warning("No profile manager available to save avatar")
            return

        try:
            self.profile_manager.update_avatar_settings(
                avatar_url=avatar_url,
                **kwargs
            )
            self.logger.info(f"Custom avatar saved: {avatar_url[:60]}...")
        except Exception as exc:
            self.logger.error(f"Failed to save custom avatar: {exc}")
