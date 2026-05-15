class OpenApiError(Exception):
    """Base exception for all Cloudmesh AI OpenAPI errors."""
    pass

class OpenApiGeneratorError(OpenApiError):
    """Raised when there is an error during the generation of the OpenAPI specification."""
    pass

class OpenApiValidationError(OpenApiError):
    """Raised when the generated OpenAPI specification fails validation."""
    pass

class OpenApiServerError(OpenApiError):
    """Raised when there is an error starting or managing the OpenAPI server."""
    pass

class OpenApiRegistryError(OpenApiError):
    """Raised when there is an error interacting with the server registry."""
    pass