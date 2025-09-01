from functools import lru_cache
from pathlib import Path

from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    # Directory where subghz scripts are stored
    SUBGHZ_DIR: str = str(Path(__file__).resolve().parents[2] / "subghz")

    # Max execution time (seconds) for a script
    SCRIPT_TIMEOUT_SEC: int = 60

    # Comma-separated list of allowed script extensions (e.g. ".py,.sh,.sub")
    SUBGHZ_ALLOWED_EXTS: str = ".py,.sh"

    # Whether to search scripts recursively within SUBGHZ_DIR
    SUBGHZ_RECURSIVE: bool = False

    # Logging level for the application (DEBUG, INFO, WARNING, ERROR)
    LOG_LEVEL: str = "INFO"

    class Config:
        env_file = ".env"
        case_sensitive = True


@lru_cache
def get_settings() -> Settings:
    return Settings()


settings = get_settings()
