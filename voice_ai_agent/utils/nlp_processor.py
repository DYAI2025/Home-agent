"""Simplistic NLU processor for intent and keyword extraction."""

from __future__ import annotations

import re
from dataclasses import dataclass
from typing import Dict, List


@dataclass
class NLUResult:
    intent: str
    keywords: List[str]
    entities: Dict[str, str]


class NLUProcessor:
    """Performs lightweight intent detection for cockpit commands."""

    _intent_keywords = {
        "reminder": ["remind", "remember", "alert"],
        "schedule": ["schedule", "appointment", "meeting"],
        "status": ["status", "state", "update"],
    }

    def __init__(self) -> None:
        self._word_pattern = re.compile(r"[\w']+")

    async def process_query(self, text: str) -> Dict[str, object]:
        tokens = [token.lower() for token in self._word_pattern.findall(text)]
        intent = "conversation"
        for candidate, keywords in self._intent_keywords.items():
            if any(word in tokens for word in keywords):
                intent = candidate
                break

        keywords = tokens[:5]
        entities: Dict[str, str] = {}
        if "pm" in tokens or "am" in tokens:
            entities["time"] = "soon"

        return {
            "intent": intent,
            "keywords": keywords,
            "entities": entities,
        }
