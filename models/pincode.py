from sqlalchemy import Column, Integer, ForeignKey, CheckConstraint
from sqlalchemy.dialects.postgresql import UUID
from db.session import Base

class PinCodeLocation(Base):
    __tablename__ = "cbs_pin_code_locations"
    __table_args__ = (
        CheckConstraint("pin_code_location_type IN ('City', 'Town', 'Village', 'Sub_District', 'District', 'State', 'Country')", name="pin_code_location_type_check"),
    )
    pin_code = Column(Integer, primary_key=True)
    country_id = Column(UUID(as_uuid=True), ForeignKey("cbs_master_countries.country_id"))
    district_id = Column(UUID(as_uuid=True), ForeignKey("cbs_master_districts.district_id"))
    state_id = Column(UUID(as_uuid=True), ForeignKey("cbs_master_states.state_id"))