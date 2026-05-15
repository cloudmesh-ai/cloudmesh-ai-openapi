# Cloudmesh AI OpenAPI Service Generator

[![License](https://img.shields.io/badge/License-Apache%202.0-blue.svg)](https://github.com/cloudmesh-ai/cloudmesh-ai-openapi/blob/main/LICENSE)

Cloudmesh AI OpenAPI is a powerful tool for automatically generating OpenAPI specifications and deploying them as production-ready microservices. By leveraging Large Language Models (LLMs), it transforms Python code into fully functional REST APIs with minimal effort.

## Key Features

*   **AI-Powered Generation**: Uses LLMs to generate OpenAPI 3.0 specifications from Python functions or classes.
*   **Self-Correcting Pipeline**: Includes a validation loop that checks generated YAML against the OpenAPI schema and automatically retries the LLM for corrections.
*   **Few-Shot Learning**: Supports an `examples/` directory to provide the AI with patterns, significantly improving generation quality.
*   **Modern Server Stack**: Built on **FastAPI** and **Uvicorn** (via Connexion) for high-performance, asynchronous API execution.
*   **Enterprise Readiness**: 
    *   **Observability**: Built-in `/health` endpoints for monitoring.
    *   **Security**: Multi-user Basic Authentication with salted SHA256 password hashing.
    *   **Containerization**: Ready-to-use `Dockerfile` and `docker-compose.yaml` for cloud-native deployment.
*   **Management Tools**: Commands to merge multiple API specifications and generate human-readable documentation.

## Prerequisites

*   **Python 3.12 or newer** (Required)
*   **pip version 21.0 or newer**
*   A configured LLM endpoint (see `config.yaml` in the source)

## Installation

```bash
python -m venv ~/ENV3
source ~/ENV3/bin/activate
mkdir cm
cd cm
pip install cloudmesh-installer
cloudmesh-installer get openapi
cms help
cms init
```

## Quick Start

### 1. Generate an API using AI
Instead of manual specification, use the `--ai` flag to let the LLM analyze your code and generate the OpenAPI YAML.

```bash
cms openapi generate get_processor_name \
    --filename=./tests/server-cpu/cpu.py \
    --ai
```
This creates `cpu.yaml` based on the logic in `cpu.py`.

### 2. Start the Service
Start the generated microservice as a background process:

```bash
cms openapi server start ./tests/server-cpu/cpu.yaml
```

### 3. Test the API
The service defaults to port 8080. You can test the endpoint or the health check:

```bash
# Test the function
curl -X GET "http://localhost:8080/cloudmesh/get_processor_name"

# Test the health check
curl -X GET "http://localhost:8080/health"
```

### 4. Manage the Service
Check running services or stop them:

```bash
cms openapi server ps
cms openapi server stop cpu
```

## Advanced Usage

### Containerization
Deploy your generated services using Docker:

```bash
# Build the image
docker build -t cloudmesh-ai-openapi .

# Run using docker-compose
docker-compose up -d
```

### Merging and Documentation
Combine multiple services into one or generate a report:

```bash
# Merge multiple specs into one
cms openapi merge service1 service2 --dir=./specs

# Generate markdown documentation for a spec
cms openapi doc ./specs/cpu.yaml --format=md
```

## Development

The project includes a `Makefile` to streamline development, testing, and documentation.

### Common Tasks
- **Install for development**: `make install`
- **Run tests**: `make test`
- **Generate documentation**: `make doc`
- **Publish documentation to GitHub Pages**: `make doc-publish`
- **View local documentation**: `make view`

## Command Overview

Detailed usage for all commands is provided in the [Manual](manual.md) file.

| Command | Description |
| --- | --- |
| `openapi generate` | Generate OpenAPI spec from Python code (supports `--ai`) |
| `openapi server start` | Start a REST service from a YAML spec |
| `openapi server stop` | Stop a running service |
| `openapi server ps` | List running services and their PIDs |
| `openapi merge` | Merge multiple specifications into one |
| `openapi doc` | Generate human-readable documentation |
| `openapi register` | Manage the service registry |

## List of Tests

Detailed test cases are available in the `tests/` directory. See [README-tests.md](README-tests.md) for a full summary.

## Acknowledgments

Work conducted to integrate this work in research projects was funded by the NSF CyberTraining: CIC: CyberTraining for Students and Technologies from Generation Z with the award numbers 1829704 and 2200409.