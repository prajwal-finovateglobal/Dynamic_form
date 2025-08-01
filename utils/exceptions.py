"""
Custom Exception Classes for CBS Submission System

This module defines custom exceptions with appropriate HTTP status codes
for different types of errors that can occur in the CBS system.
"""

from typing import Any, Dict, List, Optional
from fastapi import HTTPException


class CBSBaseException(Exception):
    """Base exception class for CBS system."""
    
    def __init__(self, message: str, status_code: int = 500, details: Optional[Dict[str, Any]] = None):
        self.message = message
        self.status_code = status_code
        self.details = details or {}
        super().__init__(self.message)


class FormNotFoundException(CBSBaseException):
    """Raised when a form is not found in the database."""
    
    def __init__(self, form_id: int, details: Optional[Dict[str, Any]] = None):
        message = f"Form with ID {form_id} not found"
        super().__init__(message, status_code=404, details=details)


class SubFormNotFoundException(CBSBaseException):
    """Raised when a subform is not found in the database."""
    
    def __init__(self, sub_form_id: int, details: Optional[Dict[str, Any]] = None):
        message = f"Subform with ID {sub_form_id} not found"
        super().__init__(message, status_code=404, details=details)


class AttributeNotFoundException(CBSBaseException):
    """Raised when an attribute is not found in the database."""
    
    def __init__(self, attribute_id: int, details: Optional[Dict[str, Any]] = None):
        message = f"Attribute with ID {attribute_id} not found"
        super().__init__(message, status_code=404, details=details)


class ValidationError(CBSBaseException):
    """Raised when form data validation fails."""
    
    def __init__(self, message: str, errors: List[str], details: Optional[Dict[str, Any]] = None):
        self.errors = errors
        details = details or {}
        details["validation_errors"] = errors
        super().__init__(message, status_code=422, details=details)


class RequiredAttributeMissingError(ValidationError):
    """Raised when a required attribute is missing from the submission."""
    
    def __init__(self, missing_attributes: List[str], details: Optional[Dict[str, Any]] = None):
        message = f"Required attributes missing: {', '.join(missing_attributes)}"
        super().__init__(message, missing_attributes, details)


class DataTypeMismatchError(ValidationError):
    """Raised when the data type doesn't match the expected type."""
    
    def __init__(self, attribute_id: int, expected_type: str, actual_value: Any, details: Optional[Dict[str, Any]] = None):
        message = f"Data type mismatch for attribute {attribute_id}: expected {expected_type}, got {type(actual_value).__name__}"
        errors = [message]
        super().__init__(message, errors, details)


class DatabaseError(CBSBaseException):
    """Raised when a database operation fails."""
    
    def __init__(self, message: str, table_name: Optional[str] = None, details: Optional[Dict[str, Any]] = None):
        self.table_name = table_name
        details = details or {}
        if table_name:
            details["table_name"] = table_name
        super().__init__(message, status_code=500, details=details)


class InsertionError(DatabaseError):
    """Raised when record insertion fails."""
    
    def __init__(self, table_name: str, record_data: Dict[str, Any], original_error: Exception, details: Optional[Dict[str, Any]] = None):
        message = f"Failed to insert record into table '{table_name}'"
        details = details or {}
        details["record_data"] = record_data
        details["original_error"] = str(original_error)
        super().__init__(message, table_name, details)


class ForeignKeyError(DatabaseError):
    """Raised when a foreign key constraint is violated."""
    
    def __init__(self, table_name: str, fk_column: str, fk_value: Any, details: Optional[Dict[str, Any]] = None):
        message = f"Foreign key constraint violation in table '{table_name}' for column '{fk_column}' with value '{fk_value}'"
        details = details or {}
        details["fk_column"] = fk_column
        details["fk_value"] = fk_value
        super().__init__(message, table_name, details)


class MetadataConfigurationError(CBSBaseException):
    """Raised when metadata configuration is invalid."""
    
    def __init__(self, message: str, form_id: Optional[int] = None, sub_form_ids: Optional[List[int]] = None, details: Optional[Dict[str, Any]] = None):
        self.form_id = form_id
        self.sub_form_ids = sub_form_ids
        details = details or {}
        if form_id:
            details["form_id"] = form_id
        if sub_form_ids:
            details["sub_form_ids"] = sub_form_ids
        super().__init__(message, status_code=400, details=details)


class TableDependencyError(CBSBaseException):
    """Raised when there's an issue with table dependencies."""
    
    def __init__(self, message: str, table_name: Optional[str] = None, dependency_graph: Optional[Dict[str, List[str]]] = None, details: Optional[Dict[str, Any]] = None):
        self.table_name = table_name
        self.dependency_graph = dependency_graph
        details = details or {}
        if table_name:
            details["table_name"] = table_name
        if dependency_graph:
            details["dependency_graph"] = dependency_graph
        super().__init__(message, status_code=400, details=details)


class CircularDependencyError(TableDependencyError):
    """Raised when a circular dependency is detected in table relationships."""
    
    def __init__(self, circular_path: List[str], details: Optional[Dict[str, Any]] = None):
        message = f"Circular dependency detected: {' -> '.join(circular_path)}"
        details = details or {}
        details["circular_path"] = circular_path
        super().__init__(message, table_name=circular_path[0] if circular_path else None, details=details)


class PayloadMappingError(CBSBaseException):
    """Raised when there's an error mapping payload to tables."""
    
    def __init__(self, message: str, form_id: Optional[int] = None, sub_form_ids: Optional[List[int]] = None, details: Optional[Dict[str, Any]] = None):
        self.form_id = form_id
        self.sub_form_ids = sub_form_ids
        details = details or {}
        if form_id:
            details["form_id"] = form_id
        if sub_form_ids:
            details["sub_form_ids"] = sub_form_ids
        super().__init__(message, status_code=400, details=details)


class ConfigurationError(CBSBaseException):
    """Raised when there's a configuration error."""
    
    def __init__(self, message: str, config_key: Optional[str] = None, details: Optional[Dict[str, Any]] = None):
        self.config_key = config_key
        details = details or {}
        if config_key:
            details["config_key"] = config_key
        super().__init__(message, status_code=500, details=details)


def convert_cbs_exception_to_http(cbs_exception: CBSBaseException) -> HTTPException:
    """Convert a CBS exception to a FastAPI HTTPException."""
    return HTTPException(
        status_code=cbs_exception.status_code,
        detail={
            "message": cbs_exception.message,
            "error_type": cbs_exception.__class__.__name__,
            "details": cbs_exception.details
        }
    )


def handle_database_error(error: Exception, table_name: Optional[str] = None) -> DatabaseError:
    """Convert a database exception to a CBS DatabaseError."""
    if "foreign key" in str(error).lower():
        return ForeignKeyError(table_name or "unknown", "unknown", "unknown", {"original_error": str(error)})
    else:
        return DatabaseError(f"Database operation failed: {str(error)}", table_name, {"original_error": str(error)}) 