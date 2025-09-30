"""Feedback collection utilities for the cockpit."""

from __future__ import annotations

import asyncio
import logging
from dataclasses import dataclass
from enum import Enum
from statistics import mean
from typing import Any, Dict, List, Optional


class FeedbackType(str, Enum):
    RATING = "rating"
    TEXT = "text"
    ISSUE = "issue"


@dataclass
class FeedbackEntry:
    user_id: str
    feedback_type: FeedbackType
    content: Any
    rating: Optional[int] = None


class FeedbackProcessor:
    """Stores feedback entries in memory and provides analytics."""

    def __init__(self) -> None:
        self.logger = logging.getLogger(self.__class__.__name__)
        self.feedback_store: List[FeedbackEntry] = []
        self._lock = asyncio.Lock()

    async def submit_rating(self, user_id: str, rating: int, comment: str = "") -> None:
        rating = max(1, min(5, rating))
        async with self._lock:
            self.feedback_store.append(
                FeedbackEntry(user_id, FeedbackType.RATING, comment, rating=rating)
            )
        self.logger.debug("Rating submitted for %s", user_id)

    async def submit_text_feedback(self, user_id: str, content: str) -> None:
        async with self._lock:
            self.feedback_store.append(
                FeedbackEntry(user_id, FeedbackType.TEXT, content)
            )
        self.logger.debug("Text feedback submitted for %s", user_id)

    async def submit_issue_report(self, user_id: str, content: Dict[str, Any]) -> None:
        async with self._lock:
            self.feedback_store.append(
                FeedbackEntry(user_id, FeedbackType.ISSUE, content)
            )
        self.logger.debug("Issue reported by %s", user_id)

    def get_user_satisfaction_score(self, user_id: str) -> float:
        ratings = [fb.rating for fb in self.feedback_store if fb.user_id == user_id and fb.rating]
        if not ratings:
            return 0.0
        return round(mean(ratings), 2)

    async def generate_feedback_report(self) -> Dict[str, Any]:
        async with self._lock:
            total = len(self.feedback_store)
            ratings = [fb.rating for fb in self.feedback_store if fb.rating]
            avg_rating = round(mean(ratings), 2) if ratings else 0.0

        return {
            "analytics": {
                "total_entries": total,
                "average_rating": avg_rating,
            },
            "improvement_suggestions": [
                "Offer more proactive reminders",
                "Provide clearer task summaries",
            ],
        }


class FeedbackIntegration:
    """Creates contextual feedback requests for the agent."""

    def __init__(self, processor: FeedbackProcessor) -> None:
        self.processor = processor

    async def get_personalized_feedback_request(self, user_id: str) -> str:
        score = self.processor.get_user_satisfaction_score(user_id)
        if score == 0:
            return "How has your experience been so far?"
        if score >= 4:
            return "Thanks for the positive feedback! Anything else I can do?"
        return "I noticed things could be better. How may I improve?"
