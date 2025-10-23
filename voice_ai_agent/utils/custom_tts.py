"""Custom TTS service supporting multiple voice providers."""

from __future__ import annotations

import asyncio
import logging
import os
from typing import Optional, AsyncIterator
from pathlib import Path

from livekit.agents import tts


class CustomTTS(tts.TTS):
    """
    Custom TTS that supports multiple voice providers:
    - OpenAI TTS
    - ElevenLabs (with voice cloning)
    - Coqui TTS (local voice cloning)
    """

    def __init__(
        self,
        provider: str = "openai",
        voice_id: Optional[str] = None,
        model: str = "tts-1",
        voice_config: Optional[dict] = None,
    ):
        """
        Initialize custom TTS.

        Args:
            provider: TTS provider ("openai", "elevenlabs", or "coqui")
            voice_id: Voice ID (provider-specific)
            model: Model name
            voice_config: Additional provider-specific configuration
        """
        super().__init__()
        self.logger = logging.getLogger(self.__class__.__name__)
        self.provider = provider.lower()
        self.voice_id = voice_id
        self.model = model
        self.voice_config = voice_config or {}

        self._tts_impl: Optional[tts.TTS] = None
        self._initialize_tts()

    def _initialize_tts(self) -> None:
        """Initialize the appropriate TTS implementation."""
        try:
            if self.provider == "openai":
                self._init_openai_tts()
            elif self.provider == "elevenlabs":
                self._init_elevenlabs_tts()
            elif self.provider == "coqui":
                self._init_coqui_tts()
            else:
                self.logger.warning(
                    f"Unknown provider '{self.provider}', falling back to OpenAI"
                )
                self._init_openai_tts()
        except Exception as exc:
            self.logger.error(f"Failed to initialize {self.provider} TTS: {exc}")
            self.logger.info("Falling back to OpenAI TTS")
            self._init_openai_tts()

    def _init_openai_tts(self) -> None:
        """Initialize OpenAI TTS."""
        from livekit.plugins import openai as openai_plugin

        # OpenAI voices: alloy, echo, fable, onyx, nova, shimmer
        voice = self.voice_id or "nova"
        self._tts_impl = openai_plugin.TTS(
            model=self.model,
            voice=voice,
        )
        self.logger.info(f"Initialized OpenAI TTS with voice '{voice}'")

    def _init_elevenlabs_tts(self) -> None:
        """Initialize ElevenLabs TTS."""
        try:
            # Check if ElevenLabs plugin is available
            from livekit.plugins import elevenlabs as elevenlabs_plugin

            api_key = os.getenv("ELEVENLABS_API_KEY")
            if not api_key:
                raise ValueError(
                    "ELEVENLABS_API_KEY not found in environment variables"
                )

            # ElevenLabs settings
            voice_id = self.voice_id or os.getenv("ELEVENLABS_VOICE_ID")
            if not voice_id:
                self.logger.warning(
                    "No ElevenLabs voice ID provided, using default voice"
                )
                voice_id = "21m00Tcm4TlvDq8ikWAM"  # Rachel (default)

            # Voice settings
            stability = self.voice_config.get("stability", 0.5)
            similarity_boost = self.voice_config.get("similarity_boost", 0.75)

            self._tts_impl = elevenlabs_plugin.TTS(
                voice=voice_id,
                model_id=self.model or "eleven_multilingual_v2",
                api_key=api_key,
                stability=stability,
                similarity_boost=similarity_boost,
            )
            self.logger.info(
                f"Initialized ElevenLabs TTS with voice '{voice_id}'"
            )

        except ImportError:
            self.logger.error(
                "ElevenLabs plugin not available. "
                "Install with: pip install livekit-plugins-elevenlabs"
            )
            raise
        except Exception as exc:
            self.logger.error(f"Failed to initialize ElevenLabs: {exc}")
            raise

    def _init_coqui_tts(self) -> None:
        """Initialize Coqui TTS (local voice cloning)."""
        self.logger.warning(
            "Coqui TTS integration is a placeholder. "
            "Full implementation requires the TTS library and model files."
        )

        # Coqui TTS would require:
        # 1. TTS library installed: pip install TTS
        # 2. Voice sample file for cloning
        # 3. Custom LiveKit plugin or wrapper

        # For now, fall back to OpenAI
        self.logger.info("Falling back to OpenAI TTS")
        self._init_openai_tts()

        # Future implementation:
        """
        from TTS.api import TTS as CoquiTTS

        voice_file = self.voice_config.get("voice_file")
        language = self.voice_config.get("language", "de")

        self._coqui_engine = CoquiTTS(
            model_name="tts_models/multilingual/multi-dataset/xtts_v2"
        )

        # Clone voice from reference audio
        if voice_file and Path(voice_file).exists():
            self.logger.info(f"Loading voice from {voice_file}")
            # Implementation for voice cloning
        """

    def synthesize(
        self, text: str
    ) -> tts.ChunkedStream:
        """
        Synthesize speech from text.

        Args:
            text: Text to synthesize

        Returns:
            ChunkedStream containing audio chunks
        """
        if self._tts_impl is None:
            raise RuntimeError("TTS not initialized")

        return self._tts_impl.synthesize(text)

    async def aclose(self) -> None:
        """Close the TTS service."""
        if self._tts_impl is not None:
            await self._tts_impl.aclose()


# Helper function to create TTS from voice profile
def create_tts_from_profile(voice_config: dict) -> CustomTTS:
    """
    Create a CustomTTS instance from voice profile configuration.

    Args:
        voice_config: Voice configuration dict from VoiceProfileManager

    Returns:
        CustomTTS instance
    """
    provider = voice_config.get("provider", "openai")
    voice_id = voice_config.get("voice_id")
    model = voice_config.get("model", "tts-1")

    return CustomTTS(
        provider=provider,
        voice_id=voice_id,
        model=model,
        voice_config=voice_config,
    )
