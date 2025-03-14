# OpenAPI Client Generator Implementation Plan

## Overview

This document outlines the implementation plan for the OpenAPI Client Generator tool, which will generate Python client libraries from OpenAPI v3 specifications. The tool will support generating clients that use `requests`, `aiohttp`, and `httpx` libraries.

## Dependencies

### Core Libraries

1. **OpenAPI Specification Parser**:
   - **pydantic** (2.x): For data validation and settings management
   - **PyYAML**: For parsing YAML OpenAPI specifications
   - **json** (standard library): For parsing JSON OpenAPI specifications

2. **Code Generation**:
   - **Jinja2**: Template engine for generating Python code
   - **ruff**: For linting and formatting the generated code

3. **CLI Interface**:
   - **argparse** (standard library): For parsing command-line arguments
   - **rich**: For enhanced terminal output (optional)

4. **HTTP Client Libraries** (runtime dependencies for generated clients):
   - **requests**: For synchronous HTTP clients
   - **aiohttp**: For asynchronous HTTP clients
   - **httpx**: For both synchronous and asynchronous HTTP clients

## Implementation Components

### 1. OpenAPI Parser

The parser will be responsible for loading and validating OpenAPI specifications from JSON or YAML files.

#### Implementation Details:

1. Create a `parser` module with the following components:
   - `OpenAPIParser` class: Main parser that loads and validates the specification
   - `OpenAPISpec` Pydantic model: Represents the OpenAPI specification structure
   - Helper functions for resolving references and handling schema components

2. Parser workflow:
   - Detect file format (JSON or YAML) based on file extension or content
   - Load the specification file
   - Validate against the OpenAPI v3 schema using Pydantic models
   - Resolve references ($ref) within the specification
   - Return a structured representation of the API specification

### 2. Code Generator

The code generator will use the parsed OpenAPI specification to generate Python client code.

#### Implementation Details:

1. Create a `generator` module with the following components:
   - `ClientGenerator` base class: Common functionality for all client generators
   - `RequestsClientGenerator`, `AiohttpClientGenerator`, and `HttpxClientGenerator` classes: Specific implementations for each HTTP library
   - Template loader and renderer using Jinja2

2. Generator workflow:
   - Load appropriate templates based on the selected HTTP client library
   - Process the parsed OpenAPI specification
   - Generate model classes for API schemas
   - Generate the `APIClient` class with methods for each API operation
   - Format the generated code using Ruff
   - Write the output to the specified directory

3. Code generation strategy:
   - Convert OpenAPI operation IDs to Python method names (snake_case)
   - Map path and query parameters to method arguments
   - Handle request body as a separate `body` parameter
   - Generate appropriate docstrings with parameter descriptions
   - Add type hints based on the OpenAPI schema
   - Implement proper error handling and response parsing

### 3. CLI Interface

The command-line interface will handle user input and orchestrate the parsing and code generation process.

#### Implementation Details:

1. Create a CLI module in `__main__.py` with the following components:
   - Command-line argument parser using `argparse`
   - Main function that orchestrates the workflow
   - Error handling and user feedback

2. CLI workflow:
   - Parse command-line arguments
   - Validate input (check if the specification file exists and is readable)
   - Initialize the appropriate parser and generator based on arguments
   - Execute the parsing and code generation process
   - Provide feedback to the user about the generation process

## Project Structure

```
openapi_client_generator/
├── __init__.py
├── __main__.py              # Entry point with CLI interface
├── parser/
│   ├── __init__.py
│   ├── openapi_parser.py    # OpenAPI specification parser
│   └── models.py            # Pydantic models for OpenAPI schema
├── generator/
│   ├── __init__.py
│   ├── base.py              # Base generator class
│   ├── requests_generator.py # Requests-specific generator
│   ├── aiohttp_generator.py # Aiohttp-specific generator
│   └── httpx_generator.py   # Httpx-specific generator
└── templates/               # Jinja2 templates for code generation
    ├── common/              # Shared templates
    ├── requests/            # Requests-specific templates
    ├── aiohttp/             # Aiohttp-specific templates
    └── httpx/               # Httpx-specific templates
```

## Implementation Workflow

1. **Setup Project Structure**:
   - Create the directory structure
   - Set up the package configuration
   - Add dependencies to requirements.txt

2. **Implement OpenAPI Parser**:
   - Create Pydantic models for OpenAPI schema
   - Implement the parser logic
   - Add tests for the parser

3. **Create Template System**:
   - Design Jinja2 templates for different components
   - Implement template loading and rendering
   - Create separate template sets for each HTTP client library

4. **Implement Code Generators**:
   - Create the base generator class
   - Implement specific generators for each HTTP client library
   - Add tests for the generators

5. **Build CLI Interface**:
   - Implement command-line argument parsing
   - Create the main workflow
   - Add error handling and user feedback

6. **Testing and Validation**:
   - Test with various OpenAPI specifications
   - Validate the generated code
   - Ensure compatibility with different Python versions

## Detailed Implementation Notes

### OpenAPI Parsing

1. **Handling Different OpenAPI Versions**:
   - Focus on OpenAPI v3.0.x and v3.1.x
   - Provide clear error messages for unsupported versions

2. **Reference Resolution**:
   - Implement proper handling of `$ref` references
   - Support both internal and external references
   - Handle circular references

3. **Schema Validation**:
   - Validate the OpenAPI specification against the official schema
   - Provide helpful error messages for invalid specifications

### Code Generation

1. **Type Mapping**:
   - Map OpenAPI types to Python types
   - Handle complex schemas (arrays, objects, etc.)
   - Support for nullable types and optional parameters

2. **Method Generation**:
   - Convert operationId to snake_case for method names
   - Handle path parameters, query parameters, and request body
   - Generate appropriate docstrings with parameter descriptions

3. **Authentication**:
   - Support different authentication methods (API key, OAuth, etc.)
   - Allow customization of authentication handling

4. **Error Handling**:
   - Generate appropriate error handling code
   - Map HTTP status codes to exceptions
   - Provide helpful error messages

### Client Usage

The generated client will follow this pattern:

```python
# For synchronous clients (requests, httpx)
client = APIClient(
    base_url="https://api.example.com",
    auth_token="your_auth_token"
)
result = client.operation_name(path_param=value, query_param=value, body=payload)

# For asynchronous clients (aiohttp, httpx)
client = APIClient(
    base_url="https://api.example.com",
    auth_token="your_auth_token"
)
result = await client.operation_name(path_param=value, query_param=value, body=payload)
await client.close()  # Don't forget to close the client
```

## Conclusion

This implementation plan provides a roadmap for developing the OpenAPI Client Generator tool. By following this plan, we will create a robust and flexible tool that can generate Python client libraries from OpenAPI specifications, supporting multiple HTTP client libraries and providing a clean, Pythonic interface to the API.
