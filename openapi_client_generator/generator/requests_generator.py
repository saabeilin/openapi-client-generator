"""
Requests client generator for OpenAPI Client Generator.

This module provides functionality for generating Python client code
using the requests library. It uses Jinja2 templates to generate the code,
which makes it more maintainable and easier to customize.

The generator uses the following templates:
- common/__init__.py.jinja2: Template for the package __init__.py file
- requests/client.py.jinja2: Template for the client.py file
- common/models.py.jinja2: Template for the models.py file

The templates are rendered with data from the OpenAPI specification,
and the resulting code is written to the output directory.
"""

from pathlib import Path
from typing import Dict, Any, List

from .base import ClientGenerator
from ..parser.models import OpenAPISpec
from ..helpers import to_snake_case


class RequestsClientGenerator(ClientGenerator):
    """
    Client generator for the requests library.

    This class generates synchronous client code using the requests library.
    """

    def _generate_client(self, spec: OpenAPISpec) -> None:
        """
        Generate client code from an OpenAPI specification.

        This method creates the package directory and generates the following files:
        - __init__.py: Package initialization file
        - client.py: API client implementation
        - models.py: Pydantic models for API schemas

        Each file is generated using a Jinja2 template, which is rendered with
        data from the OpenAPI specification.

        Args:
            spec: Parsed OpenAPI specification
        """
        # Create package directory
        package_dir = self.output_dir / self.package_name
        package_dir.mkdir(exist_ok=True)

        # Create __init__.py
        template = self.template_env.get_template("common/__init__.py.jinja2")
        content = template.render(api_title=spec.info.title, client_type='requests')
        with open(package_dir / "__init__.py", "w") as f:
            f.write(content)

        # Create client.py
        self._generate_client_file(spec, package_dir)

        # Create models.py if generate_models is True
        if self.generate_models:
            self._generate_models_file(spec, package_dir)

    def _generate_client_file(self, spec: OpenAPISpec, package_dir: Path) -> None:
        """
        Generate the client.py file.

        This method generates the API client implementation using a Jinja2 template.
        It processes the operations from the OpenAPI specification to ensure they
        are in the correct format for the template:

        1. Converts parameter objects to dictionaries with name, type_hint, and description
        2. Ensures parameter names are in snake_case format
        3. Updates path templates to use snake_case parameter names
        4. Processes request bodies to ensure they are in the correct format for the template

        The processed operations are then passed to the template for rendering.

        Args:
            spec: Parsed OpenAPI specification
            package_dir: Directory where the file will be written
        """
        # Get operations from the specification
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
        template = self.template_env.get_template("requests/client.py.jinja2")
        content = template.render(operations=operations)

        # Write the rendered template to the client.py file
        with open(package_dir / "client.py", "w") as f:
            f.write(content)
