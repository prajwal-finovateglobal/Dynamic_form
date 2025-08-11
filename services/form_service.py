from fastapi import HTTPException, Request, status
from sqlalchemy.orm import Session, joinedload
from sqlalchemy.exc import IntegrityError, DataError
from typing import List

from utils.logger import get_logger
from models.form import MasterForm, MasterSubForm, MasterSubFormConditionalCheck

logger = get_logger("Form-Service")



def find_by_id(form_id, db:Session, request: Request ) -> MasterForm:
    form = (
        db.query(MasterForm)
        .options(
            joinedload(MasterForm.sub_forms)
            .joinedload(MasterSubForm.conditional_checks.and_(
                MasterSubFormConditionalCheck.form_id == form_id
            ))
        )
        .filter(MasterForm.form_id == form_id)
        .first()
    )
    return form


def find(limit: int, offset: int, db:Session, request: Request) -> List[MasterForm]:
    return db.query(MasterForm).offset(offset).limit(limit).all()
