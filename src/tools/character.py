import json
import os
from typing import List

from langchain.tools import StructuredTool
from pydantic import BaseModel, Field

from helpers.settings import DEFAULT_CHARACTERS_STORAGE, settings
from models.character import Character, TranslatedCharacter
from models.character_collection import CharacterCollection
from tracing import log_llm_tool

# Global character collection
character_collection = CharacterCollection()
if os.path.exists(DEFAULT_CHARACTERS_STORAGE):
    character_collection = CharacterCollection.from_file(DEFAULT_CHARACTERS_STORAGE)


# Pydantic models for tool arguments
class SearchCharacterArgs(BaseModel):
    query: str = Field(
        description="The search query for finding a character by name or short name"
    )


class CreateCharacterArgs(BaseModel):
    name: str = Field(description="The name of the character to create")
    gender: str = Field(
        default="UNKNOWN", description="The gender of the character (optional)"
    )


class AddShortNameArgs(BaseModel):
    name: str = Field(description="The name of the existing character")
    short_name: str = Field(description="The short name to add to the character")


class SetGenderArgs(BaseModel):
    name: str = Field(description="The name of the existing character")
    gender: str = Field(description="The gender to set for the character")


class GetTranslationArgs(BaseModel):
    name: str = Field(description="The name of the character")
    language: str = Field(description="The language code to translate to")


class GetAllCharactersArgs(BaseModel):
    pass  # No arguments needed


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


def get_all_characters() -> str:
    """Get all characters in the system. Returns XML with name, short_names, and gender only."""
    s = settings()
    characters = character_collection.get_all_characters(s.translate_from)

    xml_parts = ["<characters>"]
    for char in characters:
        xml_parts.append("<character>")
        xml_parts.append(f"<name>{char.name}</name>")
        xml_parts.append("<short_names>")
        for sn in char.short_names:
            xml_parts.append(f"<short_name>{sn}</short_name>")
        xml_parts.append("</short_names>")
        if char.gender:
            xml_parts.append(f"<gender>{char.gender}</gender>")
        xml_parts.append("</character>")
    xml_parts.append("</characters>")

    return "".join(xml_parts)


def _search_character_with_logging(args: SearchCharacterArgs) -> str:
    log_llm_tool("SearchCharacter", args.query)
    return search_character(args.query)


def _create_character_with_logging(args: CreateCharacterArgs) -> str:
    log_llm_tool("CreateCharacter", args.name, args.gender)
    return create_character(args.name, args.gender)


def _add_short_name_with_logging(args: AddShortNameArgs) -> str:
    log_llm_tool("AddCharacterShortName", args.name, args.short_name)
    return add_character_short_name(args.name, args.short_name)


def _set_gender_with_logging(args: SetGenderArgs) -> str:
    log_llm_tool("SetCharacterGender", args.name, args.gender)
    return set_character_gender(args.name, args.gender)


def _get_translation_with_logging(args: GetTranslationArgs) -> str:
    log_llm_tool("GetCharacterTranslation", args.name, args.language)
    return get_character_translation(
        json.dumps({"name": args.name, "language": args.language})
    )


def _get_all_characters_with_logging(args: GetAllCharactersArgs) -> str:
    log_llm_tool("GetAllCharacters")
    return get_all_characters()


search_character_tool = StructuredTool.from_function(
    func=_search_character_with_logging,
    name="SearchCharacter",
    description="Search for an existing character by name or short name using fuzzy matching.",
    args_schema=SearchCharacterArgs,
)

create_character_tool = StructuredTool.from_function(
    func=_create_character_with_logging,
    name="CreateCharacter",
    description="Create a new character with the provided information.",
    args_schema=CreateCharacterArgs,
)

add_short_name_tool = StructuredTool.from_function(
    func=_add_short_name_with_logging,
    name="AddCharacterShortName",
    description="Add a short name to an existing character.",
    args_schema=AddShortNameArgs,
)

set_gender_tool = StructuredTool.from_function(
    func=_set_gender_with_logging,
    name="SetCharacterGender",
    description="Set the gender of an existing character.",
    args_schema=SetGenderArgs,
)

get_character_translation_tool = StructuredTool.from_function(
    func=_get_translation_with_logging,
    name="GetCharacterTranslation",
    description="Get character information translated to the specified language.",
    args_schema=GetTranslationArgs,
)

get_all_characters_tool = StructuredTool.from_function(
    func=_get_all_characters_with_logging,
    name="GetAllCharacters",
    description="Get a list of all characters in the system with their names, short names, and genders.",
    args_schema=GetAllCharactersArgs,
)

character_tools: List[StructuredTool] = [
    search_character_tool,
    create_character_tool,
    add_short_name_tool,
    set_gender_tool,
    get_character_translation_tool,
    get_all_characters_tool,
]
