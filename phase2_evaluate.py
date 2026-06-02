import argparse
import asyncio
import json
import os
import sys
import anthropic

SYSTEM_PROMPT = (
    "You are a helpful assistant. Answer the following multiple choice question "
    "by responding with only the letter of the correct answer (A, B, C, or D)."
)

BATCH_SIZE = 10


def get_model() -> str:
    parser = argparse.ArgumentParser()
    parser.add_argument("--model", type=str, default=None)
    args, _ = parser.parse_known_args()

    if args.model:
        return args.model

    model = input("Which model should be used for evaluation? (e.g. claude-sonnet-4-6): ").strip()
    if not model:
        print("No model specified. Exiting.")
        sys.exit(1)
    return model


def format_user_message(question_text: str, choices: list[str]) -> str:
    letters = ["A", "B", "C", "D"]
    choice_lines = "\n".join(f"{letters[i]}) {choices[i]}" for i in range(len(choices)))
    return f"{question_text}\n\n{choice_lines}"


async def evaluate_question(entry: dict, level: str, client, model: str) -> dict:
    level_key = level.lower()
    question_text = entry[level_key]
    user_message = format_user_message(question_text, entry["choices"])

    response = await client.messages.create(
        model=model,
        max_tokens=5,
        system=SYSTEM_PROMPT,
        messages=[{"role": "user", "content": user_message}],
    )

    answer_given = response.content[0].text.strip()[0].upper()

    return {
        "id": entry["id"],
        "subject": entry["subject"],
        "level": level,
        "question": question_text,
        "answer_given": answer_given,
        "correct_answer": entry["correct_answer"],
        "is_correct": answer_given == entry["correct_answer"],
        "input_tokens": response.usage.input_tokens,
        "output_tokens": response.usage.output_tokens,
        "total_tokens": response.usage.input_tokens + response.usage.output_tokens,
        "model": model,
    }


def load_question_set(path: str) -> list[dict]:
    with open(path) as f:
        return json.load(f)


async def run_evaluation(entries: list[dict], model: str, batch_size: int = BATCH_SIZE) -> list[dict]:
    client = anthropic.AsyncAnthropic()
    sem = asyncio.Semaphore(batch_size)

    async def bounded_eval(entry: dict, level: str):
        async with sem:
            return await evaluate_question(entry, level, client, model)

    tasks = [
        bounded_eval(entry, level)
        for entry in entries
        for level in ["L1", "L2", "L3"]
    ]

    total = len(tasks)
    completed = 0
    results = []

    for coro in asyncio.as_completed(tasks):
        result = await coro
        results.append(result)
        completed += 1
        print(f"\r  Progress: {completed}/{total}", end="", flush=True)

    print()
    return results


async def _main():
    from report import write_results, generate_summary_report, save_report

    model = get_model()
    question_set_path = "data/question_set.json"

    if not os.path.exists(question_set_path):
        print(f"Error: {question_set_path} not found. Run phase1_generate_questions.py first.")
        sys.exit(1)

    entries = load_question_set(question_set_path)
    print(f"Loaded {len(entries)} questions. Running {len(entries) * 3} evaluations...")

    results = await run_evaluation(entries, model=model)

    safe_model = model.replace("/", "-")
    csv_path = f"results/raw_results_{safe_model}.csv"
    xlsx_path = f"results/raw_results_{safe_model}.xlsx"
    report_path = f"results/summary_report_{safe_model}.md"

    os.makedirs("results", exist_ok=True)
    write_results(results, csv_path, xlsx_path)
    report = generate_summary_report(results, model)
    save_report(report, report_path)

    print(f"Results written to {csv_path} and {xlsx_path}")
    print(f"Summary report written to {report_path}")


if __name__ == "__main__":
    asyncio.run(_main())
