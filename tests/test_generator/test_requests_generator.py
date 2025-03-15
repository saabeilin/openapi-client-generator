"""
Tests for the requests generator.

This module contains tests for the RequestsClientGenerator class.
"""

import os
import re
import json
import tempfile
from pathlib import Path
import sys

import pytest

# Add the project root to the Python path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from openapi_client_generator.parser.openapi_parser import OpenAPIParser
from openapi_client_generator.generator.requests_generator import RequestsClientGenerator


@pytest.fixture
def sample_openapi_dict_with_all_issues():
    """
    Return a sample OpenAPI specification with all the issues we want to test.
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
            },
            "/users": {
                "post": {
                    "operationId": "createUser",
                    "summary": "Create a new user",
                    "requestBody": {
                        "description": "User object to be created",
                        "required": True,
                        "content": {
                            "application/json": {
                                "schema": {
                                    "$ref": "#/components/schemas/User"
                                }
                            }
                        }
                    },
                    "responses": {
                        "201": {
                            "description": "User created",
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
            },
            "/reference-without-type": {
                "get": {
                    "operationId": "getReferenceWithoutType",
                    "summary": "Get reference without type",
                    "responses": {
                        "200": {
                            "description": "Reference without type",
                            "content": {
                                "application/json": {
                                    "schema": {
                                        "$ref": "#/components/schemas/ReferenceWithoutType"
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
                },
                "ReferenceWithoutType": {
                    "properties": {
                        "id": {
                            "type": "integer"
                        },
                        "name": {
                            "type": "string"
                        }
                    },
                    "required": ["id", "name"]
                }
            }
        }
    }


@pytest.fixture
def sample_openapi_spec(sample_openapi_dict_with_all_issues):
    """
    Return a parsed OpenAPI specification.
    """
    # Create a temporary file with the sample specification
    with tempfile.NamedTemporaryFile(suffix=".json", mode="w+", delete=False) as f:
        json.dump(sample_openapi_dict_with_all_issues, f)
        spec_path = f.name

    try:
        # Parse the OpenAPI specification
        parser = OpenAPIParser()
        spec = parser.parse(spec_path)
        return spec
    finally:
        # Clean up the temporary file
        os.unlink(spec_path)


class TestRequestsGenerator:
    """Tests for the RequestsClientGenerator class."""

    def test_generate_client_with_operation_id(self, sample_openapi_spec, temp_output_dir):
        """Test generating a client with operation IDs."""
        # Create a generator
        generator = RequestsClientGenerator(output_dir=temp_output_dir)

        # Generate the client
        generator.generate(sample_openapi_spec)

        # Check that the client file exists
        client_path = Path(temp_output_dir) / "sample_api" / "client.py"
        assert client_path.exists()

        # Read the client file
        with open(client_path, "r") as f:
            client_code = f.read()

        # Check that the methods with operation IDs are generated correctly
        assert "def get_user_by_id(self, user_id: int)" in client_code
        assert "def create_user(self, request_body: Dict[str, Any])" in client_code

    def test_generate_client_with_request_body(self, sample_openapi_spec, temp_output_dir):
        """Test generating a client with request bodies."""
        # Create a generator
        generator = RequestsClientGenerator(output_dir=temp_output_dir)

        # Generate the client
        generator.generate(sample_openapi_spec)

        # Check that the client file exists
        client_path = Path(temp_output_dir) / "sample_api" / "client.py"
        assert client_path.exists()

        # Read the client file
        with open(client_path, "r") as f:
            client_code = f.read()

        # Check that the methods with request bodies have the request_body parameter
        assert "def create_user(self, request_body: Dict[str, Any])" in client_code
        assert 'return self._make_request("POST", url, params=params, json=request_body)' in client_code

    def test_generate_client_with_reference_without_type(self, sample_openapi_spec, temp_output_dir):
        """Test generating a client with references without type."""
        # Create a generator
        generator = RequestsClientGenerator(output_dir=temp_output_dir)

        # Generate the client
        generator.generate(sample_openapi_spec)

        # Check that the client file exists
        client_path = Path(temp_output_dir) / "sample_api" / "client.py"
        assert client_path.exists()

        # Read the client file
        with open(client_path, "r") as f:
            client_code = f.read()

        # Check that the methods with references without type return the correct type
        assert "def get_reference_without_type(self," in client_code
        assert "-> ReferenceWithoutType:" in client_code

        # Check that the models file exists
        models_path = Path(temp_output_dir) / "sample_api" / "models.py"
        assert models_path.exists()

        # Read the models file
        with open(models_path, "r") as f:
            models_code = f.read()

        # Check that the ReferenceWithoutType model is generated
        assert "class ReferenceWithoutType(BaseModel):" in models_code
