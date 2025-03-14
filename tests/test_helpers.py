"""
Tests for the helpers module.

This module contains tests for the utility functions in the helpers module.
"""

import sys
from pathlib import Path

# Add the project root to the Python path
sys.path.insert(0, str(Path(__file__).parent.parent))

import pytest
from openapi_client_generator.helpers import to_snake_case


class TestToSnakeCase:
    """Tests for the to_snake_case function."""

    def test_camel_case(self):
        """Test converting camelCase to snake_case."""
        assert to_snake_case("camelCase") == "camel_case"
        assert to_snake_case("getUserById") == "get_user_by_id"
        assert to_snake_case("APIClient") == "api_client"

    def test_pascal_case(self):
        """Test converting PascalCase to snake_case."""
        assert to_snake_case("PascalCase") == "pascal_case"
        assert to_snake_case("GetUserById") == "get_user_by_id"
        assert to_snake_case("HTTPResponse") == "http_response"

    def test_snake_case(self):
        """Test converting snake_case to snake_case (no change)."""
        assert to_snake_case("snake_case") == "snake_case"
        assert to_snake_case("get_user_by_id") == "get_user_by_id"
        assert to_snake_case("api_client") == "api_client"

    def test_kebab_case(self):
        """Test converting kebab-case to snake_case."""
        assert to_snake_case("kebab-case") == "kebab_case"
        assert to_snake_case("get-user-by-id") == "get_user_by_id"
        assert to_snake_case("api-client") == "api_client"

    def test_mixed_case(self):
        """Test converting mixed case to snake_case."""
        assert to_snake_case("mixedCase_with-different_separators") == "mixed_case_with_different_separators"
        assert to_snake_case("get_user-byId") == "get_user_by_id"

    def test_special_characters(self):
        """Test converting strings with special characters to snake_case."""
        assert to_snake_case("special@characters") == "special_characters"
        assert to_snake_case("user.name") == "user_name"
        assert to_snake_case("user/profile") == "user_profile"

    def test_empty_string(self):
        """Test converting an empty string."""
        assert to_snake_case("") == ""

    def test_single_character(self):
        """Test converting a single character."""
        assert to_snake_case("A") == "a"
        assert to_snake_case("a") == "a"
        assert to_snake_case("_") == "_"

    def test_numbers(self):
        """Test converting strings with numbers."""
        assert to_snake_case("user123") == "user123"
        assert to_snake_case("user123Name") == "user123_name"
        assert to_snake_case("123User") == "123_user"