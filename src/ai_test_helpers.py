import functools
import hashlib
import json
import os
import sys
from typing import Any, Callable, Dict


def is_test_mode() -> bool:
    return os.getenv("PYTEST_CURRENT_TEST") is not None or "pytest" in sys.argv[0]


def memoise_for_tests(func: Callable[..., Any]) -> Callable[..., Any]:
    @functools.wraps(func)
    def wrapper(*args: Any, **kwargs: Any) -> Any:
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

        data: Dict[str, Any] = {}
        if os.path.exists(filename):
            try:
                with open(filename, "r") as f:
                    data = json.load(f)
            except (json.JSONDecodeError, ValueError):
                # If file is corrupted, start fresh
                data = {}

        if key in data:
            return data[key]

        result = func(*args, **kwargs)

        try:
            data[key] = result
            with open(filename, "w") as f:
                json.dump(data, f, indent=2)
        except (TypeError, ValueError):
            # If result is not JSON serializable, skip caching
            pass

        return result

    return wrapper
