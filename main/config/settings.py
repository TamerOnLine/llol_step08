# settings.py

import os
from main.config.config_loader import load_env_config

class Config:
    """
    Central configuration class for the Flask application.
    """

    config = load_env_config()

    SECRET_KEY = os.environ.get('SECRET_KEY', 'dev_key')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    DEBUG = config.get("FLASK_DEBUG", "True") == "True"

    # ✅ إعداد اتصال PostgreSQL من .env
    DB_NAME = config["DB_NAME"]
    DB_USER = config["DB_USER"]
    DB_PASSWORD = config["DB_PASSWORD"]
    DB_HOST = config["DB_HOST"]
    DB_PORT = config["DB_PORT"]

    SQLALCHEMY_DATABASE_URI = (
        f"postgresql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"
    )
