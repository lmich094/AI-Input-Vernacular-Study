import argparse
import json
import sys

SYSTEM_PROMPT = (
    "You are a helpful assistant. Answer the following multiple choice question "
    "by responding with only the letter of the correct answer (A, B, C, or D)."
)


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


def estimate_tokens(text: str) -> int:
    """Estimate token count from character count (Claude ~4 chars/token)."""
    return max(1, len(text) // 4)


def build_result(entry: dict, level: str, answer_given: str, model: str, input_tokens: int) -> dict:
    level_key = level.lower()
    question_text = entry[level_key]
    return {
        "id": entry["id"],
        "subject": entry["subject"],
        "level": level,
        "question": question_text,
        "answer_given": answer_given,
        "correct_answer": entry["correct_answer"],
        "is_correct": answer_given == entry["correct_answer"],
        "input_tokens": input_tokens,
        "output_tokens": 1,
        "total_tokens": input_tokens + 1,
        "model": model,
    }


def load_question_set(path: str) -> list[dict]:
    with open(path) as f:
        return json.load(f)
