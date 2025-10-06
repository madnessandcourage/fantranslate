import json
import os
from unittest.mock import MagicMock, patch

import pytest

from ai import agent, ai, yesno
from main import main
from tools.hello import hello_tool


def test_ai_memoisation():
    # Test that memoise_for_tests works in test mode
    # We'll mock the openai client to return a fixed response

    # Skip if no API key (using recordings mode)
    if not os.getenv("OPENROUTER_API_KEY"):
        pytest.skip("Skipping memoisation test in recordings mode")

    with patch("ai.get_client") as mock_get_client:
        mock_client = MagicMock()
        mock_response = MagicMock()
        mock_response.choices = [MagicMock()]
        mock_response.choices[0].message.content = "Mocked AI response"
        mock_client.chat.completions.create.return_value = mock_response

        mock_get_client.return_value = mock_client

        # Call ai with specific args
        result1 = ai("test_system", "test_user", "test_model")
        assert result1 == "Mocked AI response"

        # Call again with same args, should return from cache
        result2 = ai("test_system", "test_user", "test_model")
        assert result2 == "Mocked AI response"

        # Check that the API was not called since recordings exist
        assert mock_client.chat.completions.create.call_count == 0

        # Check that the recording file exists
        assert os.path.exists(".ai_recordings/ai.json")

        # Check the content
        with open(".ai_recordings/ai.json", "r") as f:
            data = json.load(f)
        assert len(data) >= 1  # May have more recordings
        # Find the key for the test args
        key = None
        for k in data:
            if data[k] == "Mocked AI response":
                key = k
                break
        assert key is not None


def test_agent_basic():
    # Test that the agent function works

    # Test the agent with the hello tool
    system_prompt = "You are a helpful assistant. Use tools when appropriate."
    user_query = "Who should I say hello to?"
    tools = [hello_tool]

    # Call agent (recording system will handle determinism)
    response, history = agent(system_prompt, user_query, tools)

    # Assert that the agent used the tool and got the expected result
    assert isinstance(response, str)
    assert "world" in response.lower()  # The tool returns "World"
    assert isinstance(history, list)
    assert len(history) >= 2  # type: ignore[arg-type] # At least system + user + AI messages


def test_agent_with_chat_history():
    # Test that previous chat history influences the agent output

    system_prompt = "You are a helpful assistant. Use tools when appropriate."
    tools = [hello_tool]

    # First interaction
    user_query1 = "Who should I say hello to?"
    response1, history1 = agent(system_prompt, user_query1, tools)

    # Second interaction with previous history
    user_query2 = "What about goodbye?"
    previous_history = history1  # Use the history from first call
    response2, history2 = agent(system_prompt, user_query2, tools, previous_history)

    # Assert that chat history influences the response
    assert isinstance(response1, str)
    assert isinstance(response2, str)
    assert "world" in response1.lower()  # First response should mention world
    assert len(history2) > len(  # type: ignore[arg-type]
        history1
    )  # History should grow with continued conversation


def test_main_runs_without_error():
    # Test that main() runs without error (recording system handles determinism)
    try:
        main()
    except Exception as e:
        pytest.fail(f"main() raised an exception: {e}")


def test_yesno_yes_response():
    """Test yesno function with YES response."""
    with patch("ai.ai") as mock_ai:
        mock_ai.return_value = "YES"
        result, reason = yesno("Is 2 + 2 = 4?")
        assert result is True
        assert reason == ""


def test_yesno_no_response():
    """Test yesno function with NO response."""
    with patch("ai.ai") as mock_ai:
        mock_ai.return_value = "NO, because 2 + 2 = 5"
        result, reason = yesno("Is 2 + 2 = 5?")
        assert result is False
        assert reason == "because 2 + 2 = 5"


def test_yesno_retry_on_invalid():
    """Test yesno function retries on invalid response."""
    with patch("ai.ai") as mock_ai:
        # First two calls return invalid responses, third returns valid
        mock_ai.side_effect = ["Maybe", "I think YES", "YES"]
        result, reason = yesno("Is the sky blue?")
        assert result is True
        assert reason == ""
        assert mock_ai.call_count == 3


def test_yesno_max_retries_exceeded():
    """Test yesno function raises error after max retries."""
    with patch("ai.ai") as mock_ai:
        mock_ai.return_value = "Invalid response"
        with pytest.raises(
            ValueError, match="AI failed to provide a valid YES/NO response"
        ):
            yesno("Is water wet?", max_retries=2)
        assert mock_ai.call_count == 2


def test_yesno_none_response():
    """Test yesno function handles None response from ai."""
    with patch("ai.ai") as mock_ai:
        mock_ai.side_effect = [None, None, "YES"]
        result, reason = yesno("Is fire hot?")
        assert result is True
        assert reason == ""
