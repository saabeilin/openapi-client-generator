"""
Aiohttp client generator for OpenAPI Client Generator.

This module provides functionality for generating Python client code
using the aiohttp library.
"""

from pathlib import Path
from typing import Dict, Any, List

from .base import ClientGenerator
from ..parser.models import OpenAPISpec
from ..helpers import to_snake_case


class AiohttpClientGenerator(ClientGenerator):
    """
    Client generator for the aiohttp library.

    This class generates asynchronous client code using the aiohttp library.
    """

    def _generate_client(self, spec: OpenAPISpec) -> None:
        """
        Generate client code from an OpenAPI specification.

        Args:
            spec: Parsed OpenAPI specification
        """
        # Create package directory
        package_dir = self.output_dir / self.package_name
        package_dir.mkdir(exist_ok=True)

        # Create __init__.py
        with open(package_dir / "__init__.py", "w") as f:
            f.write(f'"""Generated client for {spec.info.title}."""\n\n')
            f.write("from .client import APIClient\n\n")
            f.write('__all__ = ["APIClient"]\n')

        # Create client.py
        self._generate_client_file(spec, package_dir)

        # Create models.py if generate_models is True
        if self.generate_models:
            self._generate_models_file(spec, package_dir)

    def _generate_client_file(self, spec: OpenAPISpec, package_dir: Path) -> None:
        """
        Generate the client.py file.

        Args:
            spec: Parsed OpenAPI specification
            package_dir: Directory where the file will be written
        """
        # Use the Jinja2 template for generating the client file
        template = self.template_env.get_template("aiohttp/client.py.jinja2")
        operations = spec.get_operations()

        # Process operations to ensure parameters are in the correct format for the template
        for operation in operations:
            processed_params = []
            param_name_mapping = {}  # Map original parameter names to snake_case names

            for param in operation.get("parameters", []):
                if hasattr(param, "get_python_name") and hasattr(param, "get_python_type_hint"):
                    # Parameter is a Parameter object
                    original_name = param.name
                    python_name = param.get_python_name()
                    param_name_mapping[original_name] = python_name

                    processed_params.append({
                        "name": python_name,
                        "type_hint": param.get_python_type_hint(),
                        "description": param.description or ""
                    })
                elif isinstance(param, dict) and "name" in param:
                    # Parameter is already a dictionary
                    original_name = param.get("name", "")
                    python_name = to_snake_case(original_name)
                    param_name_mapping[original_name] = python_name

                    processed_params.append({
                        "name": python_name,
                        "type_hint": "str",  # Default to str if type is not specified
                        "description": param.get("description", "")
                    })

            operation["parameters"] = processed_params

            # Update path_template to use snake_case parameter names
            path_template = operation.get("path_template", "")
            for original_name, python_name in param_name_mapping.items():
                path_template = path_template.replace(f"{{{original_name}}}", f"{{{python_name}}}")
            operation["path_template"] = path_template

            # Process request body if it exists
            if operation.get("request_body"):
                # If request_body is a Reference or RequestBody object, extract the description and type
                request_body = operation["request_body"]
                description = ""
                if hasattr(request_body, "description"):
                    description = request_body.description or ""
                elif isinstance(request_body, dict) and "description" in request_body:
                    description = request_body["description"] or ""

                # Get the request body type from the operation dictionary
                request_body_type = "Dict[str, Any]"
                if "request_body_type" in operation and operation["request_body_type"]:
                    request_body_type = operation["request_body_type"]

                # Set the request_body to a dictionary with description and type_hint
                operation["request_body"] = {
                    "description": description,
                    "type_hint": request_body_type
                }

        # Render the client template
        content = template.render(operations=operations)

        # Write the rendered template to the client.py file
        with open(package_dir / "client.py", "w") as f:
            f.write(content)
