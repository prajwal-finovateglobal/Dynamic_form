from fastapi import HTTPException, Request, status
from sqlalchemy.orm import Session, joinedload
from sqlalchemy.exc import IntegrityError, DataError
from typing import List

from utils.logger import get_logger
from models.form import MasterForm, MasterSubForm, MasterSubFormConditionalCheck

logger = get_logger("Sub-Form-Service")



def find_by_id(sub_form_id, db:Session, request: Request ) -> MasterSubForm:
    sub_form = (
        db.query(MasterSubForm)
        .options(
            joinedload(MasterSubForm.conditional_checks)
        )
        .filter(MasterSubForm.sub_form_id == sub_form_id)
        .first()
    )
    return sub_form


def find(limit: int, offset: int, db:Session, request: Request) -> List[MasterSubForm]:
    return db.query(MasterSubForm).offset(offset).limit(limit).all()
