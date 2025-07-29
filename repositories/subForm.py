from .base import (
    DB_dependency,
    List,
    Optional,
    MasterSubForm,
)

def get_sub_form_by_id(
    db: DB_dependency,
    sub_form_id: int
) -> Optional[MasterSubForm]:
    """
    Get a MasterSubForm by its ID.
    """
    return db.query(MasterSubForm).filter(MasterSubForm.sub_form_id == sub_form_id).first()

def get_sub_forms_by_ids(
    db: DB_dependency,
    sub_form_ids: List[int]
) -> Optional[List[MasterSubForm]]:
    """
    Get a list of MasterSubForm by their IDs.
    """
    return db.query(MasterSubForm).filter(MasterSubForm.sub_form_id.in_(sub_form_ids)).all()