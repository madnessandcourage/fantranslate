from io import StringIO
from unittest.mock import MagicMock, patch

import pytest

from commands.character import (
    handle_edit,
    handle_info,
    handle_list,
    handle_remove,
    handle_search,
    setup_character_parser,
)
from main import main


class TestCharacterCLI:
    """Test character CLI commands."""

    @patch("commands.character.load_character_collection")
    def test_list_empty_collection(self, mock_load):  # type: ignore
        """Test character list with empty collection."""
        mock_collection = MagicMock()
        mock_collection.get_all_characters.return_value = []
        mock_load.return_value = mock_collection

        # Capture stdout
        with patch("sys.stdout", new_callable=StringIO) as mock_stdout:
            handle_list(MagicMock())

        output = mock_stdout.getvalue()
        assert "No characters found." in output

    @patch("commands.character.load_character_collection")
    def test_list_with_characters(self, mock_load):  # type: ignore
        """Test character list with characters."""
        mock_collection = MagicMock()
        # Create mock characters with proper attributes
        mock_char1 = MagicMock()
        mock_char1.name = "Alice"
        mock_char1.short_names = ["Al"]
        mock_char1.gender = "female"
        mock_char1.characteristics = []

        mock_char2 = MagicMock()
        mock_char2.name = "Bob"
        mock_char2.short_names = []
        mock_char2.gender = None
        mock_char2.characteristics = [MagicMock()]

        mock_characters = [mock_char1, mock_char2]

        mock_collection.get_all_characters.return_value = mock_characters
        mock_load.return_value = mock_collection

        with patch("sys.stdout", new_callable=StringIO) as mock_stdout:
            handle_list(MagicMock())

        output = mock_stdout.getvalue()
        assert "Name" in output
        assert "Short Names" in output
        assert "Gender" in output
        assert "Alice" in output
        assert "Bob" in output

    @patch("commands.character.load_character_collection")
    @patch("commands.character.settings")
    def test_info_character_found(self, mock_settings, mock_load):  # type: ignore
        """Test character info when character is found."""
        mock_s = MagicMock()
        mock_s.translate_from = "en"
        mock_s.languages = ["ru"]
        mock_settings.return_value = mock_s

        mock_collection = MagicMock()
        mock_character = MagicMock()
        mock_translated = MagicMock()
        mock_translated.name = "Alice"
        mock_translated.short_names = ["Al"]
        mock_translated.gender = "female"
        mock_translated.characteristics = [
            {"sentence": "Alice is kind", "confidence": 1}
        ]
        mock_character.get_translated.return_value = mock_translated
        mock_collection.search.return_value = mock_character
        mock_load.return_value = mock_collection

        args = MagicMock()
        args.search_query = "Alice"

        with patch("sys.stdout", new_callable=StringIO) as mock_stdout:
            handle_info(args)

        output = mock_stdout.getvalue()
        assert "Name: Alice" in output
        assert "Short Names: Al" in output
        assert "Gender: female" in output
        assert "Alice is kind" in output

    @patch("commands.character.load_character_collection")
    def test_info_character_not_found(self, mock_load):  # type: ignore
        """Test character info when character is not found."""
        mock_collection = MagicMock()
        mock_collection.search.return_value = None
        mock_load.return_value = mock_collection

        args = MagicMock()
        args.search_query = "NonExistent"

        with patch("sys.stdout", new_callable=StringIO) as mock_stdout:
            handle_info(args)

        output = mock_stdout.getvalue()
        assert "Character 'NonExistent' not found." in output

    @patch("commands.character.load_character_collection")
    def test_search_character_found(self, mock_load):  # type: ignore
        """Test character search when character is found."""
        mock_collection = MagicMock()
        mock_character = MagicMock()
        mock_translated = MagicMock()
        mock_translated.name = "Alice"
        mock_translated.short_names = ["Al"]
        mock_translated.gender = "female"
        mock_character.get_translated.return_value = mock_translated
        mock_collection.search.return_value = mock_character
        mock_load.return_value = mock_collection

        args = MagicMock()
        args.search_query = "Alice"

        with patch("sys.stdout", new_callable=StringIO) as mock_stdout:
            handle_search(args)

        output = mock_stdout.getvalue()
        assert "Found: Alice" in output

    @patch("commands.character.load_character_collection")
    def test_search_character_not_found(self, mock_load):
        """Test character search when character is not found."""
        mock_collection = MagicMock()
        mock_collection.search.return_value = None
        mock_load.return_value = mock_collection

        args = MagicMock()
        args.search_query = "NonExistent"

        with patch("sys.stdout", new_callable=StringIO) as mock_stdout:
            handle_search(args)

        output = mock_stdout.getvalue()
        assert "Character 'NonExistent' not found." in output

    @patch("commands.character.load_character_collection")
    @patch("commands.character.save_character_collection")
    def test_edit_character_not_found(self, mock_save, mock_load):
        """Test character edit when character is not found."""
        mock_collection = MagicMock()
        mock_collection.search.return_value = None
        mock_load.return_value = mock_collection

        args = MagicMock()
        args.search_query = "NonExistent"
        args.add_short_name = None
        args.remove_short_name = None
        args.gender = None
        args.change_name = None
        args.add_characteristic = None
        args.remove_characteristic = None

        with patch("sys.stdout", new_callable=StringIO) as mock_stdout:
            handle_edit(args)

        output = mock_stdout.getvalue()
        assert "Character 'NonExistent' not found." in output
        mock_save.assert_not_called()

    @patch("commands.character.load_character_collection")
    @patch("commands.character.save_character_collection")
    def test_edit_add_short_name(self, mock_save, mock_load):
        """Test character edit adding short name."""
        mock_collection = MagicMock()
        mock_character = MagicMock()
        mock_character.add_short_name = MagicMock()
        mock_character.update = MagicMock()
        mock_character.add_characteristic = MagicMock()
        mock_character.remove_characteristic = MagicMock()
        mock_collection.search.return_value = mock_character
        mock_collection.rebuild_index = MagicMock()
        mock_load.return_value = mock_collection

        args = MagicMock()
        args.search_query = "Alice"
        args.add_short_name = ["Al"]
        args.remove_short_name = None
        args.gender = None
        args.change_name = None
        args.add_characteristic = None
        args.remove_characteristic = None

        with patch("sys.stdout", new_callable=StringIO) as mock_stdout:
            handle_edit(args)

        output = mock_stdout.getvalue()
        assert "Added short name: Al" in output
        assert "Character updated successfully." in output
        mock_character.add_short_name.assert_called_with("Al")
        mock_collection.rebuild_index.assert_called_once()
        mock_save.assert_called_once_with(mock_collection)

    @patch("commands.character.load_character_collection")
    @patch("commands.character.save_character_collection")
    @patch("builtins.input")
    def test_remove_character_confirmed(self, mock_input, mock_save, mock_load):
        """Test character remove with user confirmation."""
        mock_collection = MagicMock()
        mock_character = MagicMock()
        mock_character.name.original_text = "Alice"
        mock_translated = MagicMock()
        mock_translated.name = "Alice"
        mock_translated.short_names = ["Al"]
        mock_character.get_translated.return_value = mock_translated
        mock_collection.search.return_value = mock_character
        mock_collection.remove_character = MagicMock()
        mock_load.return_value = mock_collection

        mock_input.return_value = "y"

        args = MagicMock()
        args.search_query = "Alice"

        with patch("sys.stdout", new_callable=StringIO) as mock_stdout:
            handle_remove(args)

        output = mock_stdout.getvalue()
        assert "Remove character: Alice" in output
        assert "Character removed successfully." in output
        mock_collection.remove_character.assert_called_once()
        mock_save.assert_called_once_with(mock_collection)

    @patch("commands.character.load_character_collection")
    @patch("builtins.input")
    def test_remove_character_cancelled(self, mock_input, mock_load):
        """Test character remove when user cancels."""
        mock_collection = MagicMock()
        mock_character = MagicMock()
        mock_translated = MagicMock()
        mock_translated.name = "Alice"
        mock_translated.short_names = ["Al"]
        mock_character.get_translated.return_value = mock_translated
        mock_collection.search.return_value = mock_character
        mock_load.return_value = mock_collection

        mock_input.return_value = "n"

        args = MagicMock()
        args.search_query = "Alice"

        with patch("sys.stdout", new_callable=StringIO) as mock_stdout:
            handle_remove(args)

        output = mock_stdout.getvalue()
        assert "Remove character: Alice" in output
        assert "Removal cancelled." in output

    @patch("sys.argv", ["fantranslate", "character", "list"])
    @patch("commands.character.handle_list")
    def test_main_character_list_command(self, mock_handle_list):
        """Test that main() calls character list handler."""
        main()
        mock_handle_list.assert_called_once()

    @patch("sys.argv", ["fantranslate", "character", "invalid"])
    @patch("sys.stderr", new_callable=StringIO)
    def test_main_character_invalid_command(self, mock_stderr):
        """Test main() with invalid character command."""
        with pytest.raises(SystemExit):
            main()

        # Should print argparse error message to stderr
        error_output = mock_stderr.getvalue()
        assert "invalid choice" in error_output

    def test_setup_character_parser(self):
        """Test that character parser is set up correctly."""
        import argparse

        parser = argparse.ArgumentParser()
        subparsers = parser.add_subparsers(dest="command")
        setup_character_parser(subparsers)

        # Parse character list command
        args = parser.parse_args(["character", "list"])
        assert args.command == "character"
        assert args.character_command == "list"

        # Parse character info command
        args = parser.parse_args(["character", "info", "Alice"])
        assert args.command == "character"
        assert args.character_command == "info"
        assert args.search_query == "Alice"

        # Parse character edit command
        args = parser.parse_args(["character", "edit", "Alice", "--gender", "female"])
        assert args.command == "character"
        assert args.character_command == "edit"
        assert args.search_query == "Alice"
        assert args.gender == "female"
