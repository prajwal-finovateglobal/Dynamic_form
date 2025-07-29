# from fastapi import APIRouter, Depends, Request
# from db.dependencies import DB_dependency
# from utils.logger import get_logger

# from services.submission_service import SubmissionService
# from schemas.submission import SubmissionPayload

# from services.submission_helpers.payload_mapper import map_payload_to_tables
# from services.submission_helpers.table_lookup import extract_all_unique_tables_from_payload
# from services.submission_helpers.graph_builder import build_table_dependency_graph
# from services.submission_helpers.topo_sort import topological_sort
# from services.submission_helpers.db_inserter import insert_records_with_attribute_mapping

# logger = get_logger("debug_router_logger")


# router = APIRouter()

# @router.post("/test-submission")
# async def test_submission_route(
#     payload: SubmissionPayload,
#     db: DB_dependency
# ):
#     return await SubmissionService.handle_submission(payload=payload, db=db)

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
