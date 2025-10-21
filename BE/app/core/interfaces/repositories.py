# backend-api/app/core/interfaces/repositories.py

from abc import ABC, abstractmethod
from typing import List, Optional
from uuid import UUID

from ..models import camera as camera_model
from ..models import violation as violation_model


class ICameraRepository(ABC):
    @abstractmethod
    async def get_all(self, skip: int = 0, limit: int = 100) -> List[camera_model.Camera]:
        pass

    @abstractmethod
    async def create(self, *, camera_in: camera_model.CameraCreate) -> camera_model.Camera:
        pass
    
    @abstractmethod
    async def get_by_id(self, *, camera_id: UUID) -> Optional[camera_model.Camera]:
        pass

    @abstractmethod
    async def update(self, *, camera_id: UUID, camera_in: camera_model.CameraUpdate) -> Optional[camera_model.Camera]:
        pass

    @abstractmethod
    async def delete(self, *, camera_id: UUID) -> Optional[camera_model.Camera]:
        pass
    
class IViolationRepository(ABC):
    """
    Interface (hợp đồng) trừu tượng cho repository quản lý Violation.
    """
    @abstractmethod
    async def get_all(self, skip: int = 0, limit: int = 100) -> List[violation_model.Violation]:
        """Lấy danh sách tất cả vi phạm."""
        pass