"""
Pydantic models for OpenAPI specifications.

This module provides Pydantic models for representing OpenAPI specifications.
"""

from typing import Dict, List, Optional, Any, Union
from pydantic import BaseModel, Field


class OpenAPISpec(BaseModel):
    """
    Pydantic model for OpenAPI specification.
    
    This is a simplified model for the OpenAPI specification.
    In a real implementation, this would be a more complete model
    that covers all aspects of the OpenAPI specification.
    """
    
    openapi: str = Field(..., description="OpenAPI version")
    info: Dict[str, Any] = Field(..., description="API information")
    paths: Dict[str, Dict[str, Any]] = Field(..., description="API paths")
    components: Optional[Dict[str, Any]] = Field(None, description="API components")
    
    def get_operations(self) -> List[Dict[str, Any]]:
        """
        Get all operations from the specification.
        
        Returns:
            List[Dict[str, Any]]: List of operations
        """
        operations = []
        
        for path, path_item in self.paths.items():
            for method, operation in path_item.items():
                if method in ["get", "post", "put", "delete", "patch", "options", "head"]:
                    operation_info = {
                        "path": path,
                        "method": method,
                        "operation_id": operation.get("operationId", ""),
                        "summary": operation.get("summary", ""),
                        "description": operation.get("description", ""),
                        "parameters": operation.get("parameters", []),
                        "request_body": operation.get("requestBody", None),
                        "responses": operation.get("responses", {}),
                    }
                    operations.append(operation_info)
        
        return operations