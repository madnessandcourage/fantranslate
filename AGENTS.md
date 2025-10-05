# Agentic Coding Guidelines

This document provides guidelines for AI agents and automated tools working on this codebase.

## Code Quality

- **Linting**: Run `./script/lint` after any code changes to format code and check types.
- **Testing**: Always write tests for new code. Run `./script/test` before finishing a task to ensure tests pass. Use pytest for testing.
- **CI Verification**: You MUST run `./script/lint` and `./script/test` and ensure they both pass before finishing the task.

## Project Structure

- Source code goes in `src/`.
- Use `pyproject.toml` for project configuration, including dependencies and tool settings.
- Dependencies are listed in `pyproject.toml`.
- The main entry point is `src/main.py`, exposed as the `fantranslate` binary.
- AI test recordings are stored in `.ai_recordings/` and should be committed to the repository for reliable testing.

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