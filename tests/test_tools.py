import json
from unittest.mock import MagicMock, patch

from helpers.settings import Settings
from tools.character import (
    add_character_short_name,
    character_tools,
    create_character,
    get_all_characters,
    get_character_translation,
    search_character,
    set_character_gender,
)
from tools.hello import hello_tool


def test_hello_tool():
    """Test that the hello tool returns 'World'."""
    assert hello_tool.func is not None
    result = hello_tool.func("")
    assert result == "World"


def test_character_tools():
    """Test that character tools are defined."""
    assert len(character_tools) == 6
    names = [tool.name for tool in character_tools]
    assert "SearchCharacter" in names
    assert "CreateCharacter" in names
    assert "AddCharacterShortName" in names
    assert "SetCharacterGender" in names
    assert "GetCharacterTranslation" in names
    assert "GetAllCharacters" in names


@patch("models.character.settings")
@patch("models.character_collection.settings")
def test_create_character(
    mock_collection_settings: MagicMock, mock_character_settings: MagicMock
) -> None:
    """Test creating a character."""
    settings_obj = Settings(
        languages=["en", "ru", "fr"], translate_from="jp", translate_to="en"
    )
    mock_collection_settings.return_value = settings_obj
    mock_character_settings.return_value = settings_obj
    result = create_character("Frodo Baggins", "male")
    assert "created successfully" in result


@patch("tools.character.settings")
@patch("models.character.settings")
@patch("models.character_collection.settings")
def test_search_character(
    mock_tools_settings: MagicMock,
    mock_character_settings: MagicMock,
    mock_collection_settings: MagicMock,
) -> None:
    """Test searching for a character."""
    settings_obj = Settings(
        languages=["en", "ru", "fr"], translate_from="jp", translate_to="en"
    )
    mock_collection_settings.return_value = settings_obj
    mock_character_settings.return_value = settings_obj
    mock_tools_settings.return_value = settings_obj
    # Create character first
    create_character("Frodo Baggins", "male")
    add_character_short_name("Frodo Baggins", "Frodo")
    result = search_character("Frodo")
    assert "Frodo Baggins" in result


@patch("models.character.settings")
@patch("models.character_collection.settings")
def test_add_character_short_name(
    mock_collection_settings: MagicMock, mock_character_settings: MagicMock
) -> None:
    """Test adding a short name to a character."""
    settings_obj = Settings(
        languages=["en", "ru", "fr"], translate_from="jp", translate_to="en"
    )
    mock_collection_settings.return_value = settings_obj
    mock_character_settings.return_value = settings_obj
    # Create character first
    create_character("Frodo Baggins", "male")
    result = add_character_short_name("Frodo Baggins", "Frodo")
    assert "Short name 'Frodo' added" in result


@patch("models.character.settings")
@patch("models.character_collection.settings")
def test_set_character_gender(
    mock_collection_settings: MagicMock, mock_character_settings: MagicMock
) -> None:
    """Test setting character gender."""
    settings_obj = Settings(
        languages=["en", "ru", "fr"], translate_from="jp", translate_to="en"
    )
    mock_collection_settings.return_value = settings_obj
    mock_character_settings.return_value = settings_obj
    # Create character first
    create_character("Frodo Baggins", "male")
    result = set_character_gender("Frodo Baggins", "female")
    assert "Gender of character 'Frodo Baggins' set to 'female'" in result


@patch("tools.character.settings")
@patch("models.character.settings")
@patch("models.character_collection.settings")
def test_get_character_translation(
    mock_tools_settings: MagicMock,
    mock_character_settings: MagicMock,
    mock_collection_settings: MagicMock,
) -> None:
    """Test getting character translation."""
    settings_obj = Settings(
        languages=["en", "ru", "fr"], translate_from="jp", translate_to="en"
    )
    mock_collection_settings.return_value = settings_obj
    mock_character_settings.return_value = settings_obj
    mock_tools_settings.return_value = settings_obj
    # Create character first
    create_character("Frodo Baggins", "male")
    trans_data = {"name": "Frodo Baggins", "language": "es"}
    result = get_character_translation(json.dumps(trans_data))
    # Since no translations added, should return original
    assert "Frodo Baggins" in result


@patch("tools.character.settings")
@patch("models.character.settings")
@patch("models.character_collection.settings")
def test_get_all_characters(
    mock_tools_settings: MagicMock,
    mock_character_settings: MagicMock,
    mock_collection_settings: MagicMock,
) -> None:
    """Test getting all characters."""
    settings_obj = Settings(
        languages=["en", "ru", "fr"], translate_from="jp", translate_to="en"
    )
    mock_collection_settings.return_value = settings_obj
    mock_character_settings.return_value = settings_obj
    mock_tools_settings.return_value = settings_obj
    # Create characters first
    create_character("Frodo Baggins", "male")
    create_character("Gandalf", "male")
    result = get_all_characters()
    assert "<characters>" in result
    assert "<character>" in result
    assert "Frodo Baggins" in result
    assert "Gandalf" in result
    # Should not contain characteristics
    assert "<characteristics>" not in result
