# backend-api/run_consumer.py
import sys
from pathlib import Path

# Thêm thư mục gốc của dự án vào Python path
# Điều này cho phép consumer tìm thấy module 'app'
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from app.infrastructure.messaging.violation_consumer import start_consuming

if __name__ == "__main__":
    start_consuming()