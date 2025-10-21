# backend-api/app/core/models/camera.py

from typing import Optional
from uuid import UUID, uuid4

from pydantic import BaseModel, Field


class CameraBase(BaseModel):
    name: str
    url: str
    district: Optional[str] = None
    notes: Optional[str] = None
    status: str = "offline"

class CameraCreate(CameraBase):
    pass

class CameraUpdate(BaseModel):
    name: Optional[str] = None
    url: Optional[str] = None
    district: Optional[str] = None
    notes: Optional[str] = None
    status: Optional[str] = None

class Camera(CameraBase):
    id: UUID

    class Config:
        from_attributes = True