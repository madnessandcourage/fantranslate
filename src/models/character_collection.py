from typing import Any, Dict, List, Optional

from ..helpers.fuzzy import FuzzyIndex, levenshtein_distance
from .character import Character
from .translation_string import TranslationString


class CharacterCollection:
    def __init__(self):
        self.characters: List[Character] = []
        self._name_index: FuzzyIndex = FuzzyIndex()

    def _add_to_index(self, character: Character):
        # Add full name
        self._name_index.add(character.name.original_text, character)
        # Add short names
        for short_name in character.short_names:
            self._name_index.add(short_name.original_text, character)

    def _remove_from_index(self, character: Character):
        # Note: FuzzyIndex doesn't have remove, so we'll rebuild index if needed
        # For simplicity, since small collection, we can search linearly
        pass

    def search(self, query: str) -> Optional[Character]:
        """Search for a character by name or short name with fuzzy matching."""
        if not query:
            return None

        best_match = None
        best_distance = float("inf")

        for character in self.characters:
            # Check full name
            distance = levenshtein_distance(
                query.lower(), character.name.original_text.lower()
            )
            max_dist = 1 if len(query) <= 4 else 2
            if distance <= max_dist and distance < best_distance:
                best_distance = distance
                best_match = character

            # Check short names
            for short_name in character.short_names:
                distance = levenshtein_distance(
                    query.lower(), short_name.original_text.lower()
                )
                max_dist = 1 if len(query) <= 4 else 2
                if distance <= max_dist and distance < best_distance:
                    best_distance = distance
                    best_match = character

        return best_match

    def create_character(
        self,
        name: str,
        original_language: str,
        available_languages: List[str],
        short_names: Optional[List[str]] = None,
        gender: Optional[str] = None,
        biography: Optional[str] = None,
        characteristics: Optional[List[Dict[str, Any]]] = None,
    ) -> Character:
        """Create a new character and add to collection."""
        name_ts = TranslationString(name, original_language, available_languages)
        short_names_ts = [
            TranslationString(sn, original_language, available_languages)
            for sn in (short_names or [])
        ]
        gender_ts = (
            TranslationString(gender, original_language, available_languages)
            if gender
            else None
        )
        biography_ts = (
            TranslationString(biography, original_language, available_languages)
            if biography
            else None
        )
        characteristics_ts = [
            {
                "sentence": TranslationString(
                    char["sentence"], original_language, available_languages
                ),
                "confidence": char.get("confidence", 1),
            }
            for char in (characteristics or [])
        ]

        character = Character(
            name=name_ts,
            short_names=short_names_ts,
            gender=gender_ts,
            biography=biography_ts,
            characteristics=characteristics_ts,
        )
        self.characters.append(character)
        self._add_to_index(character)
        return character

    def update_character(
        self,
        name: str,
        updates: Dict[str, Any],
        original_language: str,
        available_languages: List[str],
    ) -> Optional[Character]:
        """Update an existing character."""
        character = self.search(name)
        if not character:
            return None

        # Handle updates
        if "name" in updates:
            character.name = TranslationString(
                updates["name"], original_language, available_languages
            )
        if "short_names" in updates:
            character.short_names = [
                TranslationString(sn, original_language, available_languages)
                for sn in updates["short_names"]
            ]
        if "gender" in updates:
            character.gender = (
                TranslationString(
                    updates["gender"], original_language, available_languages
                )
                if updates["gender"]
                else None
            )
        if "biography" in updates:
            character.biography = (
                TranslationString(
                    updates["biography"], original_language, available_languages
                )
                if updates["biography"]
                else None
            )
        if "characteristics" in updates:
            character.characteristics = [
                {
                    "sentence": TranslationString(
                        char["sentence"], original_language, available_languages
                    ),
                    "confidence": char.get("confidence", 1),
                }
                for char in updates["characteristics"]
            ]

        return character

    def get_character_translation(
        self, name: str, language: str
    ) -> Optional[Dict[str, Any]]:
        """Get character information translated to the specified language."""
        character = self.search(name)
        if not character:
            return None
        return character.get_translated(language)

    def to_dict(self) -> List[Dict[str, Any]]:
        return [char.to_dict() for char in self.characters]

    @classmethod
    def from_dict(cls, data: List[Dict[str, Any]]) -> "CharacterCollection":
        collection = cls()
        for char_data in data:
            character = Character.from_dict(char_data)
            collection.characters.append(character)
            collection._add_to_index(character)
        return collection
