# Changelog

All notable changes to this project will be documented in this file.

## [Unreleased]

### Added
- **Dynamic HTTP Methods**: Support for `POST`, `PUT`, and `DELETE` methods.
- **Path Parameters**: Support for RESTful path parameters via the `@openapi_path_param` decorator.
- **Request Body Support**: Automatic generation of `requestBody` in OpenAPI specs when the first function argument is a `dataclass`.
- **Spec Validation**: Integrated `openapi-spec-validator` to ensure all generated specifications are compliant with the OpenAPI 3.0 standard.
- **Custom Exception Hierarchy**: Introduced `OpenApiError` and its derivatives (`OpenApiGeneratorError`, `OpenApiServerError`, etc.) for better error traceability.
- **AI Development Guides**: Added `README-ai.md` and `prompt-ai-function.md` to facilitate AI-assisted function creation.
- **Extensive Documentation**: Created a comprehensive `README.md` covering installation, developer guides, and CLI reference.

### Changed
- **Generator Engine**: Refactored the specification generator to use `PyYAML` instead of string templates, eliminating indentation issues and improving robustness.
- **Type Mapping**: Expanded type support to include `typing` generics such as `Optional`, `Union`, `List`, and `Dict`.
- **CLI Framework**: Migrated the command-line interface from manual argument parsing to `click` for better usability and automatic help generation.
- **CLI Integration**: Updated command prefix to `cmc` to ensure seamless integration with `cloudmesh-ai-cmc` via entry points.
- **Server Error Handling**: Updated the `Server` class to use custom exceptions instead of generic `Exception` or `sys.exit()`.

### Removed
- **Obsolete Parameter Class**: Removed the `Parameter` class from `executor.py` as it was replaced by `click`'s argument handling.