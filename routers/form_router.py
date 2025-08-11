from typing import List, Dict
from fastapi import APIRouter, Depends, HTTPException, status, Request, UploadFile, File
from sqlalchemy.orm import Session
import uuid
from datetime import datetime, timezone
from utils.logger import get_logger
import time
from db.dependencies import get_db; 

from schemas.form import MasterForm as MasterFormModel
import services.form_service as FormService

logger = get_logger("Form-Router")
router = APIRouter()


@router.get("/", response_model=List[MasterFormModel])
def read_forms(
    request: Request, db: Session = Depends(get_db),
    skip: int = 0, limit: int = 100
):
    start_time = time.time()
    try:
        forms = FormService.find(limit, skip, db, request)
        response_forms: List[MasterFormModel] = [
            MasterFormModel.model_validate(b, from_attributes=True)
            for b in forms
        ]
        return response_forms
    except Exception as e:
        raise
    finally:
        db.close()


@router.get("/{form_id}", response_model=MasterFormModel)
def read_form_by_id(
    form_id: int,
    request: Request, db: Session = Depends(get_db)
):
    start_time = time.time()
    try:
        form = FormService.find_by_id(form_id, db,request)
        return MasterFormModel.model_validate(form, from_attributes=True)
    except Exception as e:
        raise
    finally:
        db.close()

