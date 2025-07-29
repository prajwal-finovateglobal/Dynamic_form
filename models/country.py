from sqlalchemy import Column, String
from sqlalchemy.dialects.postgresql import UUID
from db.session import Base
import uuid

class MasterCountry(Base):
    __tablename__ = "cbs_master_countries"
    country_id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    country_name = Column(String(255))