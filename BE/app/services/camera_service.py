# backend-api/app/services/camera_service.py

from typing import List, Optional
from uuid import UUID

from app.core.interfaces.repositories import ICameraRepository
from app.core.models import camera as camera_model


# ✅ <-- THÊM CÁC LỚP NÀY VÀO ĐẦU FILE
# Các lớp Exception tùy chỉnh để xử lý lỗi nghiệp vụ
class CameraNotFoundError(Exception):
    """Lỗi được ném ra khi không tìm thấy camera."""
    pass

class CameraAlreadyExistsError(Exception):
    """Lỗi được ném ra khi camera đã tồn tại."""
    pass
# KẾT THÚC PHẦN CẦN THÊM

class CameraService:
    def __init__(self, camera_repo: ICameraRepository):
        self._camera_repo = camera_repo

    async def get_all_cameras(self) -> List[camera_model.Camera]:
        return await self._camera_repo.get_all()

    async def create_new_camera(self, camera_in: camera_model.CameraCreate) -> camera_model.Camera:
        # (Trong tương lai, bạn có thể thêm logic kiểm tra trùng lặp ở đây
        # và `raise CameraAlreadyExistsError` nếu cần)
        new_camera = await self._camera_repo.create(camera_in=camera_in)
        return new_camera

    async def update_camera(self, camera_id: UUID, camera_in: camera_model.CameraUpdate) -> camera_model.Camera:
        updated_camera = await self._camera_repo.update(camera_id=camera_id, camera_in=camera_in)
        if not updated_camera:
            raise CameraNotFoundError("Camera not found")
        return updated_camera

    async def delete_camera(self, camera_id: UUID) -> camera_model.Camera:
        deleted_camera = await self._camera_repo.delete(camera_id=camera_id)
        if not deleted_camera:
            raise CameraNotFoundError("Camera not found")
        return deleted_camera