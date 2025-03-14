import sys
import os
import json
import tempfile
from pathlib import Path

# Add the project root to the Python path
sys.path.insert(0, os.path.abspath('.'))

# Import the main module
from openapi_client_generator.__main__ import main

# Create a sample OpenAPI specification
sample_spec = {
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

# Create a temporary file with the sample specification
with tempfile.NamedTemporaryFile(suffix=".json", mode="w+", delete=False) as f:
    json.dump(sample_spec, f)
    spec_path = f.name

# Create output directory if it doesn't exist
os.makedirs("test_output_aiohttp", exist_ok=True)

# Mock the command-line arguments
sys.argv = [
    'openapi_client_generator',
    '--aiohttp',
    '--output-dir', 'test_output_aiohttp',
    spec_path
]

# Run the main function
try:
    main()
    print("Success! The command ran without errors.")
except Exception as e:
    print(f"Error: {e}")
finally:
    # Clean up the temporary file
    os.unlink(spec_path)