from sqlalchemy import insert
from schemas.submission import SubmissionPayload
from utils.logger import get_logger

from db.dependencies import DB_dependency

from services.submission_helpers.table_lookup import extract_all_unique_tables_from_payload
from services.submission_helpers.graph_builder import build_table_dependency_graph
from services.submission_helpers.topo_sort import topological_sort
from services.submission_helpers.payload_mapper import map_payload_to_tables
from services.submission_helpers.validator import validate_required_attributes
from services.submission_helpers.db_inserter import insert_records_with_attribute_and_fk_mapping

logger = get_logger("submission_service_logger")

class SubmissionService:

    @staticmethod
    async def handle_submission(payload: SubmissionPayload, db: DB_dependency):
        logger.info("Payload received in submission service layer")
        logger.debug(f"Payload contents: {payload.model_dump()}")

        try:
            logger.info("Starting submission processing...")

            validate_required_attributes(db, payload.model_dump())

            table_names = extract_all_unique_tables_from_payload(db, payload.model_dump())
            logger.info(f"Tables involved in this submission: {table_names}")

            graph = build_table_dependency_graph(db, table_names)
            logger.debug(f"Dependency Graph: {graph}")

            insertion_order = topological_sort(graph)
            logger.info(f"Topological Insert Order: {insertion_order}")

            table_records_map = map_payload_to_tables(db, payload.model_dump())
            logger.info(f"Table-wise Mapped Records: {table_records_map}")

            inserted_mapping =insert_records_with_attribute_and_fk_mapping(
                db=db, 
                table_insert_order=insertion_order, 
                table_records_map=table_records_map
            )
            logger.info("Submission flow completed successfully")
            logger.debug(f"Final PK Mapping: {inserted_mapping}")

            return {
                "message": "Submission successful",
                "generated_ids": inserted_mapping,
                "insert_order": insertion_order,
                "tables_inserted": list(table_records_map.keys())
            }
        except Exception as e:
            logger.error(f"Error in submission flow: {e}")
            return {
                "status": "error",
                "message": str(e)
            }
