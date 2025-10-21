# backend-api/run_consumer.py
import sys
from pathlib import Path

project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from app.infrastructure.messaging.violation_consumer import start_consuming

if __name__ == "__main__":
    start_consuming()