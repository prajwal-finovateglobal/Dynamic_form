from db.dependencies import DB_dependency
from models.fk_mapping import SubformFKMapping
from typing import List

def get_fk_mappings_for_subforms(db: DB_dependency, subform_ids: List[int]) -> List[SubformFKMapping]:
    return (
        db.query(SubformFKMapping)
        .filter(SubformFKMapping.sub_form_id.in_(subform_ids))
        .all()
    )

