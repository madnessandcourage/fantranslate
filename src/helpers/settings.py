import os
from dataclasses import dataclass
from typing import Any, Dict, List, cast

import yaml

DEFAULT_CHARACTERS_STORAGE = "characters.yml"

# Directory containing application resource files (prompts, etc.)
RESOURCE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))


@dataclass
class Settings:
    languages: List[str]
    translate_from: str
    translate_to: str


__settings = None


def settings() -> Settings:
    global __settings
    if __settings is not None:
        return __settings

    project_file = os.path.join(RESOURCE_DIR, "project.yml")
    if not os.path.exists(project_file):
        raise FileNotFoundError(f"project.yml not found in {os.getcwd()}")

    with open(project_file, "r") as f:
        data = cast(Dict[str, Any], yaml.safe_load(f))

    languages = data.get("languages")
    translate_from = data.get("translate_from")
    translate_to = data.get("translate_to")

    if languages is None or translate_from is None or translate_to is None:
        raise ValueError(
            "project.yml must contain 'languages', 'translate_from', and 'translate_to'"
        )

    if not isinstance(languages, list) or not all(
        isinstance(lang, str) for lang in languages
    ):
        raise ValueError("'languages' must be a list of strings")

    if not isinstance(translate_from, str):
        raise ValueError("'translate_from' must be a string")

    if not isinstance(translate_to, str):
        raise ValueError("'translate_to' must be a string")

    if translate_from in languages:
        raise ValueError("'translate_from' must not be in 'languages'")

    if translate_to not in languages:
        raise ValueError("'translate_to' must be in 'languages'")

    __settings = Settings(
        languages=cast(List[str], languages),
        translate_from=translate_from,
        translate_to=translate_to,
    )
    return __settings
