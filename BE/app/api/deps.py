# backend-api/app/api/deps.py   
from app.core.interfaces.repositories import (ICameraRepository,
                                              IViolationRepository)
from app.infrastructure.db.postgres_setup import get_db_session
from app.infrastructure.db.repositories.camera_repository import \
    PostgresCameraRepository
from app.infrastructure.db.repositories.violation_repository import \
    PostgresViolationRepository
from app.services.camera_service import CameraService
from app.services.violation_service import ViolationService
from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession


def get_camera_repository(db_session: AsyncSession = Depends(get_db_session)) -> ICameraRepository:
    return PostgresCameraRepository(db_session)

def get_camera_service(repo: ICameraRepository = Depends(get_camera_repository)) -> CameraService:
    return CameraService(repo)

def get_violation_repository(db_session: AsyncSession = Depends(get_db_session)) -> IViolationRepository:
    return PostgresViolationRepository(db_session)

def get_violation_service(repo: IViolationRepository = Depends(get_violation_repository)) -> ViolationService:
    return ViolationService(repo)