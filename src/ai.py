import os
import sys
from pathlib import Path
from typing import Optional

from dotenv import load_dotenv
from openai import OpenAI

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent))

from ai_test_helpers import memoise_for_tests

load_dotenv()

DEFAULT_MODEL: str = os.getenv("DEFAULT_AI_MODEL", "openai/gpt-4o-mini")

_client = None


def get_client():
    global _client
    if _client is None:
        _client = OpenAI(
            base_url="https://openrouter.ai/api/v1",
            api_key=os.getenv("OPENROUTER_API_KEY"),
        )
    return _client


@memoise_for_tests
def ai(
    system_prompt: str, user_prompt: str, model: Optional[str] = None
) -> Optional[str]:
    if model is None:
        model = DEFAULT_MODEL
    client = get_client()
    response = client.chat.completions.create(
        model=model,
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt},
        ],
    )
    return response.choices[0].message.content
