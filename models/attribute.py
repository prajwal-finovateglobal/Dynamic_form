from sqlalchemy import Column, String, BigInteger, ARRAY, ForeignKey, Boolean
from sqlalchemy.orm import relationship
from db.session import Base

class MasterFormAttribute(Base):
    __tablename__ = "cbs_master_form_attributes"
    attribute_id = Column(BigInteger, primary_key=True)
    front_end_classes = Column(ARRAY(String(255)))
    attribute_data_type = Column(String(255))
    description = Column(String(255))
    label = Column(String(50))
    name = Column(String(50))
    placeholder = Column(String(50))
    status = Column(String(255))
    attribute_type = Column(String(255))
    form_ids = Column(ARRAY(BigInteger))
    sub_form_ids = Column(ARRAY(BigInteger))
    # view_only = Column(Boolean, nullable=False, default=False)

     # Relationships
    predefine_values = relationship("MasterFormAttributePredefinedValue", back_populates="attribute")

class MasterFormAttributePredefinedValue(Base):
    __tablename__ = "cbs_master_form_attribute_predefined_value"
    attribute_value_id = Column(BigInteger, primary_key=True)
    label = Column(String(255))
    value = Column(String(255))
    attribute_id = Column(BigInteger, ForeignKey("cbs_master_form_attributes.attribute_id"))
    mapped_sub_form_id = Column(BigInteger)
    description = Column(String(100))

    # Relationships
    attribute = relationship("MasterFormAttribute", back_populates="predefine_values")
