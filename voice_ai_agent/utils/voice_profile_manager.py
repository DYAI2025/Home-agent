"""Voice Profile Manager for personalized agent settings."""

from __future__ import annotations

import json
import logging
import os
from dataclasses import dataclass, asdict
from pathlib import Path
from typing import Dict, Any, Optional


@dataclass
class VoiceProfile:
    """Personal voice configuration for the agent."""

    # Voice settings
    voice_provider: str = "openai"  # openai, elevenlabs, or coqui
    voice_id: Optional[str] = None  # ElevenLabs voice ID or Coqui speaker name
    voice_model: str = "tts-1"  # OpenAI model or ElevenLabs model

    # Coqui-specific settings
    coqui_voice_file: Optional[str] = None  # Path to reference audio file
    coqui_language: str = "de"  # Language code for Coqui

    # ElevenLabs-specific settings
    elevenlabs_stability: float = 0.5
    elevenlabs_similarity_boost: float = 0.75
    elevenlabs_style: float = 0.0
    elevenlabs_use_speaker_boost: bool = True

    # General settings
    speaking_rate: float = 1.0
    pitch: float = 1.0
    volume: float = 1.0


@dataclass
class AvatarProfile:
    """Personal avatar configuration."""

    avatar_url: str = "https://readyplayerme-avatars.s3.amazonaws.com/benchmark.glb?pose=standing"
    pose: str = "standing"
    background: str = "#1e1e2f"
    auto_rotate: bool = True
    custom_animations: Dict[str, str] | None = None


@dataclass
class UserProfile:
    """Complete user personalization profile."""

    user_id: str = "default_user"
    display_name: str = "User"
    preferred_language: str = "de"

    voice: VoiceProfile | None = None
    avatar: AvatarProfile | None = None

    # Preferences
    greeting_message: str = "Hallo! Ich bin bereit, dir zu helfen."
    agent_personality: str = "friendly"  # friendly, professional, casual
    use_voice_cloning: bool = False

    def __post_init__(self):
        """Initialize nested profiles if not provided."""
        if self.voice is None:
            self.voice = VoiceProfile()
        elif isinstance(self.voice, dict):
            self.voice = VoiceProfile(**self.voice)

        if self.avatar is None:
            self.avatar = AvatarProfile()
        elif isinstance(self.avatar, dict):
            self.avatar = AvatarProfile(**self.avatar)


class VoiceProfileManager:
    """Manages user voice and avatar profiles."""

    def __init__(self, profile_path: Optional[str | Path] = None):
        """
        Initialize the profile manager.

        Args:
            profile_path: Path to user profile JSON file.
                         Defaults to ./user_profile.json
        """
        self.logger = logging.getLogger(self.__class__.__name__)

        if profile_path is None:
            # Look for profile in project root
            self.profile_path = Path(__file__).parent.parent.parent / "user_profile.json"
        else:
            self.profile_path = Path(profile_path)

        self.profile: Optional[UserProfile] = None
        self._load_profile()

    def _load_profile(self) -> None:
        """Load user profile from file."""
        if not self.profile_path.exists():
            self.logger.info(
                f"No user profile found at {self.profile_path}. Using defaults."
            )
            self.profile = UserProfile()
            return

        try:
            with open(self.profile_path, 'r', encoding='utf-8') as f:
                data = json.load(f)

            self.profile = UserProfile(**data)
            self.logger.info(
                f"Loaded profile for {self.profile.display_name} "
                f"(voice: {self.profile.voice.voice_provider})"
            )
        except Exception as exc:
            self.logger.error(f"Failed to load profile: {exc}")
            self.profile = UserProfile()

    def save_profile(self, profile: Optional[UserProfile] = None) -> bool:
        """
        Save user profile to file.

        Args:
            profile: Profile to save. If None, saves current profile.

        Returns:
            True if successful, False otherwise.
        """
        if profile is not None:
            self.profile = profile

        if self.profile is None:
            self.logger.error("No profile to save")
            return False

        try:
            # Convert to dict, handling nested dataclasses
            profile_dict = asdict(self.profile)

            with open(self.profile_path, 'w', encoding='utf-8') as f:
                json.dump(profile_dict, f, indent=2, ensure_ascii=False)

            self.logger.info(f"Profile saved to {self.profile_path}")
            return True
        except Exception as exc:
            self.logger.error(f"Failed to save profile: {exc}")
            return False

    def get_voice_config(self) -> Dict[str, Any]:
        """Get voice configuration for TTS system."""
        if self.profile is None or self.profile.voice is None:
            return {"provider": "openai", "model": "tts-1"}

        voice = self.profile.voice

        config = {
            "provider": voice.voice_provider,
            "model": voice.voice_model,
            "voice_id": voice.voice_id,
            "speaking_rate": voice.speaking_rate,
            "pitch": voice.pitch,
            "volume": voice.volume,
        }

        # Add provider-specific settings
        if voice.voice_provider == "elevenlabs":
            config.update({
                "stability": voice.elevenlabs_stability,
                "similarity_boost": voice.elevenlabs_similarity_boost,
                "style": voice.elevenlabs_style,
                "use_speaker_boost": voice.elevenlabs_use_speaker_boost,
            })
        elif voice.voice_provider == "coqui":
            config.update({
                "voice_file": voice.coqui_voice_file,
                "language": voice.coqui_language,
            })

        return config

    def get_avatar_config(self) -> Dict[str, Any]:
        """Get avatar configuration for frontend."""
        if self.profile is None or self.profile.avatar is None:
            return {
                "avatar_url": "https://readyplayerme-avatars.s3.amazonaws.com/benchmark.glb?pose=standing",
                "pose": "standing",
                "background": "#1e1e2f",
            }

        avatar = self.profile.avatar
        return {
            "avatar_url": avatar.avatar_url,
            "pose": avatar.pose,
            "background": avatar.background,
            "auto_rotate": avatar.auto_rotate,
            "custom_animations": avatar.custom_animations or {},
        }

    def get_user_preferences(self) -> Dict[str, Any]:
        """Get general user preferences."""
        if self.profile is None:
            return {}

        return {
            "user_id": self.profile.user_id,
            "display_name": self.profile.display_name,
            "preferred_language": self.profile.preferred_language,
            "greeting_message": self.profile.greeting_message,
            "agent_personality": self.profile.agent_personality,
            "use_voice_cloning": self.profile.use_voice_cloning,
        }

    def update_voice_settings(self, **kwargs) -> None:
        """Update voice settings."""
        if self.profile is None:
            self.profile = UserProfile()

        for key, value in kwargs.items():
            if hasattr(self.profile.voice, key):
                setattr(self.profile.voice, key, value)

        self.save_profile()

    def update_avatar_settings(self, **kwargs) -> None:
        """Update avatar settings."""
        if self.profile is None:
            self.profile = UserProfile()

        for key, value in kwargs.items():
            if hasattr(self.profile.avatar, key):
                setattr(self.profile.avatar, key, value)

        self.save_profile()
