"""
Pytest configuration file for OpenAPI Client Generator tests.

This file contains shared fixtures and configuration for the test suite.
"""

import os
import json
import tempfile
from pathlib import Path

import pytest
import yaml


@pytest.fixture
def sample_openapi_dict():
    """
    Return a sample OpenAPI specification as a dictionary.

    This fixture provides a minimal valid OpenAPI specification that can be used
    for testing the parser and generators.
    """
    return {
        "openapi": "3.0.0",
        "info": {
            "title": "Sample API",
            "version": "1.0.0",
            "description": "A sample API for testing"
        },
        "paths": {
            "/users/{userId}": {
                "get": {
                    "operationId": "getUserById",
                    "summary": "Get user by ID",
                    "parameters": [
                        {
                            "name": "userId",
                            "in": "path",
                            "required": True,
                            "schema": {
                                "type": "integer"
                            }
                        }
                    ],
                    "responses": {
                        "200": {
                            "description": "User found",
                            "content": {
                                "application/json": {
                                    "schema": {
                                        "$ref": "#/components/schemas/User"
                                    }
                                }
                            }
                        }
                    }
                }
            }
        },
        "components": {
            "schemas": {
                "User": {
                    "type": "object",
                    "properties": {
                        "id": {
                            "type": "integer"
                        },
                        "name": {
                            "type": "string"
                        },
                        "email": {
                            "type": "string",
                            "format": "email"
                        }
                    },
                    "required": ["id", "name", "email"]
                }
            }
        }
    }


@pytest.fixture
def sample_openapi_json_file(sample_openapi_dict):
    """
    Create a temporary JSON file with a sample OpenAPI specification.

    This fixture creates a temporary file with a sample OpenAPI specification
    in JSON format, and returns the path to the file.
    """
    with tempfile.NamedTemporaryFile(suffix=".json", mode="w+", delete=False) as f:
        json.dump(sample_openapi_dict, f)
        temp_file_path = f.name

    yield temp_file_path

    # Clean up the temporary file
    os.unlink(temp_file_path)


@pytest.fixture
def sample_openapi_yaml_file(sample_openapi_dict):
    """
    Create a temporary YAML file with a sample OpenAPI specification.

    This fixture creates a temporary file with a sample OpenAPI specification
    in YAML format, and returns the path to the file.
    """
    with tempfile.NamedTemporaryFile(suffix=".yaml", mode="w+", delete=False) as f:
        yaml.dump(sample_openapi_dict, f)
        temp_file_path = f.name

    yield temp_file_path

    # Clean up the temporary file
    os.unlink(temp_file_path)


@pytest.fixture
def temp_output_dir():
    """
    Create a temporary directory for test output.

    This fixture creates a temporary directory that can be used for testing
    code generation, and returns the path to the directory.
    """
    with tempfile.TemporaryDirectory() as temp_dir:
        yield temp_dir
