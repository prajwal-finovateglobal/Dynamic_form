from typing import List, Dict
from fastapi import APIRouter, Depends, HTTPException, status, Request, UploadFile, File
from sqlalchemy.orm import Session
import uuid
from datetime import datetime, timezone
from utils.logger import get_logger
import time
from db.dependencies import get_db; 

from schemas.form import MasterSubForm as MasterSubFormModel
import services.sub_form_service as FormService

logger = get_logger("Sub-Form-Router")
router = APIRouter()


@router.get("/sub_forms", response_model=List[MasterSubFormModel])
def read_sub_forms(
    request: Request, db: Session = Depends(get_db),
    skip: int = 0, limit: int = 100
):
    start_time = time.time()
    try:
        forms = FormService.find(limit, skip, db, request)
        response_forms: List[MasterSubFormModel] = [
            MasterSubFormModel.model_validate(b, from_attributes=True)
            for b in forms
        ]
        return response_forms
    except Exception as e:
        raise
    finally:
        db.close()


@router.get("/sub_forms/{sub_form_id}", response_model=MasterSubFormModel)
def read_sub_form_by_id(
    sub_form_id: int,
    request: Request, db: Session = Depends(get_db)
):
    start_time = time.time()
    try:
        form = FormService.find_by_id(sub_form_id, db, request)
        return MasterSubFormModel.model_validate(form, from_attributes=True)
    except Exception as e:
        raise
    finally:
        db.close()

