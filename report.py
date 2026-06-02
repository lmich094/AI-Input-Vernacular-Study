import pandas as pd


def write_results(results: list[dict], csv_path: str, xlsx_path: str) -> None:
    df = pd.DataFrame(results)
    df.to_csv(csv_path, index=False)
    df.to_excel(xlsx_path, index=False, engine="openpyxl")


def compute_stats(results: list[dict]) -> dict:
    df = pd.DataFrame(results)
    stats = {}
    for level in ["L1", "L2", "L3"]:
        lvl = df[df["level"] == level]
        stats[level] = {
            "accuracy": float(lvl["is_correct"].mean()),
            "avg_input_tokens": float(lvl["input_tokens"].mean()),
            "avg_output_tokens": float(lvl["output_tokens"].mean()),
            "avg_total_tokens": float(lvl["total_tokens"].mean()),
            "total_input_tokens": int(lvl["input_tokens"].sum()),
        }
    return stats


def generate_summary_report(results: list[dict], model: str) -> str:
    stats = compute_stats(results)
    df = pd.DataFrame(results)

    l1 = stats["L1"]
    l2 = stats["L2"]
    l3 = stats["L3"]

    l2_token_savings = (l1["avg_input_tokens"] - l2["avg_input_tokens"]) / l1["avg_input_tokens"] * 100
    l3_token_savings = (l1["avg_input_tokens"] - l3["avg_input_tokens"]) / l1["avg_input_tokens"] * 100

    subject_accuracy = (
        df.groupby(["subject", "level"])["is_correct"]
        .mean()
        .unstack("level")[["L1", "L2", "L3"]]
    )

    key_finding = _key_finding(l1, l2, l3, l2_token_savings, l3_token_savings)

    return f"""# AI Input Vernacular Study — Results

**Model:** {model}
**Questions:** {len(results) // 3} (2 per subject × 57 subjects)
**Total API calls:** {len(results)}

---

## Accuracy by Level

| Level | Description | Accuracy |
|-------|-------------|----------|
| L1 | Normal grammar (control) | {l1['accuracy']:.1%} |
| L2 | Texting abbreviations | {l2['accuracy']:.1%} |
| L3 | Texting + word truncation | {l3['accuracy']:.1%} |

## Token Usage by Level

| Level | Avg Input Tokens | Savings vs L1 |
|-------|-----------------|---------------|
| L1 | {l1['avg_input_tokens']:.1f} | — |
| L2 | {l2['avg_input_tokens']:.1f} | {l2_token_savings:.1f}% |
| L3 | {l3['avg_input_tokens']:.1f} | {l3_token_savings:.1f}% |

## Accuracy by Subject

{subject_accuracy.to_markdown(floatfmt=".0%")}

## Key Finding

{key_finding}
"""


def _key_finding(l1: dict, l2: dict, l3: dict, l2_savings: float, l3_savings: float) -> str:
    l2_drop = abs(l2["accuracy"] - l1["accuracy"])
    l3_drop = abs(l3["accuracy"] - l1["accuracy"])
    quality_held = l2_drop < 0.05 and l3_drop < 0.05

    if quality_held and l3_savings > 5:
        return (
            f"Abbreviated inputs maintained accuracy within 5% of the L1 baseline "
            f"(L1: {l1['accuracy']:.1%}, L2: {l2['accuracy']:.1%}, L3: {l3['accuracy']:.1%}) "
            f"while reducing input tokens by {l2_savings:.1f}% at L2 and {l3_savings:.1f}% at L3, "
            f"supporting the hypothesis that vernacular shorthand can reduce token usage without sacrificing quality."
        )
    elif quality_held:
        return (
            f"Abbreviated inputs maintained accuracy within 5% of the L1 baseline, "
            f"but input token savings were minimal ({l2_savings:.1f}% at L2, {l3_savings:.1f}% at L3), "
            f"suggesting abbreviations do not meaningfully reduce token usage for MMLU-style questions."
        )
    else:
        return (
            f"Abbreviated inputs reduced accuracy (L1: {l1['accuracy']:.1%}, L2: {l2['accuracy']:.1%}, "
            f"L3: {l3['accuracy']:.1%}) with {l2_savings:.1f}% and {l3_savings:.1f}% input token savings "
            f"at L2 and L3 respectively. The quality trade-off does not justify the token savings."
        )


def save_report(report: str, path: str) -> None:
    with open(path, "w") as f:
        f.write(report)
