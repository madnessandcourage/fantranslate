from dataclasses import dataclass
from typing import Any, Dict, List, Optional, Union, cast

from helpers.settings import settings

from .translation_string import TranslationString


def _ensure_ts(value: Union[str, TranslationString]) -> TranslationString:
    if isinstance(value, str):
        s = settings()
        original_language = s.translate_from
        available_languages = [s.translate_from] + s.languages
        return TranslationString(value, original_language, available_languages)
    return value


@dataclass
class TranslatedCharacter:
    name: str
    short_names: List[str]
    gender: Optional[str]
    characteristics: List[Dict[str, Union[str, int]]]


class Characteristic:
    def __init__(self, text: TranslationString, confidence: int = 1):
        self.text = text
        self.confidence = confidence

    def to_dict(self) -> Dict[str, Any]:
        return {
            "text": self.text.to_dict(),
            "confidence": self.confidence,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Characteristic":
        return cls(
            text=TranslationString.from_dict(data["text"]),
            confidence=data["confidence"],
        )


class Character:
    def __init__(
        self,
        name: Union[str, TranslationString],
        short_names: Optional[List[Union[str, TranslationString]]] = None,
        gender: Optional[Union[str, TranslationString]] = None,
        characteristics: Optional[Union[List[str], List[Characteristic]]] = None,  # type: ignore
    ):
        self.name = _ensure_ts(name)
        self.short_names = [_ensure_ts(sn) for sn in (short_names or [])]
        self.gender = _ensure_ts(gender) if gender else None
        if characteristics is None:
            self.characteristics: List[Characteristic] = []
        elif characteristics and isinstance(characteristics[0], str):
            # List of strings, assume confidence 1
            str_list = cast(List[str], characteristics)
            self.characteristics = [
                Characteristic(_ensure_ts(text), 1) for text in str_list
            ]
        else:
            self.characteristics = cast(List[Characteristic], characteristics)  # type: ignore

    def update(
        self,
        name: Optional[Union[str, TranslationString]] = None,
        gender: Optional[Union[str, TranslationString]] = None,
    ):
        if name is not None:
            self.name = _ensure_ts(name)
        if gender is not None:
            self.gender = _ensure_ts(gender)

    def add_short_name(self, short_name: Union[str, TranslationString]):
        ts = _ensure_ts(short_name)
        if ts not in self.short_names:
            self.short_names.append(ts)

    def remove_short_name(self, short_name: Union[str, TranslationString]):
        ts = _ensure_ts(short_name)
        if ts in self.short_names:
            self.short_names.remove(ts)

    def add_characteristic(self, text: str):
        ts = _ensure_ts(text)
        char = Characteristic(ts)
        self.characteristics.append(char)

    def remove_characteristic(self, text: str):
        self.characteristics = [
            c for c in self.characteristics if c.text.original_text != text
        ]

    def reinforce_characteristic(self, text: str):
        for c in self.characteristics:
            if c.text.original_text == text:
                c.confidence += 1
                break

    def decrease_confidence(self, text: str):
        for c in self.characteristics:
            if c.text.original_text == text:
                c.confidence -= 1
                break

    def limit_characteristics(self, number: int):
        self.characteristics.sort(key=lambda c: c.confidence, reverse=True)
        self.characteristics = self.characteristics[:number]

    def get_translated(self, language: str) -> TranslatedCharacter:
        def get_text(ts: TranslationString) -> str:
            translated = getattr(ts, language, None)
            return translated if translated is not None else ts.original_text

        return TranslatedCharacter(
            name=get_text(self.name),
            short_names=[get_text(sn) for sn in self.short_names],
            gender=get_text(self.gender) if self.gender else None,
            characteristics=[
                {
                    "sentence": get_text(char.text),
                    "confidence": char.confidence,
                }
                for char in self.characteristics
            ],
        )

    def to_dict(self) -> Dict[str, Any]:
        return {
            "name": self.name.to_dict(),
            "short_names": [sn.to_dict() for sn in self.short_names],
            "gender": self.gender.to_dict() if self.gender else None,
            "characteristics": [char.to_dict() for char in self.characteristics],
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Character":
        return cls(
            name=TranslationString.from_dict(data["name"]),
            short_names=[TranslationString.from_dict(sn) for sn in data["short_names"]],
            gender=(
                TranslationString.from_dict(data["gender"]) if data["gender"] else None
            ),
            characteristics=[
                Characteristic.from_dict(char) for char in data["characteristics"]
            ],
        )
