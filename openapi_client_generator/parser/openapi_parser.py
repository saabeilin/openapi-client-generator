"""
OpenAPI Parser for the OpenAPI Client Generator.

This module provides functionality for parsing OpenAPI specifications.
"""

import json
import os
from pathlib import Path
from typing import Dict, Any, Union, Optional, List, Tuple, Set, cast
from urllib.parse import urljoin, urlparse

import yaml
from pydantic import ValidationError

from .models import (
    OpenAPISpec, Reference, Schema, Components, PathItem, Operation,
    Parameter, Response, RequestBody, MediaType
)


class OpenAPIParser:
    """
    Parser for OpenAPI specifications.

    This class is responsible for loading and parsing OpenAPI specifications
    from JSON or YAML files.
    """

    def __init__(self):
        """Initialize the OpenAPI parser."""
        self.base_url: Optional[str] = None
        self.resolved_refs: Set[str] = set()

    def parse(self, spec_path: Union[str, Path]) -> OpenAPISpec:
        """
        Parse an OpenAPI specification from a file.

        Args:
            spec_path: Path to the OpenAPI specification file (JSON or YAML)

        Returns:
            OpenAPISpec: Parsed OpenAPI specification

        Raises:
            FileNotFoundError: If the specification file does not exist
            ValueError: If the specification file is not valid JSON or YAML
            ValidationError: If the specification does not conform to the OpenAPI schema
        """
        spec_path = Path(spec_path)

        if not spec_path.exists():
            raise FileNotFoundError(f"Specification file not found: {spec_path}")

        # Set base URL for resolving references
        self.base_url = f"file://{spec_path.absolute()}"
        self.resolved_refs = set()

        # Load the specification file
        spec_dict = self._load_spec_file(spec_path)

        # Resolve references
        spec_dict = self._resolve_references(spec_dict)

        # Parse the specification
        try:
            return OpenAPISpec.model_validate(spec_dict)
        except ValidationError as e:
            # Re-raise the original exception
            raise

    def _load_spec_file(self, spec_path: Path) -> Dict[str, Any]:
        """
        Load a specification file (JSON or YAML).

        Args:
            spec_path: Path to the specification file

        Returns:
            Dict[str, Any]: Loaded specification as a dictionary

        Raises:
            ValueError: If the file is not valid JSON or YAML
        """
        with open(spec_path, "r") as f:
            content = f.read()

        # Try to parse as JSON first
        try:
            return json.loads(content)
        except json.JSONDecodeError:
            # If not JSON, try YAML
            try:
                return yaml.safe_load(content)
            except yaml.YAMLError as e:
                raise ValueError(f"Invalid specification file format: {e}")

    def _resolve_references(self, obj: Any, base_path: str = "#") -> Any:
        """
        Resolve references in an OpenAPI specification.

        Args:
            obj: Object to resolve references in
            base_path: Base path for resolving references

        Returns:
            Any: Object with resolved references
        """
        if isinstance(obj, dict):
            # Check if this is a reference
            if "$ref" in obj and len(obj) == 1:
                ref = obj["$ref"]

                # Avoid circular references
                ref_key = f"{base_path}:{ref}"
                if ref_key in self.resolved_refs:
                    return obj

                self.resolved_refs.add(ref_key)

                # Resolve the reference
                resolved = self._resolve_reference(ref)

                # Recursively resolve references in the resolved object
                return self._resolve_references(resolved, ref)

            # Recursively resolve references in all values
            return {k: self._resolve_references(v, f"{base_path}/{k}") for k, v in obj.items()}
        elif isinstance(obj, list):
            # Recursively resolve references in all items
            return [self._resolve_references(item, f"{base_path}/{i}") for i, item in enumerate(obj)]

        return obj

    def _resolve_reference(self, ref: str) -> Any:
        """
        Resolve a reference.

        Args:
            ref: Reference to resolve

        Returns:
            Any: Resolved reference

        Raises:
            ValueError: If the reference cannot be resolved
        """
        # Handle local references
        if ref.startswith("#/"):
            # Split the reference path
            parts = ref[2:].split("/")

            # Load the specification file
            if self.base_url and self.base_url.startswith("file://"):
                spec_path = Path(self.base_url[7:])
                spec_dict = self._load_spec_file(spec_path)

                # Navigate to the referenced object
                obj = spec_dict
                for part in parts:
                    if part not in obj:
                        raise ValueError(f"Invalid reference: {ref}")
                    obj = obj[part]

                return obj

        # Handle external references (not implemented in this MVP)
        raise ValueError(f"External references are not supported: {ref}")
