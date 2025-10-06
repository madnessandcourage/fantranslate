#!/usr/bin/env python3

import argparse
import json
import os
import sys
from typing import Optional

from dotenv import load_dotenv

from ai import agent, ai
from tools.character import (
    add_character_short_name,
    create_character,
    get_all_characters,
    get_character_translation,
    search_character,
    set_character_gender,
)
from tools.hello import hello_tool
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
    parser.add_argument(
        "--agent",
        help="Run a specific agent (e.g., demo_agent)",
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

    # Add short name
    add_sn_parser = char_subparsers.add_parser(
        "add_short_name", help="Add a short name to a character"
    )
    add_sn_parser.add_argument("name", help="Character name")
    add_sn_parser.add_argument("short_name", help="Short name to add")

    # Set gender
    set_gender_parser = char_subparsers.add_parser(
        "set_gender", help="Set character gender"
    )
    set_gender_parser.add_argument("name", help="Character name")
    set_gender_parser.add_argument(
        "gender", choices=["male", "female", "other"], help="Gender"
    )

    # List all characters
    char_subparsers.add_parser("list", help="List all characters")

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

    # Only load .env in non-test environments
    if not (
        os.getenv("PYTEST_CURRENT_TEST")
        or os.getenv("CI")
        or os.getenv("GITHUB_ACTIONS")
        or any("pytest" in arg for arg in sys.argv)
        or any("test" in arg.lower() for arg in sys.argv)
    ):
        load_dotenv()
    api_key = os.getenv("OPENROUTER_API_KEY")

    if args.agent:
        handle_agent_command(args.agent, api_key)
    elif args.command == "character":
        handle_character_command(args, api_key)
    elif args.command == "demo":
        handle_demo(api_key)
    else:
        # Original behavior
        if api_key:
            log_info("API key loaded successfully")

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

    if args.char_command == "create":
        result = create_character(args.name, args.gender)
        print(f"Created character: {result}")
    elif args.char_command == "search":
        result = search_character(args.query)
        print(f"Search results: {result}")
    elif args.char_command == "add_short_name":
        result = add_character_short_name(args.name, args.short_name)
        print(f"Added short name: {result}")
    elif args.char_command == "set_gender":
        result = set_character_gender(args.name, args.gender)
        print(f"Set gender: {result}")
    elif args.char_command == "list":
        result = get_all_characters()
        print(result)


def handle_demo(api_key: Optional[str]) -> None:
    if not api_key:
        log_error("API key required for demo")
        return

    log_info("Running character management demo")

    # Create a character
    result = create_character("Frodo Baggins", "male")
    print(f"Created: {result}")

    # Search for it
    results = search_character("Frodo")
    print(f"Search results: {results}")

    # Get translation (assuming English to Spanish)
    translated = get_character_translation(
        json.dumps({"name": "Frodo Baggins", "language": "es"})
    )
    print(f"Translated: {translated}")

    log_info("Demo completed")


def handle_agent_command(agent_name: str, api_key: Optional[str]) -> None:
    if not api_key:
        log_error("API key required for agent operations")
        return

    if agent_name == "demo_agent":
        log_info("Running demo agent")
        output, _ = agent(
            system_prompt="You are a helpful assistant that can use tools to greet people.",
            user_query="Who should I say hello to?",
            tools=[hello_tool],
        )
        print(output)
        log_info("Demo agent completed")
    else:
        log_error(f"Unknown agent: {agent_name}")


if __name__ == "__main__":
    main()
