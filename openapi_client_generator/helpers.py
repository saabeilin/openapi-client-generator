"""
Helper functions for OpenAPI Client Generator.

This module provides utility functions used throughout the OpenAPI Client Generator.
"""

import re


def to_snake_case(text: str) -> str:
    """
    Convert a string to snake_case.

    Args:
        text: String to convert

    Returns:
        str: Converted string

    Examples:
        >>> to_snake_case("HelloWorld")
        'hello_world'
        >>> to_snake_case("getUserById")
        'get_user_by_id'
        >>> to_snake_case("user-id")
        'user_id'
        >>> to_snake_case("APIClient")
        'api_client'
        >>> to_snake_case("HTTPResponse")
        'http_response'
    """
    # Replace non-alphanumeric characters with underscores
    s1 = re.sub(r'[^a-zA-Z0-9]', '_', text)

    # Insert underscores between camelCase
    s2 = re.sub(r'([a-z0-9])([A-Z])', r'\1_\2', s1)

    # Insert underscores between consecutive uppercase letters (for acronyms)
    s3 = re.sub(r'([A-Z])([A-Z][a-z])', r'\1_\2', s2)

    # Convert to lowercase
    return s3.lower()
