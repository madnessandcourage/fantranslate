import json
from typing import List

from ai import agent, ai, yesno
from helpers.context import Context
from models.character_collection import CharacterCollection
from tools.character import character_tools
from tracing import log_enter, log_error, log_exit, log_info


def detection_judge(
    chapter_text: str, existing_characters: CharacterCollection
) -> List[str]:
    """Detect missing characters in a chapter using AI.

    Args:
        chapter_text: The full text of the book chapter
        existing_characters: The current character collection

    Returns:
        List of character names that are missing from the collection
    """
    log_enter("detection_judge")

    # Get all existing character names and short names
    existing_names = set()
    for char in existing_characters.characters:
        existing_names.add(char.name.original_text)
        for short_name in char.short_names:
            existing_names.add(short_name.original_text)

    # Build the prompt using Context
    existing_names_list = sorted(list(existing_names))
    context = (
        Context()
        .add(
            "Existing Characters",
            "The following character names and short names are already in the collection:\n"
            + "\n".join(f"- {name}" for name in existing_names_list),
        )
        .add("Chapter Text", chapter_text)
        .add(
            "Task",
            "Extract a list of character names that appear in the chapter but are NOT in the existing character collection. Only include names that clearly refer to characters (people, not places, objects, etc.).",
        )
        .add(
            "Output Format",
            'Return a JSON array of strings, where each string is a character name found in the chapter that is missing from the collection.\n\nExample: ["John Smith", "Mary Johnson", "Dr. Roberts"]',
        )
        .add(
            "Guidelines",
            "- Only include proper names that refer to people/characters\n"
            + "- Include both full names and nicknames if they appear\n"
            + "- Do not include place names, object names, or abstract concepts\n"
            + "- If a character is already in the collection (by any of their names or short names), do not include them\n"
            + "- Be thorough but avoid false positives",
        )
    )

    system_prompt = context.build()
    user_prompt = (
        f"Chapter text:\n{chapter_text}\n\nExisting characters: {existing_names_list}"
    )

    # Call AI
    response = ai(system_prompt, user_prompt)

    if response is None:
        log_info("AI returned None, returning empty list")
        log_exit("detection_judge")
        return []

    try:
        # Parse JSON response
        missing_characters = json.loads(response.strip())
        if not isinstance(missing_characters, list):
            log_info(f"AI response is not a list: {response}")
            log_exit("detection_judge")
            return []

        # Filter to ensure they are strings
        missing_characters = [
            str(name)
            for name in missing_characters
            if isinstance(name, (str, int, float))
        ]

        log_info(
            f"Detected {len(missing_characters)} missing characters: {missing_characters}"
        )
        log_exit("detection_judge")
        return missing_characters

    except json.JSONDecodeError as e:
        log_info(f"Failed to parse AI response as JSON: {response}, error: {e}")
        log_exit("detection_judge")
        return []


def extraction_agent(missing_characters: List[str], chapter_text: str) -> str:
    """Extract missing characters from a chapter using AI agent with character tools.

    Args:
        missing_characters: List of character names to extract
        chapter_text: The full text of the book chapter

    Returns:
        The agent's response/output
    """
    log_enter("extraction_agent")

    # Build the prompt using Context
    context = (
        Context()
        .add(
            "Missing Characters",
            "The following characters need to be extracted from the chapter:\n"
            + "\n".join(f"- {name}" for name in missing_characters),
        )
        .add("Chapter Text", chapter_text)
        .add(
            "Task",
            "For each missing character, use the available character tools to:\n"
            + "1. Create the character in the collection\n"
            + "2. Add any short names or nicknames you find\n"
            + "3. Set the character's gender if mentioned\n"
            + "4. Extract and add characteristics (descriptions, traits, relationships) from the text",
        )
        .add(
            "Available Tools",
            "- CreateCharacter: Create a new character\n"
            + "- AddCharacterShortName: Add short names to existing characters\n"
            + "- SetCharacterGender: Set gender information\n"
            + "- SearchCharacter: Check if a character exists\n"
            + "- GetAllCharacters: View current collection",
        )
        .add(
            "Guidelines",
            "- Be thorough in extracting character information\n"
            + "- Only create characters that are explicitly listed as missing\n"
            + "- Use the chapter text as the source of truth for all character information\n"
            + "- Add multiple characteristics if available (appearance, personality, relationships, etc.)\n"
            + "- If gender is not mentioned, leave it as default\n"
            + "- Focus on factual information from the text, not inferences",
        )
    )

    system_prompt = context.build()
    user_query = f"Extract the following characters from this chapter: {missing_characters}\n\nChapter text:\n{chapter_text}"

    # Call agent with character tools
    response, _ = agent(system_prompt, user_query, character_tools)

    log_info(f"Extraction agent completed: {response[:100]}...")
    log_exit("extraction_agent")
    return response


def completeness_judge(
    missing_characters: List[str], new_characters: List[str]
) -> bool:
    """Judge if all missing characters have been successfully extracted.

    Args:
        missing_characters: Original list of missing character names
        new_characters: List of characters that were added during extraction

    Returns:
        True if all missing characters were extracted, False otherwise
    """
    log_enter("completeness_judge")

    user_prompt = (
        f"Missing characters that should have been extracted: {missing_characters}\n"
        f"New characters that were added to the collection: {new_characters}\n\n"
        f"Have all the missing characters been successfully added to the collection?"
    )

    is_complete, reason = yesno(user_prompt)

    if is_complete:
        log_info("Completeness check passed: all missing characters extracted")
    else:
        log_info(f"Completeness check failed: {reason}")

    log_exit("completeness_judge")
    return is_complete


def extract_characters_from_chapter(chapter_path: str) -> bool:
    """Main function to extract characters from a chapter.

    Args:
        chapter_path: Path to the chapter text file

    Returns:
        True if extraction was successful and complete, False otherwise
    """
    log_enter("extract_characters_from_chapter")

    try:
        # Load chapter text
        with open(chapter_path, "r", encoding="utf-8") as f:
            chapter_text = f.read()

        # Load existing character collection
        import os

        from helpers.settings import DEFAULT_CHARACTERS_STORAGE

        if os.path.exists(DEFAULT_CHARACTERS_STORAGE):
            existing_characters = CharacterCollection.from_file(
                DEFAULT_CHARACTERS_STORAGE
            )
        else:
            existing_characters = CharacterCollection()

        log_info(f"Loaded {len(existing_characters.characters)} existing characters")

        # Step 1: Detection judge - find missing characters
        missing_characters = detection_judge(chapter_text, existing_characters)
        log_info(
            f"Found {len(missing_characters)} missing characters: {missing_characters}"
        )

        if not missing_characters:
            log_info("No missing characters found, extraction complete")
            log_exit("extract_characters_from_chapter")
            return True

        # Step 2: Extraction agent - extract missing characters
        extraction_agent(missing_characters, chapter_text)
        log_info("Character extraction completed")

        # Reload collection to get updated characters
        updated_characters = CharacterCollection.from_file(DEFAULT_CHARACTERS_STORAGE)
        new_characters = []
        for char in updated_characters.characters:
            if char.name.original_text not in [
                c.name.original_text for c in existing_characters.characters
            ]:
                new_characters.append(char.name.original_text)

        log_info(f"Added {len(new_characters)} new characters: {new_characters}")

        # Step 3: Completeness judge - verify all were extracted
        is_complete = completeness_judge(missing_characters, new_characters)

        if is_complete:
            log_info("Character extraction completed successfully")
        else:
            log_info("Character extraction incomplete")

        log_exit("extract_characters_from_chapter")
        return is_complete

    except Exception as e:
        log_error(f"Error during character extraction: {e}")
        log_exit("extract_characters_from_chapter")
        return False
