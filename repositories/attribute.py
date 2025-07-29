from .base import (
    DB_dependency,
    List,
    Dict,
    Optional,
    MasterFormAttribute
)

def get_attribute_by_id(
    db: DB_dependency,
    attribute_id: int
) -> Optional[MasterFormAttribute]:
    """
    Get a MasterFormAttribute by its ID.
    """
    return db.query(MasterFormAttribute).filter(MasterFormAttribute.attribute_id == attribute_id).first()

def get_attributes_by_ids(
    db: DB_dependency,
    attribute_ids: List[int]
) -> Optional[List[MasterFormAttribute]]:
    """
    Get a list of MasterFormAttribute by their IDs.
    """
    return db.query(MasterFormAttribute).filter(MasterFormAttribute.attribute_id.in_(attribute_ids)).all()

def get_attribute_id_name_map(
    db: DB_dependency,
    attribute_ids: List[int]
) -> Optional[Dict[int, str]]:
    """
    Get a mapping of attribute_id (as string) → attribute name (i.e. actual column name).
    """
    row = db.query(
        MasterFormAttribute.attribute_id, 
        MasterFormAttribute.name
    ).filter(
        MasterFormAttribute.attribute_id.in_(attribute_ids)
    ).all()
    return {str(r.attribute_id): r.name for r in row}