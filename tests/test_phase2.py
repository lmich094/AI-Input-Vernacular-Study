import json
import pytest
from unittest.mock import patch
from phase2_evaluate import format_user_message, get_model, load_question_set, estimate_tokens, build_result


def test_format_user_message_includes_question_and_choices():
    msg = format_user_message("What is 2+2?", ["1", "2", "3", "4"])
    assert "What is 2+2?" in msg
    assert "A) 1" in msg
    assert "B) 2" in msg
    assert "C) 3" in msg
    assert "D) 4" in msg


def test_format_user_message_choices_always_l1():
    msg = format_user_message("Wut is 2+2?", ["1", "2", "3", "4"])
    # Choices should appear verbatim, not abbreviated
    assert "A) 1" in msg


def test_get_model_from_cli_arg():
    with patch("sys.argv", ["phase2_evaluate.py", "--model", "claude-sonnet-4-6"]):
        model = get_model()
    assert model == "claude-sonnet-4-6"


def test_load_question_set(tmp_path):
    entries = [{"id": "math_0", "l1": "Q?", "l2": "Q?", "l3": "Q?"}]
    path = tmp_path / "question_set.json"
    path.write_text(json.dumps(entries))
    loaded = load_question_set(str(path))
    assert loaded == entries


def test_estimate_tokens_divides_by_four():
    assert estimate_tokens("a" * 100) == 25


def test_estimate_tokens_minimum_one():
    assert estimate_tokens("") == 1


def test_build_result_correct_answer():
    entry = {
        "id": "math_0",
        "subject": "math",
        "correct_answer": "B",
        "choices": ["Alpha", "Beta", "Gamma", "Delta"],
        "l1": "What is 2+2?",
        "l2": "Wut is 2+2?",
        "l3": "Wut is 2+2?",
    }
    result = build_result(entry, "L1", answer_given="B", model="claude-sonnet-4-6", input_tokens=50)
    assert result["is_correct"] is True
    assert result["answer_given"] == "B"
    assert result["level"] == "L1"
    assert result["input_tokens"] == 50
    assert result["output_tokens"] == 1
    assert result["total_tokens"] == 51


def test_build_result_wrong_answer():
    entry = {
        "id": "math_0", "subject": "math", "correct_answer": "B",
        "choices": ["A", "B", "C", "D"],
        "l1": "Q?", "l2": "Q?", "l3": "Q?",
    }
    result = build_result(entry, "L2", answer_given="C", model="claude-sonnet-4-6", input_tokens=40)
    assert result["is_correct"] is False
