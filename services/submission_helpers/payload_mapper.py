from hmac import new
from db.dependencies import DB_dependency
from repositories.form import get_form_by_id
from repositories.subForm import get_sub_forms_by_ids
from repositories.fk_mapping import get_fk_mappings_for_subforms
from utils.logger import get_logger

logger = get_logger("payload_mapper_logger")

def map_payload_to_tables(db: DB_dependency, payload: dict) -> dict:
    """
    Converts submission payload into table-wise grouped records ready for DB insert.
    Also attaches _fk_targets for records that need FK propagation.
    """
    form_id = payload.get('form_id')
    sub_forms = payload.get('sub_forms')

    table_records_map = {}

    # ---- Process Form Table ----
    form_model = get_form_by_id(db, form_id)
    if not form_model or not form_model.table_name:
        logger.error(f"Form with ID {form_id} not found or has no table name.")
        raise ValueError(f"Form with ID {form_id} not found or has no table name.")

    table_records_map[form_model.table_name] = {
        "records" : [payload.get('values', [])]
    }


    # ---- Process SubForm Table ----
    sub_form_ids = [sub_form['sub_form_id'] for sub_form in sub_forms]
    sub_form_models = get_sub_forms_by_ids(db, sub_form_ids)
    id_to_table = {sub_form.sub_form_id: sub_form.table_name for sub_form in sub_form_models if sub_form.table_name}

    # Fetch FK mappings for these subforms
    fk_mappings = get_fk_mappings_for_subforms(db, sub_form_ids)

    # Build lookup dict for FK mappings
    fk_map_dict = {}
    for fk_mapping in fk_mappings:
        fk_map_dict.setdefault(fk_mapping.sub_form_id, []).append({
            "source_table" : fk_mapping.source_table,
            "source_pk" : fk_mapping.source_pk,
            "target_table" : fk_mapping.target_table,
            "target_fk_column" : fk_mapping.target_fk_column
        })
    # ---- Process Each SubForm ----
    for sub_form in sub_forms:
        sub_form_id = sub_form['sub_form_id']
        sub_form_table_name = id_to_table.get(sub_form_id)

        if not sub_form_table_name:
            logger.warning(f"Sub-form with ID {sub_form_id} not found or has no table name.")
            continue
        
        sub_form_values = sub_form.get('values')


        if not sub_form_values:
            logger.warning(f"Sub-form with ID {sub_form_id} has no values.")
            continue

        if isinstance(sub_form_values, list):
            records = sub_form_values
        elif isinstance(sub_form_values, dict):
            records = [sub_form_values]
        else:
            logger.warning(f"Unsupported value format in subform ID {sub_form_id}")
            continue

        # attach FK targets if mapping exists
        for record in records:
            if sub_form_id in fk_map_dict:
                record['fk_targets'] = fk_map_dict[sub_form_id]

        # Add or merge records
        if sub_form_table_name not in table_records_map:
            table_records_map[sub_form_table_name] = { "records": records }
        else:
            existing_records = table_records_map[sub_form_table_name]["records"]

            if len(existing_records)==1 and len(records)==1:
                existing_keys = set(existing_records[0].keys()) - {"fk_targets"}
                new_keys = set(records[0].keys()) - {"fk_targets"}

                if existing_keys.isdisjoint(new_keys):
                    # Merge attributes if single record in both
                    existing_records[0].update(records[0])
                else:
                    existing_records.extend(records)
            else:
                # Otherwise, append
                existing_records.extend(records)
                


        # if isinstance(sub_form_values, list):
        #     if sub_form_table_name not in table_records_map:
        #         table_records_map[sub_form_table_name] = { "records": sub_form_values }
        #     else:
        #         table_records_map[sub_form_table_name]["records"].extend(sub_form_values)
        # elif isinstance(sub_form_values, dict):
        #     if sub_form_table_name in table_records_map:
        #         existing_records = table_records_map[sub_form_table_name]["records"]
        #         if len(existing_records) == 1:
        #             existing_records[0].update(sub_form_values)
        #         else:
        #             # Append separately if there are already multiple (unexpected)
        #             existing_records.append(sub_form_values)
        #     else:
        #         table_records_map[sub_form_table_name] = {"records": [sub_form_values]}
        # else:
        #     logger.warning(f"Unsupported value format in subform ID {sub_form_id}")
        #     continue


        
    logger.debug(f"Mapped payload to tables: {table_records_map}")
    return table_records_map