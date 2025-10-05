import functools
import hashlib
import json
import os
import sys
from typing import Optional

from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()

client = OpenAI(
    base_url="https://openrouter.ai/api/v1",
    api_key=os.getenv("OPENROUTER_API_KEY"),
)

DEFAULT_MODEL: str = os.getenv("DEFAULT_AI_MODEL", "openai/gpt-4o-mini")


def is_test_mode() -> bool:
    return os.getenv("PYTEST_CURRENT_TEST") is not None or "pytest" in sys.argv[0]


def memoise_for_tests(func):
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        if not is_test_mode():
            return func(*args, **kwargs)

        # Compute key: join all args and kwargs with :
        key_parts = [str(arg) for arg in args]
        for k in sorted(kwargs.keys()):
            key_parts.append(f"{k}={kwargs[k]}")
        key_str = ":".join(key_parts)
        key = hashlib.sha1(key_str.encode()).hexdigest()

        filename = f".ai_recordings/{func.__name__}.json"
        os.makedirs(os.path.dirname(filename), exist_ok=True)

        data = {}
        if os.path.exists(filename):
            with open(filename, "r") as f:
                data = json.load(f)

        if key in data:
            return data[key]

        result = func(*args, **kwargs)

        data[key] = result
        with open(filename, "w") as f:
            json.dump(data, f, indent=2)

        return result

    return wrapper


@memoise_for_tests
def ai(
    system_prompt: str, user_prompt: str, model: Optional[str] = None
) -> Optional[str]:
    if model is None:
        model = DEFAULT_MODEL
    response = client.chat.completions.create(
        model=model,
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt},
        ],
    )
    return response.choices[0].message.content
