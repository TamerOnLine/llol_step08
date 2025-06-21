from dotenv import load_dotenv
import os
from pathlib import Path

def load_env_config():
    # المسار إلى ملف .env في جذر المشروع
    env_path = Path(__file__).resolve().parents[2] / ".env"
    load_dotenv(dotenv_path=env_path)

    return {
        "DB_NAME": os.getenv("DB_NAME"),
        "DB_USER": os.getenv("DB_USER"),
        "DB_PASSWORD": os.getenv("DB_PASSWORD"),
        "DB_HOST": os.getenv("DB_HOST", "localhost"),
        "DB_PORT": int(os.getenv("DB_PORT", 5432)),
        "FLASK_DEBUG": os.getenv("FLASK_DEBUG", "True"),
    }
