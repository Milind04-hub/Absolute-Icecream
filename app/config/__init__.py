import os


def _database_url(default=None):
    """Read DATABASE_URL, accepting the postgres:// form some hosts provide."""
    url = os.getenv("DATABASE_URL", default)
    if url and url.startswith("postgres://"):
        url = "postgresql+psycopg://" + url[len("postgres://"):]
    elif url and url.startswith("postgresql://"):
        url = "postgresql+psycopg://" + url[len("postgresql://"):]
    return url


class BaseConfig:
    SECRET_KEY = os.getenv("SECRET_KEY", "dev-secret-key-change-me")

    SQLALCHEMY_TRACK_MODIFICATIONS = False

    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = "Lax"
    SESSION_COOKIE_SECURE = False

    MAX_CONTENT_LENGTH = 16 * 1024 * 1024

    # Public address that printed QR codes must point to, for example
    # https://absolute-icecream.onrender.com. Without it, QR links are built
    # from whatever address the page was opened on (often 127.0.0.1).
    # Render sets RENDER_EXTERNAL_URL to the service's own https address.
    PUBLIC_BASE_URL = (
        os.getenv("PUBLIC_BASE_URL") or os.getenv("RENDER_EXTERNAL_URL") or ""
    ).strip().rstrip("/")

    # Show clearly labelled sample lab results on report pages (demo only).
    SHOW_SAMPLE_LAB_REPORTS = os.getenv("SHOW_SAMPLE_LAB_REPORTS", "0") == "1"

    # Trust X-Forwarded-* headers from the hosting platform's proxy.
    TRUST_PROXY_HEADERS = os.getenv("TRUST_PROXY_HEADERS", "0") == "1"


class DevelopmentConfig(BaseConfig):
    DEBUG = True

    SQLALCHEMY_DATABASE_URI = _database_url("sqlite:///absolute_icecream.db")


class TestingConfig(BaseConfig):
    TESTING = True
    WTF_CSRF_ENABLED = False

    SQLALCHEMY_DATABASE_URI = os.getenv(
        "TEST_DATABASE_URL",
        "sqlite:///test.db"
    )


class ProductionConfig(BaseConfig):
    DEBUG = False

    SQLALCHEMY_DATABASE_URI = _database_url("sqlite:///absolute_icecream.db")

    SESSION_COOKIE_SECURE = True
    TRUST_PROXY_HEADERS = os.getenv("TRUST_PROXY_HEADERS", "1") == "1"


config_by_name = {
    "development": DevelopmentConfig,
    "testing": TestingConfig,
    "production": ProductionConfig,
}
