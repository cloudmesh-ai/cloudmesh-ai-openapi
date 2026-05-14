# Changelog

All notable changes to `cloudmesh-ai-openapi` are documented in this file.

## [0.1.0] - 2026-05-14

### Added
- **AI-Driven OpenAPI Generation**: Added `--ai` flag to `openapi generate` to automatically create OpenAPI specifications using LLMs.
- **AI-Powered Test Generation**: Introduced `openapi test generate` command to automatically create `pytest` suites by analyzing code and OpenAPI specs.
- **AI Service Registry Metadata**: Added automatic detection of AI-generated services and registration of `ai_generated` and `ai_model` metadata in the service registry.
- **AI-CMC Integration**: Updated registry configuration to use `cloudmesh.ai` namespace for better integration with the AI-CMC ecosystem.
- **Scikit-Learn Integration Guide**: Added `README-sklearn.md` demonstrating how to manually integrate scikit-learn models using the standard OpenAPI generator.

### Changed
- **Namespace Migration**: Migrated the entire codebase from `cloudmesh.openapi` to `cloudmesh.ai.openapi`.
- **Configuration Update**: Updated configuration keys to follow the `cloudmesh.ai` pattern (e.g., `cloudmesh.ai.registry.microservice.default.protocol`).
- **Structural Refactoring**: Reorganized the project structure to align with `cloudmesh-ai` standards.
- **Documentation**: Updated `MANUAL.md` to include instructions for new AI workflows.
- **Environment Requirements**: Updated minimum Python requirement to `>=3.9` and recommended pip version `21.0+`.

### Removed
- Deprecated legacy packaging and old `cloudmesh.openapi` references.
- **Windows Support**: Removed all `win32` specific logic and Windows-specific path handling.
- **MongoDB Dependency**: Removed MongoDB support and forced the use of the `pickle` protocol for the service registry.
- **Sklearn Generator**: Removed the complex `SklearnGenerator` and associated dependencies (`numpydoc`, `pandas`, `joblib`, `scikit-learn`) in favor of a manual wrapper approach.
