from fastapi import HTTPException, Request, status
from sqlalchemy.orm import Session, joinedload
from sqlalchemy.exc import IntegrityError, DataError
from typing import List, Optional

from utils.logger import get_logger
from models.attribute import MasterFormAttribute, MasterFormAttributePredefinedValue

logger = get_logger("Attribute-Service")


def find_by_id(attribute_id, db:Session, request: Request ) -> MasterFormAttribute:
    sub_form = (
        db.query(MasterFormAttribute)
        .options(
            joinedload(MasterFormAttribute.predefine_values)
        )
        .filter(MasterFormAttribute.attribute_id == attribute_id)
        .first()
    )
    return sub_form


def find(limit: int, offset: int, db:Session, request: Request) -> List[MasterFormAttribute]:
    return db.query(MasterFormAttribute).offset(offset).limit(limit).all()


def find_by_form_id(form_id: int, db:Session, request: Request ) -> List[MasterFormAttribute]:
    """
    Fetch all attributes associated with a given form_id.
    This uses the ARRAY column `form_ids` and checks if the given id is in the array.
    """
    return (
        db.query(MasterFormAttribute)
        .filter(MasterFormAttribute.form_ids.any(form_id))
        .all()
    )

def find_by_sub_form_id(sub_form_id: int, db:Session, request: Request ) -> List[MasterFormAttribute]:
    """
    Fetch all attributes associated with a given sub_form_id.
    This uses the ARRAY column `sub_form_ids` and checks if the given id is in the array.
    """
    return (
        db.query(MasterFormAttribute)
        .filter(MasterFormAttribute.sub_form_ids.any(sub_form_id))
        .all()
    )

def find_by_form_or_sub_form_id(
    db:Session, request: Request, form_id: Optional[int] = None, sub_form_id: Optional[int] = None
) -> List[MasterFormAttribute]:
    """
    Fetch attributes by either form_id or sub_form_id.
    If both are provided, it returns attributes that match either condition.
    """
    query = db.query(MasterFormAttribute)
    if form_id is not None:
        query = query.filter(MasterFormAttribute.form_ids.any(form_id))
    if sub_form_id is not None:
        query = query.filter(MasterFormAttribute.sub_form_ids.any(sub_form_id))
    return query.all()