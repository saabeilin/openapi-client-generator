"""
Tests for the references without type issue.

This module contains tests for the issue where references under schema without type: object
were returning Dict[str, Any] instead of the Pydantic class.
"""

import pytest
from pathlib import Path
import sys

# Add the project root to the Python path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from openapi_client_generator.parser.openapi_parser import OpenAPIParser
from openapi_client_generator.parser.models import (
    OpenAPISpec, Schema, Reference, Operation, Response, MediaType
)


@pytest.fixture
def sample_openapi_dict_with_reference_without_type():
    """
    Return a sample OpenAPI specification with a reference without type.
    """
    return {
        "openapi": "3.0.0",
        "info": {
            "title": "Sample API",
            "version": "1.0.0",
            "description": "A sample API for testing"
        },
        "paths": {
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


class TestReferenceWithoutType:
    """Tests for the references without type issue."""

    def test_find_model_for_schema(self, sample_openapi_dict_with_reference_without_type):
        """Test finding a model for a schema with properties but no type."""
        # Parse the OpenAPI specification
        parser = OpenAPIParser()
        spec = OpenAPISpec.model_validate(sample_openapi_dict_with_reference_without_type)

        # Create a schema with properties but no type
        schema = Schema(
            properties={
                "id": Schema(type="integer"),
                "name": Schema(type="string")
            }
        )

        # Find a model for the schema
        model_name = spec._find_model_for_schema(schema)

        # Assert that the model name is correct
        assert model_name == "ReferenceWithoutType"

    def test_get_return_type_for_reference_without_type(self, sample_openapi_dict_with_reference_without_type):
        """Test getting the return type for an operation with a reference without type."""
        # Parse the OpenAPI specification
        parser = OpenAPIParser()
        spec = OpenAPISpec.model_validate(sample_openapi_dict_with_reference_without_type)

        # Get the operation
        operation = spec.paths["/reference-without-type"].get

        # Get the return type
        return_type = operation.get_return_type()

        # Assert that the return type is the model name, not Dict[str, Any]
        assert return_type == "ReferenceWithoutType"

    def test_get_operations_with_reference_without_type(self, sample_openapi_dict_with_reference_without_type):
        """Test getting operations with a reference without type."""
        # Parse the OpenAPI specification
        parser = OpenAPIParser()
        spec = OpenAPISpec.model_validate(sample_openapi_dict_with_reference_without_type)

        # Get the operations
        operations = spec.get_operations()

        # Find the operation with the reference without type
        operation = next((op for op in operations if op["operation_id"] == "getReferenceWithoutType"), None)

        # Assert that the operation exists and has the correct return type
        assert operation is not None
        assert operation["return_type"] == "ReferenceWithoutType"