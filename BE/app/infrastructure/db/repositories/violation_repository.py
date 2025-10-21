# backend-api/app/infrastructure/db/repositories/violation_repository.py

from typing import List

from app.core.interfaces.repositories import IViolationRepository
from app.core.models import violation as violation_model
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from .. import schema as db_schema


class PostgresViolationRepository(IViolationRepository):
    def __init__(self, db_session: AsyncSession):
        self._db_session = db_session

    async def get_all(self, skip: int = 0, limit: int = 100) -> List[violation_model.Violation]:
        query = select(db_schema.Violation).order_by(db_schema.Violation.timestamp.desc()).offset(skip).limit(limit)
        result = await self._db_session.execute(query)
        violations_db = result.scalars().all()
        return [violation_model.Violation.from_orm(v) for v in violations_db]