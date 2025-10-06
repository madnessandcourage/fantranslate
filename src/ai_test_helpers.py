import functools
import hashlib
import json
import os
import sys
from typing import Any, Callable, Dict

from langchain.schema import AIMessage  # type: ignore[reportUnusedImport]
from langchain.schema import HumanMessage  # type: ignore[reportUnusedImport]
from langchain.schema import SystemMessage  # type: ignore[reportUnusedImport]
from langchain.schema import BaseMessage
from langchain.tools import BaseTool


def is_test_mode() -> bool:
    return os.getenv("PYTEST_CURRENT_TEST") is not None or "pytest" in sys.argv[0]


def _make_serializable(obj: Any) -> Any:
    """Convert objects to JSON-serializable form for caching."""
    if isinstance(obj, BaseMessage):
        return {
            "type": obj.__class__.__name__,
            "content": obj.content,  # type: ignore[reportUnknownMemberType]
            "additional_kwargs": obj.additional_kwargs,  # type: ignore[reportUnknownMemberType]
        }
    elif isinstance(obj, list):
        return [_make_serializable(item) for item in obj]
    elif isinstance(obj, tuple):
        return tuple(_make_serializable(item) for item in obj)
    elif isinstance(obj, dict):
        return {k: _make_serializable(v) for k, v in obj.items()}
    else:
        return obj


def _json_encoder(obj: Any) -> Any:
    """JSON encoder for complex objects."""
    if isinstance(obj, BaseMessage):
        return {
            "type": obj.__class__.__name__,
            "content": obj.content,  # type: ignore[reportUnknownMemberType]
            "additional_kwargs": obj.additional_kwargs,  # type: ignore[reportUnknownMemberType]
        }
    raise TypeError(f"Object of type {type(obj)} is not JSON serializable")


def _deserialize(obj: Any) -> Any:
    """Convert from JSON-serializable form back to objects."""
    if (
        isinstance(obj, dict)
        and "type" in obj
        and obj["type"] in ("HumanMessage", "AIMessage", "SystemMessage")
    ):
        # Reconstruct BaseMessage
        from langchain.schema import AIMessage, HumanMessage, SystemMessage

        msg_class = {
            "HumanMessage": HumanMessage,
            "AIMessage": AIMessage,
            "SystemMessage": SystemMessage,
        }[obj["type"]]
        return msg_class(content=obj["content"], additional_kwargs=obj.get("additional_kwargs", {}))  # type: ignore
    elif isinstance(obj, list):
        return [_deserialize(item) for item in obj]
    elif isinstance(obj, tuple):
        return tuple(_deserialize(item) for item in obj)
    elif isinstance(obj, dict):
        return {k: _deserialize(v) for k, v in obj.items()}
    else:
        return obj


def _stable_repr(obj: Any) -> str:
    """Create a stable string representation of an object for caching keys."""
    if isinstance(obj, BaseTool):
        # For BaseTool objects, use stable attributes instead of memory addresses
        return f"BaseTool(name={obj.name}, description={obj.description})"
    elif isinstance(obj, BaseMessage):
        # For BaseMessage, use stable representation
        return f"{obj.__class__.__name__}(content={repr(obj.content)}, additional_kwargs={repr(obj.additional_kwargs)})"  # type: ignore[reportUnknownMemberType,reportUnknownArgumentType]
    elif isinstance(obj, list):
        return "[" + ",".join(_stable_repr(item) for item in obj) + "]"
    else:
        return str(obj)


def memoise_for_tests(func: Callable[..., Any]) -> Callable[..., Any]:
    @functools.wraps(func)
    def wrapper(*args: Any, **kwargs: Any) -> Any:
        # Always try to use recordings if they exist, regardless of test mode
        # Compute key: join all args and kwargs with :
        key_parts = [_stable_repr(arg) for arg in args]
        for k in sorted(kwargs.keys()):
            key_parts.append(f"{k}={_stable_repr(kwargs[k])}")
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
                # If file is corrupted, fall back to normal execution
                pass

        if key in data:
            stored_result = data[key]
            # Convert back from serializable form if needed
            return _deserialize(stored_result)

        # If no recording found, check if we're in test mode
        if not is_test_mode():
            return func(*args, **kwargs)

        result = func(*args, **kwargs)

        try:
            data[key] = result
            with open(filename, "w") as f:
                json.dump(data, f, indent=2, default=_json_encoder)
        except (TypeError, ValueError):
            # If result is not JSON serializable, skip caching
            pass

        return result

    return wrapper
