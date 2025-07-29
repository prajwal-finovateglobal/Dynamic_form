from sqlalchemy import Column, String, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from db.session import Base
import uuid

class MasterState(Base):
    __tablename__ = "cbs_master_states"
    state_id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    country_id = Column(UUID(as_uuid=True), ForeignKey("cbs_master_countries.country_id"))
    state_code = Column(String(255))
    state_name = Column(String(255))

class MasterDistrict(Base):
    __tablename__ = "cbs_master_districts"
    district_id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    state_id = Column(UUID(as_uuid=True), ForeignKey("cbs_master_states.state_id"))
    district_code = Column(String(255))
    district_name = Column(String(255))