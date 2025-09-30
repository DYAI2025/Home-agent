"""Minimal multilingual processing helpers."""

from __future__ import annotations

import logging
from typing import Dict

try:
    from transformers import pipeline
except Exception:  # pragma: no cover - optional dependency guard
    pipeline = None  # type: ignore


class MultilingualProcessor:
    """Translate and keep track of the preferred language per user."""

    def __init__(self) -> None:
        self.logger = logging.getLogger(self.__class__.__name__)
        self._user_language: Dict[str, str] = {}
        self._detector = None
        if pipeline:
            try:
                self._detector = pipeline("translation", model="Helsinki-NLP/opus-mt-mul-en")
            except Exception as exc:  # pragma: no cover - model download failure
                self.logger.warning("Could not load translation pipeline: %s", exc)
                self._detector = None

    async def process_multilingual_input(self, text: str, user_id: str) -> Dict[str, str]:
        target_language = self._user_language.get(user_id, "en")
        detected_language = "en"
        processed = text
        if self._detector and target_language == "en":
            try:
                result = self._detector(text, max_length=256)
                if result and isinstance(result, list):
                    processed = result[0]["translation_text"]
                    detected_language = "auto"
            except Exception as exc:  # pragma: no cover
                self.logger.debug("Translation failed: %s", exc)

        return {
            "processed_text": processed,
            "detected_language": detected_language,
            "target_language": target_language,
        }

    async def translate_response(self, text: str, user_id: str) -> Dict[str, str]:
        target_language = self._user_language.get(user_id, "en")
        if target_language == "en" or not text:
            return {"final_response": text, "language": target_language}
        # Translation pipeline defaults to english target; since we do not ship
        # extra models, we emulate localisation with a prefix.
        translated = f"[{target_language}] {text}"
        return {"final_response": translated, "language": target_language}

    def set_user_language_preference(self, user_id: str, language: str) -> None:
        self._user_language[user_id] = language.lower()
