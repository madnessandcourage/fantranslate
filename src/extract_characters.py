import json
from typing import List, Tuple

from ai import agent, ai, yesno
from helpers.context import Context
from models.character_collection import CharacterCollection
from tools.character import (
    add_short_name_tool,
    character_collection,
    create_character_tool,
    get_all_characters_tool,
    search_character_tool,
    set_gender_tool,
)
from tracing import log_enter, log_error, log_exit, log_info

# Tools needed for character extraction
extraction_tools = [
    search_character_tool,
    create_character_tool,
    add_short_name_tool,
    set_gender_tool,
    get_all_characters_tool,
]


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

    # Build existing characters display with grouped names
    existing_chars_display = []
    for char in existing_characters.characters:
        full_name = char.name.original_text
        short_names = [sn.original_text for sn in char.short_names]
        if short_names:
            display = f"- {full_name} (a.k.a {', '.join(short_names)})"
        else:
            display = f"- {full_name}"
        existing_chars_display.append(display)

    # Build the prompt using Context
    context = (
        Context()
        .add(
            "Existing Characters",
            "The following characters are already in the collection:\n"
            + "\n".join(existing_chars_display),
        )
        .add("Chapter Text", chapter_text)
        .pipe("detection_judge")
    )

    system_prompt = context.build()
    user_prompt = f"Chapter text:\n{chapter_text}"

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


def extraction_agent(
    missing_characters: List[str], chapter_text: str
) -> Tuple[str, List[str]]:
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
        .pipe("extraction_agent")
    )

    system_prompt = context.build()
    user_query = f"Extract the following characters from this chapter: {missing_characters}\n\nChapter text:\n{chapter_text}"

    # Call agent with extraction tools
    response, _ = agent(system_prompt, user_query, extraction_tools)

    # Get all characters after extraction
    all_characters = [
        char.name.original_text for char in character_collection.characters
    ]

    log_info(f"Extraction agent completed: {response[:100]}...")
    log_info(f"Total characters in collection: {len(all_characters)}")
    log_exit("extraction_agent")
    return response, all_characters


def completeness_judge(
    missing_characters: List[str], all_characters: List[str]
) -> bool:
    """Judge if all missing characters have been successfully extracted.

    Args:
        missing_characters: Original list of missing character names
        all_characters: Full list of character names in the collection after extraction

    Returns:
        True if all missing characters were extracted, False otherwise
    """
    log_enter("completeness_judge")

    # Build the prompt using Context
    context = (
        Context()
        .add(
            "Missing Characters",
            f"Characters that should have been extracted: {missing_characters}",
        )
        .add(
            "All Characters",
            f"Characters currently in the collection: {all_characters}",
        )
        .pipe("completeness_judge")
    )

    system_prompt = context.build()
    user_prompt = (
        f"Have all the missing characters been successfully added to the collection?"
    )

    is_complete, reason = yesno(
        user_prompt, system_prompt=system_prompt, skip_examples=True
    )

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

        # Use the singleton character collection
        log_info(f"Loaded {len(character_collection.characters)} existing characters")

        # Step 1: Detection judge - find missing characters
        missing_characters = detection_judge(chapter_text, character_collection)
        log_info(
            f"Found {len(missing_characters)} missing characters: {missing_characters}"
        )

        if not missing_characters:
            log_info("No missing characters found, extraction complete")
            log_exit("extract_characters_from_chapter")
            return True

        # Step 2-3: Extraction with retry loop (up to 3 attempts)
        max_attempts = 3
        is_complete = False
        for attempt in range(max_attempts):
            log_info(f"Extraction attempt {attempt + 1}/{max_attempts}")

            # Extract characters
            _, all_characters = extraction_agent(missing_characters, chapter_text)
            log_info("Character extraction completed")

            # Check completeness
            is_complete = completeness_judge(missing_characters, all_characters)

            if is_complete:
                log_info("Character extraction completed successfully")
                break
            else:
                log_info(f"Completeness check failed on attempt {attempt + 1}")
                if attempt < max_attempts - 1:
                    log_info("Retrying extraction...")
                else:
                    log_info("Maximum attempts reached, extraction incomplete")

        # Save the updated collection
        from helpers.settings import DEFAULT_CHARACTERS_STORAGE

        character_collection.save(DEFAULT_CHARACTERS_STORAGE)

        log_exit("extract_characters_from_chapter")
        return is_complete

    except Exception as e:
        log_error(f"Error during character extraction: {e}")
        log_exit("extract_characters_from_chapter")
        return False
