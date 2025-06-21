import psycopg2
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT
from .config_loader import load_env_config  # ✅ استيراد نسبي
import logging

# ✅ إعداد نظام تسجيل الرسائل
logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')
logger = logging.getLogger(__name__)

# ✅ تحميل الإعدادات من ملف .env
config = load_env_config()
DB_NAME = config["DB_NAME"]
DB_USER = config["DB_USER"]
DB_PASSWORD = config["DB_PASSWORD"]
DB_HOST = config["DB_HOST"]
DB_PORT = config.get("DB_PORT", 5432)

def ensure_database_exists():
    logger.info(f"🧪 Connecting to admin DB 'postgres' to check/create '{DB_NAME}'...")

    try:
        with psycopg2.connect(
            dbname="postgres",
            user=DB_USER,
            password=DB_PASSWORD,
            host=DB_HOST,
            port=DB_PORT
        ) as conn:
            conn.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
            with conn.cursor() as cur:
                cur.execute("SELECT 1 FROM pg_database WHERE datname = %s;", (DB_NAME,))
                exists = cur.fetchone()

                if not exists:
                    cur.execute(f"CREATE DATABASE {DB_NAME};")
                    logger.info(f"✅ Database '{DB_NAME}' created successfully.")
                else:
                    logger.info(f"✅ Database '{DB_NAME}' already exists.")

    except Exception as e:
        logger.error("❌ Failed to verify or create the database:")
        logger.exception(e)
