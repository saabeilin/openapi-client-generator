"""
Httpx client generator for OpenAPI Client Generator.

This module provides functionality for generating Python client code
using the httpx library.
"""

from pathlib import Path
from typing import Dict, Any, List

from .base import ClientGenerator
from ..parser.models import OpenAPISpec
from ..helpers import to_snake_case


class HttpxClientGenerator(ClientGenerator):
    """
    Client generator for the httpx library.

    This class generates client code using the httpx library,
    which supports both synchronous and asynchronous operation.
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
            f.write("from .client import APIClient, AsyncAPIClient\n\n")
            f.write('__all__ = ["APIClient", "AsyncAPIClient"]\n')

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
            f.write('"""Generated API client using the httpx library."""\n\n')
            f.write("import httpx\n")
            f.write("from typing import Dict, List, Any, Optional, Union\n\n")
            f.write("from .models import *\n\n\n")

            # Synchronous client
            f.write("class APIClient:\n")
            f.write('    """Synchronous API client for interacting with the API."""\n\n')

            # Constructor
            f.write("    def __init__(self, base_url: str, auth_token: Optional[str] = None, timeout: int = 30):\n")
            f.write('        """Initialize the API client."""\n')
            f.write("        self.base_url = base_url.rstrip('/')\n")
            f.write("        self.auth_token = auth_token\n")
            f.write("        self.timeout = timeout\n")
            f.write("        self.client = httpx.Client(timeout=timeout)\n")
            f.write("        if auth_token:\n")
            f.write("            self.client.headers.update({'Authorization': f'Bearer {auth_token}'})\n\n")

            # Close method
            f.write("    def close(self):\n")
            f.write('        """Close the client."""\n')
            f.write("        self.client.close()\n\n")

            # Context manager methods
            f.write("    def __enter__(self):\n")
            f.write('        """Enter context manager."""\n')
            f.write("        return self\n\n")

            f.write("    def __exit__(self, exc_type, exc_val, exc_tb):\n")
            f.write('        """Exit context manager."""\n')
            f.write("        self.close()\n\n")

            # Methods
            for operation in operations:
                operation_id = operation.get("operation_id", "")
                if not operation_id:
                    continue

                # Convert operationId to snake_case
                method_name = to_snake_case(operation_id)

                # Method signature
                f.write(f"    def {method_name}(self, ")

                # Parameters
                params = []
                for param in operation.get("parameters", []):
                    param_name = to_snake_case(param.get("name", ""))
                    params.append(f"{param_name}: str")

                # Add request_body parameter if needed
                if operation.get("request_body"):
                    params.append("request_body: Dict[str, Any]")

                f.write(", ".join(params))
                f.write(") -> Any:\n")

                # Method docstring
                f.write(f'        """{operation.get("summary", "")}"""\n')
                f.write("        # Implementation would go here\n")
                f.write("        pass\n\n")

            # Asynchronous client
            f.write("\n\nclass AsyncAPIClient:\n")
            f.write('    """Asynchronous API client for interacting with the API."""\n\n')

            # Constructor
            f.write("    def __init__(self, base_url: str, auth_token: Optional[str] = None, timeout: int = 30):\n")
            f.write('        """Initialize the API client."""\n')
            f.write("        self.base_url = base_url.rstrip('/')\n")
            f.write("        self.auth_token = auth_token\n")
            f.write("        self.timeout = timeout\n")
            f.write("        self.client = httpx.AsyncClient(timeout=timeout)\n")
            f.write("        if auth_token:\n")
            f.write("            self.client.headers.update({'Authorization': f'Bearer {auth_token}'})\n\n")

            # Close method
            f.write("    async def close(self):\n")
            f.write('        """Close the client."""\n')
            f.write("        await self.client.aclose()\n\n")

            # Context manager methods
            f.write("    async def __aenter__(self):\n")
            f.write('        """Enter async context manager."""\n')
            f.write("        return self\n\n")

            f.write("    async def __aexit__(self, exc_type, exc_val, exc_tb):\n")
            f.write('        """Exit async context manager."""\n')
            f.write("        await self.close()\n\n")

            # Methods
            for operation in operations:
                operation_id = operation.get("operation_id", "")
                if not operation_id:
                    continue

                # Convert operationId to snake_case
                method_name = to_snake_case(operation_id)

                # Method signature
                f.write(f"    async def {method_name}(self, ")

                # Parameters
                params = []
                for param in operation.get("parameters", []):
                    param_name = to_snake_case(param.get("name", ""))
                    params.append(f"{param_name}: str")

                # Add request_body parameter if needed
                if operation.get("request_body"):
                    params.append("request_body: Dict[str, Any]")

                f.write(", ".join(params))
                f.write(") -> Any:\n")

                # Method docstring
                f.write(f'        """{operation.get("summary", "")}"""\n')
                f.write("        # Implementation would go here\n")
                f.write("        pass\n\n")
