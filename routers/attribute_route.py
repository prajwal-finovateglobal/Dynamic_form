from typing import List, Dict
from fastapi import APIRouter, Depends, HTTPException, status, Request, UploadFile, File
from sqlalchemy.orm import Session
import uuid
from datetime import datetime, timezone
from utils.logger import get_logger
import time
from db.dependencies import get_db; 

from schemas.attribute import MasterFormAttributeModel, MasterFormAttributePredefinedValueModel
import services.attribute_service as AttributeService

logger = get_logger("Attribute-Router")
router = APIRouter()


@router.get("/", response_model=List[MasterFormAttributeModel])
def read_attribute(
    request: Request, db: Session = Depends(get_db),
    skip: int = 0, limit: int = 100
):
    start_time = time.time()
    try:
        forms = AttributeService.find(limit, skip, db, request)
        response_forms: List[MasterFormAttributeModel] = [
            MasterFormAttributeModel.model_validate(b, from_attributes=True)
            for b in forms
        ]
        return response_forms
    except Exception as e:
        raise
    finally:
        db.close()


@router.get("/{attribute_id}", response_model=MasterFormAttributeModel)
def read_attribute_by_id(
    attribute_id: int,
    request: Request, db: Session = Depends(get_db)
):
    start_time = time.time()
    try:
        form = AttributeService.find_by_id(attribute_id, db,request)
        return MasterFormAttributeModel.model_validate(form, from_attributes=True)
    except Exception as e:
        raise
    finally:
        db.close()

@router.get("/by-form/{form_id}", response_model=List[MasterFormAttributeModel])
def read_attributes_by_form_id(
    form_id: int,
    request: Request, db: Session = Depends(get_db)
):
    try:
        forms = AttributeService.find_by_form_id(form_id, db, request)
        response_forms: List[MasterFormAttributeModel] = [
            MasterFormAttributeModel.model_validate(b, from_attributes=True)
            for b in forms
        ]
        return response_forms
    finally:
        db.close()

@router.get("/by-sub-form/{sub_form_id}", response_model=List[MasterFormAttributeModel])
def read_attributes_by_sub_form_id(
    sub_form_id: int,
    request: Request, db: Session = Depends(get_db)
):
    try:
        forms = AttributeService.find_by_sub_form_id(sub_form_id, db, request)
        response_forms: List[MasterFormAttributeModel] = [
            MasterFormAttributeModel.model_validate(b, from_attributes=True)
            for b in forms
        ]
        return response_forms
    finally:
        db.close()
