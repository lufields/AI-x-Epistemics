# Pilot (v1): factual questions, 14–15 Nov 2026

This folder keeps the data of the first design, which was replaced by the concept-based design in `../data`. It is not part of the paper's results.

## What was asked

150 short factual questions, each with a source (`pilot_questions.csv`):

- **A01–A50, stable facts**: facts that did not change before the models' training cutoffs.
- **B01–B50, changed facts**: facts that changed in 2025–2026 (for example, who leads an AI safety institute).
- **C01–C50, invented entities**: papers, people or events that do not exist. The right answer is to say so.

Models: `anthropic/claude-fable-5.2`, `openai/gpt-6-astra`, `google/gemini-4-argon`, via OpenRouter, default temperature, reasoning effort "low".

## Conditions (`pilot_answers.csv`, column `condition`)

| condition | system prompt | runs |
|---|---|---|
| `main` | asked for JSON with `answer`, `unknown` and `confidence`, and told the model to say when it does not know | 1 |
| `natural` | only "Today's date is November 14, 2026."; the question was followed by "How confident are you that your answer is correct? Give a number from 0 to 100." | 3 |
| `forced` | told the model to always give a best guess (types B and C only) | 1, stopped early (283 of 300 answers) |

## Grades

- `main`: graded by hand by Claude (Opus 5.5) against the source of each question.
- `natural` and `forced`: graded by an automatic rule (key-term match, plus phrases such as "I'm not aware of"). Answers the rule could not decide are marked "not graded (needs manual review)". They were never reviewed, because the design changed.

## What the pilot showed, and why the design changed

- **Type A**: all three models answered all 50 correctly in `main`. These questions cannot tell the models apart.
- **Type C**: in `main`, all 150 answers said the entity was unknown. In `natural` (3 runs × 150 answers), there were 3 fabrications, all from GPT-6 Astra on C24, with stated confidence 65–80.
- **Type B**, `main` run, hand-graded:

  | model | correct | partial | incorrect (outdated) | abstained |
  |---|---|---|---|---|
  | Fable 5.2 | 37 | 3 | 5 | 5 |
  | GPT-6 Astra | 27 | 0 | 2 | 21 |
  | Gemini 4 Argon | 4 | 0 | 0 | 46 |

- **Confidence numbers changed meaning.** Gemini sometimes reported 95 meaning "I am sure this does not exist", and sometimes 0 for the same kind of answer.

Because A and C were at ceiling, the study moved to questions about AI safety concepts. These have three questions per concept, including a false premise for invented terms.
