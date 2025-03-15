"""
Tests for the operation ID extraction issue.

This module contains tests for the issue where operation IDs were not being properly
extracted from the OpenAPI specification.
"""

import pytest
from pathlib import Path
import sys

# Add the project root to the Python path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from openapi_client_generator.parser.openapi_parser import OpenAPIParser
from openapi_client_generator.parser.models import (
    OpenAPISpec, Operation
)


@pytest.fixture
def sample_openapi_dict_with_operation_id():
    """
    Return a sample OpenAPI specification with operation IDs.
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
                    "responses": {
                        "201": {
                            "description": "User created"
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
                        }
                    },
                    "required": ["id", "name"]
                }
            }
        }
    }


class TestOperationId:
    """Tests for the operation ID extraction issue."""

    def test_operation_id_extraction(self, sample_openapi_dict_with_operation_id):
        """Test that operation IDs are properly extracted from the OpenAPI specification."""
        # Parse the OpenAPI specification
        parser = OpenAPIParser()
        spec = OpenAPISpec.model_validate(sample_openapi_dict_with_operation_id)

        # Get the operations
        get_operation = spec.paths["/users/{userId}"].get
        post_operation = spec.paths["/users"].post

        # Assert that the operation IDs are correctly extracted
        assert get_operation.operation_id == "getUserById"
        assert post_operation.operation_id == "createUser"

    def test_operation_python_method_name(self, sample_openapi_dict_with_operation_id):
        """Test that operation IDs are properly converted to Python method names."""
        # Parse the OpenAPI specification
        parser = OpenAPIParser()
        spec = OpenAPISpec.model_validate(sample_openapi_dict_with_operation_id)

        # Get the operations
        get_operation = spec.paths["/users/{userId}"].get
        post_operation = spec.paths["/users"].post

        # Assert that the Python method names are correctly generated
        assert get_operation.get_python_method_name() == "get_user_by_id"
        assert post_operation.get_python_method_name() == "create_user"

    def test_get_operations_with_operation_id(self, sample_openapi_dict_with_operation_id):
        """Test getting operations with operation IDs."""
        # Parse the OpenAPI specification
        parser = OpenAPIParser()
        spec = OpenAPISpec.model_validate(sample_openapi_dict_with_operation_id)

        # Get the operations
        operations = spec.get_operations()

        # Find the operations by operation ID
        get_operation = next((op for op in operations if op["operation_id"] == "getUserById"), None)
        post_operation = next((op for op in operations if op["operation_id"] == "createUser"), None)

        # Assert that the operations exist and have the correct method names
        assert get_operation is not None
        assert get_operation["method_name"] == "get_user_by_id"
        assert post_operation is not None
        assert post_operation["method_name"] == "create_user"

    def test_operation_without_operation_id(self):
        """Test that operations without operation IDs get a default method name."""
        # Create an operation without an operation ID
        operation = Operation(responses={})

        # Assert that the Python method name is the default
        assert operation.get_python_method_name() == "operation"