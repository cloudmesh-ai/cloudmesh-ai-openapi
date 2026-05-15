import click
import importlib.util
import os
import sys
from typing import List, Optional

from cloudmesh.ai.common.io import Console
from cloudmesh.ai.openapi.function.generator import Generator
from cloudmesh.ai.openapi.function.server import Server
from cloudmesh.ai.openapi.exceptions import OpenApiError

@click.group()
def openapi():
    """Cloudmesh AI OpenAPI CLI: Generate and manage OpenAPI servers from Python code."""
    pass

@openapi.command()
@click.option('--filename', required=True, help='Path to the Python file containing functions/classes.')
@click.option('--function', help='Specific function to generate. If omitted, all functions are processed.')
@click.option('--serverurl', default='http://localhost:8080/cloudmesh', help='Server URL for the OpenAPI spec.')
@click.option('--outdir', help='Output directory for the YAML file.')
@click.option('--yamlfile', help='Specific output YAML file path.')
@click.option('--all_functions', is_flag=True, default=False, help='Generate specs for all functions in the file.')
@click.option('--enable_upload', is_flag=True, default=False, help='Enable file upload endpoint.')
@click.option('--basic_auth', is_flag=True, default=False, help='Enable basic authentication.')
@click.option('--openapi_version', default='3.0.0', help='OpenAPI version (e.g., 3.0.0).')
@click.option('--api_version', default='1.0', help='API version.')
def generate(filename, function, serverurl, outdir, yamlfile, all_functions, enable_upload, basic_auth, openapi_version, api_version):
    """Generate an OpenAPI specification from a Python file."""
    try:
        # Load the module dynamically
        module_name = os.path.basename(filename).split('.')[0]
        spec = importlib.util.spec_from_file_location(module_name, filename)
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)

        generator = Generator()
        
        if function:
            # Generate for a single function
            func_obj = getattr(module, function)
            generator.generate_openapi(
                f=func_obj,
                filename=filename,
                serverurl=serverurl,
                outdir=outdir,
                yamlfile=yamlfile,
                enable_upload=enable_upload,
                basic_auth_enabled=basic_auth,
                openapi_version=openapi_version,
                api_version=api_version
            )
            Console.ok(f"Generated OpenAPI spec for function {function}")
        else:
            # Generate for all functions in the module
            func_objects = {name: obj for name, obj in vars(module).items() if callable(obj) and not name.startswith('_')}
            # Find dataclasses in the module
            from dataclasses import is_dataclass
            dataclass_list = [obj for obj in vars(module).values() if isinstance(obj, type) and is_dataclass(obj)]
            
            generator.generate_openapi_class(
                class_name=module_name,
                filename=filename,
                func_objects=func_objects,
                serverurl=serverurl,
                outdir=outdir,
                yamlfile=yamlfile,
                dataclass_list=dataclass_list,
                all_function=all_functions,
                enable_upload=enable_upload,
                basic_auth_enabled=basic_auth,
                openapi_version=openapi_version,
                api_version=api_version
            )
            Console.ok(f"Generated OpenAPI spec for module {module_name}")

    except OpenApiError as e:
        Console.error(f"Generation failed: {e}")
    except Exception as e:
        Console.error(f"An unexpected error occurred: {e}")

@openapi.command()
@click.option('--name', help='Server name.')
@click.option('--spec', required=True, help='Path to the OpenAPI spec YAML file.')
@click.option('--host', default='127.0.0.1', help='Host IP or DNS name.')
@click.option('--port', type=int, default=8080, help='Port to use for the service.')
@click.option('--debug', is_flag=True, default=True, help='Enable debug logging.')
@click.option('--foreground', is_flag=True, default=False, help='Run server in foreground.')
def start(name, spec, host, port, debug, foreground):
    """Start an OpenAPI server."""
    try:
        server = Server(name=name, spec=spec, host=host, port=port, debug=debug)
        pid = server.start(name=name, spec=spec, foreground=foreground)
        if pid:
            Console.ok(f"Server started with PID: {pid}")
        elif foreground:
            Console.ok("Server running in foreground")
    except OpenApiError as e:
        Console.error(f"Failed to start server: {e}")

@openapi.command()
@click.argument('name')
def stop(name):
    """Stop a running OpenAPI server by name."""
    try:
        Server.stop(name=name)
        Console.ok(f"Server {name} stopped.")
    except OpenApiError as e:
        Console.error(f"Failed to stop server: {e}")

@openapi.command()
@click.option('--name', help='Filter by server name.')
def ps(name):
    """List all actively running OpenAPI servers."""
    servers = Server.ps(name=name)
    if not servers:
        Console.info("No running servers found.")
        return
    
    Console.info(f"{'Name':<20} {'PID':<10} {'Spec':<40}")
    Console.info("-" * 70)
    for s in servers:
        Console.info(f"{s['name']:<20} {s['pid']:<10} {s['spec']:<40}")

@openapi.command()
@click.option('--name', help='Filter by server name.')
def list(name):
    """List servers registered in the Registry."""
    servers = Server.list(name=name)
    if not servers:
        Console.info("No registered servers found.")
        return
    
    for s in servers:
        Console.info(s)

def main():
    """Main entry point for the OpenAPI CLI."""
    openapi()

if __name__ == "__main__":
    main()