from sqlalchemy import Column, String, BigInteger, TIMESTAMP, UUID, ARRAY, JSON
from db.session import Base

class MasterForm(Base):
    __tablename__ = "cbs_master_forms"
    form_id = Column(BigInteger, primary_key=True)
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

class MasterSubForm(Base):
    __tablename__ = "cbs_master_sub_forms"
    sub_form_id = Column(BigInteger, primary_key=True)
    status = Column(BigInteger)
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

class MasterFormSubFormMapping(Base):
    __tablename__ = "cbs_master_form_sub_form_mapping"
    form_id = Column(UUID(as_uuid=True), primary_key=True)
    sub_form_id = Column(UUID(as_uuid=True), primary_key=True)