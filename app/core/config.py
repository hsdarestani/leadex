import os
from pydantic_settings import BaseSettings
from typing import List


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    # Application
    APP_NAME: str = "Leadex"
    APP_ENV: str = "development"
    SECRET_KEY: str
    DEBUG: bool = True

    # Database
    DATABASE_URL: str

    # Redis
    REDIS_URL: str = "redis://localhost:6379/0"

    # Server
    HOST: str = "0.0.0.0"
    PORT: int = 8000

    # Security
    ALLOWED_HOSTS: str = "localhost,127.0.0.1"
    CORS_ORIGINS: str = "http://localhost:3000"

    # reCAPTCHA
    RECAPTCHA_SECRET_KEY: str
    RECAPTCHA_SITE_KEY: str

    # Email (SendGrid)
    EMAIL_BACKEND: str = "sendgrid"
    SENDGRID_API_KEY: str
    SENDGRID_FROM_EMAIL: str

    # WhatsApp (Meta Business API)
    META_ACCESS_TOKEN: str = ""
    META_PHONE_NUMBER_ID: str = ""
    META_BUSINESS_ACCOUNT_ID: str = ""
    META_VERIFY_TOKEN: str = ""
    WHATSIPLUS_API_KEY: str = ""

    # Google Sheets
    GOOGLE_CREDENTIALS_FILE: str = "credentials.json"
    GOOGLE_SERVICE_ACCOUNT_EMAIL: str = ""

    # GeoIP
    GEOIP_DATABASE_PATH: str = "/usr/share/GeoIP/GeoLite2-City.mmdb"

    # Lead Settings
    DEDUPE_WINDOW_DAYS: int = 20
    BATCH_SIZE: int = 1
    RETRY_ATTEMPTS: int = 3
    STORED_LEADS_INTERVAL_MINUTES: int = 1

    # Credits
    DEFAULT_CREDIT_COST: float = 1.0

    # JWT
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24 * 7
    ALGORITHM: str = "HS256"

    class Config:
        env_file = ".env"
        case_sensitive = True

    @property
    def allowed_hosts_list(self) -> List[str]:
        return [host.strip() for host in self.ALLOWED_HOSTS.split(",")]

    @property
    def cors_origins_list(self) -> List[str]:
        return [origin.strip() for origin in self.CORS_ORIGINS.split(",")]


settings = Settings()
