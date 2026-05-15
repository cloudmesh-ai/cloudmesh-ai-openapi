import yaml
import os
from pathlib import Path
from typing import List, Dict, Any, Optional
from cloudmesh.ai.common.io import Console

class OpenAPIMarkdown:
    """Generates human-readable documentation from OpenAPI specifications."""
    def __init__(self):
        """Initializes the OpenAPIMarkdown object."""
        self.output = []

    def _indent(self, text: str, indent: int) -> str:
        """Indents a string by a specified number of levels.

        Args:
            text (str): The text to indent.
            indent (int): The number of indentation levels (2 spaces each).

        Returns:
            str: The indented text.
        """
        return "  " * indent + text

    def title(self, filename: str, indent: int = 0):
        """Extracts and appends the title, version, and description from the OpenAPI spec.

        Args:
            filename (str): Path to the OpenAPI YAML file.
            indent (int): Indentation level. Defaults to 0.
        """
        with open(filename, "r") as f:
            spec = yaml.safe_load(f)
        
        info = spec.get("info", {})
        title = info.get("title", "OpenAPI Service")
        version = info.get("version", "1.0.0")
        description = info.get("description", "No description provided.")
        
        self.output.append(self._indent(f"# {title} (v{version})", indent))
        self.output.append(self._indent(description, indent))
        self.output.append("\n")

    def convert_definitions(self, filename: str, indent: int = 0):
        """Converts OpenAPI schema definitions into a Markdown list.

        Args:
            filename (str): Path to the OpenAPI YAML file.
            indent (int): Indentation level. Defaults to 0.
        """
        with open(filename, "r") as f:
            spec = yaml.safe_load(f)
        
        components = spec.get("components", {})
        schemas = components.get("schemas", {})
        
        if not schemas:
            return

        self.output.append(self._indent("## Data Models", indent))
        for name, schema in schemas.items():
            self.output.append(self._indent(f"### {name}", indent + 1))
            properties = schema.get("properties", {})
            for prop, details in properties.items():
                ptype = details.get("type", "unknown")
                self.output.append(self._indent(f"- {prop} ({ptype})", indent + 2))
            self.output.append("")

    def convert_paths(self, filename: str, indent: int = 0):
        """Converts OpenAPI paths and methods into a Markdown list.

        Args:
            filename (str): Path to the OpenAPI YAML file.
            indent (int): Indentation level. Defaults to 0.
        """
        with open(filename, "r") as f:
            spec = yaml.safe_load(f)
        
        paths = spec.get("paths", {})
        if not paths:
            return

        self.output.append(self._indent("## API Endpoints", indent))
        for path, methods in paths.items():
            self.output.append(self._indent(f"### {path}", indent + 1))
            for method, details in methods.items():
                if method.lower() in ["get", "post", "put", "delete", "patch"]:
                    summary = details.get("summary", "No summary")
                    self.output.append(self._indent(f"- **{method.upper()}**: {summary}", indent + 2))
            self.output.append("")

    def get_text(self) -> str:
        """Returns the accumulated Markdown text.

        Returns:
            str: The complete Markdown documentation.
        """
        return "\n".join(self.output)

class Manager:
    """Manages OpenAPI specifications, including merging and documentation."""
    def __init__(self, debug: bool = False):
        """Initializes the Manager.

        Args:
            debug (bool): Flag to enable debug logging. Defaults to False.
        """
        self.debug = debug

    def merge(self, directory: str, services: List[str]) -> Dict[str, Any]:
        """Merges multiple OpenAPI specifications into one.

        Args:
            directory (str): Directory containing the OpenAPI YAML files.
            services (List[str]): List of service names (filenames without extension).

        Returns:
            Dict[str, Any]: The merged OpenAPI specification as a dictionary.
        """
        merged_spec = {
            "openapi": "3.0.0",
            "info": {"title": "Merged AI Services", "version": "1.0.0"},
            "paths": {},
            "components": {"schemas": {}}
        }

        for service in services:
            spec_path = Path(directory) / f"{service}.yaml"
            if not spec_path.exists():
                Console.error(f"Specification file {spec_path} not found")
                continue
            
            with open(spec_path, "r") as f:
                try:
                    spec = yaml.safe_load(f)
                    if not spec:
                        continue
                    
                    # Merge paths
                    paths = spec.get("paths", {})
                    merged_spec["paths"].update(paths)
                    
                    # Merge components/schemas
                    components = spec.get("components", {})
                    schemas = components.get("schemas", {})
                    merged_spec["components"]["schemas"].update(schemas)
                except yaml.YAMLError as e:
                    Console.error(f"Error parsing {spec_path}: {e}")

        return merged_spec

    def description(self, directory: str, services: List[str]) -> str:
        """Generates a combined description for multiple services.

        Args:
            directory (str): Directory containing the OpenAPI YAML files.
            services (List[str]): List of service names.

        Returns:
            str: The combined Markdown description.
        """
        full_doc = []
        for service in services:
            spec_path = Path(directory) / f"{service}.yaml"
            if spec_path.exists():
                converter = OpenAPIMarkdown()
                converter.title(str(spec_path))
                converter.convert_paths(str(spec_path), indent=1)
                full_doc.append(converter.get_text())
        
        return "\n\n---\n\n".join(full_doc)

    def codegen(self, services: List[str], directory: str):
        """Placeholder for codegen functionality.

        Args:
            services (List[str]): List of services to generate code for.
            directory (str): Directory containing the specifications.
        """
        Console.info(f"Codegen requested for services: {services} in {directory}")
        # Implementation would go here