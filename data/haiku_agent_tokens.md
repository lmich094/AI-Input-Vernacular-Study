# Haiku Agent Token Usage (Phase 1 L3 Generation)

Per-agent token consumption for the Haiku agents that generated the L3
abbreviations. Data extracted from the Claude Code workflow subagent transcripts
for the two Phase 1 runs.

**File:** `haiku_agent_tokens.csv`

## Runs

| `run` value  | Workflow ID      | What it was |
|--------------|------------------|-------------|
| `generation` | `wf_f57c8978-012`| Main L3 generation run (114 questions) + the resumed save step |
| `fix`        | `wf_3b8cf304-3de`| Re-run of 21 entries that had instruction leakage / reverted L3 |

## Columns

| Column | Meaning |
|--------|---------|
| `run` | Which workflow run (see table above) |
| `agent_id` | Subagent ID from the transcript filename |
| `model` | Model that served the call (`claude-haiku-4-5-20251001` for L3 work) |
| `role` | `l3_generation` for abbreviation agents; `other` for the workflow's load/read/save helper agents |
| `uncached_input_tokens` | Input tokens billed at full rate |
| `cache_creation_input_tokens` | Input tokens written to cache (billed ~1.25×) |
| `cache_read_input_tokens` | Input tokens served from cache (billed ~0.1×) |
| `total_input_tokens` | Sum of the three input components |
| `output_tokens` | Output tokens (the abbreviated text) |
| `l3_output` | The L3 abbreviation the agent returned (newlines flattened to spaces) |

## Key facts

- **L3 generation agents (non-zero): 136**, averaging ~15,400 total input tokens
  and ~233 output tokens each.
- **~73% of input is cache reads** (the agent system prompt + tool definitions,
  which are identical across calls). This is billed at ~0.1× and dominates the
  raw token count while contributing little to actual cost.
- The actual question text is a tiny fraction of each call — the bulk is fixed
  agent scaffolding. This is why per-call cost is driven by overhead, not by
  question length, and why cache-read pricing must be factored into any cost
  projection for Phase 2.
- A few `other` / zero-token rows are the workflow's load/read/save helper agents
  and cache-resumed agents (replayed instantly, so no fresh token usage).

## Pricing reference (per 1M tokens)

| Model | Input | Output |
|-------|-------|--------|
| Claude Haiku 4.5 (`claude-haiku-4-5`) | $1.00 | $5.00 |

Cache reads bill at ~0.1× input; cache writes at ~1.25× input.
