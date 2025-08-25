from sqlalchemy import Table, Column, String, BigInteger, Boolean, Text, SmallInteger, JSON, ForeignKey, CheckConstraint
from sqlalchemy import Column, String, BigInteger, TIMESTAMP, UUID, ARRAY, JSON
from sqlalchemy.orm import relationship, declarative_base
from sqlalchemy.dialects.postgresql import ARRAY, INTEGER
from sqlalchemy.dialects.postgresql import ENUM

from db.session import Base


Base = declarative_base()
CbsMasterFormSubFormMapping = Table(
    "cbs_master_form_sub_form_mapping",
    Base.metadata,
    Column("form_id", BigInteger, ForeignKey("cbs_master_forms.form_id"), primary_key=True),
    Column("sub_form_id", BigInteger, ForeignKey("cbs_master_sub_forms.sub_form_id"), primary_key=True)
)

class MasterForm(Base):
    __tablename__ = "cbs_master_forms"
    form_id = Column(BigInteger, primary_key=True, autoincrement= True)
    created_at = Column(TIMESTAMP)
    updated_at = Column(TIMESTAMP)
    version = Column(BigInteger)
    updated_by = Column(UUID(as_uuid=True))
    name = Column(String(50), nullable=False)
    primary_key = Column(String(50))
    table_name = Column(String(50))
    created_by = Column(String(255))
    created_ip_address = Column(String(255))
    created_user_agent = Column(String(255))
    description = Column(String(255))
    updated_ip_address = Column(String(255))
    updated_user_agent = Column(String(255))
    attribute_ids = Column(ARRAY(BigInteger))
    editable_attribute_ids = Column(ARRAY(BigInteger))
    metadata_attribute_ids = Column(ARRAY(BigInteger))
    required_attribute_ids = Column(ARRAY(BigInteger))
    status = Column(String(255))
    attribute_order = Column(JSON)

     # Relationships
    # Many-to-many with sub_forms through mapping table
    sub_forms = relationship("MasterSubForm", secondary="cbs_master_form_sub_form_mapping", back_populates="forms")

class MasterSubForm(Base):
    __tablename__ = "cbs_master_sub_forms"
    sub_form_id = Column(BigInteger, primary_key=True, autoincrement=True)
    status = Column(String(255))
    created_at = Column(TIMESTAMP)
    updated_at = Column(TIMESTAMP)
    version = Column(BigInteger)
    updated_by = Column(UUID(as_uuid=True))
    name = Column(String(50), nullable=False)
    created_by = Column(String(255))
    created_ip_address = Column(String(255))
    created_user_agent = Column(String(255))
    description = Column(String(255))
    updated_ip_address = Column(String(255))
    updated_user_agent = Column(String(255))
    attribute_ids = Column(ARRAY(BigInteger))
    editable_attribute_ids = Column(ARRAY(BigInteger))
    metadata_attribute_ids = Column(ARRAY(BigInteger))
    required_attribute_ids = Column(ARRAY(BigInteger))
    primary_key = Column(String(255))
    table_name = Column(String(50))
    conditional_attribute_id = Column(BigInteger)
    attribute_order = Column(JSON)
    child_sub_form_ids = Column(ARRAY(BigInteger))

    forms = relationship("MasterForm", secondary="cbs_master_form_sub_form_mapping", back_populates="sub_forms", lazy="select")
    conditional_checks = relationship("MasterSubFormConditionalCheck", back_populates="sub_form", foreign_keys="MasterSubFormConditionalCheck.sub_form_id")


class MasterSubFormConditionalCheck(Base):
    __tablename__ = "cbs_master_sub_form_conditional_checks"
    
    check_id = Column(BigInteger, primary_key=True, autoincrement=True)
    sub_form_id = Column(BigInteger, ForeignKey("cbs_master_sub_forms.sub_form_id"), nullable=False)
    form_id = Column(BigInteger, ForeignKey("cbs_master_forms.form_id"), nullable=False)
    condition_expression = Column(String(255), nullable=False)
    action = Column(String(255), nullable=False)
    
    
    # Relationships
    sub_form = relationship("MasterSubForm", back_populates="conditional_checks", foreign_keys=[sub_form_id], lazy= "select")