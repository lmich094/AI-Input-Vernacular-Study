import pytest
from unittest.mock import patch, AsyncMock, MagicMock
from phase2_evaluate import format_user_message, evaluate_question, get_model

SAMPLE_ENTRY = {
    "id": "math_0",
    "subject": "high_school_mathematics",
    "correct_answer": "B",
    "choices": ["Alpha", "Beta", "Gamma", "Delta"],
    "l1": "What is the derivative of x squared?",
    "l2": "Wut is d derivative of x squared?",
    "l3": "Wut is d deriv of x sqrd?",
}

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

@pytest.mark.asyncio
async def test_evaluate_question_returns_correct_structure():
    mock_response = MagicMock()
    mock_response.content = [MagicMock(text="B")]
    mock_response.usage.input_tokens = 42
    mock_response.usage.output_tokens = 1

    mock_client = MagicMock()
    mock_client.messages.create = AsyncMock(return_value=mock_response)

    result = await evaluate_question(SAMPLE_ENTRY, "L1", mock_client, "claude-sonnet-4-6")

    assert result["id"] == "math_0"
    assert result["subject"] == "high_school_mathematics"
    assert result["level"] == "L1"
    assert result["answer_given"] == "B"
    assert result["correct_answer"] == "B"
    assert result["is_correct"] is True
    assert result["input_tokens"] == 42
    assert result["output_tokens"] == 1
    assert result["total_tokens"] == 43
    assert result["model"] == "claude-sonnet-4-6"

@pytest.mark.asyncio
async def test_evaluate_question_uses_correct_level_text():
    mock_response = MagicMock()
    mock_response.content = [MagicMock(text="A")]
    mock_response.usage.input_tokens = 30
    mock_response.usage.output_tokens = 1

    mock_client = MagicMock()
    mock_client.messages.create = AsyncMock(return_value=mock_response)

    await evaluate_question(SAMPLE_ENTRY, "L2", mock_client, "claude-sonnet-4-6")

    call_args = mock_client.messages.create.call_args
    user_content = call_args.kwargs["messages"][0]["content"]
    assert "Wut is d derivative of x squared?" in user_content

@pytest.mark.asyncio
async def test_evaluate_question_marks_wrong_answer():
    mock_response = MagicMock()
    mock_response.content = [MagicMock(text="C")]
    mock_response.usage.input_tokens = 42
    mock_response.usage.output_tokens = 1

    mock_client = MagicMock()
    mock_client.messages.create = AsyncMock(return_value=mock_response)

    result = await evaluate_question(SAMPLE_ENTRY, "L1", mock_client, "claude-sonnet-4-6")
    assert result["is_correct"] is False

def test_get_model_from_cli_arg():
    with patch("sys.argv", ["phase2_evaluate.py", "--model", "claude-sonnet-4-6"]):
        model = get_model()
    assert model == "claude-sonnet-4-6"
