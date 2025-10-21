# backend-api/app/core/models/violation.py

from datetime import datetime
from typing import Optional
from uuid import UUID

from pydantic import BaseModel


# Lớp cơ sở chứa các thuộc tính chung
class ViolationBase(BaseModel):
    violation_type: str
    license_plate: Optional[str] = None
    image_url: Optional[str] = None

# Model dùng để tạo violation (sẽ được consumer sử dụng sau này)
class ViolationCreate(ViolationBase):
    camera_id: UUID
    timestamp: datetime
    image_base64: str # Dữ liệu ảnh thô từ AI service

# Model đầy đủ để trả về cho API
class Violation(ViolationBase):
    id: UUID
    timestamp: datetime
    camera_id: UUID

    class Config:
        from_attributes = True # Cho phép Pydantic đọc từ đối tượng ORM