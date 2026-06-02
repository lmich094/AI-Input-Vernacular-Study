import argparse
import asyncio
import json
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
