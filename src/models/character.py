from typing import Any, Dict, List, Optional

from .translation_string import TranslationString


class Character:
    def __init__(
        self,
        name: TranslationString,
        short_names: Optional[List[TranslationString]] = None,
        gender: Optional[TranslationString] = None,
        biography: Optional[TranslationString] = None,
        characteristics: Optional[List[Dict[str, Any]]] = None,
    ):
        self.name = name
        self.short_names = short_names or []
        self.gender = gender
        self.biography = biography
        self.characteristics = characteristics or []

    def update(
        self,
        name: Optional[TranslationString] = None,
        short_names: Optional[List[TranslationString]] = None,
        gender: Optional[TranslationString] = None,
        biography: Optional[TranslationString] = None,
        characteristics: Optional[List[Dict[str, Any]]] = None,
    ):
        if name is not None:
            self.name = name
        if short_names is not None:
            self.short_names = short_names
        if gender is not None:
            self.gender = gender
        if biography is not None:
            self.biography = biography
        if characteristics is not None:
            self.characteristics = characteristics

    def get_translated(self, language: str) -> Dict[str, Any]:
        def get_text(ts: TranslationString) -> str:
            translated = getattr(ts, language, None)
            return translated if translated is not None else ts.original_text

        return {
            "name": get_text(self.name),
            "short_names": [get_text(sn) for sn in self.short_names],
            "gender": get_text(self.gender) if self.gender else None,
            "biography": get_text(self.biography) if self.biography else None,
            "characteristics": [
                {
                    "sentence": get_text(char["sentence"]),
                    "confidence": char["confidence"],
                }
                for char in self.characteristics
            ],
        }

    def to_dict(self) -> Dict[str, Any]:
        return {
            "name": self.name.to_dict(),
            "short_names": [sn.to_dict() for sn in self.short_names],
            "gender": self.gender.to_dict() if self.gender else None,
            "biography": self.biography.to_dict() if self.biography else None,
            "characteristics": [
                {
                    "sentence": char["sentence"].to_dict(),
                    "confidence": char["confidence"],
                }
                for char in self.characteristics
            ],
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Character":
        return cls(
            name=TranslationString.from_dict(data["name"]),
            short_names=[TranslationString.from_dict(sn) for sn in data["short_names"]],
            gender=(
                TranslationString.from_dict(data["gender"]) if data["gender"] else None
            ),
            biography=(
                TranslationString.from_dict(data["biography"])
                if data["biography"]
                else None
            ),
            characteristics=[
                {
                    "sentence": TranslationString.from_dict(char["sentence"]),
                    "confidence": char["confidence"],
                }
                for char in data["characteristics"]
            ],
        )
