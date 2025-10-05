import os
from pathlib import Path

import pytest
import yaml

from src.helpers.settings import settings


@pytest.fixture(autouse=True)
def clear_settings_cache():
    # Reset the cached settings before each test
    import src.helpers.settings
    src.helpers.settings.__settings = None
    yield


def test_settings_success(tmp_path: Path):
    os.chdir(str(tmp_path))
    project_yml = {
        "languages": ["en", "ru", "fr"],
        "translate_from": "jp",
        "translate_to": "en",
    }
    with open("project.yml", "w") as f:
        yaml.dump(project_yml, f)

    result = settings()
    assert result.languages == ["en", "ru", "fr"]
    assert result.translate_from == "jp"
    assert result.translate_to == "en"


def test_settings_file_not_found(tmp_path: Path):
    os.chdir(str(tmp_path))
    with pytest.raises(FileNotFoundError, match="project.yml not found"):
        settings()


def test_settings_missing_languages(tmp_path: Path):
    os.chdir(str(tmp_path))
    project_yml = {"translate_from": "jp", "translate_to": "en"}
    with open("project.yml", "w") as f:
        yaml.dump(project_yml, f)

    with pytest.raises(ValueError, match="must contain 'languages'"):
        settings()


def test_settings_missing_translate_from(tmp_path: Path):
    os.chdir(str(tmp_path))
    project_yml = {"languages": ["en", "ru"], "translate_to": "en"}
    with open("project.yml", "w") as f:
        yaml.dump(project_yml, f)

    with pytest.raises(
        ValueError,
        match="must contain 'languages', 'translate_from', and 'translate_to'",
    ):
        settings()


def test_settings_missing_translate_to(tmp_path: Path):
    os.chdir(str(tmp_path))
    project_yml = {"languages": ["en", "ru"], "translate_from": "jp"}
    with open("project.yml", "w") as f:
        yaml.dump(project_yml, f)

    with pytest.raises(
        ValueError,
        match="must contain 'languages', 'translate_from', and 'translate_to'",
    ):
        settings()


def test_settings_invalid_languages_type(tmp_path: Path):
    os.chdir(str(tmp_path))
    project_yml = {"languages": "en ru", "translate_from": "jp", "translate_to": "en"}
    with open("project.yml", "w") as f:
        yaml.dump(project_yml, f)

    with pytest.raises(ValueError, match="'languages' must be a list of strings"):
        settings()


def test_settings_languages_not_strings(tmp_path: Path):
    os.chdir(str(tmp_path))
    project_yml = {
        "languages": ["en", 123],
        "translate_from": "jp",
        "translate_to": "en",
    }
    with open("project.yml", "w") as f:
        yaml.dump(project_yml, f)

    with pytest.raises(ValueError, match="'languages' must be a list of strings"):
        settings()


def test_settings_translate_from_not_string(tmp_path: Path):
    os.chdir(str(tmp_path))
    project_yml = {
        "languages": ["en", "ru"],
        "translate_from": 123,
        "translate_to": "en",
    }
    with open("project.yml", "w") as f:
        yaml.dump(project_yml, f)

    with pytest.raises(ValueError, match="'translate_from' must be a string"):
        settings()


def test_settings_translate_to_not_string(tmp_path: Path):
    os.chdir(str(tmp_path))
    project_yml = {
        "languages": ["en", "ru"],
        "translate_from": "jp",
        "translate_to": 123,
    }
    with open("project.yml", "w") as f:
        yaml.dump(project_yml, f)

    with pytest.raises(ValueError, match="'translate_to' must be a string"):
        settings()


def test_settings_translate_from_in_languages(tmp_path: Path):
    os.chdir(str(tmp_path))
    project_yml = {
        "languages": ["en", "ru", "jp"],
        "translate_from": "jp",
        "translate_to": "en",
    }
    with open("project.yml", "w") as f:
        yaml.dump(project_yml, f)

    with pytest.raises(ValueError, match="'translate_from' must not be in 'languages'"):
        settings()


def test_settings_translate_to_not_in_languages(tmp_path: Path):
    os.chdir(str(tmp_path))
    project_yml = {
        "languages": ["en", "ru"],
        "translate_from": "jp",
        "translate_to": "fr",
    }
    with open("project.yml", "w") as f:
        yaml.dump(project_yml, f)

    with pytest.raises(ValueError, match="'translate_to' must be in 'languages'"):
        settings()
