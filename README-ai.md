# AI-Assisted Function Development for Cloudmesh AI OpenAPI

This project uses a "Code-to-Spec" architecture where Python functions are the source of truth for the OpenAPI specification. To ensure that AI-generated functions are fully compatible with the `Generator` and result in a valid OpenAPI spec, specific coding standards must be followed.

## How it Works

The `Generator` inspects your Python code to build the API:
- **Type Hints** $\rightarrow$ Define the OpenAPI schema (types, required fields, arrays, objects).
- **Docstrings** $\rightarrow$ Define the API documentation (summaries, parameter descriptions).
- **Dataclasses** $\rightarrow$ Define complex request and response models in `components/schemas`.

## Requirements for AI-Generated Functions

To get the best results from an AI, ensure the generated code adheres to these rules:

1. **Strict Type Hinting**: Every parameter and the return value must have a type hint. Use the `typing` module for `Optional`, `List`, `Dict`, and `Union`.
2. **Google-Style Docstrings**: Use a clear summary on the first line and a detailed `Args:` and `Returns:` section.
3. **Dataclasses for Objects**: Any complex return type or input object must be defined as a `@dataclass`.
4. **Cloudmesh AI Common**: Use `cloudmesh.ai.common.io.Console` for all logging instead of `print()`.

## Using the AI Prompt

We provide a specialized prompt in `prompt-ai-function.md`. Copy and paste that prompt into your AI of choice (GPT-4, Claude, Gemini, etc.), and simply add your specific function logic at the end.

The resulting code can then be processed by the CLI:
```bash
cms openapi generate --filename=your_function.py