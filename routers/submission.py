from fastapi import APIRouter
from starlette.routing import Router
from services.submission_service import SubmissionService
from db.dependencies import DB_dependency
from schemas.submission import (
    SubmissionPayload
)
from utils.logger import get_logger

logger = get_logger("submission_router_logger")

router = APIRouter()

@router.post("/submit")
async def submit_form(
    payload: SubmissionPayload,
    db: DB_dependency
):
    """
    Submit a form dynamically.
    """
    logger.info("Submission endpoint called")
    return await SubmissionService.handle_submission(payload, db)
