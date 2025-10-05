import json
from typing import List

from langchain.tools import Tool

from ..models.character_collection import CharacterCollection

# Global character collection
character_collection = CharacterCollection()


def search_character(query: str) -> str:
    """Search for a character by name or short name. Input: search query string."""
    character = character_collection.search(query)
    if character:
        return json.dumps(character.to_dict())
    else:
        return "Character not found"


def create_character(input_str: str) -> str:
    """Create a new character. Input: JSON with name (required), short_names, gender, biography, characteristics, original_language, available_languages."""
    try:
        data = json.loads(input_str)
        name = data["name"]
        original_language = data["original_language"]
        available_languages = data["available_languages"]
        short_names = data.get("short_names", [])
        gender = data.get("gender")
        biography = data.get("biography")
        characteristics = data.get("characteristics", [])
        character_collection.create_character(
            name=name,
            original_language=original_language,
            available_languages=available_languages,
            short_names=short_names,
            gender=gender,
            biography=biography,
            characteristics=characteristics,
        )
        return f"Character '{name}' created successfully"
    except Exception as e:
        return f"Error creating character: {str(e)}"


def update_character(input_str: str) -> str:
    """Update an existing character. Input: JSON with name (to identify), updates dict, original_language, available_languages. WARNING: Editing name is dangerous."""
    try:
        data = json.loads(input_str)
        name = data["name"]
        updates = data["updates"]
        original_language = data["original_language"]
        available_languages = data["available_languages"]
        character = character_collection.update_character(
            name=name,
            updates=updates,
            original_language=original_language,
            available_languages=available_languages,
        )
        if character:
            return f"Character '{name}' updated successfully"
        else:
            return f"Character '{name}' not found"
    except Exception as e:
        return f"Error updating character: {str(e)}"


def get_character_translation(input_str: str) -> str:
    """Get character information translated to a language. Input: JSON with name and language."""
    try:
        data = json.loads(input_str)
        name = data["name"]
        language = data["language"]
        translated = character_collection.get_character_translation(name, language)
        if translated:
            return json.dumps(translated)
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

update_character_tool = Tool(
    name="UpdateCharacter",
    description="Update information of an existing character. Be careful with editing the name.",
    func=update_character,
)

get_character_translation_tool = Tool(
    name="GetCharacterTranslation",
    description="Get character information translated to the specified language.",
    func=get_character_translation,
)

character_tools: List[Tool] = [
    search_character_tool,
    create_character_tool,
    update_character_tool,
    get_character_translation_tool,
]
