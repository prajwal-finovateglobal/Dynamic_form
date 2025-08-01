from sqlalchemy import insert
from schemas.submission import SubmissionPayload
from utils.logger import get_logger
from utils.exceptions import (
    FormNotFoundException,
    ValidationError,
    DatabaseError,
    PayloadMappingError,
    MetadataConfigurationError
)

from db.dependencies import DB_dependency

from services.submission_helpers.table_lookup import extract_all_unique_tables_from_payload
from services.submission_helpers.graph_builder import build_table_dependency_graph
from services.submission_helpers.topo_sort import topological_sort
from services.submission_helpers.payload_mapper import map_payload_to_tables
from services.submission_helpers.validator import validate_required_attributes
from services.submission_helpers.db_inserter import insert_records_with_attribute_and_fk_mapping
from utils.metadata_utils import create_metadata_handler

logger = get_logger("submission_service_logger")

class SubmissionService:

    @staticmethod
    async def handle_submission(payload: SubmissionPayload, db: DB_dependency, ip_address: str = None, user_id: str = None, user_agent: str = None):
        logger.info("Payload received in submission service layer")
        logger.debug(f"Payload contents: {payload.model_dump()}")

        try:
            logger.info("Starting submission processing...")

            # Validate required attributes
            try:
                validate_required_attributes(db, payload.model_dump())
            except Exception as e:
                raise ValidationError("Form validation failed", [str(e)])

            # Extract table names
            try:
                table_names = extract_all_unique_tables_from_payload(db, payload.model_dump())
                logger.info(f"Tables involved in this submission: {table_names}")
            except Exception as e:
                raise PayloadMappingError(f"Failed to extract table names: {str(e)}", payload.form_id)

            # Build dependency graph
            try:
                graph = build_table_dependency_graph(db, table_names)
                logger.debug(f"Dependency Graph: {graph}")
            except Exception as e:
                raise PayloadMappingError(f"Failed to build dependency graph: {str(e)}", payload.form_id)

            # Perform topological sort
            try:
                insertion_order = topological_sort(graph)
                logger.info(f"Topological Insert Order: {insertion_order}")
            except Exception as e:
                raise PayloadMappingError(f"Failed to determine insertion order: {str(e)}", payload.form_id)

            # Map payload to tables
            try:
                table_records_map = map_payload_to_tables(db, payload.model_dump())
                logger.info(f"Table-wise Mapped Records: {table_records_map}")
            except Exception as e:
                raise PayloadMappingError(f"Failed to map payload to tables: {str(e)}", payload.form_id)

            # Extract form_id and sub_form_ids from payload for metadata handling
            form_id = payload.form_id
            sub_form_ids = [sub_form.sub_form_id for sub_form in payload.sub_forms]
            
            logger.info(f"Processing metadata for form_id={form_id}, sub_form_ids={sub_form_ids}")
            logger.info(f"Request metadata - IP: {ip_address}, User: {user_id}, User-Agent: {user_agent}")

            # Create metadata handler and inject metadata into records
            try:
                metadata_handler = create_metadata_handler(db)
                table_records_map_with_metadata = metadata_handler.inject_metadata_into_records(
                    table_records_map=table_records_map,
                    form_id=form_id,
                    sub_form_ids=sub_form_ids,
                    ip_address=ip_address,
                    user_id=user_id
                )
            except Exception as e:
                raise MetadataConfigurationError(f"Failed to inject metadata: {str(e)}", form_id, sub_form_ids)

            # Insert records
            try:
                inserted_mapping = insert_records_with_attribute_and_fk_mapping(
                    db=db, 
                    table_insert_order=insertion_order, 
                    table_records_map=table_records_map_with_metadata
                )
            except Exception as e:
                raise DatabaseError(f"Failed to insert records: {str(e)}")

            logger.info("Submission flow completed successfully")
            logger.debug(f"Final PK Mapping: {inserted_mapping}")

            return {
                "message": "Submission successful",
                "generated_ids": inserted_mapping,
                "insert_order": insertion_order,
                "tables_inserted": list(table_records_map.keys())
            }
        except (ValidationError, PayloadMappingError, MetadataConfigurationError, DatabaseError):
            # Re-raise CBS exceptions as-is
            raise
        except Exception as e:
            logger.error(f"Unexpected error in submission flow: {e}")
            raise DatabaseError(f"Unexpected error during submission: {str(e)}")
