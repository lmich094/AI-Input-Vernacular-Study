import os
import json
import pandas as pd
import pytest
from report import write_results, compute_stats, generate_summary_report, save_report

SAMPLE_RESULTS = [
    {"id": "math_0", "subject": "math", "level": "L1", "question": "Q?",
     "answer_given": "B", "correct_answer": "B", "is_correct": True,
     "input_tokens": 50, "output_tokens": 1, "total_tokens": 51, "model": "claude-sonnet-4-6"},
    {"id": "math_0", "subject": "math", "level": "L2", "question": "Q?",
     "answer_given": "B", "correct_answer": "B", "is_correct": True,
     "input_tokens": 40, "output_tokens": 1, "total_tokens": 41, "model": "claude-sonnet-4-6"},
    {"id": "math_0", "subject": "math", "level": "L3", "question": "Q?",
     "answer_given": "C", "correct_answer": "B", "is_correct": False,
     "input_tokens": 35, "output_tokens": 1, "total_tokens": 36, "model": "claude-sonnet-4-6"},
]

def test_write_results_creates_csv(tmp_path):
    csv_path = str(tmp_path / "results.csv")
    xlsx_path = str(tmp_path / "results.xlsx")
    write_results(SAMPLE_RESULTS, csv_path, xlsx_path)
    assert os.path.exists(csv_path)
    df = pd.read_csv(csv_path)
    assert len(df) == 3
    assert list(df.columns) == [
        "id", "subject", "level", "question", "answer_given",
        "correct_answer", "is_correct", "input_tokens", "output_tokens",
        "total_tokens", "model"
    ]

def test_write_results_creates_xlsx(tmp_path):
    csv_path = str(tmp_path / "results.csv")
    xlsx_path = str(tmp_path / "results.xlsx")
    write_results(SAMPLE_RESULTS, csv_path, xlsx_path)
    assert os.path.exists(xlsx_path)
    df = pd.read_excel(xlsx_path)
    assert len(df) == 3

def test_compute_stats_accuracy_per_level():
    stats = compute_stats(SAMPLE_RESULTS)
    assert stats["L1"]["accuracy"] == 1.0
    assert stats["L2"]["accuracy"] == 1.0
    assert stats["L3"]["accuracy"] == 0.0

def test_compute_stats_avg_input_tokens():
    stats = compute_stats(SAMPLE_RESULTS)
    assert stats["L1"]["avg_input_tokens"] == 50.0
    assert stats["L2"]["avg_input_tokens"] == 40.0
    assert stats["L3"]["avg_input_tokens"] == 35.0

def test_generate_summary_report_contains_key_sections():
    report = generate_summary_report(SAMPLE_RESULTS, "claude-sonnet-4-6")
    assert "claude-sonnet-4-6" in report
    assert "Accuracy by Level" in report
    assert "Token Usage by Level" in report
    assert "Token savings" in report.lower() or "%" in report
    assert "Key Finding" in report

def test_generate_summary_report_shows_token_savings():
    report = generate_summary_report(SAMPLE_RESULTS, "claude-sonnet-4-6")
    # L2 saves (50-40)/50 = 20%, L3 saves (50-35)/50 = 30%
    assert "20.0%" in report or "20%" in report

def test_save_report_writes_file(tmp_path):
    path = str(tmp_path / "report.md")
    save_report("# Report\nContent here", path)
    assert os.path.exists(path)
    with open(path) as f:
        assert f.read() == "# Report\nContent here"
