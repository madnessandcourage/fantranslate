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

    # Check that we got a response
    assert isinstance(response, str)
    assert len(response) > 0
    assert isinstance(history, list)
    assert len(history) > 0


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
