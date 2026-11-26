"""
Central application configuration.

All values are pulled from environment variables (see .env.example) so the
same codebase can move between local SQLite demos and a real local MySQL
install without touching any Python code — a core "environment configuration"
requirement of the project.
"""
import os
from pathlib import Path
from dotenv import load_dotenv

BASE_DIR = Path(__file__).resolve().parent
load_dotenv(BASE_DIR / ".env")


def _bool(value, default=False):
    if value is None:
        return default
    return str(value).strip().lower() in {"1", "true", "yes", "on"}


class Config:
    """Base configuration shared by every environment."""

    SECRET_KEY = os.getenv("SECRET_KEY", "dev-secret-key-change-me")

    # --- Database -----------------------------------------------------
    USE_SQLITE_FALLBACK = _bool(os.getenv("USE_SQLITE_FALLBACK"), default=True)

    if USE_SQLITE_FALLBACK:
        INSTANCE_DIR = BASE_DIR / "instance"
        INSTANCE_DIR.mkdir(exist_ok=True)
        SQLALCHEMY_DATABASE_URI = f"sqlite:///{INSTANCE_DIR / 'smart_restaurant.db'}"
    else:
        DB_ENGINE = os.getenv("DB_ENGINE", "mysql+pymysql")
        DB_USER = os.getenv("DB_USER", "root")
        DB_PASSWORD = os.getenv("DB_PASSWORD", "")
        DB_HOST = os.getenv("DB_HOST", "127.0.0.1")
        DB_PORT = os.getenv("DB_PORT", "3306")
        DB_NAME = os.getenv("DB_NAME", "smart_restaurant_db")
        SQLALCHEMY_DATABASE_URI = (
            f"{DB_ENGINE}://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"
            f"?charset=utf8mb4"
        )

    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_ENGINE_OPTIONS = {"pool_pre_ping": True}

    # --- Business settings ---------------------------------------------
    RESTAURANT_NAME = os.getenv("RESTAURANT_NAME", "Smart Restaurant")
    RESTAURANT_ADDRESS = os.getenv("RESTAURANT_ADDRESS", "")
    RESTAURANT_PHONE = os.getenv("RESTAURANT_PHONE", "")
    RESTAURANT_GSTIN = os.getenv("RESTAURANT_GSTIN", "")
    DEFAULT_GST_PERCENT = float(os.getenv("DEFAULT_GST_PERCENT", "5.0"))
    CURRENCY_SYMBOL = os.getenv("CURRENCY_SYMBOL", "Rs.")

    # --- Backups ---------------------------------------------------------
    BACKUP_DIR = Path(os.getenv("BACKUP_DIR", str(BASE_DIR / "backups")))
    AUTO_BACKUP_ON_STARTUP = _bool(os.getenv("AUTO_BACKUP_ON_STARTUP"), default=False)

    # --- Uploads / exports -------------------------------------------
    EXPORT_DIR = Path(os.getenv("EXPORT_DIR", str(BASE_DIR / "exports")))

    # --- Pagination -----------------------------------------------------
    ITEMS_PER_PAGE = 20

    # --- Logging ---------------------------------------------------------
    LOG_DIR = Path(os.getenv("LOG_DIR", str(BASE_DIR / "logs")))
    LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")


class DevelopmentConfig(Config):
    DEBUG = True


class ProductionConfig(Config):
    DEBUG = False


class TestingConfig(Config):
    TESTING = True
    SQLALCHEMY_DATABASE_URI = "sqlite:///:memory:"
    WTF_CSRF_ENABLED = False


CONFIG_MAP = {
    "development": DevelopmentConfig,
    "production": ProductionConfig,
    "testing": TestingConfig,
}


def get_config(name: str | None = None):
    name = name or os.getenv("FLASK_ENV", "development")
    return CONFIG_MAP.get(name, DevelopmentConfig)
