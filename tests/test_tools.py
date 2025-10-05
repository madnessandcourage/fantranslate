import json
from unittest.mock import MagicMock, patch

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


@patch("src.models.character.settings")
@patch("src.models.character_collection.settings")
def test_create_character(
    mock_collection_settings: MagicMock, mock_character_settings: MagicMock
) -> None:
    """Test creating a character."""
    settings_obj = Settings(
        languages=["en", "ru", "fr"], translate_from="jp", translate_to="en"
    )
    mock_collection_settings.return_value = settings_obj
    mock_character_settings.return_value = settings_obj
    input_data = {
        "name": "Frodo Baggins",
        "short_names": ["Frodo"],
        "gender": "male",
        "characteristics": [{"sentence": "Brave and loyal.", "confidence": 1}],
    }
    result = create_character(json.dumps(input_data))
    assert "created successfully" in result


@patch("src.models.character.settings")
@patch("src.models.character_collection.settings")
def test_search_character(
    mock_collection_settings: MagicMock, mock_character_settings: MagicMock
) -> None:
    """Test searching for a character."""
    settings_obj = Settings(
        languages=["en", "ru", "fr"], translate_from="jp", translate_to="en"
    )
    mock_collection_settings.return_value = settings_obj
    mock_character_settings.return_value = settings_obj
    # Create character first
    input_data = {
        "name": "Frodo Baggins",
        "short_names": ["Frodo"],
        "gender": "male",
        "characteristics": [],
    }
    create_character(json.dumps(input_data))
    result = search_character("Frodo")
    assert "Frodo Baggins" in result


@patch("src.models.character.settings")
@patch("src.models.character_collection.settings")
def test_update_character(
    mock_collection_settings: MagicMock, mock_character_settings: MagicMock
) -> None:
    """Test updating a character."""
    settings_obj = Settings(
        languages=["en", "ru", "fr"], translate_from="jp", translate_to="en"
    )
    mock_collection_settings.return_value = settings_obj
    mock_character_settings.return_value = settings_obj
    # Create character first
    input_data = {
        "name": "Frodo Baggins",
        "short_names": ["Frodo"],
        "gender": "male",
        "characteristics": [],
    }
    create_character(json.dumps(input_data))
    update_data = {"name": "Frodo", "updates": {"gender": "male"}}
    result = update_character(json.dumps(update_data))
    assert "updated successfully" in result


@patch("src.models.character.settings")
@patch("src.models.character_collection.settings")
def test_get_character_translation(
    mock_collection_settings: MagicMock, mock_character_settings: MagicMock
) -> None:
    """Test getting character translation."""
    settings_obj = Settings(
        languages=["en", "ru", "fr"], translate_from="jp", translate_to="en"
    )
    mock_collection_settings.return_value = settings_obj
    mock_character_settings.return_value = settings_obj
    # Create character first
    input_data = {
        "name": "Frodo Baggins",
        "short_names": ["Frodo"],
        "gender": "male",
        "characteristics": [],
    }
    create_character(json.dumps(input_data))
    trans_data = {"name": "Frodo", "language": "es"}
    result = get_character_translation(json.dumps(trans_data))
    # Since no translations added, should return original
    assert "Frodo Baggins" in result
