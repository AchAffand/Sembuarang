from datetime import datetime
from sqlalchemy import Column, Integer, String, DateTime, Boolean, ForeignKey
from sqlalchemy.orm import relationship

from .database import Base


class PhoneNumber(Base):
	__tablename__ = "phone_numbers"

	id = Column(Integer, primary_key=True, index=True)
	e164 = Column(String(20), unique=True, index=True, nullable=False)
	region = Column(String(4), nullable=False, default="ID")
	carrier = Column(String(64), nullable=True)
	line_type = Column(String(32), nullable=True)
	created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

	reports = relationship("Report", back_populates="number", cascade="all, delete-orphan")


class Report(Base):
	__tablename__ = "reports"

	id = Column(Integer, primary_key=True, index=True)
	number_id = Column(Integer, ForeignKey("phone_numbers.id"), nullable=False, index=True)
	category = Column(String(32), nullable=False)  # spam, fraud, scam, harassment, other
	confidence = Column(Integer, nullable=False, default=50)  # 0..100
	note = Column(String(1000), nullable=True)
	is_approved = Column(Boolean, default=False, nullable=False)
	is_hidden = Column(Boolean, default=False, nullable=False)
	created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

	number = relationship("PhoneNumber", back_populates="reports")