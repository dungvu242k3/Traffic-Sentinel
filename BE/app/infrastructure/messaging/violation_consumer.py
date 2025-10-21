# backend-api/app/infrastructure/messaging/violation_consumer.py
import asyncio
import base64
import functools
import json
import threading
import uuid
from datetime import datetime
from pathlib import Path

import pika
from app.core.models.violation import ViolationCreate
from app.infrastructure.db.postgres_setup import AsyncSessionLocal
from app.infrastructure.db.schema import Camera, Violation

IMAGE_SAVE_PATH = Path("static/images")
IMAGE_SAVE_PATH.mkdir(parents=True, exist_ok=True)

class AsyncioEventLoopThread(threading.Thread):
    """Một thread riêng chỉ để chạy asyncio event loop."""
    def __init__(self):
        super().__init__(daemon=True)
        self.loop = asyncio.new_event_loop()
        self.running = False

    def run(self):
        asyncio.set_event_loop(self.loop)
        self.running = True
        self.loop.run_forever()

    def stop(self):
        if self.running:
            self.loop.call_soon_threadsafe(self.loop.stop)

    def submit_coroutine(self, coro):
        """Gửi một coroutine để thực thi trong event loop của thread này."""
        return asyncio.run_coroutine_threadsafe(coro, self.loop)

async def save_violation_to_db(violation_data: dict):
    # ... (Hàm này giữ nguyên như cũ, không cần thay đổi)
    async with AsyncSessionLocal() as session:
        async with session.begin():
            camera = await session.get(Camera, violation_data["camera_id"])
            if not camera:
                print(f"Lỗi: Không tìm thấy camera ID {violation_data['camera_id']}.")
                return
            new_violation = Violation(
                camera_id=camera.id,
                timestamp=violation_data["timestamp"],
                violation_type=violation_data["violation_type"],
                license_plate=violation_data["license_plate"],
                image_url=violation_data["image_url"]
            )
            session.add(new_violation)
            await session.commit()
            print(f"✅ Đã lưu thành công vi phạm {new_violation.id} vào database.")

def process_message(channel, method, properties, body, asyncio_thread: AsyncioEventLoopThread):
    print(f" [📥] Đã nhận một tin nhắn vi phạm mới.")
    try:
        message = json.loads(body)
        violation_in = ViolationCreate(**message)

        image_data = base64.b64decode(violation_in.image_base64)
        image_filename = f"{uuid.uuid4()}.jpg"
        image_path = IMAGE_SAVE_PATH / image_filename
        
        with open(image_path, "wb") as f:
            f.write(image_data)
        print(f"📸 Ảnh đã được lưu tại: {image_path}")

        db_data = violation_in.model_dump()
        db_data["image_url"] = f"static/images/{image_filename}"
        
        # ✅ THAY THẾ asyncio.run() BẰNG CÁCH NÀY:
        # Gửi tác vụ lưu DB vào event loop đang chạy trong thread riêng.
        future = asyncio_thread.submit_coroutine(save_violation_to_db(db_data))
        future.result() # Đợi cho đến khi tác vụ hoàn thành (nếu cần)

        channel.basic_ack(delivery_tag=method.delivery_tag)

    except Exception as e:
        print(f"❌ Lỗi khi xử lý tin nhắn: {e}")
        import traceback
        traceback.print_exc()

def start_consuming():
    print("Đang khởi động trình tiêu thụ vi phạm...")
    
    # Khởi động event loop trong một thread riêng
    asyncio_thread = AsyncioEventLoopThread()
    asyncio_thread.start()
    
    connection = None
    try:
        connection = pika.BlockingConnection(pika.ConnectionParameters(host='localhost'))
        channel = connection.channel()
        channel.queue_declare(queue='violation_queue', durable=True)
        print(' [*] Đang chờ tin nhắn vi phạm. Để thoát, nhấn CTRL+C')
        channel.basic_qos(prefetch_count=1)
        
        # Dùng functools.partial để truyền đối tượng asyncio_thread vào callback
        on_message_callback = functools.partial(process_message, asyncio_thread=asyncio_thread)
        
        channel.basic_consume(queue='violation_queue', on_message_callback=on_message_callback)
        channel.start_consuming()

    except pika.exceptions.AMQPConnectionError as e:
        print(f"🔴 Không thể kết nối đến RabbitMQ: {e}.")
    except KeyboardInterrupt:
        print("\nĐang dừng consumer...")
    finally:
        if connection and connection.is_open:
            connection.close()
        # Dừng event loop thread một cách an toàn
        asyncio_thread.stop()
        print("Consumer đã dừng.")