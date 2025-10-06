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

    def translate(self, chapter_contents: str) -> None:
        """Translate character properties using AI based on chapter context."""
        from ai import ai
        from helpers.context import Context
        from helpers.settings import settings
        from tracing import log_enter, log_exit, log_info

        log_enter("translate_character")

        s = settings()

        # Step 1: Get chapter summary focusing on this character
        summary_prompt = f"""Summarize the chapter focusing on the character "{self.name.original_text}".
Include key events, interactions, and descriptions related to this character.
Keep the summary concise but informative."""

        log_info("Getting chapter summary for character")
        chapter_summary = ai(summary_prompt, chapter_contents)
        if not chapter_summary:
            log_info("Failed to get chapter summary")
            log_exit("translate_character")
            return

        # Step 2: Build context
        context = Context()
        context = context.add(
            "PROBLEM",
            "We need to translate character information from a book chapter to make it available in multiple languages.",
        )
        context = context.add("CHAPTER SUMMARY", chapter_summary)
        context = context.wrap("CHARACTER_DATA", self.to_xml())

        # Step 3: Translate each property independently
        system_prompt = context.pipe("character_translator").build()

        # Translate name
        if self.name.original_text:
            name_prompt = f"Translate the character's name '{self.name.original_text}' to {s.translate_to}."
            translated_name = ai(system_prompt, name_prompt)
            if translated_name:
                setattr(self.name, s.translate_to, translated_name.strip())

        # Translate short names
        for short_name in self.short_names:
            if short_name.original_text:
                sn_prompt = f"Translate the character's short name '{short_name.original_text}' to {s.translate_to}."
                translated_sn = ai(system_prompt, sn_prompt)
                if translated_sn:
                    setattr(short_name, s.translate_to, translated_sn.strip())

        # Translate gender
        if self.gender and self.gender.original_text:
            gender_prompt = f"Translate the character's gender '{self.gender.original_text}' to {s.translate_to}."
            translated_gender = ai(system_prompt, gender_prompt)
            if translated_gender:
                setattr(self.gender, s.translate_to, translated_gender.strip())

        # Translate characteristics
        for char in self.characteristics:
            if char.text.original_text:
                char_prompt = f"Translate this character description: '{char.text.original_text}' to {s.translate_to}."
                translated_char = ai(system_prompt, char_prompt)
                if translated_char:
                    setattr(char.text, s.translate_to, translated_char.strip())

        log_exit("translate_character")

    def to_xml(self) -> str:
        """Serialize character to XML format for AI consumption."""
        xml_parts = ["<character>"]

        xml_parts.append(f"<name>{self.name.original_text}</name>")

        if self.short_names:
            xml_parts.append("<short_names>")
            for sn in self.short_names:
                xml_parts.append(f"<name>{sn.original_text}</name>")
            xml_parts.append("</short_names>")

        if self.gender:
            xml_parts.append(f"<gender>{self.gender.original_text}</gender>")

        if self.characteristics:
            xml_parts.append("<characteristics>")
            for char in self.characteristics:
                xml_parts.append(
                    f"<characteristic confidence='{char.confidence}'>{char.text.original_text}</characteristic>"
                )
            xml_parts.append("</characteristics>")

        xml_parts.append("</character>")
        return "\n".join(xml_parts)

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
