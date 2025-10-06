import json
from typing import List

from langchain.tools import Tool

from helpers.settings import settings
from models.character import Character, TranslatedCharacter
from models.character_collection import CharacterCollection

# Global character collection
character_collection = CharacterCollection()


def _character_to_xml(translated: TranslatedCharacter) -> str:
    """Convert TranslatedCharacter to XML for AI."""
    xml_parts = ["<character>"]
    xml_parts.append(f"<name>{translated.name}</name>")
    xml_parts.append("<short_names>")
    for sn in translated.short_names:
        xml_parts.append(f"<short_name>{sn}</short_name>")
    xml_parts.append("</short_names>")
    if translated.gender:
        xml_parts.append(f"<gender>{translated.gender}</gender>")
    xml_parts.append("<characteristics>")
    for char in translated.characteristics:
        xml_parts.append("<characteristic>")
        xml_parts.append(f"<sentence>{char['sentence']}</sentence>")
        xml_parts.append(f"<confidence>{char['confidence']}</confidence>")
        xml_parts.append("</characteristic>")
    xml_parts.append("</characteristics>")
    xml_parts.append("</character>")
    return "".join(xml_parts)


def search_character(query: str) -> str:
    """Search for a character by name or short name. Input: search query string."""
    character = character_collection.search(query)
    if character:
        s = settings()
        translated = character.get_translated(s.translate_from)
        return _character_to_xml(translated)
    else:
        return "Character not found"


def create_character(name: str, gender: str = "UNKNOWN") -> str:
    """Create a new character. Input: name (required), gender (optional, default 'other')."""
    try:
        character = Character(
            name=name,
            gender=gender,
            characteristics=[],
        )
        character_collection.add_character(character)
        return f"Character '{name}' created successfully"
    except Exception as e:
        return f"Error creating character: {str(e)}"


def add_character_short_name(name: str, short_name: str) -> str:
    """Add a short name to an existing character. Input: character name, short name to add."""
    try:
        character = character_collection.search(name)
        if not character:
            return f"Character '{name}' not found"
        character.add_short_name(short_name)
        character_collection._rebuild_index()  # type: ignore
        return f"Short name '{short_name}' added to character '{name}'"
    except Exception as e:
        return f"Error adding short name: {str(e)}"


def set_character_gender(name: str, gender: str) -> str:
    """Set the gender of an existing character. Input: character name, gender."""
    try:
        character = character_collection.search(name)
        if not character:
            return f"Character '{name}' not found"
        character.update(gender=gender)
        return f"Gender of character '{name}' set to '{gender}'"
    except Exception as e:
        return f"Error setting gender: {str(e)}"


def get_character_translation(input_str: str) -> str:
    """Get character information translated to a language. Input: JSON with name and language."""
    try:
        data = json.loads(input_str)
        name = data["name"]
        language = data["language"]
        translated = character_collection.get_character_translation(name, language)
        if translated:
            return _character_to_xml(translated)
        else:
            return f"Character '{name}' not found"
    except Exception as e:
        return f"Error getting translation: {str(e)}"


search_character_tool = Tool(
    name="SearchCharacter",
    description="Search for an existing character by name or short name using fuzzy matching.",
    func=search_character,
)

create_character_tool = Tool(
    name="CreateCharacter",
    description="Create a new character with the provided information.",
    func=create_character,
)

add_short_name_tool = Tool(
    name="AddCharacterShortName",
    description="Add a short name to an existing character.",
    func=add_character_short_name,
)

set_gender_tool = Tool(
    name="SetCharacterGender",
    description="Set the gender of an existing character.",
    func=set_character_gender,
)

get_character_translation_tool = Tool(
    name="GetCharacterTranslation",
    description="Get character information translated to the specified language.",
    func=get_character_translation,
)

character_tools: List[Tool] = [
    search_character_tool,
    create_character_tool,
    add_short_name_tool,
    set_gender_tool,
    get_character_translation_tool,
]
