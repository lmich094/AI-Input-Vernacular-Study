import json
import os
import asyncio
import anthropic
from datasets import load_dataset
from abbreviations import apply_abbreviations

MMLU_SUBJECTS = [
    "abstract_algebra", "anatomy", "astronomy", "business_ethics",
    "clinical_knowledge", "college_biology", "college_chemistry",
    "college_computer_science", "college_mathematics", "college_medicine",
    "college_physics", "computer_security", "conceptual_physics",
    "econometrics", "electrical_engineering", "elementary_mathematics",
    "formal_logic", "global_facts", "high_school_biology",
    "high_school_chemistry", "high_school_computer_science",
    "high_school_european_history", "high_school_geography",
    "high_school_government_and_politics", "high_school_macroeconomics",
    "high_school_mathematics", "high_school_microeconomics",
    "high_school_physics", "high_school_psychology",
    "high_school_statistics", "high_school_us_history",
    "high_school_world_history", "human_aging", "human_sexuality",
    "international_law", "jurisprudence", "logical_fallacies",
    "machine_learning", "management", "marketing", "medical_genetics",
    "miscellaneous", "moral_disputes", "moral_scenarios", "nutrition",
    "philosophy", "prehistory", "professional_accounting",
    "professional_law", "professional_medicine", "professional_psychology",
    "public_relations", "security_studies", "sociology", "us_foreign_policy",
    "virology", "world_religions",
]

ANSWER_LETTERS = ["A", "B", "C", "D"]

L3_SYSTEM_PROMPT = (
    "You are a text abbreviation engine. Your job is to shorten words in the input "
    "text where the abbreviated form would still be understandable to a human reader. "
    "Do not change any words that are already short (4 characters or fewer). Do not "
    "alter proper nouns, numbers, or answer choices. Return only the abbreviated text "
    "with no explanation."
)

GENERATION_MODEL = "claude-haiku-4-5-20251001"


def load_mmlu_sample(n_per_subject: int = 2) -> list[dict]:
    entries = []
    for subject in MMLU_SUBJECTS:
        ds = load_dataset("cais/mmlu", subject, split="test")
        sample = ds.select(range(min(n_per_subject, len(ds))))
        for i, item in enumerate(sample):
            entries.append({
                "id": f"{subject}_{i}",
                "subject": subject,
                "question": item["question"],
                "choices": item["choices"],
                "correct_answer": ANSWER_LETTERS[item["answer"]],
            })
    return entries


def build_entry(raw: dict, l3_question: str) -> dict:
    l2_question = apply_abbreviations(raw["question"])
    return {
        "id": raw["id"],
        "subject": raw["subject"],
        "correct_answer": raw["correct_answer"],
        "choices": raw["choices"],
        "l1": raw["question"],
        "l2": l2_question,
        "l3": l3_question,
        "l3_generation_model": GENERATION_MODEL,
    }


async def generate_l3_variants(raw_entries: list[dict], batch_size: int = 10) -> list[str]:
    """Send each L2 question to the LLM to produce an L3 variant. Returns list of L3 strings."""
    client = anthropic.AsyncAnthropic()
    sem = asyncio.Semaphore(batch_size)

    async def _generate_one(entry: dict) -> str:
        async with sem:
            response = await client.messages.create(
                model=GENERATION_MODEL,
                max_tokens=512,
                system=L3_SYSTEM_PROMPT,
                messages=[{"role": "user", "content": entry["question"]}],
            )
            return response.content[0].text.strip()

    tasks = [_generate_one(entry) for entry in raw_entries]
    return await asyncio.gather(*tasks)


def save_question_set(entries: list[dict], path: str) -> None:
    if os.path.dirname(path):
        os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w") as f:
        json.dump(entries, f, indent=2)


async def _main():
    print("Loading MMLU sample (2 per subject)...")
    raw_entries = load_mmlu_sample(n_per_subject=2)
    print(f"Loaded {len(raw_entries)} questions across {len(MMLU_SUBJECTS)} subjects.")

    print("Generating L3 variants via LLM (this may take a few minutes)...")
    l3_variants = await generate_l3_variants(raw_entries)

    print("Building final entries...")
    entries = [build_entry(raw, l3) for raw, l3 in zip(raw_entries, l3_variants)]

    output_path = "data/question_set.json"
    save_question_set(entries, output_path)
    print(f"Saved {len(entries)} entries to {output_path}")
    print("Review data/question_set.json, then commit it to the repo.")


if __name__ == "__main__":
    asyncio.run(_main())
