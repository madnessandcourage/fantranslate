#!/usr/bin/env python3

import argparse
import json
import os
from typing import Optional

from dotenv import load_dotenv

from tracing import (
    LogLevel,
    log_enter,
    log_error,
    log_exit,
    log_info,
    log_trace,
    set_log_level,
)


def main():
    parser = argparse.ArgumentParser(description="FanTranslate CLI")
    parser.add_argument(
        "-v",
        "--verbose",
        action="count",
        default=0,
        help="Increase verbosity (use -v for debug, -vv for trace)",
    )

    subparsers = parser.add_subparsers(dest="command", help="Available commands")

    # Character management subcommands
    char_parser = subparsers.add_parser(
        "character", help="Character management operations"
    )
    char_subparsers = char_parser.add_subparsers(
        dest="char_command", help="Character commands"
    )

    # Create character
    create_parser = char_subparsers.add_parser("create", help="Create a new character")
    create_parser.add_argument("name", help="Character name")
    create_parser.add_argument(
        "--gender",
        choices=["male", "female", "other"],
        default="other",
        help="Character gender",
    )

    # Search character
    search_parser = char_subparsers.add_parser("search", help="Search for characters")
    search_parser.add_argument("query", help="Search query")

    # Update character
    update_parser = char_subparsers.add_parser("update", help="Update a character")
    update_parser.add_argument("name", help="Character name to update")
    update_parser.add_argument("--new_name", help="New name")
    update_parser.add_argument(
        "--gender", choices=["male", "female", "other"], help="New gender"
    )

    # Demo workflow
    subparsers.add_parser("demo", help="Run character management demo")

    args = parser.parse_args()

    # Set log level based on verbosity
    if args.verbose >= 2:
        set_log_level(LogLevel.TRACE)
    elif args.verbose == 1:
        set_log_level(LogLevel.DEBUG)
    else:
        set_log_level(LogLevel.NORMAL)

    log_enter("main")
    log_info(
        "Log level set to {}".format(
            "TRACE" if args.verbose >= 2 else "DEBUG" if args.verbose == 1 else "NORMAL"
        )
    )

    load_dotenv()
    api_key = os.getenv("OPENROUTER_API_KEY")

    if args.command == "character":
        handle_character_command(args, api_key)
    elif args.command == "demo":
        handle_demo(api_key)
    else:
        # Original behavior
        if api_key:
            log_info("API key loaded successfully")
            from ai import ai

            log_enter("ai_call")
            joke = ai("You are a comedian.", "Tell me a funny joke not about science.")
            log_exit("ai_call")
            if joke:
                print(joke)
            else:
                log_error("Failed to get joke from AI")
        else:
            log_error("Failed to load API key")
        log_trace("Model", "openai/gpt-4o-mini")
        print("Hello World")

    log_exit("main")


def handle_character_command(args: argparse.Namespace, api_key: Optional[str]) -> None:
    if not api_key:
        log_error("API key required for character operations")
        return

    from fantranslate.tools.character import (  # type: ignore
        create_character,
        search_character,
        update_character,
    )

    if args.char_command == "create":
        data = {"name": args.name, "gender": args.gender}
        result = create_character(json.dumps(data))
        print(f"Created character: {result}")
    elif args.char_command == "search":
        result = search_character(args.query)
        print(f"Search results: {result}")
    elif args.char_command == "update":
        updates = {}
        if args.new_name:
            updates["name"] = args.new_name
        if args.gender:
            updates["gender"] = args.gender
        if updates:
            data = {"name": args.name, "updates": updates}
            result = update_character(json.dumps(data))
            print(f"Updated character: {result}")
        else:
            log_error("No updates specified")


def handle_demo(api_key: Optional[str]) -> None:
    if not api_key:
        log_error("API key required for demo")
        return

    log_info("Running character management demo")

    from fantranslate.tools.character import (  # type: ignore
        create_character,
        get_character_translation,
        search_character,
    )

    # Create a character
    data = {"name": "Frodo Baggins", "gender": "male"}
    result = create_character(json.dumps(data))
    print(f"Created: {result}")

    # Search for it
    results = search_character("Frodo")
    print(f"Search results: {results}")

    # Get translation (assuming English to Spanish)
    trans_data = {"name": "Frodo Baggins", "language": "es"}
    translated = get_character_translation(json.dumps(trans_data))
    print(f"Translated: {translated}")

    log_info("Demo completed")


if __name__ == "__main__":
    main()
