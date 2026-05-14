# Cloudmesh AI OpenAPI Manual

## Usage

```
openapi generate [FUNCTION] --filename=FILENAME
                                 [--serverurl=SERVERURL]
                                 [--yamlfile=YAML]
                                 [--import_class]
                                 [--all_functions]
                                 [--enable_upload]
                                 [--ai]
                                 [--verbose]
                                 [--basic_auth=CREDENTIALS]
openapi server start YAML [NAME]
                    [--directory=DIRECTORY]
                    [--port=PORT]
                    [--server=SERVER]
                    [--host=HOST]
                    [--verbose]
                    [--debug]
                    [--fg]
                    [--os]
openapi server stop NAME
openapi server list [NAME] [--output=OUTPUT]
openapi server ps [NAME] [--output=OUTPUT]
openapi register add NAME ENDPOINT
openapi register filename NAME
openapi register delete NAME
openapi register list [NAME] [--output=OUTPUT]
openapi register protocol PROTOCOL
openapi test generate [FUNCTION] --filename=FILENAME --yamlfile=YAML
openapi TODO merge [SERVICES...] [--dir=DIR] [--verbose]
openapi TODO doc FILE --format=(txt|md)[--indent=INDENT]
openapi TODO doc [SERVICES...] [--dir=DIR]
openapi sklearn FUNCTION MODELTAG
openapi sklearnreadfile FUNCTION MODELTAG
openapi sklearn upload --filename=FILENAME
```

## Arguments

- **FUNCTION**: The name for the function or class
- **MODELTAG**: The arbirtary name choosen by the user to store the Sklearn trained model as Pickle object
- **FILENAME**: Path to python file containing the function or class
- **SERVERURL**: OpenAPI server URL Default: https://localhost:8080/cloudmesh
- **YAML**: Path to yaml file that will contain OpenAPI spec. Default: FILENAME with .py replaced by .yaml
- **DIR**: The directory of the specifications
- **FILE**: The specification

## Options

- `--import_class`: FUNCTION is a required class name instead of an optional function name
- `--all_functions`: Generate OpenAPI spec for all functions in FILENAME
- `--debug`: Use the server in debug mode
- `--verbose`: Specifies to run in debug mode [default: False]
- `--port=PORT`: The port for the server [default: 8080]
- `--directory=DIRECTORY`: The directory in which the server is run
- `--server=SERVER`: The server [default: flask]
- `--output=OUTPUT`: The outputformat, table, csv, yaml, json [default: table]
- `--ai`: Use AI to generate the OpenAPI specification
- `--srcdir=SRCDIR`: The directory of the specifications
- `--destdir=DESTDIR`: The directory where the generated code is placed

## Description

This command does some useful things.

### Documentation Generation
`openapi TODO doc FILE --format=(txt|md|rst) [--indent=INDENT]`
Sometimes it is useful to generate the openapi documentation in another format. We provide functionality to generate the documentation from the yaml file in a different format.

`openapi TODO doc --format=(txt|md|rst) [SERVICES...]`
Creates a short documentation from services registered in the registry.

### Service Merging
`openapi TODO merge [SERVICES...] [--dir=DIR] [--verbose]`
Merges two service specifications into a single service.

### Sklearn Integration
`openapi sklearn sklearn.linear_model.LogisticRegression`
Generates the .py file for the Model given for the generator.

`openapi sklearnreadfile sklearn.linear_model.LogisticRegression`
Generates the .py file for the Model given for the generator which supports reading files.

### OpenAPI Generation
`openapi generate [FUNCTION] --filename=FILENAME [--serverurl=SERVERURL] [--yamlfile=YAML] [--import_class] [--all_functions] [--enable_upload] [--ai] [--verbose] [--basic_auth=CREDENTIALS]`
Generates an OpenAPI specification for FUNCTION in FILENAME and writes the result to YAML. Use `--import_class` to import a class with its associated class methods, or use `--all_functions` to import all functions in FILENAME. These options ignore functions whose names start with '_'. Use `--enable_upload` to add file upload functionality to a copy of your python file and the resulting yaml file.

Use the `--ai` flag to leverage LLMs to generate the specification based on the code analysis.

For optional basic authorization, we support (temporarily) a single user credential. CREDENTIALS should be formatted as `user:password`. Example: `--basic_auth=admin:secret`.

### Server Management
`openapi server start YAML [NAME] [--directory=DIRECTORY] [--port=PORT] [--server=SERVER] [--host=HOST] [--verbose] [--debug] [--fg] [--os]`
Starts an openapi web service using YAML as a specification.

`openapi server stop NAME`
Stops the openapi service with the given name.

`openapi server list [NAME] [--output=OUTPUT]`
Provides a list of all OpenAPI services in the registry.

`openapi server ps [NAME] [--output=OUTPUT]`
List the running openapi service.

### Registry Management
`openapi register add NAME ENDPOINT`
Openapi comes with a service registry in which we can register openapi services.

`openapi register filename NAME`
In case you have a yaml file the openapi service can also be registered from a yaml file.

`openapi register delete NAME`
Deletes the named service from the registry.

`openapi register list [NAME] [--output=OUTPUT]`
Provides a list of all registered OpenAPI services.

### AI-Powered Testing
`openapi test generate [FUNCTION] --filename=FILENAME --yamlfile=YAML`
Generates a `pytest` suite for the specified function by analyzing both the Python implementation and the OpenAPI specification using AI. The tests are written to `tests/ai-generated/`.

### AI Service Registry
When starting a server using `openapi server start`, the system automatically detects if the service was AI-generated (via `config.yaml`) and adds `ai_generated` and `ai_model` metadata to the registry entry for better discovery in the AI-CMC.
