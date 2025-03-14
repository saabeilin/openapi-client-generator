"""
Parser module for OpenAPI Client Generator.

This module provides functionality for parsing OpenAPI specifications.
"""

from .openapi_parser import OpenAPIParser
from .models import OpenAPISpec

__all__ = ["OpenAPIParser", "OpenAPISpec"]