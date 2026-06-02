# AI Input Vernacular Study — Design Spec
_Date: 2026-06-02_

## Goal

Determine whether abbreviated or informal input vernacular (texting shorthand, word truncation) can maintain AI output quality while reducing input token usage. The study compares three levels of input formality against MMLU benchmark questions with known correct answers, tracking accuracy and token usage at each level.

---

## Study Design

### Input Levels

Every question is tested at three levels. The only variable between levels is the question text itself — all other inputs are held constant.

| Level | Description | Example |
|-------|-------------|---------|
| L1 | Normal spelling and grammar (control) | "What are the primary causes of inflation?" |
| L2 | Texting-style abbreviations only | "Wut r d primary causes of inflation?" |
| L3 | L2 abbreviations + further word truncation via LLM | "Wut r d prmry causes of infltn?" |

### Benchmark

- **Dataset:** MMLU (Massive Multitask Language Understanding) via Hugging Face `datasets`
- **Split:** test
- **Sample:** 2 questions per subject × 57 subjects = **114 questions**
- **Total API calls (evaluation):** 114 × 3 levels = **342 calls**

---

## Project Structure

```
/
├── data/
│   └── question_set.json         # generated once, committed to repo
├── results/
│   ├── raw_results.csv           # one row per API call (342 rows)
│   ├── raw_results.xlsx          # same data, Excel format
│   └── summary_report.md         # auto-generated findings
├── phase1_generate_questions.py  # run once to build question_set.json
├── phase2_evaluate.py            # runs the study
├── abbreviations.py              # L2 lookup table
└── requirements.txt
```

`question_set.json` is a committed artifact — it locks in the exact questions and all three variants, making the study fully reproducible by anyone who clones the repo.

---

## Phase 1: Question Set Generation

**Script:** `phase1_generate_questions.py`
**Run:** once, output committed to repo

### Steps

1. **Load MMLU** — use `datasets` library to load the test split, sample 2 questions per subject
2. **Generate L2** — apply the lookup table in `abbreviations.py` to substitute texting abbreviations into each question
3. **Generate L3** — send each L2 question to Claude via API with an instruction to further abbreviate words where a human would still understand the meaning (e.g. "manufacture" → "manfctr", "completely" → "compltly"). Runs as a batch of 114 API calls.
4. **Save** — write all three variants plus correct answer and subject to `data/question_set.json`

### question_set.json format

```json
[
  {
    "id": "high_school_mathematics_0",
    "subject": "high_school_mathematics",
    "correct_answer": "B",
    "choices": ["A) ...", "B) ...", "C) ...", "D) ..."],
    "l1": "What is the derivative of x^2?",
    "l2": "Wut is d derivative of x^2?",
    "l3": "Wut is d deriv of x^2?"
  }
]
```

### L2 Lookup Table (`abbreviations.py`)

A dictionary mapping common words to their texting abbreviations. Examples:

```python
ABBREVIATIONS = {
    "you": "u",
    "are": "r",
    "what": "wut",
    "the": "d",
    "to": "2",
    "for": "4",
    "and": "n",
    "with": "w/",
    "because": "bc",
    "before": "b4",
    "please": "plz",
    "thanks": "thx",
    # ... etc.
}
```

Substitution is case-insensitive and whole-word only (does not match substrings).

### L3 LLM Prompt

Sent to Claude once per question during Phase 1:

```
System: "You are a text abbreviation engine. Your job is to shorten words in the input text where the abbreviated form would still be understandable to a human reader. Do not change any words that are already short (4 characters or fewer). Do not alter proper nouns, numbers, or answer choices. Return only the abbreviated text with no explanation."

User: [L2 question text]
```

---

## Phase 2: Evaluation Runner

**Script:** `phase2_evaluate.py`

### Model Selection

At startup, the script prompts interactively if no model is specified:

```
Which model should be used for evaluation? (e.g. claude-sonnet-4-6):
```

Can also be passed as a CLI argument to skip the prompt:

```bash
python phase2_evaluate.py --model claude-sonnet-4-6
```

The model name is recorded in every row of the results CSV.

### Prompt Structure

Every one of the 342 API calls uses the exact same system prompt. The only difference between calls is the question text:

```
System: "You are a helpful assistant. Answer the following multiple choice question by responding with only the letter of the correct answer (A, B, C, or D)."

User: [question text at its level, including answer choices]
```

No conversation history. No prior context. Each call is a fresh, isolated API request.

### Batching

Calls are executed asynchronously using the async Anthropic SDK client (`AsyncAnthropic`). A configurable `BATCH_SIZE` constant (default: 10) controls how many concurrent requests run at once, preventing rate limit errors. All 342 calls are dispatched in batches of 10.

### Token Tracking

Every API response's `usage` object is captured:
- `input_tokens`
- `output_tokens`
- `total_tokens` (derived: input + output)

These are recorded per call and used in the summary report to compute token savings across levels.

---

## Output Files

### raw_results.csv / raw_results.xlsx

One row per API call (342 rows). Columns:

| Column | Description |
|--------|-------------|
| `id` | Question ID (e.g. `high_school_mathematics_0`) |
| `subject` | MMLU subject |
| `level` | L1, L2, or L3 |
| `question` | The question text used in this call |
| `answer_given` | Model's response (A/B/C/D) |
| `correct_answer` | Ground truth |
| `is_correct` | Boolean |
| `input_tokens` | Input tokens for this call |
| `output_tokens` | Output tokens for this call |
| `total_tokens` | input + output |
| `model` | Model used |

### summary_report.md

Auto-generated after all calls complete. Sections:

1. **Study parameters** — model, date, sample size, batch size
2. **Accuracy by level** — L1 / L2 / L3 overall accuracy
3. **Accuracy by subject × level** — table of accuracy per subject at each level
4. **Token usage by level** — average input tokens per call at each level
5. **Token savings** — % reduction in input tokens: L2 vs L1, L3 vs L1
6. **Key finding** — one-sentence summary of whether quality held while tokens dropped

---

## Extensibility

To run the study against a second model (e.g. Codex), run `phase2_evaluate.py` again and specify the new model at the prompt. Results write to `raw_results_<model>.csv` so outputs from different models don't overwrite each other. The summary report can optionally compare across models when multiple result files are present.

---

## Key Constraints

- The system prompt must be **byte-for-byte identical** across all 342 evaluation calls — any difference outside the question text would introduce token variance that contaminates the comparison
- **Answer choices are never abbreviated** — only the question stem (the question itself) is transformed at L2 and L3. Choices remain in their original L1 form across all levels, ensuring the only variable is the question stem wording
- `question_set.json` must be committed before Phase 2 runs — it is the single source of truth for the study
- L3 variants are generated once in Phase 1 and never regenerated — this ensures L3 is consistent across all runs
- The model used for L3 generation in Phase 1 should be recorded in `question_set.json` for reproducibility
