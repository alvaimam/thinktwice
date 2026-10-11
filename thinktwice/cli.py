"""Terminal entry point for the first one-question ThinkTwice slice."""

from __future__ import annotations

import argparse
import json
import os
import re
from pathlib import Path
from typing import Any

from .generator import generate_question
from .providers.openai_provider import OpenAIProvider
from .question import is_correct, parse_answer


GUIDANCE_PATH = Path(__file__).resolve().parent.parent / "data" / "question_guidance.json"
MODEL_ID = "gpt-6-luna"


def safe_error_detail(error: Exception) -> str:
    """Show a concise provider error without exposing a key if one appears in it."""
    detail = f"{type(error).__name__}: {error}"
    detail = re.sub(
        r"(?i)(incorrect api key provided:\s*)[^\"'\n]+",
        r"\1[redacted]",
        detail,
    )
    detail = re.sub(r"sk-[A-Za-z0-9_-]{8,}", "[redacted API key]", detail)
    detail = re.sub(r"(?i)Bearer\s+\S+", "Bearer [redacted]", detail)
    detail = re.sub(r"(?i)(api[_ -]?key\s*[:=]\s*)\S+", r"\1[redacted]", detail)
    return detail[:500]


def load_categories() -> list[dict[str, Any]]:
    with GUIDANCE_PATH.open(encoding="utf-8") as guidance_file:
        data = json.load(guidance_file)
    categories = data.get("categories")
    if not isinstance(categories, list) or not categories:
        raise ValueError("Question guidance does not contain categories.")
    return categories


def run_question() -> int:
    if not os.environ.get("OPENAI_API_KEY"):
        print("OpenAI API key is missing. Set OPENAI_API_KEY in your Terminal environment.")
        print("No provider request was sent. Your key is not stored in ThinkTwice files.")
        return 1

    try:
        categories = load_categories()
        provider = OpenAIProvider()
    except Exception as exc:
        print("ThinkTwice could not prepare the OpenAI question generator.")
        print(f"Details: {safe_error_detail(exc)}")
        return 1

    print(f"\nGenerating with ThinkTwice's default model ({MODEL_ID})...")
    # This early preview uses the first guided topic. The complete assessment
    # will automatically cover all seven topics; learners do not choose one.
    category_data = categories[0]

    try:
        question = generate_question(provider, MODEL_ID, category_data)
    except Exception as exc:
        print("There is currently an LLM error. Please close this Terminal window.")
        print(f"Details: {safe_error_detail(exc)}")
        return 1

    print("\nThinkTwice — practice scenario (not real news)\n")
    print(f"Topic: {question.category}")
    print(question.scenario)
    for choice in question.choices:
        print(f"{choice.letter}. {choice.text}")
    print("\nChoose one or more answers, separated by commas (example: A,B).")

    while True:
        answer = parse_answer(input("Your answer: "))
        if answer is not None:
            break
        print("That answer is invalid. Please check what you typed on the keyboard.")

    correct = is_correct(question, answer)
    print("\nCorrect." if correct else "\nNot quite.")
    print(f"Correct answer(s): {', '.join(sorted(question.correct_choices))}")
    print(f"Strongest reasoning: {question.strongest_reasoning}")
    print("\nChoice feedback:")
    for choice in question.choices:
        fallacy_note = f" Logical fallacy: {choice.fallacy}." if choice.fallacy else ""
        print(f"{choice.letter}: {choice.explanation}{fallacy_note}")
    print("\nOne-question practice complete. Your answer was checked locally.")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(description="ThinkTwice critical-thinking practice")
    parser.parse_args()
    print("ThinkTwice — one-question practice")
    print("This is a practice scenario, not real news.")
    print("The first build step is a one-question preview; the full assessment comes next.\n")
    return run_question()
