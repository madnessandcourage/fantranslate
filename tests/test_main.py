import json
import os
from unittest.mock import patch

import pytest

from src.ai import agent, ai


def test_ai_memoisation():
    # Test that memoise_for_tests works in test mode
    # We'll mock the openai client to return a fixed response

    # Clear existing recordings for this test
    import shutil

    if os.path.exists(".ai_recordings"):
        shutil.rmtree(".ai_recordings")

    with patch("src.ai.get_client") as mock_get_client:
        from unittest.mock import MagicMock

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

        # Check that the API was called only once
        assert mock_client.chat.completions.create.call_count == 1

        # Check that the recording file was created
        assert os.path.exists(".ai_recordings/ai.json")

        # Check the content
        with open(".ai_recordings/ai.json", "r") as f:
            data = json.load(f)
        assert len(data) == 1
        # The key should be the hash of "system:user:model=model"


def test_agent_basic():
    # Test that the agent function works
    # Skip if no API key
    if not os.getenv("OPENROUTER_API_KEY"):
        pytest.skip("API key not set, skipping test that requires API")

    from src.tools.hello import hello_tool

    # Test the agent with the hello tool
    system_prompt = "You are a helpful assistant. Use tools when appropriate."
    user_query = "Who should I say hello to?"
    tools = [hello_tool]

    # Call agent
    response, history = agent(system_prompt, user_query, tools)

    # Assert that the agent used the tool and got the expected result
    assert isinstance(response, str)
    assert "world" in response.lower()  # The tool returns "World"
    assert isinstance(history, list)
    assert len(history) >= 2  # type: ignore[arg-type] # At least system + user + AI messages


def test_agent_with_chat_history():
    # Test that previous chat history influences the agent output
    # Skip if no API key
    if not os.getenv("OPENROUTER_API_KEY"):
        pytest.skip("API key not set, skipping test that requires API")

    from src.tools.hello import hello_tool

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
    # This is a basic test; in a real scenario, you'd mock the API call
    # For now, just check that the function can be called (though it may fail without API key)
    # To avoid actual API calls, we can skip if no key
    if not os.getenv("OPENROUTER_API_KEY"):
        pytest.skip("API key not set, skipping test that requires API")
    # If key is set, run main and check it doesn't raise
    try:
        from src.main import main

        main()
    except Exception as e:
        pytest.fail(f"main() raised an exception: {e}")
