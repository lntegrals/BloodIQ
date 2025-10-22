import os
from dataclasses import dataclass
from dotenv import load_dotenv


load_dotenv()


@dataclass
class Config:
    SECRET_KEY: str = os.getenv("SECRET_KEY", os.urandom(24).hex())
    GEMINI_API_KEY: str | None = os.getenv("GEMINI_API_KEY")
    AI_ENABLED: bool = bool(GEMINI_API_KEY)
    JSON_SORT_KEYS: bool = False
    CORS_ORIGINS: str = os.getenv("CORS_ORIGINS", "*")
    RATELIMIT_DEFAULT: str = os.getenv("RATELIMIT_DEFAULT", "20/minute")
    RATELIMIT_STORAGE_URI: str = os.getenv("RATELIMIT_STORAGE_URI", "memory://")

