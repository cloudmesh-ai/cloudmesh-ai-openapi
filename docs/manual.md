# Cloudmesh AI OpenAPI Manual

## Overview

Cloudmesh AI OpenAPI is a framework for automatically generating OpenAPI specifications from Python code and deploying them as high-performance microservices. It leverages Large Language Models (LLMs) to bridge the gap between implementation and specification.

## Prerequisites

*   **Python 3.12 or newer**
*   **pip version 21.0 or newer**
*   A configured LLM endpoint in `config.yaml` for AI features.

## Usage

### Generation
```bash
openapi generate [FUNCTION] 
    --filename=FILENAME
    [--serverurl=SERVERURL]
    [--yamlfile=YAML]
    [--import_class]
    [--all_functions]
    [--enable_upload]
    [--ai]
    [--verbose]
    [--basic_auth=CREDENTIALS]
```

### Server Management
```bash
openapi server start YAML [NAME]
    [--directory=DIRECTORY]
    [--port=PORT]
    [--server=SERVER]
    [--host=HOST]
    [--verbose]
    [--debug]
    [--fg]
openapi server stop NAME
openapi server list [NAME] [--output=OUTPUT]
openapi server ps [NAME] [--output=OUTPUT]
```

### Registry Management
```bash
openapi register add NAME ENDPOINT
openapi register filename NAME
openapi register delete NAME
openapi register list [NAME] [--output=OUTPUT]
openapi register protocol PROTOCOL
```

### Testing & Documentation
```bash
openapi test generate [FUNCTION] --filename=FILENAME --yamlfile=YAML
openapi merge [SERVICES...] [--dir=DIR] [--verbose]
openapi doc FILE --format=(txt|md) [--indent=INDENT]
openapi doc [SERVICES...] [--dir=DIR]
```

## Arguments

- **FUNCTION**: The name for the function or class to generate a spec for.
- **FILENAME**: Path to the Python file containing the function or class.
- **SERVERURL**: OpenAPI server URL. Default: `http://localhost:8080/cloudmesh`
- **YAML**: Path to the YAML file for the OpenAPI spec. Default: `FILENAME` with `.py` replaced by `.yaml`.
- **DIR**: The directory containing the specifications.
- **FILE**: The specific OpenAPI specification file.
- **SERVICES**: A list of service names (without `.yaml` extension) to merge or document.

## Options

- `--import_class`: Indicates that `FUNCTION` is a class name.
- `--all_functions`: Generates specs for all public functions in `FILENAME`.
- `--debug`: Enables debug mode for the server.
- `--verbose`: Enables verbose logging.
- `--port=PORT`: The port for the server [default: 8080].
- `--directory=DIRECTORY`: The directory in which the server is run.
- `--server=SERVER`: The server backend [default: fastapi].
- `--output=OUTPUT`: Output format: `table`, `csv`, `yaml`, `json` [default: table].
- `--ai`: Use AI to generate the OpenAPI specification.
- `--basic_auth=CREDENTIALS`: Enable basic auth using `user:password`.

## Detailed Command Descriptions

### AI-Powered OpenAPI Generation

* `openapi generate [FUNCTION] --filename=FILENAME [--ai] ...`

  Generates an OpenAPI 3.0 specification. When the `--ai` flag is used, the system employs a sophisticated generation pipeline:

  1.  **Few-Shot Prompting**: The generator loads Python/YAML pairs from the `examples/` directory to 
        provide the LLM with context and desired patterns.
  2.  **Validation Loop**: The generated YAML is passed through a two-stage validator:
      *  **Syntax Check**: Ensures the output is valid YAML.
      *  **Schema Check**: Uses `openapi-spec-validator` to ensure the output adheres to the 
         OpenAPI 3.0 specification.
  3.  **Self-Correction**: If validation fails, the error message is fed back to the LLM for automatic correction (up to 3 retries).

### Server Management
The server is built on **FastAPI** and **Uvicorn**, providing asynchronous execution and high concurrency.

* `openapi server start YAML [NAME] [--port=PORT] [--host=HOST] [--fg]`
Starts the service. By default, it runs in the background.

    *   **Health Check**: Every started server includes a `/health` endpoint (e.g., `http://localhost:8080/health`) for monitoring.
    *   **PID Tracking**: The server writes its process ID to a `{name}.pid` file in the service directory for robust management.

* `openapi server ps [NAME]`
  Lists running servers by scanning for `.pid` files and verifying the process status.

* `openapi server stop NAME`
  Stops the server using the PID stored in the `.pid` file.

### Service Merging & Documentation

* `openapi merge [SERVICES...] [--dir=DIR]`
  Combines multiple OpenAPI specifications into a single unified specification. It merges the `paths` and `components/schemas` sections.

* `openapi doc FILE --format=(txt|md) [--indent=INDENT]`
  Generates human-readable documentation from a single YAML file. Supports Markdown (`md`) and plain text (`txt`).

* `openapi doc [SERVICES...] [--dir=DIR]`
  Generates a combined documentation report for multiple services found in the specified directory.

### Security & Authentication

The system supports multi-user Basic Authentication.
*   **Storage**: Users are stored in `~/.cloudmesh/.auth_users.json`.
*   **Hashing**: Passwords are not stored in plain text; they are hashed using **HMAC-SHA256** with a unique salt per user.
*   **Configuration**: Use `--basic_auth=user:password` during generation to set up credentials.

### Containerization

Generated services can be deployed as containers using the provided `Dockerfile` and `docker-compose.yaml`.

1.  Build: `docker build -t cloudmesh-ai-openapi .`
2.  Run: `docker-compose up -d`

### AI-Powered Testing

* `openapi test generate [FUNCTION] --filename=FILENAME --yamlfile=YAML`
  Generates a `pytest` suite by analyzing both the Python implementation and the OpenAPI spec. Tests are saved to `tests/ai-generated/`.

### AI Service Registry

When a server starts, the system detects if it was AI-generated (via `config.yaml`) and registers `ai_generated` and `ai_model` metadata in the registry for discovery.

## Development & Build

The project uses a `Makefile` to automate common development tasks.

### Build and Test
- `make install`: Install the package in editable mode for local development.
- `make test`: Run the pytest suite.
- `make test-html`: Run tests and generate an HTML report.
- `make test-cov`: Run tests with coverage analysis.
- `make clean`: Remove build artifacts and temporary files.

### Documentation Pipeline
- `make doc`: Generate the full Sphinx documentation suite, including conversion of Markdown files to RST.
- `make view`: Open the generated documentation in the default web browser.
- `make doc-publish`: Generate documentation and push it to the `gh-pages` branch of the repository. This target automatically handles the `.nojekyll` configuration to ensure correct rendering on GitHub Pages.

### Release Process
- `make build`: Create sdist and wheel distributions.
- `make check`: Validate distribution metadata using twine.
- `make tag`: Create and push a git tag based on the `VERSION` file.
- `make release`: Perform the full production cycle (upload and tag).