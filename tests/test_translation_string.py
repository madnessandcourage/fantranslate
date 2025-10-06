import pytest

from models.translation_string import TranslationString


def test_initialization():
    s = TranslationString(
        "Cat", original_language="en", available_languages=["ru", "ua"]
    )
    assert s.original_text == "Cat"
    assert s.original_language == "en"
    assert s.available_languages == ["ru", "ua"]
    assert s.translations == {}


def test_get_original_language():
    s = TranslationString(
        "Cat", original_language="en", available_languages=["ru", "ua"]
    )
    assert s.en == "Cat"


def test_equality_with_original():
    s = TranslationString(
        "Cat", original_language="en", available_languages=["ru", "ua"]
    )
    assert s == "Cat"
    assert "Cat" == s


def test_print():
    s = TranslationString(
        "Cat", original_language="en", available_languages=["ru", "ua"]
    )
    assert str(s) == "Cat"


def test_set_translation():
    s = TranslationString(
        "Cat", original_language="en", available_languages=["ru", "ua"]
    )
    s.ru = "Кот"
    assert s.ru == "Кот"


def test_equality_with_translation():
    s = TranslationString(
        "Cat", original_language="en", available_languages=["ru", "ua"]
    )
    s.ru = "Кот"
    assert s == "Кот"
    assert s == "Cat"  # Still true


def test_unset_translation_returns_none():
    s = TranslationString(
        "Cat", original_language="en", available_languages=["ru", "ua"]
    )
    assert s.ua is None


def test_invalid_language_assignment():
    s = TranslationString(
        "Cat", original_language="en", available_languages=["ru", "ua"]
    )
    with pytest.raises(AttributeError):
        s.ge = "Kitten"


def test_serialization():
    s = TranslationString(
        "Cat", original_language="en", available_languages=["ru", "ua"]
    )
    s.ru = "Кот"
    data = s.to_dict()
    expected = {
        "original_text": "Cat",
        "original_language": "en",
        "available_languages": ["ru", "ua"],
        "translations": {"ru": "Кот"},
    }
    assert data == expected


def test_deserialization():
    data = {
        "original_text": "Cat",
        "original_language": "en",
        "available_languages": ["ru", "ua"],
        "translations": {"ru": "Кот"},
    }
    s = TranslationString.from_dict(data)
    assert s.original_text == "Cat"
    assert s.en == "Cat"
    assert s.ru == "Кот"
    assert s.ua is None


def test_json_serialization():
    s = TranslationString(
        "Cat", original_language="en", available_languages=["ru", "ua"]
    )
    s.ru = "Кот"
    json_str = s.to_json()
    s2 = TranslationString.from_json(json_str)
    assert s2 == s
    assert s2.en == "Cat"
    assert s2.ru == "Кот"


def test_equality_false():
    s = TranslationString(
        "Cat", original_language="en", available_languages=["ru", "ua"]
    )
    assert (s == "Dog") is False
    assert (s == 123) is False
