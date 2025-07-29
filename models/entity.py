from sqlalchemy import Column, String, UUID, Date, BigInteger, ForeignKey, CheckConstraint, UniqueConstraint
from db.session import Base
import uuid

class CustomerEntityDetails(Base):
    __tablename__ = "cbs_customer_entity_details"
    __table_args__ = (
        CheckConstraint("status IN ('INACTIVE', 'ACTIVE', 'SUSPENDED', 'DELETED')", name="status_check"),
        UniqueConstraint("customer_details_id", name="ukpq88htr30csoqiqktnppme9bg")
    )
    entity_details_id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    cin = Column(String(21))
    date_of_incorporation = Column(Date, nullable=False)
    entity_nature_id = Column(BigInteger)
    entity_type_id = Column(BigInteger, nullable=False)
    gst_number = Column(String(15))
    name = Column(String(100), nullable=False)
    pan_number = Column(String(10), nullable=False)
    tan_number = Column(String(10))
    udyam_registration_number = Column(String(12))
    customer_details_id = Column(UUID(as_uuid=True), ForeignKey("cbs_customer_details.customer_details_id"), nullable=False)

class CustomerEntityMemberDetails(Base):
    __tablename__ = "cbs_customer_entity_member_details"
    __table_args__ = (
        CheckConstraint("member_type IN ('Customer', 'Non_Customer')", name="cbs_customer_entity_member_details_member_type_check"),
    )
    member_id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    aadhaar_number = Column(String(50))
    date_of_birth = Column(Date)
    designation = Column(String(100))
    din = Column(String(8))
    email_id = Column(String(255))
    full_name = Column(String(255))
    member_type = Column(String(255))
    mobile_number = Column(String(20))
    pan_number = Column(String(50))
    customer_details_id = Column(UUID(as_uuid=True), ForeignKey("cbs_customer_details.customer_details_id"), nullable=False)
    member_customer_id = Column(UUID(as_uuid=True), nullable=False)