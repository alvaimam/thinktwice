"""Shared provider behavior used by the question generator."""

from __future__ import annotations

from typing import Protocol


class QuestionProvider(Protocol):
    def create_structured_response(
        self, model: str, instructions: str, prompt: str, schema: dict[str, object]
    ) -> str: ...
