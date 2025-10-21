# backend-api/app/services/violation_service.py

from typing import List

from app.core.interfaces.repositories import IViolationRepository
from app.core.models import violation as violation_model


class ViolationNotFoundError(Exception):
    pass

class ViolationService:
    def __init__(self, violation_repo: IViolationRepository):
        self._violation_repo = violation_repo

    async def get_all_violations(self) -> List[violation_model.Violation]:
        return await self._violation_repo.get_all()