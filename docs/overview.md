# OpenAPI Client Generator

## Overview

The `openapi_client_generator` is a command-line tool designed to generate Python client libraries from OpenAPI v3 specifications. It simplifies the process of interacting with RESTful APIs by automatically generating client code that handles the details of making HTTP requests, serializing/deserializing data, and managing authentication.

## Features

- Generates Python client libraries from OpenAPI v3 specifications
- Supports multiple HTTP client libraries:
  - `requests`: Synchronous HTTP client
  - `aiohttp`: Asynchronous HTTP client
  - `httpx`: Modern HTTP client with both synchronous and asynchronous support
- Handles serialization and deserialization of request/response data
- Generates type hints for better IDE support and code quality
- Provides a clean, Pythonic interface to the API

## Command-Line Interface

The tool is used via a command-line interface with the following arguments:

```
openapi_client_generator [OPTIONS] SPEC_PATH
```

### Required Arguments

- `SPEC_PATH`: Path to the OpenAPI specification file (JSON or YAML format)

### Optional Arguments

- `--requests`: Generate a client using the `requests` library (synchronous)
- `--aiohttp`: Generate a client using the `aiohttp` library (asynchronous)
- `--httpx`: Generate a client using the `httpx` library (both synchronous and asynchronous)
- `--output-dir PATH`: Directory where the generated client will be placed (default: current directory)
- `--package-name NAME`: Name of the generated Python package (default: derived from the API title in the spec)
- `--no-models`: Skip generation of model classes

## HTTP Client Libraries

### requests

The `requests` option generates a synchronous client using the popular `requests` library. This is a good choice for scripts, command-line tools, or applications that don't require asynchronous operation.

### aiohttp

The `aiohttp` option generates an asynchronous client using the `aiohttp` library. This is ideal for high-performance applications that need to make many concurrent API calls, such as web servers or data processing pipelines.

### httpx

The `httpx` option generates a client using the `httpx` library, which supports both synchronous and asynchronous operation. This is a good choice for libraries or applications that need to support both modes of operation.

## Input/Output

### Input

The tool takes an OpenAPI v3 specification file as input. This file can be in either JSON or YAML format and must conform to the OpenAPI v3 specification.

### Output

The tool generates a Python package containing:

- An `APIClient` class for interacting with the API
- Model classes representing the data structures used by the API
- Utility functions for authentication, serialization, etc.

#### Generated Client Structure

The generated client follows this structure:

- `APIClient`: The main class that users will instantiate to interact with the API
  - Constructor parameters include:
    - Custom cookiejar (optional)
    - Authentication token (optional)
    - Library-specific parameters (optional)
  - Methods are named after the `operationId` in the OpenAPI spec, transformed to `python_case`
    - For example, if the OpenAPI spec has an operation with `operationId: getUserProfile`, the generated method will be `get_user_profile()`
  - Method parameters follow these conventions:
    - Path and query string parameters are passed as named arguments with the same name but "pythonized"
      - For example, if the API endpoint has a path parameter `{userId}`, the method parameter would be `user_id`
    - Request body payload is passed as a separate argument named `body`

## Usage Examples

### Basic Usage

```bash
# Generate a client using the requests library
openapi_client_generator --requests path/to/openapi.yaml

# Generate a client using the aiohttp library
openapi_client_generator --aiohttp path/to/openapi.json

# Generate a client using the httpx library
openapi_client_generator --httpx path/to/openapi.yaml
```

### Advanced Usage

```bash
# Generate a client with a custom package name and output directory
openapi_client_generator --requests --package-name my_api_client --output-dir ./generated path/to/openapi.yaml
```

### Using the Generated Client

Once you've generated the client, you can use it in your Python code like this:

```python
# For a client generated with the requests library
from my_api_client import APIClient

# Create an instance of the client
client = APIClient(
    base_url="https://api.example.com",
    auth_token="your_auth_token",  # Optional
    timeout=30  # Optional, library-specific parameter
)

# Call API methods (converted from operationId in the OpenAPI spec)
# If the spec has operationId: getUserProfile and a path parameter {userId}
user = client.get_user_profile(user_id=123)

# If the spec has operationId: createNewOrder with query parameters product_id and quantity
# and a request body payload
order = client.create_new_order(
    product_id=456,  # Path or query parameter
    quantity=2,      # Path or query parameter
    body={           # Request body payload
        "shipping_address": {
            "street": "123 Main St",
            "city": "Anytown",
            "zip": "12345"
        },
        "payment_method": "credit_card"
    }
)
```

For asynchronous clients (generated with `--aiohttp` or `--httpx`):

```python
import asyncio
from my_api_client import APIClient

async def main():
    # Create an instance of the async client
    client = APIClient(
        base_url="https://api.example.com",
        auth_token="your_auth_token"
    )

    # Call API methods asynchronously
    user = await client.get_user_profile(user_id=123)  # Path parameter
    order = await client.create_new_order(
        product_id=456,  # Path or query parameter
        quantity=2,      # Path or query parameter
        body={           # Request body payload
            "shipping_details": "express",
            "gift_wrap": True
        }
    )

    # Don't forget to close the client when done
    await client.close()

# Run the async function
asyncio.run(main())
```

## Future Development

Future versions of the tool may include:

- Support for additional HTTP client libraries
- Customization options for the generated code
- Support for OpenAPI extensions
- Integration with API gateways and service discovery mechanisms
