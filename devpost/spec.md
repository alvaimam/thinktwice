---
doc: spec
status: approved
---

# ThinkTwice — Technical Spec

## How This Works, In Plain Language

ThinkTwice is a Python program that runs in Terminal. It uses OpenAI's `gpt-6-luna` model automatically; it does not ask learners to choose a model or fetch a model list. The API key comes from the computer's environment and is never written to the project or a ThinkTwice settings file.

When a quiz starts, ThinkTwice reads the seven category guides from the project's JSON file. It presents each category's short learning note, then generates and asks five questions in that category before continuing to the next one. The learner does not choose topics. The provider returns each practice question, four choices, the correct choice or choices, and explanations in a structured format. ThinkTwice shows the learner only the question and choices. The learner's answer stays in the running program; Python checks it locally, shows the prepared explanations, and updates the score in memory. After 35 questions, the program prints the result and then discards the session data when it exits.

The only information sent to OpenAI is the fixed model ID, category/topic guidance, instructions, and structured-output schema needed to generate each question. ThinkTwice does not send names, learner answers, or quiz results. Provider calls are required for this feature and may incur charges according to the model. The app does not call the provider until a learner with an API key starts question generation.

## The Core Journey Through the System

PRD ref: `prd.md > The Core Journey`.

```text
Learner starts ThinkTwice
  → CLI reads OPENAI_API_KEY from the environment
  → ThinkTwice selects the fixed model gpt-6-luna automatically
  → quiz reads JSON category guidance and teaches each short category note
  → quiz automatically generates five questions for each of the seven categories
  → selected adapter requests a structured question from the provider
  → learner chooses A, B, C, or D (possibly more than one)
  → local scorer compares the selection with the answer key
  → CLI shows feedback and stores category totals in memory
  → after question 35, CLI prints pass/fail and category results
  → session data disappears when ThinkTwice exits
```

## Stack

- **Python 3.11 or newer** for a familiar language and straightforward Terminal interaction. [Python documentation](https://docs.python.org/3/).
- **Python standard library** for command-line input, JSON guidance/configuration, paths, and local scoring; no web framework or database.
- **OpenAI Python SDK** for question generation using `gpt-6-luna`. [Official Python SDK](https://github.com/openai/openai-python), [OpenAI Responses API quickstart](https://developers.openai.com/api/docs/quickstart?api-mode=responses), [Structured Outputs](https://developers.openai.com/api/docs/guides/structured-outputs?api-mode=responses).

The OpenAI SDK handles provider-specific request formatting; the quiz and scoring code use one shared question shape. The exact installed SDK version will be pinned during the build after checking the current official release documentation.

## Where It Runs and How Someone Tries It

- **Runtime:** local Python process in Terminal on the learner's computer. No web hosting, login, database, or deployment is needed for this proof of concept.
- **Requirements:** Python 3.11+, internet access for question requests, and an OpenAI API account/key with access to `gpt-6-luna`.
- **Keys:** `OPENAI_API_KEY`, configured in the learner's shell environment. ThinkTwice never writes the key into project files or settings.
- **Start a quiz:** from the project directory, run `python3.11 -m thinktwice`.
- **Model:** the preview automatically uses `gpt-6-luna`; there is no model-selection prompt or model-list request.
- **Demo recording:** use the same local Terminal command and show the practice notice, a generated practice question, feedback, and the final pass/fail/category summary. A full 35-question run is the product behavior; any shorter demo sequence must be clearly labeled as a preview rather than a complete assessment.

The Devpost submission still requires a short demo video and public GitHub repository. Deployment is optional and is not part of this local proof of concept.

## Look and Feel

Readable plain Terminal text, short lines, and clear numbered prompts. The tone is respectful and direct for people aged 12 and up. Always label generated challenges as practice scenarios, not real news. Error messages should state the next action in plain language.

## Components

### Terminal app

Starts the quiz and uses the fixed OpenAI model `gpt-6-luna`. It has no Settings or model-selection prompt in this proof of concept. Implements `prd.md > The Core Journey`, `Screens and Layout`, and `States and Boundaries`.

### Provider credentials

The OpenAI SDK reads `OPENAI_API_KEY` from the process environment. Missing credentials block the external request and produce setup instructions. No key, learner identity, answer, or result is stored in a project file. Implements `prd.md > States and Boundaries` and `Product Decisions`.

### Question guidance and generator

Loads the fixed category, learner-facing learning note, and question-type guide from `data/question_guidance.json`. The quiz presents each learning note before its five-question group; for each question, the generator combines the relevant category guidance with a prompt that asks `gpt-6-luna` to create an age-appropriate practice scenario, four choices, one or more correct choices, reasoning for the strongest answer, and explanations of the other choices. Uses a structured JSON response schema and validates the response before showing it. One provider request generates one question, so a complete session makes 35 generation requests. Implements `prd.md > Session and Questions`.

### Provider adapters

`OpenAIProvider` sends a structured question-generation request to `POST /v1/responses` using `gpt-6-luna` and `store: false`. It makes no model-list request. Provider errors include a short sanitized diagnostic below the learner-facing error message. Implements `prd.md > Session and Questions` and `States and Boundaries`.

### Quiz, input, and local scoring

Runs the 35-question sequence with exactly five questions assigned to each of the seven categories. Parses comma-separated letters, rejects invalid entries without advancing, and scores all-or-nothing: all correct choices and no extra incorrect choice must be selected. It calculates pass at 28/35 or higher and aggregates category totals entirely in memory. Learner selections are not sent to either provider. Implements `prd.md > Session and Questions`, `Feedback and Results`, and `States and Boundaries`.

### Feedback and final summary

Displays correctness and the generated explanation after each answer. At the end, prints the score, percentage, pass/fail, and category-level correct/incorrect counts with missed-reasoning feedback. Implements `prd.md > Feedback and Results` and `Screens and Layout`.

## Data Model

- **Question guidance:** static project-authored JSON with seven category IDs and question-type/topic instructions. It contains guidance, not a question bank or personal information.
- **Question:** one in-memory object containing category, scenario text, four choice strings, correct choice letters, explanation of the strongest reasoning, and explanations of alternative choices/fallacies.
- **Answer and result:** selected letters, correctness, and category counters exist only in process memory for the active session. No identity is requested and no results are saved after exit.
- **Model:** `gpt-6-luna`, fixed in the application for this proof of concept.

## File Structure

```text
thinktwice-project/
├── thinktwice/
│   ├── __init__.py                 # Python package marker
│   ├── __main__.py                 # `python3 -m thinktwice` entry point
│   ├── cli.py                      # Start screen, prompts, and output
│   ├── question.py                 # Shared question shape and validation
│   ├── generator.py                # Builds prompt and requests one question
│   ├── quiz.py                     # 35-question flow and answer input
│   ├── scoring.py                  # Local scoring and category aggregation
│   └── providers/
│       ├── __init__.py             # Provider adapter exports
│       ├── base.py                 # Shared provider interface
│       └── openai_provider.py      # GPT-6 Luna Responses API call
├── data/
│   └── question_guidance.json      # Fixed categories and question-type guidance
├── requirements.txt               # OpenAI SDK
├── README.md                       # Install, key setup, settings, run instructions
└── devpost/                        # Learner planning documents
```

## External Services and Dependencies

### OpenAI API

- **Calls:** `POST https://api.openai.com/v1/responses` once for each generated question. No model-list request is made.
- **Request content:** fixed model ID `gpt-6-luna`, category/topic guidance, generation instructions, and a JSON schema for the question. No learner answer, identity, or result is included.
- **Key:** `OPENAI_API_KEY`, read by the official Python SDK from the local environment.
- **Retention:** OpenAI states API data is not used for training by default. Its Responses endpoint has up to 30-day abuse-monitoring retention by default; `store: false` avoids Responses application-state storage but does not remove abuse-monitoring retention. See [OpenAI data controls](https://developers.openai.com/api/docs/guides/your-data).
- **Cost:** the user pays usage charges for `gpt-6-luna` through their OpenAI API account. See [OpenAI API pricing](https://developers.openai.com/api/docs/pricing).
- **Docs:** [Responses API](https://developers.openai.com/api/docs/quickstart?api-mode=responses), [GPT-6 model guidance](https://developers.openai.com/api/docs/models), [Structured Outputs](https://developers.openai.com/api/docs/guides/structured-outputs?api-mode=responses).

OpenAI receives the question-generation data because live generation is the product's core feature. The user should check the provider's current model access, pricing, and retention terms. No learner answers or personal information are sent.

## Important Failure Modes

- **Missing/invalid API key** → explain which environment variable is needed and do not start or continue the provider call.
- **Default model unavailable** → show the agreed generation-error message and a short sanitized provider detail; do not ask the learner to select another model.
- **Generation failure, malformed JSON, or unsupported model** → show the agreed LLM-error message and tell the learner to close Terminal; do not score an incomplete question.
- **Invalid answer letters** → explain the input is invalid and ask the learner to check what they typed; keep the same question open.

## What Was Simplified and Why

- A local Terminal program instead of the planned future web version — keeps the proof of concept aligned with the approved first experience and avoids hosting/accounts.
- One learner session held in memory instead of accounts, a database, or saved results — proves the learning and assessment loop without collecting learner identity or history.
- One fixed OpenAI model for this proof of concept — avoids making a learner choose among models with different API capabilities; provider switching remains a possible later enhancement.
- One question request at a time — keeps question creation and feedback easy to follow; the tradeoff is 35 model calls and possible provider latency during a full session.

## Decisions and Open Issues

- **Learner decision:** use Python and a Terminal app. Rationale: Python is familiar, while the CLI keeps the first version small. Tradeoff: it is not yet convenient for broad public use like a hosted web app.
- **Learner decision:** use OpenAI `gpt-6-luna` automatically, without a model-selection prompt. Tradeoff: this model must be available to the user's API account; provider switching and alternate models are deferred.
- **Learner decision:** read the API key from the environment and never store it in project files. Tradeoff: users must configure their shell environment.
- **Privacy boundary:** answers, names, and results stay local; only category guidance and the generation request go to OpenAI. Provider retention terms still apply to those prompts and generated questions.
- **Useful uncertainty clarified:** the user's API rejected `gpt-4` because that model does not support the Structured Outputs format used by ThinkTwice. The app now uses the documented compatible default `gpt-6-luna` instead of asking a learner to choose.
