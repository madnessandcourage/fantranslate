import argparse
import os
import sys

from helpers.settings import DEFAULT_CHARACTERS_STORAGE, settings
from models.character_collection import CharacterCollection
from tracing import log_enter, log_error, log_exit


def load_character_collection() -> CharacterCollection:
    """Load the character collection from file."""
    collection = CharacterCollection()
    if os.path.exists(DEFAULT_CHARACTERS_STORAGE):
        collection = CharacterCollection.from_file(DEFAULT_CHARACTERS_STORAGE)
    return collection


def save_character_collection(collection: CharacterCollection) -> None:
    """Save the character collection to file."""
    collection.save(DEFAULT_CHARACTERS_STORAGE)


def handle_list(args: argparse.Namespace) -> None:
    """Handle the 'character list' command."""
    log_enter("handle_list")

    try:
        collection = load_character_collection()
        s = settings()
        characters = collection.get_all_characters(s.translate_from)

        if not characters:
            print("No characters found.")
            log_exit("handle_list")
            return

        # Print table
        if characters:
            print(f"{'Name':<20} {'Short Names':<35} {'Gender':<10} {'Chars'}")
            print("-" * 85)
            for char in characters:
                short_names = ", ".join(char.short_names) if char.short_names else ""
                name = char.name[:19] if len(char.name) > 19 else char.name
                short = short_names[:34] if len(short_names) > 34 else short_names
                gender = (char.gender or "")[:9]
                print(
                    f"{name:<20} {short:<35} {gender:<10} {len(char.characteristics)}"
                )

    except Exception as e:
        log_error(f"Error listing characters: {e}")
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)

    log_exit("handle_list")


def handle_info(args: argparse.Namespace) -> None:
    """Handle the 'character info' command."""
    log_enter("handle_info")

    try:
        collection = load_character_collection()
        character = collection.search(args.search_query)

        if not character:
            print(f"Character '{args.search_query}' not found.")
            log_exit("handle_info")
            return

        s = settings()
        translated = character.get_translated(s.translate_from)

        print(f"Name: {translated.name}")
        if translated.short_names:
            print(f"Short Names: {', '.join(translated.short_names)}")
        if translated.gender:
            print(f"Gender: {translated.gender}")

        if translated.characteristics:
            print("Characteristics:")
            for char in sorted(
                translated.characteristics, key=lambda x: x["confidence"], reverse=True
            ):
                print(f"  - {char['sentence']} (confidence: {char['confidence']})")
        else:
            print("Characteristics: None")

        # Show translations if available
        print("\nTranslations:")
        for lang in s.languages:
            if lang != s.translate_from:
                trans = character.get_translated(lang)
                print(f"  {lang.upper()}: {trans.name}")
                if trans.short_names:
                    print(f"    Short Names: {', '.join(trans.short_names)}")
                if trans.gender:
                    print(f"    Gender: {trans.gender}")

    except Exception as e:
        log_error(f"Error getting character info: {e}")
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)

    log_exit("handle_info")


def handle_search(args: argparse.Namespace) -> None:
    """Handle the 'character search' command."""
    log_enter("handle_search")

    try:
        collection = load_character_collection()
        character = collection.search(args.search_query)

        if not character:
            print(f"Character '{args.search_query}' not found.")
            log_exit("handle_search")
            return

        s = settings()
        translated = character.get_translated(s.translate_from)

        print(f"Found: {translated.name}")
        if translated.short_names:
            print(f"Short Names: {', '.join(translated.short_names)}")
        if translated.gender:
            print(f"Gender: {translated.gender}")

    except Exception as e:
        log_error(f"Error searching character: {e}")
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)

    log_exit("handle_search")


def handle_edit(args: argparse.Namespace) -> None:
    """Handle the 'character edit' command."""
    log_enter("handle_edit")

    try:
        collection = load_character_collection()
        character = collection.search(args.search_query)

        if not character:
            print(f"Character '{args.search_query}' not found.")
            log_exit("handle_edit")
            return

        modified = False

        # Handle short name additions/removals
        if args.add_short_name:
            for name in args.add_short_name:
                # Check if short name exactly matches the full name
                if name.strip().lower() == character.name.original_text.strip().lower():
                    print(
                        f"Error: Short name '{name}' cannot be the same as the character's full name '{character.name.original_text}'. Short names should be abbreviations or alternative forms, not duplicates of the full name."
                    )
                    continue
                character.add_short_name(name)
                print(f"Added short name: {name}")
                modified = True

        if args.remove_short_name:
            for name in args.remove_short_name:
                character.remove_short_name(name)
                print(f"Removed short name: {name}")
                modified = True

        # Handle gender change
        if args.gender:
            character.update(gender=args.gender)
            print(f"Set gender to: {args.gender}")
            modified = True

        # Handle name change
        if args.change_name:
            character.update(name=args.change_name)
            print(f"Changed name to: {args.change_name}")
            modified = True

        # Handle characteristic additions/removals
        if args.add_characteristic:
            for char_text in args.add_characteristic:
                character.add_characteristic(char_text)
                print(f"Added characteristic: {char_text}")
                modified = True

        if args.remove_characteristic:
            for char_text in args.remove_characteristic:
                character.remove_characteristic(char_text)
                print(f"Removed characteristic: {char_text}")
                modified = True

        if modified:
            collection.rebuild_index()
            save_character_collection(collection)
            print("Character updated successfully.")
        else:
            print("No changes made.")

    except Exception as e:
        log_error(f"Error editing character: {e}")
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)

    log_exit("handle_edit")


def handle_edit_translation(args: argparse.Namespace) -> None:
    """Handle the 'character edit-translation' command."""
    log_enter("handle_edit_translation")

    try:
        collection = load_character_collection()
        character = collection.search(args.name)

        if not character:
            print(f"Character '{args.name}' not found.")
            log_exit("handle_edit_translation")
            return

        s = settings()
        if args.lang not in s.languages:
            print(f"Language '{args.lang}' is not configured in project.yml")
            log_exit("handle_edit_translation")
            return

        modified = False

        # Handle short name additions/removals for translation
        if args.add_short_name:
            for name in args.add_short_name:
                # Add translation to all existing short names
                for sn in character.short_names:
                    setattr(sn, args.lang, name)
                    print(
                        f"Added {args.lang} translation '{name}' for short name '{sn.original_text}'"
                    )
                    modified = True

        if args.remove_short_name:
            for name in args.remove_short_name:
                # Find short name with this translation and remove it
                for sn in character.short_names:
                    if getattr(sn, args.lang, None) == name:
                        delattr(sn, args.lang)
                        print(
                            f"Removed {args.lang} translation '{name}' for short name '{sn.original_text}'"
                        )
                        modified = True
                        break

        # Handle gender translation
        if args.gender:
            if character.gender:
                setattr(character.gender, args.lang, args.gender)
                print(f"Set {args.lang} gender translation to: {args.gender}")
                modified = True

        # Handle name translation
        if args.change_name:
            setattr(character.name, args.lang, args.change_name)
            print(f"Set {args.lang} name translation to: {args.change_name}")
            modified = True

        # Handle characteristic translations
        if args.add_characteristic:
            for char_text in args.add_characteristic:
                # Find existing characteristic and add translation
                for char in character.characteristics:
                    if char.text.original_text == char_text:
                        setattr(char.text, args.lang, char_text)
                        print(
                            f"Added {args.lang} translation for characteristic: {char_text}"
                        )
                        modified = True
                        break

        if args.remove_characteristic:
            for char_text in args.remove_characteristic:
                # Find existing characteristic and remove translation
                for char in character.characteristics:
                    if char.text.original_text == char_text:
                        if hasattr(char.text, args.lang):
                            delattr(char.text, args.lang)
                        print(
                            f"Removed {args.lang} translation for characteristic: {char_text}"
                        )
                        modified = True
                        break

        if modified:
            save_character_collection(collection)
            print("Character translation updated successfully.")
        else:
            print("No changes made.")

    except Exception as e:
        log_error(f"Error editing character translation: {e}")
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)

    log_exit("handle_edit_translation")


def handle_create(args: argparse.Namespace) -> None:
    """Handle the 'character create' command."""
    log_enter("handle_create")

    try:
        collection = load_character_collection()

        # Check if character already exists
        existing = collection.search(args.name)
        if existing:
            print(f"Character '{args.name}' already exists.")
            log_exit("handle_create")
            return

        # Create new character
        # Filter out short names that match the full name
        from typing import List, Union

        from models.character import Character
        from models.translation_string import TranslationString

        filtered_short_names: List[Union[str, TranslationString]] = []
        if args.short_name:
            for sn in args.short_name:
                if sn.strip().lower() == args.name.strip().lower():
                    print(
                        f"Warning: Skipping short name '{sn}' as it matches the character's full name '{args.name}'. Short names should be abbreviations or alternative forms, not duplicates of the full name."
                    )
                else:
                    filtered_short_names.append(sn)

        character = Character(
            name=args.name,
            short_names=filtered_short_names,
            gender=args.gender,
            characteristics=args.characteristic or [],
        )

        collection.add_character(character)
        save_character_collection(collection)
        print(f"Character '{args.name}' created successfully.")

    except Exception as e:
        log_error(f"Error creating character: {e}")
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)

    log_exit("handle_create")


def handle_remove(args: argparse.Namespace) -> None:
    """Handle the 'character remove' command."""
    log_enter("handle_remove")

    try:
        collection = load_character_collection()
        character = collection.search(args.search_query)

        if not character:
            print(f"Character '{args.search_query}' not found.")
            log_exit("handle_remove")
            return

        # Confirm removal
        s = settings()
        translated = character.get_translated(s.translate_from)
        print(f"Remove character: {translated.name}")
        if translated.short_names:
            print(f"Short names: {', '.join(translated.short_names)}")

        confirm = input("Are you sure? (y/N): ").lower().strip()
        if confirm not in ["y", "yes"]:
            print("Removal cancelled.")
            log_exit("handle_remove")
            return

        collection.remove_character(character.name.original_text)
        save_character_collection(collection)
        print("Character removed successfully.")

    except Exception as e:
        log_error(f"Error removing character: {e}")
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)

    log_exit("handle_remove")


def handle_translate(args: argparse.Namespace) -> None:
    """Handle the 'character translate' command."""
    log_enter("handle_translate")

    try:
        collection = load_character_collection()
        character = collection.search(args.search_query)

        if not character:
            print(f"Character '{args.search_query}' not found.")
            log_exit("handle_translate")
            return

        # Check if chapter file exists
        if not os.path.exists(args.chapter_path):
            print(f"Chapter file not found: {args.chapter_path}")
            log_exit("handle_translate")
            return

        # Check if target language is configured
        s = settings()
        if args.to not in s.languages:
            print(f"Language '{args.to}' is not configured in project.yml")
            log_exit("handle_translate")
            return

        # Read chapter contents
        with open(args.chapter_path, "r", encoding="utf-8") as f:
            chapter_contents = f.read()

        # Temporarily set translate_to to the target language
        original_translate_to = s.translate_to
        s.translate_to = args.to

        try:
            # Translate the character
            character.translate(chapter_contents)
            print(
                f"Character '{character.name.original_text}' translated to {args.to} successfully."
            )

            # Save the updated collection
            collection.rebuild_index()
            save_character_collection(collection)

        finally:
            # Restore original translate_to
            s.translate_to = original_translate_to

    except Exception as e:
        log_error(f"Error translating character: {e}")
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)

    log_exit("handle_translate")


def setup_character_parser(subparsers):  # type: ignore
    """Set up the character subcommand parser."""
    character_parser = subparsers.add_parser("character", help="Manage characters")  # type: ignore
    character_subparsers = character_parser.add_subparsers(dest="character_command", help="Character commands")  # type: ignore

    # character list
    character_subparsers.add_parser("list", help="List all characters")  # type: ignore

    # character create <name> [options]
    create_parser = character_subparsers.add_parser("create", help="Create a new character")  # type: ignore
    create_parser.add_argument("name", help="Character name")  # type: ignore
    create_parser.add_argument("--short-name", action="append", help="Add a short name")  # type: ignore
    create_parser.add_argument("--gender", help="Set gender")  # type: ignore
    create_parser.add_argument("--characteristic", action="append", help="Add a characteristic")  # type: ignore

    # character info <search_query>
    info_parser = character_subparsers.add_parser("info", help="Show detailed character information")  # type: ignore
    info_parser.add_argument("search_query", help="Character name or short name to search for")  # type: ignore

    # character search <search_query>
    search_parser = character_subparsers.add_parser("search", help="Search for a character")  # type: ignore
    search_parser.add_argument("search_query", help="Character name or short name to search for")  # type: ignore

    # character edit <search_query> [options]
    edit_parser = character_subparsers.add_parser("edit", help="Edit a character")  # type: ignore
    edit_parser.add_argument("search_query", help="Character name or short name to edit")  # type: ignore
    edit_parser.add_argument("--add-short-name", action="append", help="Add a short name")  # type: ignore
    edit_parser.add_argument("--remove-short-name", action="append", help="Remove a short name")  # type: ignore
    edit_parser.add_argument("--gender", help="Set gender")  # type: ignore
    edit_parser.add_argument("--change-name", help="Change the character name")  # type: ignore
    edit_parser.add_argument("--add-characteristic", action="append", help="Add a characteristic")  # type: ignore
    edit_parser.add_argument("--remove-characteristic", action="append", help="Remove a characteristic")  # type: ignore

    # character edit-translation <name> --lang <lang> [options]
    edit_trans_parser = character_subparsers.add_parser("edit-translation", help="Edit character translations")  # type: ignore
    edit_trans_parser.add_argument("name", help="Character name")  # type: ignore
    edit_trans_parser.add_argument("--lang", required=True, help="Language code")  # type: ignore
    edit_trans_parser.add_argument("--add-short-name", action="append", help="Add translated short name")  # type: ignore
    edit_trans_parser.add_argument("--remove-short-name", action="append", help="Remove translated short name")  # type: ignore
    edit_trans_parser.add_argument("--gender", help="Set translated gender")  # type: ignore
    edit_trans_parser.add_argument("--change-name", help="Set translated name")  # type: ignore
    edit_trans_parser.add_argument("--add-characteristic", action="append", help="Add translated characteristic")  # type: ignore
    edit_trans_parser.add_argument("--remove-characteristic", action="append", help="Remove translated characteristic")  # type: ignore

    # character remove <search_query>
    remove_parser = character_subparsers.add_parser("remove", help="Remove a character")  # type: ignore
    remove_parser.add_argument("search_query", help="Character name or short name to remove")  # type: ignore

    # character translate <search_query> <chapter_path> --to <lang>
    translate_parser = character_subparsers.add_parser("translate", help="Translate character using AI")  # type: ignore
    translate_parser.add_argument("search_query", help="Character name or short name to translate")  # type: ignore
    translate_parser.add_argument("chapter_path", help="Path to chapter file for context")  # type: ignore
    translate_parser.add_argument("--to", required=True, help="Target language code")  # type: ignore


def handle_character_command(args: argparse.Namespace) -> None:
    """Handle character subcommands."""
    if args.character_command == "list":
        handle_list(args)
    elif args.character_command == "create":
        handle_create(args)
    elif args.character_command == "info":
        handle_info(args)
    elif args.character_command == "search":
        handle_search(args)
    elif args.character_command == "edit":
        handle_edit(args)
    elif args.character_command == "edit-translation":
        handle_edit_translation(args)
    elif args.character_command == "remove":
        handle_remove(args)
    elif args.character_command == "translate":
        handle_translate(args)
    else:
        print(
            "Unknown character command. Use 'fantranslate character --help' for help."
        )
