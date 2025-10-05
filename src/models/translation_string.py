import json
from typing import Any, Dict, List, Optional


class TranslationString:
    def __init__(
        self, original_text: str, original_language: str, available_languages: List[str]
    ):
        self.original_text = original_text
        self.original_language = original_language
        self.available_languages = available_languages
        self.translations: Dict[str, str] = {}

    def __getattr__(self, name: str) -> Optional[str]:
        if name == self.original_language:
            return self.original_text
        return self.translations.get(name, None)

    def __setattr__(self, name: str, value: Any) -> None:
        if name in [
            "original_text",
            "original_language",
            "available_languages",
            "translations",
        ]:
            object.__setattr__(self, name, value)
        elif name in self.available_languages:
            self.translations[name] = value
        else:
            raise AttributeError(
                f"'{self.__class__.__name__}' object has no attribute '{name}'"
            )

    def __eq__(self, other: object) -> bool:
        if isinstance(other, TranslationString):
            return (
                self.original_text == other.original_text
                and self.original_language == other.original_language
                and self.available_languages == other.available_languages
                and self.translations == other.translations
            )
        if isinstance(other, str):
            if other == self.original_text:
                return True
            return other in self.translations.values()
        return False

    def __str__(self) -> str:
        return self.original_text

    def to_dict(self) -> Dict[str, Any]:
        return {
            "original_text": self.original_text,
            "original_language": self.original_language,
            "available_languages": self.available_languages,
            "translations": self.translations,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "TranslationString":
        obj = cls(
            data["original_text"],
            data["original_language"],
            data["available_languages"],
        )
        obj.translations = data["translations"]
        return obj

    def to_json(self) -> str:
        return json.dumps(self.to_dict())

    @classmethod
    def from_json(cls, json_str: str) -> "TranslationString":
        data = json.loads(json_str)
        return cls.from_dict(data)
