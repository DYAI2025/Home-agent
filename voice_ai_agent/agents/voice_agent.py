"""Core conversational agent used by the integrated system."""

from __future__ import annotations

import logging
import os
from typing import Optional

try:  # Optional dependency if an API key is provided
    from openai import AsyncOpenAI
except Exception:  # pragma: no cover - import guard for environments without openai
    AsyncOpenAI = None  # type: ignore


class VoiceAIAgent:
    """Simple orchestrator around the LLM or a rule-based fallback."""

    def __init__(self) -> None:
        self.logger = logging.getLogger(self.__class__.__name__)
        api_key = os.getenv("OPENAI_API_KEY")
        self._client: Optional[AsyncOpenAI] = None
        if AsyncOpenAI and api_key:
            try:
                self._client = AsyncOpenAI(api_key=api_key)
                self.logger.debug("AsyncOpenAI client initialised")
            except Exception as exc:  # pragma: no cover - network failures
                self.logger.warning("Failed to initialise OpenAI client: %s", exc)
                self._client = None

        self._fallback_responses = [
            "I am ready to help you with your tasks.",
            "Let's work together to get things done.",
            "How can I support you today?",
        ]

    async def process_user_query(self, text: str, user_id: str) -> str:
        """Return a response for the provided user query."""

        cleaned = text.strip()
        if not cleaned:
            return "I didn't quite catch that. Could you repeat it?"

        if self._client is None:
            # Provide a deterministic but friendly fallback response.
            idx = abs(hash((user_id, cleaned))) % len(self._fallback_responses)
            response = self._fallback_responses[idx]
            self.logger.debug("Fallback response selected: %s", response)
            return response

        prompt = (
            "You are an empathetic voice assistant that controls a smart home "
            "cockpit. Provide concise and actionable replies."
        )
        try:
            result = await self._client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {"role": "system", "content": prompt},
                    {"role": "user", "content": cleaned},
                ],
                max_tokens=200,
            )
        except Exception as exc:  # pragma: no cover - network/API failure
            self.logger.warning("OpenAI request failed: %s", exc)
            idx = abs(hash(("error", cleaned))) % len(self._fallback_responses)
            return self._fallback_responses[idx]

        message = result.choices[0].message.content if result.choices else None
        if not message:
            return "I am here if you need anything else."
        return message.strip()
