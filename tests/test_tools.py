import json

from src.tools.hello import hello_tool
from src.tools.character import character_tools, search_character, create_character, update_character, get_character_translation


def test_hello_tool():
    """Test that the hello tool returns 'World'."""
    assert hello_tool.func is not None
    result = hello_tool.func("")
    assert result == "World"


def test_character_tools():
    """Test that character tools are defined."""
    assert len(character_tools) == 4
    names = [tool.name for tool in character_tools]
    assert "SearchCharacter" in names
    assert "CreateCharacter" in names
    assert "UpdateCharacter" in names
    assert "GetCharacterTranslation" in names


def test_create_character():
    """Test creating a character."""
    input_data = {
        "name": "Frodo Baggins",
        "original_language": "en",
        "available_languages": ["en", "es"],
        "short_names": ["Frodo"],
        "gender": "male",
        "biography": "A hobbit from the Shire.",
        "characteristics": [{"sentence": "Brave and loyal.", "confidence": 1}]
    }
    result = create_character(json.dumps(input_data))
    assert "created successfully" in result


def test_search_character():
    """Test searching for a character."""
    result = search_character("Frodo")
    assert "Frodo Baggins" in result


def test_update_character():
    """Test updating a character."""
    input_data = {
        "name": "Frodo",
        "updates": {"biography": "A brave hobbit."},
        "original_language": "en",
        "available_languages": ["en", "es"]
    }
    result = update_character(json.dumps(input_data))
    assert "updated successfully" in result


def test_get_character_translation():
    """Test getting character translation."""
    input_data = {"name": "Frodo", "language": "es"}
    result = get_character_translation(json.dumps(input_data))
    # Since no translations added, should return original
    assert "Frodo Baggins" in result
