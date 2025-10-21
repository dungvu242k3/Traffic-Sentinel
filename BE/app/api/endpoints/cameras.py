# backend-api/app/api/endpoints/cameras.py

from typing import List
from uuid import UUID

from app.core.models import camera as camera_model
# Import Service thay vì Repository
from app.services.camera_service import (CameraAlreadyExistsError,
                                         CameraNotFoundError, CameraService)
from fastapi import APIRouter, Depends, HTTPException, status

from .. import deps

# Tạo một router riêng cho camera
router = APIRouter()

@router.get(
    "/", 
    response_model=List[camera_model.Camera], 
    summary="Lấy danh sách tất cả camera"
)
async def get_all_cameras(
    # Endpoint giờ phụ thuộc vào Service
    service: CameraService = Depends(deps.get_camera_service)
):
    """
    API để lấy danh sách tất cả các camera trong hệ thống.
    Endpoint chỉ đơn giản là gọi service để lấy dữ liệu.
    """
    return await service.get_all_cameras()


@router.post(
    "/", 
    response_model=camera_model.Camera, 
    status_code=status.HTTP_201_CREATED, 
    summary="Tạo một camera mới"
)
async def create_camera(
    *,
    camera_in: camera_model.CameraCreate,
    # Endpoint giờ phụ thuộc vào Service
    service: CameraService = Depends(deps.get_camera_service)
):
    """
    API để tạo một camera mới.
    Logic nghiệp vụ (ví dụ: kiểm tra trùng lặp) được xử lý trong service.
    """
    try:
        new_camera = await service.create_new_camera(camera_in=camera_in)
        return new_camera
    except CameraAlreadyExistsError as e:
        # Bắt lỗi nghiệp vụ từ service và chuyển thành lỗi HTTP
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=str(e)
        )


@router.put(
    "/{camera_id}", 
    response_model=camera_model.Camera, 
    summary="Cập nhật một camera"
)
async def update_camera(
    *,
    camera_id: UUID,
    camera_in: camera_model.CameraUpdate,
    service: CameraService = Depends(deps.get_camera_service)
):
    """
    API để cập nhật thông tin của một camera đã tồn tại.
    """
    try:
        updated_camera = await service.update_camera(camera_id=camera_id, camera_in=camera_in)
        return updated_camera
    except CameraNotFoundError:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Camera not found"
        )


@router.delete(
    "/{camera_id}", 
    response_model=camera_model.Camera, 
    summary="Xóa một camera"
)
async def delete_camera(
    *,
    camera_id: UUID,
    service: CameraService = Depends(deps.get_camera_service)
):
    """
    API để xóa một camera khỏi hệ thống.
    """
    try:
        deleted_camera = await service.delete_camera(camera_id=camera_id)
        return deleted_camera
    except CameraNotFoundError:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Camera not found"
        )