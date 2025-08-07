from db.dependencies import DB_dependency
from typing import Dict, List, Any
from uuid import UUID
from repositories.attribute import get_attributes_by_ids
from repositories.form import get_form_by_id
from repositories.subForm import get_sub_forms_by_ids
from utils.logger import get_logger
from utils.exceptions import (
    ValidationError,
    RequiredAttributeMissingError,
    DataTypeMismatchError,
    FormNotFoundException,
    SubFormNotFoundException
)

logger = get_logger("validation_logger")

ALLOWED_ATTRIBUTE_TYPES = {
    "STRING", "INTEGER", "DOUBLE", "BOOLEAN", "DATE",
    "LONG", "UUID", "BIGINT", "BIGDECIMAL",
    "LOCALDATE", "LOCALDATETIME", "LOCALTIME", "ARRAY"
}

def _validate_type(value: Any, data_type: str) -> bool:
    import json
    data_type = data_type.upper()

    if data_type not in ALLOWED_ATTRIBUTE_TYPES:
        raise ValueError(f"Unsupported attribute data type: {data_type}")

    # All values are strings, so handle accordingly
    if data_type == "STRING":
        return isinstance(value, str)
    elif data_type in ["INTEGER", "BIGINT", "LONG"]:
        try:
            int(value)
            return True
        except (ValueError, TypeError):
            return False
    elif data_type in ["DOUBLE", "BIGDECIMAL"]:
        try:
            float(value)
            return True
        except (ValueError, TypeError):
            return False
    elif data_type == "BOOLEAN":
        if isinstance(value, str):
            return value.strip().lower() in ["true", "false", "1", "0", "yes", "no"]
        return False
    elif data_type in ["DATE", "LOCALDATE", "LOCALDATETIME", "LOCALTIME"]:
        return isinstance(value, str)  # Optionally, add date format validation
    elif data_type == "UUID":
        try:
            UUID(str(value))
            return True
        except (ValueError, TypeError):
            return False
    # if data_type == "ARRAY":
        # Accept JSON string representing a list
    elif data_type == "ARRAY":
        if isinstance(value, str):
            try:
                arr = json.loads(value)
                return isinstance(arr, list)
            except Exception:
                return False
        return False

    return False 

def _validate_attributes_by_ids(
    db: DB_dependency,
    source_name: str,
    provided_values: Dict[str, Any],
    attribute_ids: List[int],
    required_attribute_ids: List[int],
    errors: List[str]
) -> None:
    """
    Validates if all attributes with the given IDs exist in the database.
    """

    logger.info(f"Required attributes IDs: {required_attribute_ids}")
    logger.info(f"Provided values: {provided_values}")

    attributes = get_attributes_by_ids(db, attribute_ids)
    attr_map = {attr.attribute_id: attr for attr in attributes}

    # Check if all required attributes are present in the provided values
    for required_attr_id in required_attribute_ids:
        if str(required_attr_id) not in provided_values or provided_values.get(str(required_attr_id)) in [None, ""]:
            errors.append(f"[{source_name}] Missing required attribute ID: {required_attr_id}")

    for attr in attr_map.values():
        attr_id = attr.attribute_id
        value = provided_values.get(str(attr_id))

        logger.info(f"Attribute ID: {attr_id}, Value: {value}")

        # For all attributes (required or not), validate data type if value is provided
        if value is not None and value != "":
            logger.info(f"check : {attr.attribute_data_type}")
            if not _validate_type(value, attr.attribute_data_type):
                errors.append(f"[{source_name}] Attribute {attr_id} expects {attr.attribute_data_type}, got {type(value).__name__}")
    
    logger.info(f"Errors: {errors}")


def validate_required_attributes(
    db: DB_dependency,
    payload: Dict[str, Any]
) -> None:
    """
    Validates if all required attributes are present in the payload.
    """
    form_id = payload.get("form_id")
    if not form_id:
        raise ValidationError("Form ID is missing in the payload", ["Form ID is required"])
    
    sub_forms = payload.get("sub_forms", [])

    all_errors = []

    form = get_form_by_id(db, form_id)
    if not form:
        raise FormNotFoundException(form_id)
    
    form_values = payload.get("values", {})
    form_attribute_ids = list(map(int, form_values.keys()))

    _validate_attributes_by_ids(
        db=db,
        source_name= f"Form {form_id}",
        provided_values=form_values,
        attribute_ids=form_attribute_ids,
        required_attribute_ids=form.required_attribute_ids,
        errors=all_errors
    )

    sub_form_ids = [sub_form.get("sub_form_id") for sub_form in sub_forms]
    sub_form_models = get_sub_forms_by_ids(db, sub_form_ids)
    sub_form_table_map = {sub_form.sub_form_id: sub_form.table_name for sub_form in sub_form_models}
    sub_form_required_attribute_ids_map = {
        sub_form.sub_form_id: sub_form.required_attribute_ids or [] 
        for sub_form in sub_form_models
    }

    for sub_form in sub_forms:
        sub_form_id = sub_form.get("sub_form_id")
        required_ids = sub_form_required_attribute_ids_map.get(sub_form_id, [])
        sub_form_values = sub_form.get("values", [])

        if not sub_form_values:
            logger.warning(f"Sub-form {sub_form_id} has no values, skipping validation.")
            continue

        if isinstance(sub_form_values, dict):
            sub_form_values = [sub_form_values]
        
        for record in  sub_form_values:
            record_ids = list(map(int, record.keys()))
            _validate_attributes_by_ids(
                db=db,
                source_name=f"Sub_form {sub_form_id}",
                provided_values=record,
                attribute_ids=record_ids,
                required_attribute_ids=required_ids,
                errors=all_errors
            )
    logger.info(f"All errors: {all_errors}")
    if all_errors:
        raise ValidationError(f"Validation failed for form {form_id}", all_errors)
    
    