from sqlalchemy import Column, String, TIMESTAMP, ForeignKey, Integer, Date, Numeric, Boolean, CheckConstraint, UniqueConstraint, PrimaryKeyConstraint
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from db.session import Base
import uuid

class CustomerDetails(Base):
    __tablename__ = "cbs_customer_details"
    __table_args__ = (
        CheckConstraint("customer_type IN ('Individual', 'Entity')", name="customer_type_check"),
        CheckConstraint("status IN ('INACTIVE', 'ACTIVE', 'SUSPENDED', 'DELETED')", name="status_check")
    )
    customer_details_id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    address_id = Column(UUID(as_uuid=True), ForeignKey("cbs_addresses.address_id"))
    branch_id = Column(UUID(as_uuid=True))
    communication_address_id = Column(UUID(as_uuid=True))
    created_at = Column(TIMESTAMP)
    customer_id = Column(String(15), nullable=False)
    customer_type = Column(String(255), nullable=False)
    status = Column(String(255))
    updated_at = Column(TIMESTAMP)
    address = relationship("Address", back_populates="customers")


class CustomerIndividualDetails(Base):
    __tablename__ = "cbs_customer_individual_details"
    __table_args__ = (
        CheckConstraint("category IN ('Senior_Citizen', 'Minor', 'Staff', 'General', 'Others')", name="category_check"),
        CheckConstraint("gender IN ('Male', 'Female', 'Others')", name="gender_check"),
        CheckConstraint("marital_status IN ('Single', 'Married', 'Divorced', 'Widowed')", name="marital_status_check"),
        CheckConstraint("salutation IN ('Mr', 'Mrs', 'Miss', 'Ms', 'Dr', 'Prof', 'Rev', 'Hon', 'Sir', 'Madam', 'Mx', 'Capt', 'Lt', 'Col')", name="salutation_check"),
        UniqueConstraint("customer_details_id", name="ukpq88htr30csoqiqktnppme9bg")
    )
    individual_details_id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    caste = Column(String(50))
    category = Column(String(255))
    country_code = Column(String(5))
    date_of_birth = Column(Date)
    email_id = Column(String(100))
    father_name = Column(String(100))
    first_name = Column(String(50))
    full_name = Column(String(150))
    gender = Column(String(255))
    guardian_name = Column(String(100))
    last_name = Column(String(50))
    marital_status = Column(String(255))
    middle_name = Column(String(50))
    mobile_number = Column(String(15))
    mother_name = Column(String(100))
    nationality = Column(String(100))
    others_category = Column(String(100))
    religion = Column(String(50))
    salutation = Column(String(255))
    spouse_name = Column(String(100))
    customer_details_id = Column(UUID(as_uuid=True), ForeignKey("cbs_customer_details.customer_details_id"))
    aadhar_number = Column(String(255))
    pan_number = Column(String(255))
    age = Column(Integer)

class CustomerOccupationDetails(Base):
    __tablename__ = "cbs_customer_occupation_details"
    __table_args__ = (
        CheckConstraint("occupation IN ('Salaried', 'Self_Employed', 'Student', 'Retired', 'Housewife', 'Others')", name="occupation_check"),
        CheckConstraint("years_of_experience <= 150", name="years_of_experience_check"),
        UniqueConstraint("customer_details_id", name="ukosgxdn5tpd2umsv4aq62rrelr"),
        PrimaryKeyConstraint("occupation_details_id", "customer_details_id"),
        UniqueConstraint("customer_details_id", name="ukosgxdn5tpd2umsv4aq62rrelr")
    )
    occupation_details_id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    annual_income = Column(Numeric(15, 2))
    company_name = Column(String(150))
    department = Column(String(100))
    designation = Column(String(100))
    expected_annual_transactions = Column(Numeric(15, 2))
    industry = Column(String(100))
    occupation = Column(String(255))
    profile = Column(String(100))
    years_of_experience = Column(Integer)
    customer_details_id = Column(UUID(as_uuid=True), ForeignKey("cbs_customer_details.customer_details_id"))