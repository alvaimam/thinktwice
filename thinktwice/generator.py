"""Prompt construction and validation for generated questions."""

from __future__ import annotations

import json

from .providers.base import QuestionProvider
from .question import Question, question_from_response


QUESTION_SCHEMA: dict[str, object] = {
    "type": "object",
    "properties": {
        "scenario": {"type": "string"},
        "choices": {
            "type": "array",
            "items": {
                "type": "object",
                "properties": {
                    "letter": {"type": "string", "enum": ["A", "B", "C", "D"]},
                    "text": {"type": "string"},
                },
                "required": ["letter", "text"],
                "additionalProperties": False,
            },
        },
        "correct_choices": {
            "type": "array",
            "items": {"type": "string", "enum": ["A", "B", "C", "D"]},
        },
        "strongest_reasoning": {"type": "string"},
        "choice_explanations": {
            "type": "array",
            "items": {
                "type": "object",
                "properties": {
                    "letter": {"type": "string", "enum": ["A", "B", "C", "D"]},
                    "explanation": {"type": "string"},
                    "fallacy": {"type": ["string", "null"]},
                },
                "required": ["letter", "explanation", "fallacy"],
                "additionalProperties": False,
            },
        },
    },
    "required": [
        "scenario",
        "choices",
        "correct_choices",
        "strongest_reasoning",
        "choice_explanations",
    ],
    "additionalProperties": False,
}

QUESTION_INSTRUCTIONS = (
    "You write age-appropriate critical-thinking practice for learners aged 12 and up. "
    "Create a fictional, realistic social-media scenario. It is not real news and must "
    "not name real people or present invented claims as facts. Write four plausible "
    "choices A-D, one or more correct choices, a clear explanation of the strongest "
    "reasoning, and an explanation for every choice. Name a logical fallacy only when "
    "one is actually present; otherwise use null. Keep the language concise and kind. "
    "Do not ask the learner for personal information."
    "Include confusing correlation with causation as a possible reasoning error: a scenario may describe two things that occur together or change together, then incorrectly claim that one caused the other without sufficient evidence. When appropriate, test whether the learner can recognize that correlation alone does not establish causation. Do not label a claim as fallacious merely because it describes a correlation; explain what additional evidence would be needed to support a causal conclusion."
)


def generate_question(provider: QuestionProvider, model: str, category: dict[str, object]) -> Question:
    category_name = str(category["name"])
    prompt = (
        f"Create one question in the category {category_name!r}. "
        f"Use this topic and question-type guidance: {json.dumps(category, ensure_ascii=False)}"
    )
    response_text = provider.create_structured_response(
        model, QUESTION_INSTRUCTIONS, prompt, QUESTION_SCHEMA
    )
    if not response_text:
        raise ValueError("The model returned no question text.")
    try:
        payload = json.loads(response_text)
    except json.JSONDecodeError as exc:
        raise ValueError("The model response was not valid JSON.") from exc
    if not isinstance(payload, dict):
        raise ValueError("The model response was not a question object.")
    return question_from_response(category_name, payload)
