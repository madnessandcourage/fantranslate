from typing import Any, Dict, List, Optional, Union

from .translation_string import TranslationString


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
        name: TranslationString,
        short_names: Optional[List[TranslationString]] = None,
        gender: Optional[TranslationString] = None,
        characteristics: Optional[List[Characteristic]] = None,
    ):
        self.name = name
        self.short_names = short_names or []
        self.gender = gender
        self.characteristics = characteristics or []

    def update(
        self,
        name: Optional[TranslationString] = None,
        gender: Optional[TranslationString] = None,
    ):
        if name is not None:
            self.name = name
        if gender is not None:
            self.gender = gender

    def add_short_name(self, short_name: TranslationString):
        if short_name not in self.short_names:
            self.short_names.append(short_name)

    def remove_short_name(self, short_name: TranslationString):
        if short_name in self.short_names:
            self.short_names.remove(short_name)

    def add_characteristic(
        self, text: str, original_language: str, available_languages: List[str]
    ):
        ts = TranslationString(text, original_language, available_languages)
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

    def get_translated(
        self, language: str
    ) -> Dict[str, Union[str, List[str], None, List[Dict[str, Union[str, int]]]]]:
        def get_text(ts: TranslationString) -> str:
            translated = getattr(ts, language, None)
            return translated if translated is not None else ts.original_text

        return {
            "name": get_text(self.name),
            "short_names": [get_text(sn) for sn in self.short_names],
            "gender": get_text(self.gender) if self.gender else None,
            "characteristics": [
                {
                    "sentence": get_text(char.text),
                    "confidence": char.confidence,
                }
                for char in self.characteristics
            ],
        }

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
