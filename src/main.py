#!/usr/bin/env python3

import argparse
import os
from typing import List

import yaml

from tracing import (
    LogLevel,
    log_enter,
    log_error,
    log_exit,
    log_info,
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

    # Init command
    init_parser = subparsers.add_parser("init", help="Initialize project.yml")
    init_parser.add_argument(
        "--from",
        dest="from_lang",
        default="en",
        help="Source language (default: en)",
    )
    init_parser.add_argument(
        "--to",
        dest="to_langs",
        default="ru",
        help="Target languages, comma-separated (default: ru)",
    )

    # Extract characters command
    extract_parser = subparsers.add_parser(
        "extract_characters", help="Extract characters from a chapter"
    )
    extract_parser.add_argument(
        "chapter_path",
        help="Path to the chapter text file",
    )

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

    if args.command == "init":
        handle_init(args.from_lang, args.to_langs)
    elif args.command == "extract_characters":
        handle_extract_characters(args.chapter_path)
    else:
        parser.print_help()

    log_exit("main")


def handle_init(from_lang: str, to_langs_str: str) -> None:
    log_info(f"Initializing project with from={from_lang}, to={to_langs_str}")

    # Parse comma-separated languages
    to_langs: List[str] = [
        lang.strip() for lang in to_langs_str.split(",") if lang.strip()
    ]

    if not to_langs:
        log_error("At least one target language must be specified")
        return

    # Use the first target language as translate_to
    translate_to = to_langs[0]

    project_data = {
        "languages": to_langs,
        "translate_from": from_lang,
        "translate_to": translate_to,
    }

    project_file = os.path.join(os.getcwd(), "project.yml")
    if os.path.exists(project_file):
        log_error(f"project.yml already exists in {os.getcwd()}")
        return

    try:
        with open(project_file, "w") as f:
            yaml.safe_dump(project_data, f, default_flow_style=False)
        log_info(f"Created {project_file}")
        print(
            f"Project initialized with source: {from_lang}, targets: {', '.join(to_langs)}"
        )
    except Exception as e:
        log_error(f"Failed to create project.yml: {e}")


def handle_extract_characters(chapter_path: str) -> None:
    log_info(f"Extracting characters from chapter: {chapter_path}")

    if not os.path.exists(chapter_path):
        log_error(f"Chapter file not found: {chapter_path}")
        return

    # Import here to avoid circular imports
    from extract_characters import extract_characters_from_chapter

    success = extract_characters_from_chapter(chapter_path)

    if success:
        print("Character extraction completed successfully")
    else:
        print("Character extraction failed or incomplete")
        exit(1)


if __name__ == "__main__":
    main()
