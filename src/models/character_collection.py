from typing import Any, Dict, List, Optional

from ..helpers.fuzzy import FuzzyIndex
from ..helpers.settings import settings  # type: ignore
from .character import Character, TranslatedCharacter


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

    def _rebuild_index(self):
        self._name_index = FuzzyIndex()
        for character in self.characters:
            self._add_to_index(character)

    def search(self, query: str) -> Optional[Character]:
        """Search for a character by name or short name with fuzzy matching."""
        if not query:
            return None

        max_distance = 1 if len(query) <= 4 else 2
        _, character = self._name_index.search(query, max_distance)
        return character

    def add_character(self, character: Character):
        """Add a character to the collection."""
        self.characters.append(character)
        self._add_to_index(character)

    def remove_character(self, name: str):
        """Remove a character from the collection."""
        self.characters = [c for c in self.characters if c.name.original_text != name]
        self._rebuild_index()

    def get_character_translation(
        self, name: str, language: str
    ) -> Optional[TranslatedCharacter]:
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
