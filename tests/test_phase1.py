from unittest.mock import patch, MagicMock
from phase1_generate_questions import load_mmlu_sample, build_entry

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
