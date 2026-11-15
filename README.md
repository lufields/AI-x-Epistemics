# Do frontier models know which AI-safety concepts exist?

Code and data for a project at the Apart Research AI x Epistemics Research Sprint (November 2026), Track 1: Model Epistemics.

We ask three frontier models (Claude Fable 5.2, GPT-6 Astra, Gemini 4 Argon) three questions about each of 150 AI-safety concepts. 100 concepts are real, each with a source. 50 are invented names that sound like real mechanisms. Each answer also comes with the model's own confidence (0–100). We then measure:

- how well the models understand the real concepts;
- how often they treat an invented term as real, depending on how the question is framed;
- whether their stated confidence is lower when they are wrong.

## Layout

| Path | What it holds |
|---|---|
| `data/real_concepts.json` | 100 real concepts: term, MIT AI Risk Repository subdomain, risk/method, source URL, source type, supporting passage, reference keys, application scenario and its yes/no answer |
| `data/invented.py`, `data/invented_status.json` | 50 invented terms with their scenarios; results of the exact-phrase web searches (passed and rejected candidates) |
| `data/questions_v2.jsonl` | the 450 questions exactly as sent (before the fixed suffix) |
| `data/raw_v2/repN/*.jsonl` | full API responses, one file per model and repetition |
| `data/grades_v2/<judge>/repN/*.jsonl` | grades from each judge model, with a one-sentence reason |
| `data/adjudication.json` | hand decisions on judge disagreements, and items excluded from analysis |
| `code/run_v2.py`, `code/run.py` | sends the questions through OpenRouter |
| `code/judge.py` | grading prompts and judge calls |
| `code/analyze_v2.py`, `code/figures.py`, `code/stats.py` | tables, figure, Wilson intervals and confidence parsing |
| `pilot/` | an earlier design (factual questions), with its questions, raw answers, grades and scripts; see `pilot/README.md` |

## Reproducing

```bash
export OPENROUTER_API_KEY=...   # or put the key in a file named .orkey
BREV=1 THREADS=3 TAG=rep1 python3 code/run_v2.py anthropic/claude-fable-5.2
JUDGE=deepseek/deepseek-v4-pro-0813 python3 code/judge.py data/raw_v2/rep1/*.jsonl
python3 code/analyze_v2.py
```

Model outputs vary between runs (default temperature), and the models may be updated or withdrawn, so a rerun will not give identical numbers.

## What was run

Each of the 450 questions was asked three times per model (`rep1`–`rep3`), on 15 November 2026.

- GPT-6 Astra is missing 22 answers in `rep2`, all on invented terms: the credit ran out before 19 were sent (F046–F050 all three questions, F045-2, F045-3, F039-3, F044-3), and 3 returned API errors and were not re-sent (F023-1, F032-2, F035-1). The system message says 14 November because the first run started at 01:59 UTC on 15 November, still 14 November in Buenos Aires.
- In `rep2`, only the invented-term answers (all models) and Gemini 4 Argon's real-concept answers were graded by the judges. The paper's real-concept results therefore use `rep1` and `rep3`.
- The main judge is DeepSeek V4 Pro and the second is Qwen 3.8 Flash. Their disagreements were decided by Claude (Opus 5.5), one by one (`data/adjudication.json`).

## Caveats

The concepts, keys, scenarios and invented terms were drafted with Claude (Anthropic), and one evaluated model is from the same family. See the paper's limitations section.
