from sqlalchemy import table
from db.dependencies import DB_dependency
from typing import List,Dict
from schemas.submission import SubmissionPayload
from repositories.form import get_forms_by_ids
from repositories.subForm import get_sub_forms_by_ids
from utils.logger import get_logger

logger = get_logger("table_lookup_logger")

def extract_all_unique_tables_from_payload(db:DB_dependency, payload: dict) -> List[str]:
    """
    Get all unique tables associated with forms and sub_forms from the payload.
    """
    # Extract form_id and sub_form_ids from the payload
    form_id = payload.get('form_id')
    sub_form_ids = [sub_form.get('sub_form_id') for sub_form in payload.get('sub_forms')]

    # Fetch form and sub_form objects from the database
    form_objs = get_forms_by_ids(db, [form_id])
    sub_form_objs = get_sub_forms_by_ids(db, sub_form_ids)

    # Extract table names from the form and sub_form objects
    table_names = set()

    for form in form_objs:
        if form and form.table_name:
            table_names.add(form.table_name)
    
    for sub_form in sub_form_objs:
        if sub_form and sub_form.table_name:
            table_names.add(sub_form.table_name)

    
    return list(table_names)

