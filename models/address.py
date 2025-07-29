from sqlalchemy import Column, String, Integer, ForeignKey, CheckConstraint
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from db.session import Base
import uuid

class Address(Base):
    __tablename__ = "cbs_addresses"
    __table_args__ = (
        CheckConstraint("address_type IN ('Permanent', 'Registered', 'Communication')", name="address_type_check"),
    )
    address_id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    line_1 = Column(String(255))
    line_2 = Column(String(255))
    pin_code = Column(Integer)
    address_type = Column(String(255))
    country_id = Column(UUID(as_uuid=True), ForeignKey("cbs_master_countries.country_id"))
    district_id = Column(UUID(as_uuid=True), ForeignKey("cbs_master_districts.district_id"))
    state_id = Column(UUID(as_uuid=True), ForeignKey("cbs_master_states.state_id"))
    landmark = Column(String(255))
    customers = relationship("CustomerDetails", back_populates="address")


