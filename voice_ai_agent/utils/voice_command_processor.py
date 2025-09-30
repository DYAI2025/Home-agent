"""Detects simple voice commands that should be handled instantly."""

from __future__ import annotations

from typing import Optional, Tuple


class VoiceCommandProcessor:
    """Looks for a small curated set of cockpit commands."""

    _commands = {
        "lights on": ("lights_on", "Turning the lights on."),
        "lights off": ("lights_off", "Turning the lights off."),
        "open dashboard": ("open_dashboard", "Opening the cockpit dashboard."),
    }

    async def process_text(self, text: str) -> Optional[Tuple[str, str]]:
        lowered = text.lower().strip()
        for phrase, result in self._commands.items():
            if phrase in lowered:
                return result
        return None
