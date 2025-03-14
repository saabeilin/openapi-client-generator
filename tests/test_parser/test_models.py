"""
Tests for the OpenAPI models.

This module contains tests for the Pydantic models used to represent OpenAPI specifications.
"""

import pytest
from pydantic import ValidationError

import sys
from pathlib import Path

# Add the project root to the Python path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from openapi_client_generator.parser.models import (
    OpenAPISpec, Info, PathItem, Operation, Parameter, Schema, Reference,
    SchemaType, ParameterLocation
)


class TestOpenAPIModels:
    """Tests for the OpenAPI models."""

    def test_openapi_spec_validation(self):
        """Test validation of the OpenAPISpec model."""
        # Valid specification
        valid_spec = {
            "openapi": "3.0.0",
            "info": {
                "title": "Test API",
                "version": "1.0.0"
            },
            "paths": {}
        }

        spec = OpenAPISpec.model_validate(valid_spec)

        assert spec.openapi == "3.0.0"
        assert spec.info.title == "Test API"
        assert spec.info.version == "1.0.0"

        # Invalid specification (missing required fields)
        invalid_spec = {
            "openapi": "3.0.0"
        }

        with pytest.raises(ValidationError):
            OpenAPISpec.model_validate(invalid_spec)

    def test_info_validation(self):
        """Test validation of the Info model."""
        # Valid info
        valid_info = {
            "title": "Test API",
            "version": "1.0.0"
        }

        info = Info.model_validate(valid_info)

        assert info.title == "Test API"
        assert info.version == "1.0.0"

        # Invalid info (missing required fields)
        invalid_info = {
            "title": "Test API"
        }

        with pytest.raises(ValidationError):
            Info.model_validate(invalid_info)

    def test_schema_type_hints(self):
        """Test getting Python type hints from schemas."""
        # String schema
        string_schema = Schema(type=SchemaType.STRING)
        assert string_schema.get_python_type_hint() == "str"

        # Integer schema
        integer_schema = Schema(type=SchemaType.INTEGER)
        assert integer_schema.get_python_type_hint() == "int"

        # Boolean schema
        boolean_schema = Schema(type=SchemaType.BOOLEAN)
        assert boolean_schema.get_python_type_hint() == "bool"

        # Array schema
        array_schema = Schema(
            type=SchemaType.ARRAY,
            items=Schema(type=SchemaType.STRING)
        )
        assert array_schema.get_python_type_hint() == "List[str]"

        # Object schema
        object_schema = Schema(
            type=SchemaType.OBJECT,
            properties={"name": Schema(type=SchemaType.STRING)}
        )
        assert object_schema.get_python_type_hint() == "Dict[str, Any]"

        # Reference
        reference = Reference(**{"$ref": "#/components/schemas/User"})
        assert reference.get_python_type_hint() == "User"

    def test_parameter_python_name(self):
        """Test getting Python names from parameters."""
        # Simple parameter
        simple_param = Parameter(
            name="userId",
            **{"in": "path"}
        )
        assert simple_param.get_python_name() == "user_id"

        # Parameter with special characters
        special_param = Parameter(
            name="user-id",
            **{"in": "path"}
        )
        assert special_param.get_python_name() == "user_id"

        # Parameter with mixed case
        mixed_case_param = Parameter(
            name="userID",
            **{"in": "path"}
        )
        assert mixed_case_param.get_python_name() == "user_id"

    def test_operation_python_method_name(self):
        """Test getting Python method names from operations."""
        # Simple operation ID
        simple_op = Operation(
            **{"operationId": "getUserById", "responses": {}}
        )
        assert simple_op.get_python_method_name() == "get_user_by_id"

        # Operation ID with special characters
        special_op = Operation(
            **{"operationId": "get-user-by-id", "responses": {}}
        )
        assert special_op.get_python_method_name() == "get_user_by_id"

        # Operation ID with mixed case
        mixed_case_op = Operation(
            **{"operationId": "GetUserByID", "responses": {}}
        )
        assert mixed_case_op.get_python_method_name() == "get_user_by_id"

        # No operation ID
        no_op_id = Operation(responses={})
        assert no_op_id.get_python_method_name() == "operation"
