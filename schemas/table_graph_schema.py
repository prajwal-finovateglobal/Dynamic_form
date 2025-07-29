from typing import List, Optional, Dict
from pydantic import BaseModel

class RelationDetail(BaseModel):
    table: str
    fk_column: str
    pk_column: str
    relation_type: str  # '1:N', 'N:1', etc.
    fk_constraint_name: Optional[str] = None

class TableGraph(BaseModel):
    parents: List[RelationDetail]
    children: List[RelationDetail]

GraphSchema = Dict[str, TableGraph]