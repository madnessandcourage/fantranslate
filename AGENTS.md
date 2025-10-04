# Agentic Coding Guidelines

This document provides guidelines for AI agents and automated tools working on this codebase.

## Code Quality

- **Linting**: Run `black src/` and `isort src/` after any code changes to format code.
- **Type Checking**: Run `pyright` to check types after changes.
- **Testing**: Run tests if available (check for pytest or similar in pyproject.toml).

## Project Structure

- Source code goes in `src/`.
- Use `pyproject.toml` for project configuration, including dependencies and tool settings.
- Dependencies are listed in `requirements.txt`.
- The main entry point is `src/main.py`, exposed as the `fantranslate` binary.

## Development Workflow

- Install in editable mode: `pip install -e .`
- For new features, update `src/main.py` and adjust entry points in `pyproject.toml` if needed.
- Commit changes only when explicitly requested.

## Security

- Never introduce code that exposes secrets or keys.
- Follow Python best practices for security.

## Conventions

- Use type hints where possible.
- Follow PEP 8 style, enforced by black and isort.
- Keep functions and modules focused and small.