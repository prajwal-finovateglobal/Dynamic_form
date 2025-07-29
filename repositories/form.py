from .base import (
    DB_dependency,
    List,
    Optional,
    MasterForm,
)
def get_form_by_id(
    db: DB_dependency,
    form_id: int
) -> Optional[MasterForm]:
    """
    Get a MasterForm by its ID.
    """
    return db.query(MasterForm).filter(MasterForm.form_id == form_id).first()

def get_forms_by_ids(
    db: DB_dependency,
    form_ids: List[int]
) -> Optional[List[MasterForm]]:
    """
    Get a list of MasterForm by their IDs.
    """
    return db.query(MasterForm).filter(MasterForm.form_id.in_(form_ids)).all()