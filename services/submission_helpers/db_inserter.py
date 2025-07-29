from sqlalchemy import Table, insert
from sqlalchemy.exc import SQLAlchemyError
from db.dependencies import DB_dependency
from typing import List, Dict, Any
from repositories.attribute import get_attributes_by_ids
from db.session import metadata
from utils.logger import get_logger

logger = get_logger("dB_inserter_logger")


def insert_records_with_attribute_and_fk_mapping(
    db: DB_dependency,
    table_insert_order: List[str],
    table_records_map: Dict[str, Dict[str, List[Dict[str, Any]]]]
) -> Dict[str, Any]:
    """
    Inserts records into DB in topological order.
     Converts attribute IDs → column names.
     Captures PKs for each inserted record.
     Handles multiple PK → FK mappings for child tables.
     Logs every important step for debugging.
    """

    generated_ids: Dict[str, Any] = {}

    try:
        for table_name in table_insert_order:
            logger.info(f" Processing table: {table_name}")

            #  Validate metadata
            if table_name not in metadata.tables:
                logger.warning(f" Table {table_name} not found in metadata. Skipping.")
                continue

            if table_name not in table_records_map:
                logger.info(f" No records found for table: {table_name}")
                continue

            table_obj: Table = metadata.tables[table_name]
            records = table_records_map[table_name].get("records", [])

            if not records:
                logger.info(f" No data to insert for table: {table_name}")
                continue

            #  Build attribute_id → column_name mapping
            attr_ids = {k for r in records for k in r.keys() if k.isdigit()}
            attributes = get_attributes_by_ids(db, list(map(int, attr_ids)))
            attr_map = {str(attr.attribute_id): attr.name for attr in attributes}

            pk_col_name = list(table_obj.primary_key.columns.keys())[0]

            for record in records:
                logger.info(f" Preparing to insert record: {record}")
                logger.debug(f"Current generated_ids state: {generated_ids}")

                transformed_record = {}

                for attr_id, value in record.items():
                    if attr_id == "fk_targets":
                        continue
                    col_name = attr_map.get(attr_id)
                    if col_name:
                        transformed_record[col_name] = value

                #  Inject FK values from previously inserted tables
                logger.debug(f"Checking for FK injections into {table_name}")
                for parent_table, parent_data in generated_ids.items():
                    if parent_table == table_name:
                        logger.debug(f"Skipping same table {parent_table}")
                        continue

                    logger.debug(f"Checking parent table {parent_table} with data: {parent_data}")
                    parent_pk_col = str(parent_data.get("pk_col"))
                    parent_pk_val = str(parent_data.get("pk_value"))

                    # Don't inject if it's the primary key of current table
                    if parent_pk_col in table_obj.columns and parent_pk_col not in transformed_record and parent_pk_col != pk_col_name:
                        transformed_record[parent_pk_col] = parent_pk_val
                        logger.debug(f" Added FK {parent_pk_col}={parent_pk_val} to {table_name}")

                    #  Inject mapped FKs from parent table
                    for fk_col, mapping in parent_data.get("mappings", {}).items():
                        fk_col = str(fk_col)
                        logger.debug(f"Checking FK mapping: {fk_col} -> {mapping} for table {table_name}")
                        # Don't inject if it's the primary key of current table
                        if fk_col in table_obj.columns and fk_col not in transformed_record and fk_col != pk_col_name:
                            if mapping:
                                fk_value = list(mapping.values())[-1]
                                transformed_record[fk_col] = fk_value
                                logger.debug(f"  Added mapped FK {fk_col}={fk_value} to {table_name}")
                            else:
                                logger.debug(f"  Empty mapping for {fk_col}")
                        else:
                            logger.debug(f"  FK {fk_col} not applicable: in_columns={fk_col in table_obj.columns}, in_record={fk_col in transformed_record}, is_pk={fk_col == pk_col_name}")

                # Check if this table has any mappings that should be applied
                if table_name in generated_ids and "mappings" in generated_ids[table_name]:
                    logger.debug(f"Table {table_name} has pre-existing mappings: {generated_ids[table_name]['mappings']}")
                    for fk_col, mapping in generated_ids[table_name]["mappings"].items():
                        if fk_col in table_obj.columns and fk_col not in transformed_record and fk_col != pk_col_name:
                            if mapping:
                                fk_value = list(mapping.values())[-1]
                                transformed_record[fk_col] = fk_value
                                logger.debug(f"  Applied pre-existing mapping {fk_col}={fk_value} to {table_name}")
                        else:
                            logger.debug(f"  Pre-existing mapping {fk_col} not applicable")

                try:
                    #  Insert record
                    result = db.execute(insert(table_obj).values(transformed_record))
                    inserted_pk = result.inserted_primary_key[0]
                    logger.info(f" Inserted into {table_name} → PK={inserted_pk}.")

                    generated_ids[table_name] = {
                        "pk_col": pk_col_name,
                        "pk_value": inserted_pk,
                        "mappings": generated_ids.get(table_name, {}).get("mappings", {}),
                    }

                    if "fk_targets" in record:
                        for target in record["fk_targets"]:
                            tgt_table = target["target_table"]
                            tgt_fk_col = target.get("target_pk") or target.get("target_fk_column")
                            
                            if tgt_table not in generated_ids:
                                generated_ids[tgt_table] = {"pk_col": None, "pk_value": None, "mappings": {}}

                            if tgt_fk_col not in generated_ids[tgt_table]["mappings"]:
                                generated_ids[tgt_table]["mappings"][tgt_fk_col] = {}

                            generated_ids[tgt_table]["mappings"][tgt_fk_col][str(inserted_pk)] = inserted_pk
                            logger.debug(f" FK Mapping saved: {tgt_table}.{tgt_fk_col} → {inserted_pk}")

                    db.commit()

                except SQLAlchemyError as e:
                    logger.error(f" DB Error inserting into {table_name}: {e}")
                    db.rollback()
                    raise

        logger.info(" All records inserted successfully.")
        logger.debug(f"Final Generated IDs: {generated_ids}")
        return generated_ids

    except Exception as e:
        logger.error(f" Fatal Error in insert flow: {e}")
        db.rollback()
        raise
