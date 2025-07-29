# app/schemas/submission.py

from typing import Union, Dict, List, Any
from pydantic import BaseModel

class SubForm(BaseModel):
    sub_form_id: int
    values: Union[Dict[str, Any], List[Dict[str, Any]]]

class SubmissionPayload(BaseModel):
    form_id: int
    values: Union[Dict[str, Any], List[Dict[str, Any]]]
    sub_forms: List[SubForm]
