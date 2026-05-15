import pathlib
import textwrap
import re
from dataclasses import is_dataclass
from typing import Any, Dict, List, Optional, Union, get_origin, get_args

import requests
import yaml
from openapi_spec_validator import validate_spec
from cloudmesh.ai.common.io import Console
from cloudmesh.ai.common.debug import VERBOSE
from docstring_parser import parse

from cloudmesh.ai.openapi.exceptions import OpenApiGeneratorError, OpenApiValidationError

def openapi_method(method: str):
    """Decorator to explicitly set the HTTP method for an OpenAPI endpoint."""
    def decorator(func):
        func._openapi_method = method.upper()
        return func
    return decorator

def openapi_path_param(param_name: str):
    """Decorator to mark a parameter as a path parameter."""
    def decorator(func):
        if not hasattr(func, '_openapi_path_params'):
            func._openapi_path_params = []
        func._openapi_path_params.append(param_name)
        return func
    return decorator

class Generator:
    """Generates OpenAPI specifications from Python functions and dataclasses."""

    def __init__(self):
        # Mapping of basic Python types to OpenAPI types
        self.type_map = {
            'int': 'integer',
            'bool': 'boolean',
            'float': 'number',
            'str': 'string',
            'list': 'array',
            'array': 'array',
            'dict': 'object',
            'object': 'object'
        }

    def parse_type(self, _type: Any) -> Dict[str, Any]:
        """
        Look up and output supported OpenApi data type using python data type as input.
        Handles basic types and typing generics.
        """
        if _type is None:
            return {"type": "string"}

        # Handle string representation of types
        if isinstance(_type, str):
            t_name = _type
        else:
            t_name = getattr(_type, '__name__', str(_type))

        # Handle Dataclasses
        if is_dataclass(_type):
            return {"$ref": f"#/components/schemas/{_type.__name__}"}

        # Handle typing generics (Optional, List, Dict, Union)
        origin = get_origin(_type)
        if origin is not None:
            args = get_args(_type)
            if origin is Union:
                # Handle Optional[T] which is Union[T, NoneType]
                non_none_args = [a for a in args if a is not type(None)]
                if len(non_none_args) == 1:
                    return self.parse_type(non_none_args[0])
                return {"anyOf": [self.parse_type(a) for a in non_none_args]}
            
            if origin is list or origin is List:
                item_type = args[0] if args else str
                return {
                    "type": "array",
                    "items": self.parse_type(item_type)
                }
            
            if origin is dict or origin is Dict:
                val_type = args[1] if len(args) > 1 else Any
                return {
                    "type": "object",
                    "additionalProperties": self.parse_type(val_type)
                }

        # Handle basic types
        # Normalize type name (e.g., 'int' from <class 'int'>)
        normalized_name = t_name.lower() if isinstance(t_name, str) else str(t_name).lower()
        
        # Try to find in map
        for key, val in self.type_map.items():
            if key in normalized_name:
                return {"type": val}

        Console.info(f"Unsupported data type supplied: {_type}, defaulting to string")
        return {"type": "string"}

    def generate_parameter(self, name: str, _type: Any, description: str, location: str = "query") -> Dict[str, Any]:
        """Generate a single OpenApi parameter object."""
        return {
            "name": name.strip(),
            "in": location,
            "description": description.strip() if description else "No description provided",
            "required": True if location == "path" else False,
            "schema": self.parse_type(_type)
        }

    def generate_response(self, code: str, _type: Any, description: str) -> Dict[str, Any]:
        """Generate a single OpenApi response object."""
        response = {"description": description.strip() if description else "OK"}
        
        if _type == "No Response" or _type is None:
            return response

        schema = self.parse_type(_type)
        content_type = "application/json" if schema.get("type") == "object" or "$ref" in schema else "text/plain"
        
        response["content"] = {
            content_type: {
                "schema": schema
            }
        }
        return response

    def generate_request_body(self, _type: Any) -> Dict[str, Any]:
        """Generate an OpenAPI request body object for a dataclass."""
        return {
            "content": {
                "application/json": {
                    "schema": self.parse_type(_type)
                }
            }
        }

    def generate_schema(self, _class: type) -> Dict[str, Any]:
        """Generate an OpenAPI schema from a Python dataclass."""
        if not is_dataclass(_class):
            raise OpenApiGeneratorError(f'{_class.__name__} is not a dataclass.')

        properties = {}
        for attr, _type in _class.__annotations__.items():
            properties[attr] = self.parse_type(_type)

        return {
            "type": "object",
            "properties": properties
        }

    def populate_parameters(self, func_obj: callable) -> tuple[List[Dict[str, Any]], Optional[Any]]:
        """
        Convert Python function parameters into OpenAPI parameters list.
        Returns a tuple of (parameters, request_body_type).
        """
        params = []
        request_body_type = None
        docstring = parse(func_obj.__doc__) if func_obj.__doc__ else None
        
        # Get annotations
        annotations = func_obj.__annotations__
        
        # Get path parameters from decorator
        path_params = getattr(func_obj, '_openapi_path_params', [])
        
        # Get parameters from function signature
        import inspect
        sig = inspect.signature(func_obj)
        param_names = list(sig.parameters.keys())
        
        if param_names:
            first_param = param_names[0]
            first_type = annotations.get(first_param)
            if first_type and is_dataclass(first_type):
                request_body_type = first_type
                # Skip this parameter in the parameters list
                start_idx = 1
            else:
                start_idx = 0
        else:
            start_idx = 0

        for i in range(start_idx, len(param_names)):
            parameter = param_names[i]
            _type = annotations.get(parameter, Any)
            
            description = None
            if docstring:
                for p in docstring.params:
                    if p.arg_name == parameter:
                        description = p.description
                        break
            
            # Determine location: path or query
            location = "path" if parameter in path_params else "query"
            
            params.append(self.generate_parameter(parameter, _type, description, location))
        
        return params, request_body_type

    def get_http_method(self, func_obj: callable) -> str:
        """Determine the HTTP method for a function."""
        # 1. Check for explicit decorator
        if hasattr(func_obj, '_openapi_method'):
            return func_obj._openapi_method
        
        # 2. Check naming conventions
        name = func_obj.__name__.lower()
        if name.startswith('post_'):
            return 'post'
        if name.startswith('put_'):
            return 'put'
        if name.startswith('delete_'):
            return 'delete'
        
        # 3. Default to GET
        return 'get'

    def generate_openapi_class(self,
                               class_name: str = None,
                               class_description: str = None,
                               filename: str = None,
                               func_objects: Dict[str, Any] = None,
                               serverurl: str = None,
                               outdir: str = None,
                               yamlfile: str = None,
                               dataclass_list: List[type] = None,
                               all_function: bool = False,
                               enable_upload: bool = False,
                               basic_auth_enabled: bool = False,
                               write: bool = True,
                               openapi_version: str = "3.0.0",
                               api_version: str = "1.0"):
        """Generates the full OpenAPI specification for a python class or module."""
        
        filename_stem = pathlib.Path(filename).stem if filename else "api"
        description = class_description or "No description found"
        
        spec = {
            "openapi": openapi_version,
            "info": {
                "title": class_name or filename_stem,
                "description": description,
                "version": api_version
            },
            "servers": [
                {"url": serverurl, "description": description}
            ],
            "paths": {},
            "components": {"schemas": {}}
        }

        # Process functions
        for func_name, v in func_objects.items():
            if func_name == 'upload' and enable_upload:
                continue
            
            docstring = parse(v.__doc__) if v.__doc__ else None
            func_description = docstring.short_description if docstring else func_name
            func_ldescription = docstring.long_description if docstring and docstring.long_description else ""

            # Path construction
            # Check for path parameters to inject into the path key
            path_params = getattr(v, '_openapi_path_params', [])
            base_path = f"/{class_name}/{func_name}" if class_name else f"/{func_name}"
            
            # If there are path parameters, we append them to the path: /func/{param1}/{param2}
            if path_params:
                path_suffix = "".join([f"/{{{p}}}" for p in path_params])
                path_key = f"{base_path}{path_suffix}"
            else:
                path_key = base_path
            
            # Operation ID
            if all_function:
                op_id = f"{filename_stem}.{func_name}"
            else:
                op_id = f"{filename_stem}.{class_name}.{func_name}"

            # Method detection
            method = self.get_http_method(v)
            
            # Parameters and Request Body
            parameters, request_body_type = self.populate_parameters(v)
            
            if 'return' in v.__annotations__:
                responses = {"200": self.generate_response('200', v.__annotations__['return'], 'OK')}
            else:
                responses = {"204": self.generate_response('204', "No Response", 'This operation returns no response.')}

            operation = {
                "summary": func_description,
                "description": func_ldescription,
                "operationId": op_id,
                "parameters": parameters,
                "responses": responses
            }

            if request_body_type:
                operation["requestBody"] = self.generate_request_body(request_body_type)

            if path_key not in spec["paths"]:
                spec["paths"][path_key] = {}
            
            spec["paths"][path_key][method] = operation

        # Process Dataclasses
        if dataclass_list:
            for dc in dataclass_list:
                spec["components"]["schemas"][dc.__name__] = self.generate_schema(dc)

        # Handle Upload
        if enable_upload:
            spec["paths"]["/upload"] = {
                "post": {
                    "summary": "upload a file",
                    "operationId": f"{filename_stem}.upload",
                    "requestBody": {
                        "content": {
                            "multipart/form-data": {
                                "schema": {
                                    "type": "object",
                                    "properties": {
                                        "upload": {"type": "string", "format": "binary"}
                                    }
                                }
                            }
                        }
                    },
                    "responses": {
                        "200": {
                            "description": "OK",
                            "content": {"text/plain": {"schema": {"type": "string"}}}
                        }
                    }
                }
            }

        # Handle Basic Auth
        if basic_auth_enabled:
            spec["components"]["securitySchemes"] = {
                "basicAuth": {
                    "type": "http",
                    "scheme": "basic",
                    "x-basicInfoFunc": f"{filename_stem}.basic_auth"
                }
            }
            spec["security"] = [{"basicAuth": []}]

        # Validation
        try:
            validate_spec(spec)
            VERBOSE("OpenAPI specification validated successfully")
        except Exception as e:
            Console.error(f"OpenAPI validation failed: {e}")
            raise OpenApiValidationError(f"Generated spec is invalid: {e}")

        # Write to file
        if write:
            try:
                target_file = yamlfile if yamlfile else f"{outdir}/{class_name}.yaml"
                with open(target_file, 'w') as f:
                    yaml.dump(spec, f, sort_keys=False)
            except IOError as e:
                raise OpenApiGeneratorError(f"Unable to write yaml file: {e}")

        return spec

    def generate_openapi(self,
                        f=None,
                        filename=None,
                        serverurl=None,
                        outdir=None,
                        yamlfile=None,
                        dataclass_list=None,
                        enable_upload=False,
                        basic_auth_enabled=False,
                        write=True,
                        openapi_version: str = "3.0.0",
                        api_version: str = "1.0"):
        """Main entry point for a single function."""
        
        filename_stem = pathlib.Path(filename).stem if filename else "api"
        description = f.__doc__.strip().split("\n")[0] if f.__doc__ else "No description"
        
        # Wrap single function in a dummy dict to reuse generate_openapi_class
        func_objects = {f.__name__: f}
        
        return self.generate_openapi_class(
            class_name=f.__name__,
            class_description=description,
            filename=filename,
            func_objects=func_objects,
            serverurl=serverurl,
            outdir=outdir,
            yamlfile=yamlfile,
            dataclass_list=dataclass_list or [],
            enable_upload=enable_upload,
            basic_auth_enabled=basic_auth_enabled,
            write=write,
            openapi_version=openapi_version,
            api_version=api_version,
            all_function=True
        )