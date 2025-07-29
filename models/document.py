from sqlalchemy import Column, String, Boolean, BigInteger, ForeignKey,CheckConstraint
from sqlalchemy.dialects.postgresql import UUID
from db.session import Base
import uuid

class MasterDocumentType(Base):
    __tablename__ = "cbs_master_document_types"
    __table_args__ = (
        CheckConstraint("status IN ('INACTIVE', 'ACTIVE', 'DELETED')", name="cbs_master_document_types_status_check"),
    )
    document_type_id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    document_name = Column(String(100), nullable=False)
    status = Column(String(255), nullable=False)
    verification_required = Column(Boolean, nullable=False)

class CustomerDocumentDetails(Base):
    __tablename__ = "cbs_customer_document_details"
    document_id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    document_number = Column(String(50))
    document_path = Column(String(500))
    document_type_id = Column(BigInteger, ForeignKey("cbs_master_document_types.document_type_id"), nullable=False)
    customer_details_id = Column(UUID(as_uuid=True), ForeignKey("cbs_customer_details.customer_details_id"), nullable=False)