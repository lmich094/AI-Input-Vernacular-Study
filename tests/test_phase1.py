import json
import os
import pytest
from unittest.mock import patch, MagicMock
from phase1_generate_questions import load_mmlu_sample, build_entry, save_question_set, save_raw_questions

def _make_fake_dataset(questions):
    """Return a mock HF dataset-like object."""
    items = [
        {"question": q, "choices": ["Alpha", "Beta", "Gamma", "Delta"], "answer": 1}
        for q in questions
    ]
    mock_ds = MagicMock()
    mock_ds.__len__ = lambda self: len(items)
    mock_ds.select = lambda indices: [items[i] for i in indices]
    mock_ds.__iter__ = lambda self: iter(items)
    return mock_ds

def test_load_mmlu_sample_returns_correct_count():
    fake_ds = _make_fake_dataset(["Q1?", "Q2?", "Q3?"])
    with patch("phase1_generate_questions.load_dataset", return_value=fake_ds):
        with patch("phase1_generate_questions.MMLU_SUBJECTS", ["math", "science"]):
            entries = load_mmlu_sample(n_per_subject=2)
    assert len(entries) == 4  # 2 subjects × 2 questions

def test_load_mmlu_sample_entry_structure():
    fake_ds = _make_fake_dataset(["What is 2+2?"])
    with patch("phase1_generate_questions.load_dataset", return_value=fake_ds):
        with patch("phase1_generate_questions.MMLU_SUBJECTS", ["math"]):
            entries = load_mmlu_sample(n_per_subject=1)
    entry = entries[0]
    assert entry["id"] == "math_0"
    assert entry["subject"] == "math"
    assert entry["question"] == "What is 2+2?"
    assert entry["choices"] == ["Alpha", "Beta", "Gamma", "Delta"]
    assert entry["correct_answer"] == "B"  # answer index 1 → "B"

def test_build_entry_applies_l2_and_stores_l3():
    raw = {
        "id": "math_0",
        "subject": "math",
        "question": "What are you doing?",
        "choices": ["Alpha", "Beta", "Gamma", "Delta"],
        "correct_answer": "B",
    }
    entry = build_entry(raw, l3_question="Wut r u doin?")
    assert entry["l1"] == "What are you doing?"
    assert entry["l2"] == "Wut r u doing?"  # apply_abbreviations result
    assert entry["l3"] == "Wut r u doin?"
    assert entry["choices"] == ["Alpha", "Beta", "Gamma", "Delta"]
    assert entry["correct_answer"] == "B"
    assert "question" not in entry  # raw field removed


def test_save_question_set_writes_valid_json(tmp_path):
    entries = [{"id": "math_0", "l1": "Q?", "l2": "Q?", "l3": "Q?"}]
    path = str(tmp_path / "question_set.json")
    save_question_set(entries, path)
    with open(path) as f:
        loaded = json.load(f)
    assert loaded == entries

def test_save_question_set_creates_parent_dirs(tmp_path):
    entries = [{"id": "math_0"}]
    path = str(tmp_path / "nested" / "dir" / "question_set.json")
    save_question_set(entries, path)
    assert os.path.exists(path)

def test_save_raw_questions_writes_expected_fields(tmp_path):
    raw_entries = [
        {
            "id": "math_0",
            "subject": "math",
            "question": "What are you doing?",
            "choices": ["A", "B", "C", "D"],
            "correct_answer": "B",
        }
    ]
    path = str(tmp_path / "raw_questions.json")
    save_raw_questions(raw_entries, path)
    with open(path) as f:
        data = json.load(f)
    assert len(data) == 1
    entry = data[0]
    assert entry["l1"] == "What are you doing?"
    assert entry["l2"] == "Wut r u doing?"
    assert entry["question"] == "What are you doing?"
    assert "l3" not in entry
