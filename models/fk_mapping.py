from sqlalchemy import Column, BigInteger, String, TIMESTAMP, func
from db.session import Base

class SubformFKMapping(Base):
    __tablename__ = "cbs_subform_fk_mapping"

    id = Column(BigInteger, primary_key=True, autoincrement=True)
    sub_form_id = Column(BigInteger, nullable=False)
    source_table = Column(String(100), nullable=False)
    source_pk = Column(String(100), nullable=False)
    target_table = Column(String(100), nullable=False)
    target_fk_column = Column(String(100), nullable=False)
    created_at = Column(TIMESTAMP, server_default=func.now())
    updated_at = Column(TIMESTAMP, server_default=func.now(), onupdate=func.now())
