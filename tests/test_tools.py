import json
from unittest.mock import patch

from src.helpers.settings import Settings
from src.tools.character import (
    character_tools,
    create_character,
    get_character_translation,
    search_character,
    update_character,
)
from src.tools.hello import hello_tool


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


@patch("src.models.character_collection.settings")
def test_create_character(mock_settings):
    """Test creating a character."""
    mock_settings.return_value = Settings(
        languages=["en", "ru", "fr"], translate_from="jp", translate_to="en"
    )
    input_data = {
        "name": "Frodo Baggins",
        "short_names": ["Frodo"],
        "gender": "male",
        "characteristics": [{"sentence": "Brave and loyal.", "confidence": 1}],
    }
    result = create_character(json.dumps(input_data))
    assert "created successfully" in result


@patch("src.models.character_collection.settings")
def test_search_character(mock_settings):
    """Test searching for a character."""
    mock_settings.return_value = Settings(
        languages=["en", "ru", "fr"], translate_from="jp", translate_to="en"
    )
    result = search_character("Frodo")
    assert "Frodo Baggins" in result


@patch("src.models.character_collection.settings")
def test_update_character(mock_settings):
    """Test updating a character."""
    mock_settings.return_value = Settings(
        languages=["en", "ru", "fr"], translate_from="jp", translate_to="en"
    )
    input_data = {"name": "Frodo", "updates": {"gender": "male"}}
    result = update_character(json.dumps(input_data))
    assert "updated successfully" in result


@patch("src.models.character_collection.settings")
def test_get_character_translation(mock_settings):
    """Test getting character translation."""
    mock_settings.return_value = Settings(
        languages=["en", "ru", "fr"], translate_from="jp", translate_to="en"
    )
    input_data = {"name": "Frodo", "language": "es"}
    result = get_character_translation(json.dumps(input_data))
    # Since no translations added, should return original
    assert "Frodo Baggins" in result
