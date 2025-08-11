from typing import Optional, List
from uuid import UUID as UUIDType
from datetime import datetime
from pydantic import BaseModel, Field


# ---------- MasterForm ----------
class MasterFormBase(BaseModel):
    name: str = Field(..., max_length=50)
    primary_key: Optional[str] = Field(None, max_length=50)
    table_name: Optional[str] = Field(None, max_length=50)
    description: Optional[str]
    attribute_ids: Optional[List[int]]
    editable_attribute_ids: Optional[List[int]]
    metadata_attribute_ids: Optional[List[int]]
    required_attribute_ids: Optional[List[int]]
    status: Optional[str]
    attribute_order: Optional[dict]



class MasterForm(MasterFormBase):
    form_id: int
    version: Optional[int]
    sub_forms: Optional[List["MasterSubForm"]] = [] # forward reference

    class Config:
        orm_mode = True


# ---------- MasterSubForm ----------
class MasterSubFormBase(BaseModel):
    status: Optional[int]
    name: str = Field(..., max_length=50)
    description: Optional[str]
    attribute_ids: Optional[List[int]]
    editable_attribute_ids: Optional[List[int]]
    metadata_attribute_ids: Optional[List[int]]
    required_attribute_ids: Optional[List[int]]
    primary_key: Optional[str]
    table_name: Optional[str]
    conditional_attribute_id: Optional[int]
    attribute_order: Optional[dict]
    child_sub_form_ids: Optional[List[int]]


class MasterSubForm(MasterSubFormBase):
    sub_form_id: int
    version: Optional[int]
    # forms: Optional[List[MasterForm]]
    conditional_checks: Optional[List["MasterSubFormConditionalCheck"]]

    class Config:
        orm_mode = True
    

# ---------- MasterSubFormConditionalCheck ----------
class MasterSubFormConditionalCheckBase(BaseModel):
    sub_form_id: int
    form_id: int
    condition_expression: str
    action: str


class MasterSubFormConditionalCheck(MasterSubFormConditionalCheckBase):
    check_id: int

    class Config:
        orm_mode = True

