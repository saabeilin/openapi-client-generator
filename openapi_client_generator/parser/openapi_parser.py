"""
OpenAPI Parser for the OpenAPI Client Generator.

This module provides functionality for parsing OpenAPI specifications.
"""

import json
import os
from pathlib import Path
from typing import Dict, Any, Union, Optional

import yaml
from pydantic import ValidationError

from .models import OpenAPISpec


class OpenAPIParser:
    """
    Parser for OpenAPI specifications.
    
    This class is responsible for loading and parsing OpenAPI specifications
    from JSON or YAML files.
    """
    
    def __init__(self):
        """Initialize the OpenAPI parser."""
        pass
    
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
        
        # Load the specification file
        spec_dict = self._load_spec_file(spec_path)
        
        # Parse the specification
        try:
            return OpenAPISpec.model_validate(spec_dict)
        except ValidationError as e:
            raise ValidationError(f"Invalid OpenAPI specification: {e}")
    
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