"""
Aiohttp client generator for OpenAPI Client Generator.

This module provides functionality for generating Python client code
using the aiohttp library.
"""

from pathlib import Path
from typing import Dict, Any, List

from .base import ClientGenerator
from ..parser.models import OpenAPISpec


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

        # Create models.py
        self._generate_models_file(spec, package_dir)

    def _generate_client_file(self, spec: OpenAPISpec, package_dir: Path) -> None:
        """
        Generate the client.py file.

        Args:
            spec: Parsed OpenAPI specification
            package_dir: Directory where the file will be written
        """
        # In a real implementation, this would use Jinja2 templates
        # For now, we'll just create a simple stub

        operations = spec.get_operations()

        with open(package_dir / "client.py", "w") as f:
            f.write('"""Generated API client using the aiohttp library."""\n\n')
            f.write("import aiohttp\n")
            f.write("from typing import Dict, List, Any, Optional, Union\n\n")
            f.write("from .models import *\n\n\n")

            f.write("class APIClient:\n")
            f.write('    """API client for interacting with the API."""\n\n')

            # Constructor
            f.write("    def __init__(self, base_url: str, auth_token: Optional[str] = None, timeout: int = 30):\n")
            f.write('        """Initialize the API client."""\n')
            f.write("        self.base_url = base_url.rstrip('/')\n")
            f.write("        self.auth_token = auth_token\n")
            f.write("        self.timeout = timeout\n")
            f.write("        self.session = None\n\n")

            # Create session method
            f.write("    async def _ensure_session(self):\n")
            f.write('        """Ensure that a session exists."""\n')
            f.write("        if self.session is None:\n")
            f.write("            self.session = aiohttp.ClientSession()\n")
            f.write("            if self.auth_token:\n")
            f.write("                self.session.headers.update({'Authorization': f'Bearer {self.auth_token}'})\n\n")

            # Close method
            f.write("    async def close(self):\n")
            f.write('        """Close the session."""\n')
            f.write("        if self.session is not None:\n")
            f.write("            await self.session.close()\n")
            f.write("            self.session = None\n\n")

            # Methods
            for operation in operations:
                operation_id = operation.get("operation_id", "")
                if not operation_id:
                    continue

                # Convert operationId to snake_case
                method_name = self._to_snake_case(operation_id)

                # Method signature
                f.write(f"    async def {method_name}(self, ")

                # Parameters
                params = []
                for param in operation.get("parameters", []):
                    param_name = self._to_snake_case(param.get("name", ""))
                    params.append(f"{param_name}: str")

                # Add body parameter if needed
                if operation.get("request_body"):
                    params.append("body: Dict[str, Any]")

                f.write(", ".join(params))
                f.write(") -> Any:\n")

                # Method docstring
                f.write(f'        """{operation.get("summary", "")}"""\n')
                f.write("        await self._ensure_session()\n")
                f.write("        # Implementation would go here\n")
                f.write("        pass\n\n")

    def _generate_models_file(self, spec: OpenAPISpec, package_dir: Path) -> None:
        """
        Generate the models.py file.

        Args:
            spec: Parsed OpenAPI specification
            package_dir: Directory where the file will be written
        """
        # In a real implementation, this would use Jinja2 templates
        # For now, we'll just create a simple stub

        with open(package_dir / "models.py", "w") as f:
            f.write('"""Generated models for the API."""\n\n')
            f.write("from typing import Dict, List, Any, Optional, Union\n")
            f.write("from pydantic import BaseModel, Field\n\n\n")

            # In a real implementation, we would generate models based on the schema
            f.write("# Models would be generated here based on the schema\n")

    def _to_snake_case(self, text: str) -> str:
        """
        Convert a string to snake_case.

        Args:
            text: String to convert

        Returns:
            str: Converted string
        """
        import re

        # Replace non-alphanumeric characters with underscores
        s1 = re.sub(r'[^a-zA-Z0-9]', '_', text)

        # Insert underscores between camelCase
        s2 = re.sub(r'([a-z0-9])([A-Z])', r'\1_\2', s1)

        # Convert to lowercase
        return s2.lower()
