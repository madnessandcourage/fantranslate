import sys
from enum import Enum
from typing import Any


class LogLevel(Enum):
    NORMAL = 0  # Only errors
    DEBUG = 1  # Everything except trace
    TRACE = 2  # Everything


_current_log_level = LogLevel.NORMAL
_current_indent = 0


def set_log_level(level: LogLevel) -> None:
    global _current_log_level
    _current_log_level = level


def get_log_level() -> LogLevel:
    return _current_log_level


def _should_log(level: LogLevel) -> bool:
    return _current_log_level.value >= level.value


def _get_indent() -> str:
    return "  " * _current_indent


def _trim_to_100_words(text: str) -> str:
    words = text.split()
    if len(words) <= 100:
        return text
    return " ".join(words[:100]) + "..."


def log_enter(message: str) -> None:
    global _current_indent
    if _should_log(LogLevel.DEBUG):
        print(f"{_get_indent()}ENTER: {message}", file=sys.stderr)
    _current_indent += 1


def log_exit(message: str) -> None:
    global _current_indent
    _current_indent -= 1
    if _should_log(LogLevel.DEBUG):
        print(f"{_get_indent()}EXIT: {message}", file=sys.stderr)


def log_info(message: str) -> None:
    if _should_log(LogLevel.DEBUG):
        print(f"{_get_indent()}INFO: {message}", file=sys.stderr)


def log_trace(message: str, *args: Any) -> None:
    if _should_log(LogLevel.TRACE):
        formatted_args = " ".join(str(arg) for arg in args)
        if formatted_args:
            message = f"{message} {formatted_args}"
        print(f"{_get_indent()}TRACE: {message}", file=sys.stderr)


def log_llm_system(message: str) -> None:
    if _should_log(LogLevel.DEBUG):
        trimmed = _trim_to_100_words(message)
        print(f"{_get_indent()}LLM_SYSTEM: {trimmed}", file=sys.stderr)


def log_llm_operator(message: str) -> None:
    if _should_log(LogLevel.DEBUG):
        trimmed = _trim_to_100_words(message)
        print(f"{_get_indent()}LLM_OPERATOR: {trimmed}", file=sys.stderr)


def log_llm_ai(message: str) -> None:
    if _should_log(LogLevel.DEBUG):
        trimmed = _trim_to_100_words(message)
        print(f"{_get_indent()}LLM_AI: {trimmed}", file=sys.stderr)


def log_llm_tool(tool: str, *args: Any) -> None:
    if _should_log(LogLevel.DEBUG):
        formatted_args = " ".join(str(arg) for arg in args)
        message = f"Tool used: {tool}"
        if formatted_args:
            message += f" {formatted_args}"
        print(f"{_get_indent()}LLM_TOOL: {message}", file=sys.stderr)


def log_error(message: str) -> None:
    print(f"{_get_indent()}ERROR: {message}", file=sys.stderr)
