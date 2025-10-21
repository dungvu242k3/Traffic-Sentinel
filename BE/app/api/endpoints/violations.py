# backend-api/app/api/endpoints/violations.py

from typing import List

from app.core.models import violation as violation_model
from app.services.violation_service import ViolationService
from fastapi import APIRouter, Depends

from .. import deps

router = APIRouter()

@router.get(
    "/",
    response_model=List[violation_model.Violation],
    summary="Lấy danh sách vi phạm"
)
async def get_all_violations(
    service: ViolationService = Depends(deps.get_violation_service)
):
    """
    API để lấy danh sách tất cả các vi phạm đã được ghi nhận trong hệ thống.
    """
    return await service.get_all_violations()