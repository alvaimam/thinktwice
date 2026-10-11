"""OpenAI API adapter for ThinkTwice's default model and structured responses."""

from __future__ import annotations


class OpenAIProvider:
    def __init__(self) -> None:
        try:
            from openai import OpenAI
        except ImportError as exc:
            raise RuntimeError("The OpenAI package is missing. Install requirements first.") from exc
        self._client = OpenAI()

    def create_structured_response(
        self, model: str, instructions: str, prompt: str, schema: dict[str, object]
    ) -> str:
        response = self._client.responses.create(
            model=model,
            instructions=instructions,
            input=prompt,
            text={
                "format": {
                    "type": "json_schema",
                    "name": "thinktwice_question",
                    "strict": True,
                    "schema": schema,
                }
            },
            store=False,
            max_output_tokens=1200,
        )
        return response.output_text or ""
