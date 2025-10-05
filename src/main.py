#!/usr/bin/env python3

import argparse
import os
import sys

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


if __name__ == "__main__":
    main()
