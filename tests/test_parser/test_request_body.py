"""
Tests for the request body parameters issue.

This module contains tests for the issue where operations with request bodies
were not generating parameters to pass them.
"""

import pytest
from pathlib import Path
import sys

# Add the project root to the Python path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from openapi_client_generator.parser.openapi_parser import OpenAPIParser
from openapi_client_generator.parser.models import (
    OpenAPISpec, Schema, Reference, Operation, Response, MediaType, RequestBody
)


@pytest.fixture
def sample_openapi_dict_with_request_body():
    """
    Return a sample OpenAPI specification with a request body.
    """
    return {
        "openapi": "3.0.0",
        "info": {
            "title": "Sample API",
            "version": "1.0.0",
            "description": "A sample API for testing"
        },
        "paths": {
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


class TestRequestBody:
    """Tests for the request body parameters issue."""

    def test_operation_with_request_body(self, sample_openapi_dict_with_request_body):
        """Test that an operation with a request body has the request_body field set."""
        # Parse the OpenAPI specification
        parser = OpenAPIParser()
        spec = OpenAPISpec.model_validate(sample_openapi_dict_with_request_body)

        # Get the operation
        operation = spec.paths["/users"].post

        # Assert that the operation has a request_body
        assert operation.request_body is not None
        assert operation.request_body.description == "User object to be created"
        assert operation.request_body.required is True

    def test_get_operations_with_request_body(self, sample_openapi_dict_with_request_body):
        """Test getting operations with a request body."""
        # Parse the OpenAPI specification
        parser = OpenAPIParser()
        spec = OpenAPISpec.model_validate(sample_openapi_dict_with_request_body)

        # Get the operations
        operations = spec.get_operations()

        # Find the operation with the request body
        operation = next((op for op in operations if op["operation_id"] == "createUser"), None)

        # Assert that the operation exists and has a request_body
        assert operation is not None
        assert operation["request_body"] is not None