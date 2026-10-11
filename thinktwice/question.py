"""Question response shape and learner answer handling."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any


LETTERS = ("A", "B", "C", "D")


@dataclass(frozen=True)
class Choice:
    letter: str
    text: str
    explanation: str
    fallacy: str | None


@dataclass(frozen=True)
class Question:
    category: str
    scenario: str
    choices: tuple[Choice, ...]
    correct_choices: frozenset[str]
    strongest_reasoning: str


def question_from_response(category: str, payload: dict[str, Any]) -> Question:
    """Validate structured model output before displaying it."""
    scenario = payload.get("scenario")
    strongest_reasoning = payload.get("strongest_reasoning")
    raw_choices = payload.get("choices")
    correct = payload.get("correct_choices")
    raw_explanations = payload.get("choice_explanations")

    if not isinstance(scenario, str) or not scenario.strip():
        raise ValueError("The generated scenario is missing.")
    if not isinstance(strongest_reasoning, str) or not strongest_reasoning.strip():
        raise ValueError("The generated reasoning is missing.")
    if not isinstance(raw_choices, list) or len(raw_choices) != 4:
        raise ValueError("The generated question must have four choices.")
    if not isinstance(correct, list) or not correct:
        raise ValueError("The generated question must have at least one correct choice.")
    if any(letter not in LETTERS for letter in correct) or len(set(correct)) != len(correct):
        raise ValueError("The generated answer key is invalid.")
    if not isinstance(raw_explanations, list) or len(raw_explanations) != 4:
        raise ValueError("The generated question must explain all four choices.")

    choice_text: dict[str, str] = {}
    for item in raw_choices:
        if not isinstance(item, dict):
            raise ValueError("A generated choice is invalid.")
        letter = item.get("letter")
        text = item.get("text")
        if letter not in LETTERS or not isinstance(text, str) or not text.strip() or letter in choice_text:
            raise ValueError("The generated choices must be labeled A, B, C, and D.")
        choice_text[letter] = text.strip()
    if set(choice_text) != set(LETTERS):
        raise ValueError("The generated choices must include A, B, C, and D.")

    explanations: dict[str, tuple[str, str | None]] = {}
    for item in raw_explanations:
        if not isinstance(item, dict):
            raise ValueError("A choice explanation is invalid.")
        letter = item.get("letter")
        explanation = item.get("explanation")
        fallacy = item.get("fallacy")
        if (
            letter not in LETTERS
            or letter in explanations
            or not isinstance(explanation, str)
            or not explanation.strip()
            or (fallacy is not None and not isinstance(fallacy, str))
        ):
            raise ValueError("The generated choice explanations are incomplete.")
        explanations[letter] = (explanation.strip(), fallacy.strip() if fallacy else None)
    if set(explanations) != set(LETTERS):
        raise ValueError("The generated response must explain all four choices.")

    choices = tuple(
        Choice(letter, choice_text[letter], *explanations[letter]) for letter in LETTERS
    )
    return Question(
        category=category,
        scenario=scenario.strip(),
        choices=choices,
        correct_choices=frozenset(correct),
        strongest_reasoning=strongest_reasoning.strip(),
    )


def parse_answer(raw: str) -> frozenset[str] | None:
    """Return normalized selected letters, or None when input is invalid."""
    parts = [part.strip().upper() for part in raw.split(",")]
    if not parts or any(part not in LETTERS for part in parts):
        return None
    if len(set(parts)) != len(parts):
        return None
    return frozenset(parts)


def is_correct(question: Question, answer: frozenset[str]) -> bool:
    return answer == question.correct_choices
