# backend-api/app/infrastructure/db/schema.py
import uuid
from datetime import datetime

from sqlalchemy import Column, DateTime, ForeignKey, String
from sqlalchemy.dialects.postgresql import UUID

from .postgres_setup import Base


class Camera(Base):
    __tablename__ = "cameras"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String, index=True, nullable=False)
    url = Column(String, nullable=False)
    district = Column(String, index=True)
    notes = Column(String)
    status = Column(String, default="offline", nullable=False)

class Violation(Base):
    __tablename__ = "violations"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    timestamp = Column(DateTime(timezone=True), default=datetime.utcnow, nullable=False)
    violation_type = Column(String, index=True, nullable=False)
    license_plate = Column(String, index=True)
    image_url = Column(String, nullable=False)
    camera_id = Column(UUID(as_uuid=True), ForeignKey("cameras.id"), nullable=False)