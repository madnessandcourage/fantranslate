# Agentic Coding Guidelines

This document provides guidelines for AI agents and automated tools working on this codebase.

## Code Quality

- **Linting**: Run `./script/lint` after any code changes to format code and check types. Linting MUST ALWAYS pass with 0 errors, 0 warnings, 0 informations.
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
- **Don't type anything as `Any` until this is a last resort.** Prefer specific types like `Union`, `Optional`, or custom types.
- **Type ignores should only be used as a last resort** when:
  - Third-party libraries have incomplete or incorrect type stubs
  - Complex generic types cannot be properly expressed
  - The typing issue doesn't affect runtime behavior
- When using type ignores, add a comment explaining why: `# type: ignore[error-code] # explanation`
- Prefer fixing the root cause (correct imports, type annotations, etc.) over ignoring

## Tracing and Debugging

This codebase includes a comprehensive tracing framework for debugging and monitoring code execution, especially LLM interactions.

### Tracing Functions

Use the following functions from `src/tracing.py` to add tracing throughout the codebase:

```python
from tracing import (
    log_enter, log_exit, log_info, log_trace,
    log_llm_system, log_llm_operator, log_llm_ai, log_llm_tool, log_error
)

# Function entry/exit with automatic indentation
log_enter("function_name")
# ... function code ...
log_exit("function_name")

# General logging
log_info("Informational message")
log_trace("key", "value")  # Only shown in trace mode
log_error("Error message")

# LLM-specific logging (automatically trims to 100 words)
log_llm_system("System prompt")
log_llm_operator("User query")
log_llm_ai("AI response")
log_llm_tool("tool_name", "arg1", "arg2")  # Tool usage
```

### Debug Levels

Control tracing verbosity via command line arguments:

- **Normal** (default): Only `log_error` messages
- **Debug** (`-v`): All messages except `log_trace`
- **Trace** (`-vv`): All messages including `log_trace`

### Usage Examples

```bash
# Normal mode - errors only
./script/fantranslate

# Debug mode - function calls, LLM interactions
./script/fantranslate -v

# Trace mode - includes trace messages
./script/fantranslate -vv
```

### Integration Guidelines

- Always use `log_enter`/`log_exit` for function boundaries
- Use LLM-specific functions for all AI interactions
- Use `log_trace` for detailed debugging information
- Use `log_info` for important state changes
- Use `log_error` for error conditions

### AgentExecutor Logging

The `AgentExecutor` in `src/ai.py` has `verbose=False` by default. Our custom tracing framework provides more comprehensive and controlled logging than LangChain's built-in verbose mode, which would output unstructured text to stdout. We prefer our structured tracing system for the following reasons:

- **Structured output**: Our tracing goes to stderr with proper indentation and prefixes
- **Level control**: Different verbosity levels (normal, debug, trace)
- **LLM-specific handling**: Automatic trimming of long responses to 100 words
- **Consistency**: Uniform logging format across the entire codebase

If LangChain's verbose mode is ever needed for debugging specific LangChain issues, the `verbose` parameter can be temporarily set to `True`, but our custom tracing should be used for all production logging.

## Import Organization

- **All imports must be at the top of the file**: Do not place import statements inside functions, classes, or anywhere else in the code. All imports should be grouped at the beginning of the file, after any module docstrings but before any executable code.
- **Import order**: Follow the standard Python import order:
  1. Standard library imports
  2. Third-party imports
  3. Local imports (from the current package)
- **Use isort**: The `./script/lint` command runs `isort` which automatically sorts and organizes imports according to the configuration in `pyproject.toml`.
- **Avoid conditional imports**: Do not use imports inside `if` statements or try/except blocks unless absolutely necessary for optional dependencies.
- **Avoid relative imports**: Do not use relative imports (imports starting with `.`). Configure PYTHONPATH to ensure imports work consistently between app and tests. Imports should NOT contain `src` - use absolute imports from the project root.

## Testing Best Practices

- **Never skip tests**: All tests must be active and passing. If tests are being skipped, unskip and fix them immediately.
- **AI must write tests**: Always write comprehensive tests for new code, especially for AI-powered functions.
- **AI must run tests**: Always run `./script/test` before finishing any task to ensure tests pass.
- **Test AI functions thoroughly**: When testing AI functions, ensure chat history actually influences output by testing with and without history.

## AI Prompt Engineering

- **Use ContextManager for prompt composition**: Build complex AI prompts using immutable ContextManager patterns with sections, wrapped content, examples, and failure examples.
- **Implement retry logic**: AI calls should include retry mechanisms (default 3 retries) for prompts where we can 100% check that AI failed and enforce retry.
- **Stabilize prompts with examples**: Provide good and bad examples in prompts to improve AI response consistency.
- **Use specific response formats**: For yesno prompts, require exact formats like "YES" or "NO, <reason>" with no additional prefixes.
- **Prefer XML for AI data**: When serializing data for AI consumption, prefer XML over JSON as AIs handle XML better.

## API Design Patterns

- **Design for dual interfaces**: APIs should work for both Python code and AI tools (e.g., character management functions).
- **Use tuple returns**: Functions returning multiple related values should return tuples (e.g., `(bool, reason)` for yes/no helpers).
- **Implement immutability**: Use immutable patterns where appropriate (e.g., ContextManager returns new instances).
- **Validate constraints**: Implement proper validation for domain constraints (e.g., language availability in TranslationString).
- **Implement fuzzy search**: Provide fuzzy search capabilities with configurable typo tolerance.

## Data Modeling Conventions

- **Custom equality behavior**: Implement domain-specific equality for objects (e.g., TranslationString equality across languages).
- **Serialization methods**: Use `to_dict` / `from_dict` methods for object serialization.
- **Confidence levels**: Include confidence scores for uncertain data (e.g., character characteristics).
- **Language validation**: Validate language constraints and provide clear error messages for violations.

## Error Handling

- **Fail fast on configuration**: Immediately throw errors when required configuration is missing or invalid.
- **Clear error messages**: Provide specific, actionable error messages for constraint violations.
- **No silent failures**: Never silently ignore errors or constraints.

## Performance Optimization

- **Implement fast search**: Use optimized fuzzy search algorithms for performance-critical operations.
- **Memoization**: Use memoization decorators for expensive operations, especially AI calls.
- **Dependency caching**: Use CI caching mechanisms to reduce build times (e.g., GitHub Actions dependency caching).
- **Profile bottlenecks**: Identify and optimize performance bottlenecks (e.g., 25+ second dependency installations).

## CLI Design

- **Use argparse**: Implement command-line interfaces using argparse for proper argument parsing.
- **Debug levels**: Provide multiple verbosity levels (-v for debug, -vv for trace).
- **Extensible commands**: Design command structures that can be easily extended with subcommands.
- **Standard script infrastructure**: Use consistent script patterns (./script/setup, ./script/test, ./script/lint).

## LangChain Integration

- **Custom tracing over verbose**: Disable LangChain's verbose mode and use custom tracing framework for better control.
- **Tool design**: Create tools that work seamlessly with agentic workflows.
- **Dual interfaces**: Ensure functionality is accessible through both Python APIs and LangChain tools.

## Tool Writing Best Practices

When creating tools for LangChain agents, follow these critical patterns to ensure reliable operation:

### Function Signatures for StructuredTool

- **Accept individual parameters, not Pydantic models**: When using `StructuredTool.from_function()`, the underlying function must accept individual parameters that match the Pydantic schema fields, not the Pydantic model instance itself.

  ```python
  # ❌ Incorrect - function receives Pydantic model
  def _create_character_with_logging(args: CreateCharacterArgs) -> str:
      return create_character(args.name, args.gender)

  # ✅ Correct - function receives individual parameters
  def _create_character_with_logging(name: str, gender: str = "UNKNOWN") -> str:
      return create_character(name, gender)
  ```

- **Match parameter names exactly**: Parameter names in the function signature must match the field names in the Pydantic `args_schema`.

### Error Handling

- **Never let exceptions crash the agent**: Always wrap tool implementations with try-catch blocks and return error messages as strings instead of raising exceptions.

  ```python
  def _create_character_with_logging(name: str, gender: str = "UNKNOWN") -> str:
      try:
          return create_character(name, gender)
      except Exception as e:
          return f"Error creating character: {str(e)}"
  ```

- **Return meaningful error messages**: Error messages should be descriptive and help the AI understand what went wrong, allowing it to potentially retry or adjust its approach.

### Configuration and Dependencies

- **Load settings from correct paths**: Ensure configuration files are loaded from the project root (`RESOURCE_DIR`) rather than the current working directory, as scripts may change the working directory.

  ```python
  # In src/helpers/settings.py
  project_file = os.path.join(RESOURCE_DIR, "project.yml")  # ✅ Correct
  # NOT: project_file = os.path.join(os.getcwd(), "project.yml")  # ❌ Incorrect
  ```

### Logging

- **Use LLM-specific logging**: Always log tool usage with `log_llm_tool()` for proper tracing and debugging.

  ```python
  def _create_character_with_logging(name: str, gender: str = "UNKNOWN") -> str:
      log_llm_tool("CreateCharacter", name, gender)  # Log tool usage
      try:
          return create_character(name, gender)
      except Exception as e:
          return f"Error creating character: {str(e)}"
  ```

### Testing

- **Test tool error handling**: Write tests that verify tools handle exceptions gracefully and return appropriate error messages.
- **Test with real agent execution**: Ensure tools work correctly when called by LangChain agents, not just in isolation.

## Project Infrastructure

- **Venv management**: Use `./script/setup` to setup venv and install dependencies, `./script/fantranslate` to run, `./script/lint` to lint, etc. No direct pip installs - only through scripts.
- **Standardized scripts**: Implement consistent script infrastructure with proper flags (-e for bash scripts to fail on first error).
- **Gitignore patterns**: Use specific gitignore patterns for project artifacts (playground folders, etc.). **NEVER** put ai_recordings into .gitignore.
- **Code organization**: Split large functionality into appropriate subdirectories (src/commands/, src/tools/, etc.).

## Security

- Never introduce code that exposes secrets or keys.
- Store API keys in .env files with proper loading mechanisms.
- Follow Python best practices for security.

## Conventions

- Use type hints where possible.
- Follow PEP 8 style, enforced by black and isort.
- Keep functions and modules focused and small.
- Use `to_dict` / `from_dict` methods for serialization of objects.
- `original_language` and `available_languages` should ALWAYS be read from settings, not passed as arguments.
- When serializing data for AI consumption, prefer XML over JSON as AIs tend to handle XML better.
- Use `DEFAULT_CHARACTERS_STORAGE` constant from `src/helpers/settings.py` for all character and character collection operations.
- **Use `** BOLD **` for all headers in AI prompts**: Use `** HEADER NAME **` format instead of markdown headers (`#`, `##`, etc.) for consistency across all AI prompts. Documentation should continue using standard markdown headers (`#`, `##`, etc.).