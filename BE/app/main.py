# backend-api/app/main.py
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import Response
from fastapi.staticfiles import StaticFiles

from .api.endpoints import cameras, violations
from .infrastructure.db import schema
from .infrastructure.db.postgres_setup import Base, engine

app = FastAPI(
    title="Hanoi Traffic Sentinel API",
    version="1.0.0",
    description="API cho hệ thống Giám sát Giao thông Hà Nội."
)
async def create_tables():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
app.mount("/static", StaticFiles(directory="static"), name="static")



# Gắn cả hai router vào ứng dụng
app.include_router(cameras.router, prefix="/api/v1/cameras", tags=["Cameras"])
app.include_router(violations.router, prefix="/api/v1/violations", tags=["Violations"])

@app.on_event("startup")
async def on_startup():
    print("Khởi động server... Đang tạo bảng trong database nếu chưa có.")
    await create_tables()
    print("Khởi động hoàn tất.")
@app.get("/", tags=["Health Check"])
def read_root():
    return {"message": "Hanoi Traffic Sentinel API is running!"}

@app.get("/favicon.ico", include_in_schema=False)
async def favicon():
    # Return a 204 No Content response
    return Response(status_code=204)