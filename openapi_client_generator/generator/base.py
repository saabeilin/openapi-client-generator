"""
Base generator for OpenAPI Client Generator.

This module provides the base class for client generators.
"""

import os
from abc import ABC, abstractmethod
from pathlib import Path
from typing import Dict, Any, List, Optional

from jinja2 import Environment, FileSystemLoader

from ..parser.models import OpenAPISpec


class ClientGenerator(ABC):
    """
    Base class for client generators.

    This class provides common functionality for generating client code
    from OpenAPI specifications.
    """

    def __init__(self, output_dir: str, package_name: Optional[str] = None):
        """
        Initialize the client generator.

        Args:
            output_dir: Directory where the generated code will be written
            package_name: Name of the generated package (default: derived from API title)
        """
        self.output_dir = Path(output_dir)
        self.package_name = package_name
        self.template_env = None

    def generate(self, spec: OpenAPISpec) -> None:
        """
        Generate client code from an OpenAPI specification.

        Args:
            spec: Parsed OpenAPI specification
        """
        # Create output directory if it doesn't exist
        os.makedirs(self.output_dir, exist_ok=True)

        # Determine package name if not provided
        if not self.package_name:
            self.package_name = self._derive_package_name(spec)

        # Initialize template environment
        self._init_template_env()

        # Generate client code
        self._generate_client(spec)

    def _derive_package_name(self, spec: OpenAPISpec) -> str:
        """
        Derive package name from API title.

        Args:
            spec: Parsed OpenAPI specification

        Returns:
            str: Derived package name
        """
        # Get API title from spec
        title = spec.info.title

        # Convert to snake_case
        package_name = title.lower().replace(" ", "_").replace("-", "_")

        return package_name

    def _init_template_env(self) -> None:
        """Initialize the Jinja2 template environment."""
        # Get the path to the templates directory
        templates_dir = Path(__file__).parent.parent / "templates"

        # Create Jinja2 environment
        self.template_env = Environment(
            loader=FileSystemLoader(templates_dir),
            trim_blocks=True,
            lstrip_blocks=True,
        )

    @abstractmethod
    def _generate_client(self, spec: OpenAPISpec) -> None:
        """
        Generate client code from an OpenAPI specification.

        This method should be implemented by subclasses to generate
        client code for specific HTTP libraries.

        Args:
            spec: Parsed OpenAPI specification
        """
        pass
