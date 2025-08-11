from typing import List, Optional
from pydantic import BaseModel


# -------------------------------
# MasterFormAttributePredefinedValue Models
# -------------------------------
class MasterFormAttributePredefinedValueBase(BaseModel):
    label: Optional[str] = None
    value: Optional[str] = None
    attribute_id: Optional[int] = None
    mapped_sub_form_id: Optional[int] = None
    description: Optional[str] = None

class MasterFormAttributePredefinedValueModel(MasterFormAttributePredefinedValueBase):
    attribute_value_id: int

    class Config:
        from_attributes = True 


# -------------------------------
# MasterFormAttribute Models
# -------------------------------
class MasterFormAttributeBase(BaseModel):
    front_end_classes: Optional[List[str]] = None
    attribute_data_type: Optional[str] = None
    description: Optional[str] = None
    label: Optional[str] = None
    name: Optional[str] = None
    placeholder: Optional[str] = None
    status: Optional[str] = None
    attribute_type: Optional[str] = None
    form_ids: Optional[List[int]] = None
    sub_form_ids: Optional[List[int]] = None
    # view_only: bool = False

class MasterFormAttributeModel(MasterFormAttributeBase):
    attribute_id: int
    predefine_values: Optional[List[MasterFormAttributePredefinedValueModel]] = []

    class Config:
        from_attributes = True 