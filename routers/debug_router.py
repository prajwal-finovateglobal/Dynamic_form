from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from db.dependencies import get_db
from schemas.submission import SubmissionPayload
from services.submission_service import SubmissionService

router = APIRouter(prefix="/debug", tags=["Debug"])

@router.post("/test-submission")
async def test_submission_flow(
    payload: SubmissionPayload,
    db: Session = Depends(get_db)
):
    return await SubmissionService.handle_submission(payload, db)
