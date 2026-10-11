---
doc: checklist
status: approved
---

# Build Checklist

Build mode: learn

## Slices

- [ ] **1. You can generate and answer one live practice question**
  Becomes usable: A local Terminal preview uses OpenAI `gpt-6-luna` automatically, generates one practice question from the first JSON category, accepts comma-separated answer letters, scores locally, and shows the model's explanations and safe error details.
  Why now: This exercises the unique kernel—LLM-created scenarios and reasoning feedback—before we build the larger 35-question assessment around it.
  PRD ref: `prd.md > The Core Journey`, `Features and Behavior > Session and Questions`, `Feedback and Results`
  Spec ref: `spec.md > Stack`, `Components > Question guidance and generator`, `Components > Provider adapters`, `Components > Quiz, input, and local scoring`, `External Services and Dependencies`
  Build: Bootstrap the Python package, add the question guidance JSON and shared question shape, install the OpenAI SDK, generate a structured question with fixed default model `gpt-6-luna`, accept and locally score an answer, and display the feedback. Do not fetch a model list or ask the learner to select one. Read the API key only from `OPENAI_API_KEY`; never store it in project files.
  Verify (mechanical): Run `python3.11 -m compileall thinktwice` and `python3.11 -m thinktwice --help`; with `OPENAI_API_KEY` removed from that process, run `python3.11 -m thinktwice` and confirm it exits with a clear missing-key message before attempting a provider request.
  Learner check: Set your OpenAI API key in your own Terminal without sharing it here. Run the preview, answer its generated first-topic question, and tell me whether the scenario and feedback make sense.
  Commit: `Add first live ThinkTwice challenge`

- [ ] **2. The assessment covers all seven topics and reports pass/fail**
  Becomes usable: One complete session teaches a short basic idea for each category and then asks five questions in each of the seven categories without asking the learner to choose a topic or model. It scores each all-or-nothing, shows immediate feedback, and ends with the 80% pass/fail result and category breakdown.
  Why now: The one-question preview establishes dynamic question generation. This slice delivers the full learning and assessment journey without extra setup choices.
  PRD ref: `prd.md > The Core Journey`, `Screens and Layout`, `Features and Behavior > Session and Questions`, `States and Boundaries`, `Product Decisions`
  Spec ref: `spec.md > Components > Quiz, input, and local scoring`, `Components > Feedback and final summary`, `Data Model`, `Important Failure Modes`
  Build: Add the 35-question category sequence, short learner-friendly category notes from JSON, comma-separated validation and retry, all-or-nothing scoring, immediate feedback, category totals and explanations, final pass/fail, 80% threshold, generation-error message, and run/setup instructions in `README.md`.
  Verify (mechanical): Run `python3.11 -m compileall thinktwice` and launch ThinkTwice without provider keys to confirm it stops before the first question with the expected setup message. Inspect the 35-question category allocation and scoring path in the running implementation; do not send learner answers to either provider.
  Learner check: With your OpenAI key configured locally, complete a full session; try a malformed answer once, then finish and check the 35-question count, category breakdown, and pass/fail result.
  Commit: `Complete ThinkTwice assessment flow`

## Hands-on Checkpoints

- [ ] Early usable behavior explored — after slice 1, try one live generated question and give feedback on its realism and explanation.
- [ ] Final kick-the-tires exploration and feedback completed — after slice 3, try the full assessment and note anything confusing or broken.

## Final Review

- [ ] Final review complete — feedback resolved and learner confirms ready to ship

## Code Tour and App Map

- [ ] Learning activity complete — guided route, focused alternative, prior practice connected, or brief recap
- [ ] Optional edit and transfer reflection addressed — offered/declined/already covered/not applicable as appropriate
- [ ] `devpost/app-map.html` generated from finished code, checked, and shown, including a project-grounded practice to reuse

Activity and evidence: [record after build]
Route and stops: [record actual source paths and symbols]
Edit outcome: [record tried/kept/reverted/declined/not applicable]
Reflection: [record offered/answered/declined/already covered; personal response belongs only in ignored profile]
Activity mode: [record live app/editor or explicit static fallback]

## Revisions

- The learner asked that the assessment start directly and cover all seven categories, with five questions per category, rather than asking the test taker to choose a topic. Add a short basic learning note before each category group. The one-question build slice remains a preview so the LLM-generated question flow can be tried before the full assessment is assembled.
- The learner saw an LLM error with no underlying explanation. Slice 1 now prints a brief sanitized error detail so model compatibility, account, connection, or response errors can be distinguished without exposing an API key.
- The learner's error detail identified `gpt-4` as incompatible with the Structured Outputs request. The learner asked ThinkTwice to use OpenAI `gpt-6-luna` automatically, with no model-list request or model-selection prompt. OpenAI documents GPT-6 models as supporting Structured Outputs. Provider access can still vary by account; the app will show a sanitized error if the configured model is unavailable.
