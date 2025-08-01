"""
Global Exception Handlers for CBS Submission System

This module provides exception handlers for FastAPI to handle CBS exceptions
and other errors with appropriate HTTP status codes and error responses.
"""

from fastapi import Request, status
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from sqlalchemy.exc import SQLAlchemyError, IntegrityError, DataError
from typing import Union
import traceback

from utils.exceptions import (
    CBSBaseException, 
    convert_cbs_exception_to_http,
    handle_database_error,
    DatabaseError
)
from utils.logger import get_logger

logger = get_logger("exception_handlers")


async def cbs_exception_handler(request: Request, exc: CBSBaseException) -> JSONResponse:
    """
    Handle CBS custom exceptions and return appropriate HTTP responses.
    """
    logger.error(f"CBS Exception: {exc.message}", extra={
        "status_code": exc.status_code,
        "error_type": exc.__class__.__name__,
        "details": exc.details,
        "path": request.url.path,
        "method": request.method
    })
    
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "error": {
                "type": exc.__class__.__name__,
                "message": exc.message,
                "status_code": exc.status_code,
                "details": exc.details
            }
        }
    )


async def validation_exception_handler(request: Request, exc: RequestValidationError) -> JSONResponse:
    """
    Handle FastAPI validation errors (422 errors).
    """
    logger.error(f"Validation Error: {exc.errors()}", extra={
        "status_code": status.HTTP_422_UNPROCESSABLE_ENTITY,
        "error_type": "RequestValidationError",
        "path": request.url.path,
        "method": request.method
    })
    
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content={
            "error": {
                "type": "ValidationError",
                "message": "Request validation failed",
                "status_code": status.HTTP_422_UNPROCESSABLE_ENTITY,
                "details": {
                    "validation_errors": exc.errors()
                }
            }
        }
    )


async def database_exception_handler(request: Request, exc: SQLAlchemyError) -> JSONResponse:
    """
    Handle SQLAlchemy database errors.
    """
    logger.error(f"Database Error: {str(exc)}", extra={
        "status_code": status.HTTP_500_INTERNAL_SERVER_ERROR,
        "error_type": exc.__class__.__name__,
        "path": request.url.path,
        "method": request.method,
        "traceback": traceback.format_exc()
    })
    
    # Convert to CBS DatabaseError
    cbs_error = handle_database_error(exc)
    
    return JSONResponse(
        status_code=cbs_error.status_code,
        content={
            "error": {
                "type": cbs_error.__class__.__name__,
                "message": cbs_error.message,
                "status_code": cbs_error.status_code,
                "details": cbs_error.details
            }
        }
    )


async def integrity_error_handler(request: Request, exc: IntegrityError) -> JSONResponse:
    """
    Handle database integrity constraint violations.
    """
    logger.error(f"Integrity Error: {str(exc)}", extra={
        "status_code": status.HTTP_400_BAD_REQUEST,
        "error_type": "IntegrityError",
        "path": request.url.path,
        "method": request.method
    })
    
    # Check for specific constraint violations
    error_message = str(exc)
    if "foreign key" in error_message.lower():
        cbs_error = handle_database_error(exc)
        status_code = status.HTTP_400_BAD_REQUEST
    elif "unique" in error_message.lower():
        cbs_error = DatabaseError("Duplicate record violation", details={"original_error": str(exc)})
        status_code = status.HTTP_409_CONFLICT
    else:
        cbs_error = handle_database_error(exc)
        status_code = status.HTTP_400_BAD_REQUEST
    
    return JSONResponse(
        status_code=status_code,
        content={
            "error": {
                "type": cbs_error.__class__.__name__,
                "message": cbs_error.message,
                "status_code": status_code,
                "details": cbs_error.details
            }
        }
    )


async def data_error_handler(request: Request, exc: DataError) -> JSONResponse:
    """
    Handle database data type errors.
    """
    logger.error(f"Data Error: {str(exc)}", extra={
        "status_code": status.HTTP_400_BAD_REQUEST,
        "error_type": "DataError",
        "path": request.url.path,
        "method": request.method
    })
    
    cbs_error = DatabaseError("Data type error in database operation", details={"original_error": str(exc)})
    
    return JSONResponse(
        status_code=status.HTTP_400_BAD_REQUEST,
        content={
            "error": {
                "type": cbs_error.__class__.__name__,
                "message": cbs_error.message,
                "status_code": status.HTTP_400_BAD_REQUEST,
                "details": cbs_error.details
            }
        }
    )


async def general_exception_handler(request: Request, exc: Exception) -> JSONResponse:
    """
    Handle any unhandled exceptions.
    """
    logger.error(f"Unhandled Exception: {str(exc)}", extra={
        "status_code": status.HTTP_500_INTERNAL_SERVER_ERROR,
        "error_type": exc.__class__.__name__,
        "path": request.url.path,
        "method": request.method,
        "traceback": traceback.format_exc()
    })
    
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={
            "error": {
                "type": "InternalServerError",
                "message": "An unexpected error occurred",
                "status_code": status.HTTP_500_INTERNAL_SERVER_ERROR,
                "details": {
                    "error_type": exc.__class__.__name__,
                    "message": str(exc)
                }
            }
        }
    )


def register_exception_handlers(app):
    """
    Register all exception handlers with the FastAPI app.
    """
    from utils.exceptions import CBSBaseException
    
    # Register CBS custom exceptions
    app.add_exception_handler(CBSBaseException, cbs_exception_handler)
    
    # Register FastAPI validation errors
    app.add_exception_handler(RequestValidationError, validation_exception_handler)
    
    # Register database exceptions
    app.add_exception_handler(SQLAlchemyError, database_exception_handler)
    app.add_exception_handler(IntegrityError, integrity_error_handler)
    app.add_exception_handler(DataError, data_error_handler)
    
    # Register general exception handler (should be last)
    app.add_exception_handler(Exception, general_exception_handler)
    
    logger.info("Exception handlers registered successfully") 