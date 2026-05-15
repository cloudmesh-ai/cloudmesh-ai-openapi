# Cloudmesh AI OpenAPI

Cloudmesh AI OpenAPI is a framework that enables the automatic generation of OpenAPI 3.0 specifications directly from Python source code. It implements a "Code-to-Spec" architecture, where Python functions, type hints, and docstrings serve as the single source of truth for the API definition.

Once a specification is generated, the framework provides a built-in server manager to deploy these APIs instantly using Connexion and FastAPI.

## Key Features

### Automatic Specification Generation
Convert Python functions into valid OpenAPI 3.0 YAML files without manual YAML authoring. The generator analyzes the function signature and docstrings to build the API structure.

### Rich Type Support
- **Typing Generics**: Full support for `Optional`, `Union`, `List`, and `Dict` from the `typing` module.
- **Complex Objects**: Use Python `@dataclasses` to define complex request and response bodies, which are automatically mapped to OpenAPI components/schemas.

### Flexible HTTP Method Mapping
- **Automatic Detection**: Functions starting with `post_`, `put_`, or `delete_` are automatically mapped to the corresponding HTTP method.
- **Explicit Control**: Use the `@openapi_method("METHOD")` decorator to override the default method.
- **Default Behavior**: Any function without a specific prefix or decorator defaults to a `GET` request.

### RESTful Path Parameters
Use the `@openapi_path_param("param_name")` decorator to mark specific function arguments as path parameters. The generator will automatically transform the endpoint path (e.g., `/my_function` becomes `/my_function/{param_name}`).

### Integrated Server Management
A built-in server manager handles the lifecycle of the generated APIs:
- **FastAPI Backend**: High-performance execution via Connexion and FastAPI.
- **Background Execution**: Ability to run servers in the background with PID tracking.
- **Service Registry**: A centralized registry to track and manage multiple running OpenAPI services.

## Installation

Ensure you have the required dependencies installed:

```bash
pip install PyYAML openapi-spec-validator connexion fastapi uvicorn click docstring-parser
```

## Developer Guide

### Writing Compatible Functions

To ensure the generator creates a correct specification, follow these standards:

1. **Type Hints**: Every parameter and the return value must have a type hint.
2. **Docstrings**: Use Google-style docstrings with a summary, `Args:`, and `Returns:` section.
3. **Dataclasses**: Define complex input/output objects as dataclasses.

### Example Implementation

#### Simple Example
This example demonstrates a basic function that defaults to a `GET` request without using any decorators.

```python
from cloudmesh.ai.common.io import Console

def add_numbers(a: int, b: int) -> int:
    """
    Adds two integers together.

    Args:
        a (int): The first number.
        b (int): The second number.

    Returns:
        int: The sum of the two numbers.
    """
    Console.info(f"Adding {a} and {b}")
    return a + b
```

#### Example with Dataclass
This example demonstrates the use of decorators for explicit method and path parameter definition, as well as a dataclass for a structured response.

```python
from dataclasses import dataclass
from typing import Optional
from cloudmesh.ai.openapi.function.generator import openapi_method, openapi_path_param
from cloudmesh.ai.common.io import Console

@dataclass
class UserProfile:
    username: str
    email: str
    age: Optional[int] = None

@openapi_method("GET")
@openapi_path_param("user_id")
def get_user_profile(user_id: str, detail_level: str = "basic") -> UserProfile:
    """
    Retrieves a user profile by ID.

    Args:
        user_id (str): The unique identifier of the user.
        detail_level (str): Level of detail to return.

    Returns:
        UserProfile: The profile information of the user.
    """
    Console.info(f"Fetching profile for {user_id}")
    return UserProfile(username="jdoe", email="jane@example.com")
```

## CLI Reference

The CLI is the primary interface for managing the OpenAPI lifecycle.

### Generating Specifications
```bash
cmc openapi generate --filename=my_api.py --serverurl=http://localhost:8080/api
```
- `--filename`: Path to the Python file.
- `--serverurl`: The base URL for the generated API.
- `--outdir`: Directory to save the resulting YAML.

### Managing Servers
- **Start a server**:
  ```bash
  cmc openapi start --spec=my_api.yaml --port=8080
  ```
- **Stop a server**:
  ```bash
  cmc openapi stop my_api
  ```
- **List running servers**:
  ```bash
  cmc openapi ps
  ```
- **List registered services**:
  ```bash
  cmc openapi list
  ```

## Architecture Flow

1. **Python Code**: Developer writes functions with type hints and docstrings.
2. **Generator**: The `Generator` class parses the code and produces an OpenAPI 3.0 YAML spec.
3. **Validation**: The spec is validated using `openapi-spec-validator`.
4. **Server**: The `Server` class uses `connexion` to map the YAML spec to the Python functions and starts a `uvicorn` server.

## AI Assistance

For developers using AI to generate compatible functions, please refer to:
- `README-ai.md`: Guide on AI-assisted development.
- `prompt-ai-function.md`: A ready-to-use prompt for AI models.