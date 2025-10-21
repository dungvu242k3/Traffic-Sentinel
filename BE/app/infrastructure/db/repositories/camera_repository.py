# backend-api/app/infrastructure/db/repositories/camera_repository.py

from typing import Any, Dict, List, Optional
from uuid import UUID

from app.core.interfaces.repositories import ICameraRepository
from app.core.models import camera as camera_model
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from .. import schema as db_schema


class PostgresCameraRepository(ICameraRepository):
    def __init__(self, db_session: AsyncSession):
        self._db_session = db_session

    async def get_all(self, skip: int = 0, limit: int = 100) -> List[camera_model.Camera]:
        query = select(db_schema.Camera).offset(skip).limit(limit)
        result = await self._db_session.execute(query)
        return [camera_model.Camera.from_orm(c) for c in result.scalars().all()]

    async def create(self, *, camera_in: camera_model.CameraCreate) -> camera_model.Camera:
        print("\n--- BƯỚC 1: Đã vào hàm create() trong repository ---")
        try:
            # Dòng này chuyển đổi dữ liệu từ API thành đối tượng để lưu vào DB
            camera_db_obj = db_schema.Camera(**camera_in.model_dump())
            print(f"--- BƯỚC 2: Đã tạo đối tượng DB cho camera: {camera_db_obj.name} ---")

            # Dòng này thêm đối tượng vào "khu vực chờ" của session
            self._db_session.add(camera_db_obj)
            print("--- BƯỚC 3: Đã thêm đối tượng vào session (chưa lưu) ---")

            # Dòng này thực sự ghi dữ liệu vào database
            print("--- BƯỚC 4: Chuẩn bị commit (lưu vào DB)... ---")
            await self._db_session.commit()
            print("--- BƯỚC 5: ✅ COMMIT THÀNH CÔNG! Dữ liệu phải ở trong DB. ---")

            # Dòng này tải lại đối tượng từ DB để đảm bảo nó đã được lưu
            await self._db_session.refresh(camera_db_obj)
            print("--- BƯỚC 6: Đã refresh đối tượng từ DB. ---")

            return camera_model.Camera.from_orm(camera_db_obj)

        except Exception as e:
        # Nếu có bất kỳ lỗi nào xảy ra, nó sẽ được in ra ở đây
            print(f"!!!!!!!!!!!!!! ❌ LỖI NGHIÊM TRỌNG TRONG HÀM CREATE: {e} !!!!!!!!!!!!!!")
            await self._db_session.rollback() # Hủy bỏ mọi thay đổi nếu có lỗi
            raise e

    async def get_by_id(self, *, camera_id: UUID) -> Optional[camera_model.Camera]:
        result = await self._db_session.get(db_schema.Camera, camera_id)
        return camera_model.Camera.from_orm(result) if result else None
        
    async def update(self, *, camera_id: UUID, camera_in: camera_model.CameraUpdate) -> Optional[camera_model.Camera]:
        camera_db = await self._db_session.get(db_schema.Camera, camera_id)
        if not camera_db:
            return None
        
        update_data = camera_in.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(camera_db, field, value)
            
        await self._db_session.commit()
        await self._db_session.refresh(camera_db)
        return camera_model.Camera.from_orm(camera_db)

    async def delete(self, *, camera_id: UUID) -> Optional[camera_model.Camera]:
        camera_db = await self._db_session.get(db_schema.Camera, camera_id)
        if not camera_db:
            return None
        
        await self._db_session.delete(camera_db)
        await self._db_session.commit()
        return camera_model.Camera.from_orm(camera_db)