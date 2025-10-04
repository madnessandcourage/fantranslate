import pytest
from src.main import main


def test_main_runs_without_error():
    # This is a basic test; in a real scenario, you'd mock the API call
    # For now, just check that the function can be called (though it may fail without API key)
    # To avoid actual API calls, we can skip if no key
    import os
    if not os.getenv("OPENROUTER_API_KEY"):
        pytest.skip("API key not set, skipping test that requires API")
    # If key is set, run main and check it doesn't raise
    try:
        main()
    except Exception as e:
        pytest.fail(f"main() raised an exception: {e}")