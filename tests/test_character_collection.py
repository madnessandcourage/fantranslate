import os
import tempfile

from src.models.character import Character
from src.models.character_collection import CharacterCollection


def test_character_collection_initialization():
    collection = CharacterCollection()
    assert collection.characters == []


def test_add_character():
    collection = CharacterCollection()
    char = Character("Alice")
    collection.add_character(char)
    assert len(collection.characters) == 1
    assert collection.characters[0] == char


def test_search_character():
    collection = CharacterCollection()
    char = Character("Alice", short_names=["Al"])
    collection.add_character(char)

    found = collection.search("Alice")
    assert found == char

    found_short = collection.search("Al")
    assert found_short == char

    not_found = collection.search("Bob")
    assert not_found is None


def test_remove_character():
    collection = CharacterCollection()
    char = Character("Alice")
    collection.add_character(char)
    assert len(collection.characters) == 1

    collection.remove_character("Alice")
    assert len(collection.characters) == 0


def test_to_dict_from_dict():
    collection = CharacterCollection()
    char = Character("Alice", short_names=["Al"], gender="female")
    collection.add_character(char)

    data = collection.to_dict()
    assert len(data) == 1

    new_collection = CharacterCollection.from_dict(data)
    assert len(new_collection.characters) == 1
    assert new_collection.characters[0].name.original_text == "Alice"


def test_save_and_load_from_file():
    collection = CharacterCollection()
    char = Character("Alice", short_names=["Al"], gender="female")
    collection.add_character(char)

    with tempfile.NamedTemporaryFile(mode="w", suffix=".yml", delete=False) as f:
        temp_file = f.name

    try:
        # Save to file
        collection.save(temp_file)

        # Load from file
        loaded_collection = CharacterCollection.from_file(temp_file)

        assert len(loaded_collection.characters) == 1
        assert loaded_collection.characters[0].name.original_text == "Alice"
        assert loaded_collection.characters[0].short_names[0].original_text == "Al"
        assert loaded_collection.characters[0].gender is not None
        assert loaded_collection.characters[0].gender.original_text == "female"

    finally:
        os.unlink(temp_file)


def test_from_file_classmethod():
    collection = CharacterCollection()
    char = Character("Bob", gender="male")
    collection.add_character(char)

    with tempfile.NamedTemporaryFile(mode="w", suffix=".yml", delete=False) as f:
        temp_file = f.name

    try:
        collection.save(temp_file)
        loaded_collection = CharacterCollection.from_file(temp_file)

        assert len(loaded_collection.characters) == 1
        assert loaded_collection.characters[0].name.original_text == "Bob"

    finally:
        os.unlink(temp_file)
