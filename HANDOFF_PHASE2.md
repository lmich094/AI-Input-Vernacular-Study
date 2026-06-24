# Handoff: Run Phase 2 Evaluation (Opus 4.8)

**Repo:** `/home/liam_michka/tokenUse/AI-Input-Vernacular-Study` (git, pushes to `origin/main`)

## State
- **Phase 1 done.** `data/question_set.json` = 114 MMLU questions, 57 subjects, each with L1 (original) / L2 (rule-based abbrev) / L3 (Haiku abbrev). Committed.
- Haiku generation token data archived in `data/haiku_agent_tokens.csv` (+ `.md`).
- **Cost test passed.** Ran 3 real Opus 4.8 calls (1 question × L1/L2/L3) — all correct. Validated the harness. Test cost ~$0.54. Full run not started.

## What to run
Phase 2 = 342 isolated Opus agent calls (114 questions × 3 levels), each answering an MMLU multiple-choice question; writes results + summary.

Launch the workflow at `workflows/phase2_evaluation.js` with model `claude-opus-4-8`:
> "Run the phase2-evaluation workflow with model claude-opus-4-8"

(or `Workflow({ name/scriptPath of phase2_evaluation.js, args: { model: "claude-opus-4-8" } })`)

## Cost expectation
- **Realistic ~$8–12**, hard-capped ~$34 if caching fully fails.
- Each call ≈ 16K input / ~120 output; ~13.6K of input is **fixed agent scaffolding** (cached at scale, ~0.1× after warm-up). Question length is noise against scaffolding — the L1/L2/L3 *billed* token difference is ~0.
- Opus 4.8 pricing: $5/M in, $25/M out; cache read ~0.1×, cache write ~1.25×.

## Outputs (gitignored)
- `results/raw_results_claude-opus-4-8.csv` / `.xlsx`
- `results/summary_report_claude-opus-4-8.md`
- Token columns in results are **chars/4 estimates** (the study metric), NOT billed tokens.

## After the run
1. Inspect accuracy + token-estimate by level (`df.groupby('level')`).
2. Confirm 342/342 results (no failed agents filtered).
3. Decide whether to commit results / run additional models for comparison.

## Notes
- Stale doc `HANDOFF.md` predates Phase 1 completion — ignore it; this file supersedes.
- Watch live progress with `/workflows`.
