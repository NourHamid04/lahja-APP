from functools import lru_cache
import os

from dotenv import load_dotenv

load_dotenv()


class Settings:
    def __init__(self) -> None:
        self.app_name = "Lahja API"
        self.app_version = "0.1.0"
        self.environment = os.getenv("ENVIRONMENT", "development")
        self.openai_api_key = os.getenv("OPENAI_API_KEY", "")
        self.openai_model = os.getenv("OPENAI_MODEL", "gpt-5.6-luna")
        self.mock_mode = os.getenv("LAHJA_MOCK_MODE", "false").lower() == "true"
        self.max_text_length = int(os.getenv("MAX_TEXT_LENGTH", "2000"))
        self.rate_limit_per_minute = int(os.getenv("RATE_LIMIT_PER_MINUTE", "20"))
        origins = os.getenv(
            "ALLOWED_ORIGINS",
            "http://localhost:5173,http://127.0.0.1:5173",
        )
        self.allowed_origins = [origin.strip() for origin in origins.split(",") if origin.strip()]


@lru_cache
def get_settings() -> Settings:
    return Settings()
