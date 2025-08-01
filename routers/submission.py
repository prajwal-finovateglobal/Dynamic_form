from fastapi import APIRouter, Request, HTTPException
from starlette.routing import Router
from services.submission_service import SubmissionService
from db.dependencies import DB_dependency
from schemas.submission import (
    SubmissionPayload
)
from utils.logger import get_logger
from utils.exceptions import CBSBaseException, convert_cbs_exception_to_http

logger = get_logger("submission_router_logger")

router = APIRouter()

@router.post("/submit")
async def submit_form(
    request: Request,
    payload: SubmissionPayload,
    db: DB_dependency
):
    """
    Submit a form dynamically.
    """
    logger.info("Submission endpoint called")
    
    # Extract IP address from request
    ip_address = None
    if request.headers.get("X-Forwarded-For"):
        ip_address = request.headers.get("X-Forwarded-For").split(",")[0].strip()
    elif request.headers.get("X-Real-IP"):
        ip_address = request.headers.get("X-Real-IP")
    elif request.client:
        ip_address = request.client.host
    
    # Extract user agent
    user_agent = request.headers.get("User-Agent")
    
    # TODO: Extract user_id from authentication context
    # For now, we'll use a placeholder - this should be implemented based on your auth system
    user_id = None  # Should be extracted from JWT token, session, or other auth mechanism
    
    logger.info(f"Request from IP: {ip_address}, User-Agent: {user_agent}")
    
    try:
        return await SubmissionService.handle_submission(payload, db, ip_address, user_id, user_agent)
    except CBSBaseException as e:
        # Convert CBS exceptions to HTTP exceptions
        raise convert_cbs_exception_to_http(e)
    except Exception as e:
        # Handle any other unexpected errors
        logger.error(f"Unexpected error in submission endpoint: {e}")
        raise HTTPException(
            status_code=500,
            detail={
                "message": "An unexpected error occurred",
                "error_type": "InternalServerError",
                "details": {"original_error": str(e)}
            }
        )
