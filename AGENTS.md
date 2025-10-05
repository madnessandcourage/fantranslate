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

## Testing AI Functions

When writing tests for AI functions that use the `@memoise_for_tests` decorator:

1. **Write incomplete tests first**: Start with a test that calls the AI function and prints the output, without assertions. This allows the AI response to be recorded.

2. **Run the test**: Execute the test to generate the `.ai_recordings/` files with the AI responses.

3. **Complete the test**: Once the AI output is recorded and stable, read the expected output from the recordings and add proper assertions.

4. **Example pattern**:
   ```python
   def test_ai_function():
       # Call the function
       result = ai_function("input")

       # During development, print to see output
       print(f"AI output: {result}")

       # After recording is stable, assert the expected output
       assert result == "expected response"
   ```

5. **Chat history testing**: When testing functions that accept previous chat history, ensure the history actually influences the output by testing with and without history.

## Type Checking

- Use type hints where possible and strive for full type coverage.
- **Type ignores should only be used as a last resort** when:
  - Third-party libraries have incomplete or incorrect type stubs
  - Complex generic types cannot be properly expressed
  - The typing issue doesn't affect runtime behavior
- When using type ignores, add a comment explaining why: `# type: ignore[error-code] # explanation`
- Prefer fixing the root cause (correct imports, type annotations, etc.) over ignoring

## Conventions

- Use type hints where possible.
- Follow PEP 8 style, enforced by black and isort.
- Keep functions and modules focused and small.