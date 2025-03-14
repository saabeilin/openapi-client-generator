"""
Pydantic models for OpenAPI specifications.

This module provides Pydantic models for representing OpenAPI specifications.
"""

from __future__ import annotations

import re
from enum import Enum
from typing import Dict, List, Optional, Any, Union, Literal, TypeVar, Generic, Set, Annotated
from typing import cast
from pydantic import BaseModel, Field, AnyUrl, ConfigDict, field_validator, model_validator


class Contact(BaseModel):
    """Contact information for the API."""

    name: Optional[str] = Field(None, description="The name of the contact")
    url: Optional[AnyUrl] = Field(None, description="The URL pointing to the contact information")
    email: Optional[str] = Field(None, description="The email address of the contact")


class License(BaseModel):
    """License information for the API."""

    name: str = Field(..., description="The name of the license")
    url: Optional[AnyUrl] = Field(None, description="The URL pointing to the license")


class Info(BaseModel):
    """Information about the API."""

    title: str = Field(..., description="The title of the API")
    version: str = Field(..., description="The version of the API")
    description: Optional[str] = Field(None, description="A description of the API")
    terms_of_service: Optional[AnyUrl] = Field(None, description="The terms of service for the API")
    contact: Optional[Contact] = Field(None, description="Contact information for the API")
    license: Optional[License] = Field(None, description="License information for the API")


class ServerVariable(BaseModel):
    """Variable substitution for server URL template."""

    enum: Optional[List[str]] = Field(None, description="Enumeration of string values to be used if the substitution options are from a limited set")
    default: str = Field(..., description="The default value to use for substitution")
    description: Optional[str] = Field(None, description="A description for the server variable")


class Server(BaseModel):
    """Server information."""

    url: str = Field(..., description="A URL to the target host")
    description: Optional[str] = Field(None, description="A description of the server")
    variables: Optional[Dict[str, ServerVariable]] = Field(None, description="A map between a variable name and its value")


class ExternalDocumentation(BaseModel):
    """External documentation."""

    url: AnyUrl = Field(..., description="The URL for the external documentation")
    description: Optional[str] = Field(None, description="A description of the external documentation")


class ParameterLocation(str, Enum):
    """Parameter location."""

    QUERY = "query"
    HEADER = "header"
    PATH = "path"
    COOKIE = "cookie"


class ParameterStyle(str, Enum):
    """Parameter style."""

    MATRIX = "matrix"
    LABEL = "label"
    FORM = "form"
    SIMPLE = "simple"
    SPACE_DELIMITED = "spaceDelimited"
    PIPE_DELIMITED = "pipeDelimited"
    DEEP_OBJECT = "deepObject"


class SchemaType(str, Enum):
    """Schema type."""

    STRING = "string"
    NUMBER = "number"
    INTEGER = "integer"
    BOOLEAN = "boolean"
    ARRAY = "array"
    OBJECT = "object"


class Reference(BaseModel):
    """Reference object."""

    ref: str = Field(..., alias="$ref", description="Reference to another component")

    def get_python_type_hint(self) -> str:
        """
        Get the Python type hint for the reference.

        Returns:
            str: Python type hint
        """
        # Extract the model name from the reference
        model_name = self.ref.split("/")[-1]
        return model_name


class Schema(BaseModel):
    """Schema object."""

    model_config = ConfigDict(extra="allow")

    type: Optional[SchemaType] = Field(None, description="The type of the schema")
    format: Optional[str] = Field(None, description="The format of the schema")
    title: Optional[str] = Field(None, description="The title of the schema")
    description: Optional[str] = Field(None, description="A description of the schema")
    default: Optional[Any] = Field(None, description="The default value of the schema")
    nullable: Optional[bool] = Field(None, description="Whether the schema is nullable")
    required: Optional[List[str]] = Field(None, description="The required properties of the schema")
    enum: Optional[List[Any]] = Field(None, description="The enumeration of values that the schema can take")

    # Array-specific fields
    items: Optional[Union[Schema, Reference]] = Field(None, description="The items of the array")

    # Object-specific fields
    properties: Optional[Dict[str, Union[Schema, Reference]]] = Field(None, description="The properties of the object")
    additional_properties: Optional[Union[bool, Schema, Reference]] = Field(None, description="Whether additional properties are allowed")

    # Number-specific fields
    minimum: Optional[float] = Field(None, description="The minimum value of the number")
    maximum: Optional[float] = Field(None, description="The maximum value of the number")
    exclusive_minimum: Optional[bool] = Field(None, description="Whether the minimum value is exclusive")
    exclusive_maximum: Optional[bool] = Field(None, description="Whether the maximum value is exclusive")
    multiple_of: Optional[float] = Field(None, description="The multiple of the number")

    # String-specific fields
    min_length: Optional[int] = Field(None, description="The minimum length of the string")
    max_length: Optional[int] = Field(None, description="The maximum length of the string")
    pattern: Optional[str] = Field(None, description="The pattern of the string")

    # Reference
    ref: Optional[str] = Field(None, alias="$ref", description="Reference to another schema")

    def get_python_type_hint(self) -> str:
        """
        Get the Python type hint for the schema.

        Returns:
            str: Python type hint
        """
        if self.ref:
            # Extract the model name from the reference
            model_name = self.ref.split("/")[-1]
            return model_name

        if self.type == SchemaType.STRING:
            return "str"
        elif self.type == SchemaType.NUMBER:
            return "float"
        elif self.type == SchemaType.INTEGER:
            return "int"
        elif self.type == SchemaType.BOOLEAN:
            return "bool"
        elif self.type == SchemaType.ARRAY:
            if self.items:
                item_type = self.items.get_python_type_hint() if isinstance(self.items, Schema) else self.items.get_python_type_hint()
                return f"List[{item_type}]"
            return "List[Any]"
        elif self.type == SchemaType.OBJECT:
            if self.properties:
                return "Dict[str, Any]"
            return "Dict[str, Any]"

        return "Any"

    def get_field_args(self) -> str:
        """
        Get the arguments for the Pydantic Field constructor.

        Returns:
            str: Field arguments
        """
        args = []

        if self.default is not None:
            if isinstance(self.default, str):
                args.append(f'default="{self.default}"')
            else:
                args.append(f"default={self.default}")
        elif self.nullable:
            args.append("default=None")
        else:
            args.append("...")

        if self.description:
            args.append(f'description="{self.description}"')

        return ", ".join(args)


class MediaType(BaseModel):
    """Media type object."""

    schema_: Optional[Union[Schema, Reference]] = Field(None, alias="schema", description="The schema of the media type")
    example: Optional[Any] = Field(None, description="Example of the media type")
    examples: Optional[Dict[str, Any]] = Field(None, description="Examples of the media type")
    encoding: Optional[Dict[str, Any]] = Field(None, description="Encoding of the media type")


class RequestBody(BaseModel):
    """Request body object."""

    description: Optional[str] = Field(None, description="A description of the request body")
    content: Dict[str, MediaType] = Field(..., description="The content of the request body")
    required: Optional[bool] = Field(None, description="Whether the request body is required")


class Response(BaseModel):
    """Response object."""

    description: str = Field(..., description="A description of the response")
    content: Optional[Dict[str, MediaType]] = Field(None, description="The content of the response")
    headers: Optional[Dict[str, Union["Parameter", Reference]]] = Field(None, description="The headers of the response")


class Parameter(BaseModel):
    """Parameter object."""

    name: str = Field(..., description="The name of the parameter")
    in_: ParameterLocation = Field(..., alias="in", description="The location of the parameter")
    description: Optional[str] = Field(None, description="A description of the parameter")
    required: Optional[bool] = Field(None, description="Whether the parameter is required")
    deprecated: Optional[bool] = Field(None, description="Whether the parameter is deprecated")
    style: Optional[ParameterStyle] = Field(None, description="The style of the parameter")
    explode: Optional[bool] = Field(None, description="Whether the parameter is exploded")
    schema_: Optional[Union[Schema, Reference]] = Field(None, alias="schema", description="The schema of the parameter")

    def get_python_name(self) -> str:
        """
        Get the Python name for the parameter.

        Returns:
            str: Python name
        """
        # Convert to snake_case
        s1 = re.sub(r'[^a-zA-Z0-9]', '_', self.name)
        s2 = re.sub(r'([a-z0-9])([A-Z])', r'\1_\2', s1)
        return s2.lower()

    def get_python_type_hint(self) -> str:
        """
        Get the Python type hint for the parameter.

        Returns:
            str: Python type hint
        """
        if self.schema_:
            type_hint = self.schema_.get_python_type_hint() if isinstance(self.schema_, Schema) else self.schema_.get_python_type_hint()
            if not self.required:
                return f"Optional[{type_hint}]"
            return type_hint
        return "Any"


class Operation(BaseModel):
    """Operation object."""

    tags: Optional[List[str]] = Field(None, description="Tags for the operation")
    summary: Optional[str] = Field(None, description="A summary of the operation")
    description: Optional[str] = Field(None, description="A description of the operation")
    external_docs: Optional[ExternalDocumentation] = Field(None, description="External documentation for the operation")
    operation_id: Optional[str] = Field(None, alias="operationId", description="A unique identifier for the operation")
    parameters: Optional[List[Union[Parameter, Reference]]] = Field(None, description="Parameters for the operation")
    request_body: Optional[Union[RequestBody, Reference]] = Field(None, description="Request body for the operation")
    responses: Dict[str, Union[Response, Reference]] = Field(..., description="Responses for the operation")
    deprecated: Optional[bool] = Field(None, description="Whether the operation is deprecated")
    security: Optional[List[Dict[str, List[str]]]] = Field(None, description="Security requirements for the operation")

    def get_python_method_name(self) -> str:
        """
        Get the Python method name for the operation.

        Returns:
            str: Python method name
        """
        if not self.operation_id:
            return "operation"

        # Convert to snake_case
        s1 = re.sub(r'[^a-zA-Z0-9]', '_', self.operation_id)
        s2 = re.sub(r'([a-z0-9])([A-Z])', r'\1_\2', s1)
        return s2.lower()

    def get_return_type(self) -> str:
        """
        Get the return type for the operation.

        Returns:
            str: Return type
        """
        # Get the 200 or 201 response if available
        response = self.responses.get("200") or self.responses.get("201")
        if response and hasattr(response, "content") and response.content:
            # Get the first content type
            content_type = next(iter(response.content))
            media_type = response.content[content_type]
            if media_type.schema_:
                return media_type.schema_.get_python_type_hint() if isinstance(media_type.schema_, Schema) else media_type.schema_.get_python_type_hint()

        return "Any"


class PathItem(BaseModel):
    """Path item object."""

    ref: Optional[str] = Field(None, alias="$ref", description="Reference to another path item")
    summary: Optional[str] = Field(None, description="A summary of the path item")
    description: Optional[str] = Field(None, description="A description of the path item")
    get: Optional[Operation] = Field(None, description="GET operation")
    put: Optional[Operation] = Field(None, description="PUT operation")
    post: Optional[Operation] = Field(None, description="POST operation")
    delete: Optional[Operation] = Field(None, description="DELETE operation")
    options: Optional[Operation] = Field(None, description="OPTIONS operation")
    head: Optional[Operation] = Field(None, description="HEAD operation")
    patch: Optional[Operation] = Field(None, description="PATCH operation")
    trace: Optional[Operation] = Field(None, description="TRACE operation")
    servers: Optional[List[Server]] = Field(None, description="Servers for the path item")
    parameters: Optional[List[Union[Parameter, Reference]]] = Field(None, description="Parameters for the path item")


class Components(BaseModel):
    """Components object."""

    schemas: Optional[Dict[str, Union[Schema, Reference]]] = Field(None, description="Reusable schemas")
    responses: Optional[Dict[str, Union[Response, Reference]]] = Field(None, description="Reusable responses")
    parameters: Optional[Dict[str, Union[Parameter, Reference]]] = Field(None, description="Reusable parameters")
    examples: Optional[Dict[str, Any]] = Field(None, description="Reusable examples")
    request_bodies: Optional[Dict[str, Union[RequestBody, Reference]]] = Field(None, description="Reusable request bodies")
    headers: Optional[Dict[str, Union[Parameter, Reference]]] = Field(None, description="Reusable headers")
    security_schemes: Optional[Dict[str, Any]] = Field(None, description="Reusable security schemes")
    links: Optional[Dict[str, Any]] = Field(None, description="Reusable links")
    callbacks: Optional[Dict[str, Any]] = Field(None, description="Reusable callbacks")


class OpenAPISpec(BaseModel):
    """OpenAPI specification."""

    openapi: str = Field(..., description="OpenAPI version")
    info: Info = Field(..., description="API information")
    servers: Optional[List[Server]] = Field(None, description="API servers")
    paths: Dict[str, PathItem] = Field(..., description="API paths")
    components: Optional[Components] = Field(None, description="API components")
    security: Optional[List[Dict[str, List[str]]]] = Field(None, description="API security requirements")
    tags: Optional[List[Dict[str, Any]]] = Field(None, description="API tags")
    external_docs: Optional[ExternalDocumentation] = Field(None, description="API external documentation")

    def get_operations(self) -> List[Dict[str, Any]]:
        """
        Get all operations from the specification.

        Returns:
            List[Dict[str, Any]]: List of operations
        """
        operations = []

        for path, path_item in self.paths.items():
            for method in ["get", "put", "post", "delete", "options", "head", "patch", "trace"]:
                operation = getattr(path_item, method, None)
                if operation:
                    operation_info = {
                        "path": path,
                        "method": method,
                        "operation_id": operation.operation_id or "",
                        "summary": operation.summary or "",
                        "description": operation.description or "",
                        "parameters": operation.parameters or [],
                        "request_body": operation.request_body,
                        "responses": operation.responses,
                        "path_template": self._get_path_template(path),
                        "method_name": operation.get_python_method_name(),
                        "return_type": operation.get_return_type(),
                        "return_type_description": "The response from the API",
                    }
                    operations.append(operation_info)

        return operations

    def _get_path_template(self, path: str) -> str:
        """
        Get the path template for an operation.

        Args:
            path: Path from the OpenAPI specification

        Returns:
            str: Path template for string formatting
        """
        # Replace {param} with {param} for string formatting
        return path.replace("{", "{")

    def get_models(self) -> Dict[str, Dict[str, Any]]:
        """
        Get all models from the specification.

        Returns:
            Dict[str, Dict[str, Any]]: Dictionary of models
        """
        models = {}

        if self.components and self.components.schemas:
            for name, schema in self.components.schemas.items():
                if isinstance(schema, Schema) and schema.properties:
                    model_info = {
                        "description": schema.description or name,
                        "properties": {},
                    }

                    for prop_name, prop_schema in schema.properties.items():
                        prop_info = {
                            "type_hint": prop_schema.get_python_type_hint() if isinstance(prop_schema, Schema) else prop_schema.get_python_type_hint(),
                            "field_args": prop_schema.get_field_args() if isinstance(prop_schema, Schema) else "...",
                        }
                        model_info["properties"][prop_name] = prop_info

                    models[name] = model_info

        return models
