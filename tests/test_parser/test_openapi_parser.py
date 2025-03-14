"""
Tests for the OpenAPI parser.

This module contains tests for the OpenAPIParser class.
"""

import json
import os
from pathlib import Path
from typing import Dict, Any

import pytest
from pydantic import ValidationError

import sys
from pathlib import Path

# Add the project root to the Python path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from openapi_client_generator.parser.openapi_parser import OpenAPIParser
from openapi_client_generator.parser.models import OpenAPISpec


class TestOpenAPIParser:
    """Tests for the OpenAPIParser class."""

    def test_parse_json(self, sample_openapi_json_file):
        """Test parsing a JSON OpenAPI specification."""
        parser = OpenAPIParser()
        spec = parser.parse(sample_openapi_json_file)

        assert isinstance(spec, OpenAPISpec)
        assert spec.openapi == "3.0.0"
        assert spec.info.title == "Sample API"
        assert spec.info.version == "1.0.0"
        assert len(spec.paths) == 1
        assert "/users/{userId}" in spec.paths

    def test_parse_yaml(self, sample_openapi_yaml_file):
        """Test parsing a YAML OpenAPI specification."""
        parser = OpenAPIParser()
        spec = parser.parse(sample_openapi_yaml_file)

        assert isinstance(spec, OpenAPISpec)
        assert spec.openapi == "3.0.0"
        assert spec.info.title == "Sample API"
        assert spec.info.version == "1.0.0"
        assert len(spec.paths) == 1
        assert "/users/{userId}" in spec.paths

    def test_parse_nonexistent_file(self):
        """Test parsing a nonexistent file."""
        parser = OpenAPIParser()

        with pytest.raises(FileNotFoundError):
            parser.parse("nonexistent.json")

    def test_parse_invalid_json(self, tmp_path):
        """Test parsing an invalid JSON file."""
        # Create an invalid JSON file
        invalid_json_file = tmp_path / "invalid.json"
        with open(invalid_json_file, "w") as f:
            f.write("{")

        parser = OpenAPIParser()

        with pytest.raises(ValueError):
            parser.parse(invalid_json_file)

    def test_parse_invalid_yaml(self, tmp_path):
        """Test parsing an invalid YAML file."""
        # Create an invalid YAML file
        invalid_yaml_file = tmp_path / "invalid.yaml"
        with open(invalid_yaml_file, "w") as f:
            f.write(":")

        parser = OpenAPIParser()

        with pytest.raises(ValueError):
            parser.parse(invalid_yaml_file)

    def test_parse_invalid_openapi(self, tmp_path):
        """Test parsing an invalid OpenAPI specification."""
        # Create an invalid OpenAPI specification
        invalid_openapi_file = tmp_path / "invalid.json"
        with open(invalid_openapi_file, "w") as f:
            json.dump({"openapi": "3.0.0"}, f)  # Missing required fields

        parser = OpenAPIParser()

        with pytest.raises(ValidationError):
            parser.parse(invalid_openapi_file)

    def test_get_operations(self, sample_openapi_json_file):
        """Test getting operations from a specification."""
        parser = OpenAPIParser()
        spec = parser.parse(sample_openapi_json_file)

        operations = spec.get_operations()

        assert len(operations) == 1
        assert operations[0]["method"] == "get"
        assert operations[0]["path"] == "/users/{userId}"
        # The operation_id is now being parsed correctly
        assert operations[0]["operation_id"] == "getUserById"
        assert operations[0]["method_name"] == "get_user_by_id"

    def test_get_models(self, sample_openapi_json_file):
        """Test getting models from a specification."""
        parser = OpenAPIParser()
        spec = parser.parse(sample_openapi_json_file)

        models = spec.get_models()

        assert len(models) == 1
        assert "User" in models
        assert "id" in models["User"]["properties"]
        assert "name" in models["User"]["properties"]
        assert "email" in models["User"]["properties"]
        assert models["User"]["properties"]["id"]["type_hint"] == "int"
        assert models["User"]["properties"]["name"]["type_hint"] == "str"
        assert models["User"]["properties"]["email"]["type_hint"] == "str"
