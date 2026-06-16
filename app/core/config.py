import os
from typing import List, Union
from pydantic import field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict

# Determine configuration files to load.
# Order: .env (local default) -> config.env (default override) -> CONFIG_PATH (explicit override)
_env_files = [".env"]

if os.path.exists("config.env"):
    _env_files.append("config.env")

_custom_config = os.getenv("CONFIG_PATH")
if _custom_config and os.path.exists(_custom_config):
    _env_files.append(_custom_config)

class Settings(BaseSettings):
    PROJECT_NAME: str = "迅捷后台管理系统"
    API_V1_STR: str = "/api/v1"
    SECRET_KEY: str = "supersecretkeyreplaceinproduction"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 10080
    DATABASE_URL: str = "sqlite+aiosqlite:///./sqlite.db"
    
    # JWT Algorithm
    ALGORITHM: str = "HS256"
    
    # CORS Origins
    BACKEND_CORS_ORIGINS: Union[str, List[str]] = [
        "http://localhost",
        "http://localhost:5173",
        "http://127.0.0.1:5173",
        "http://localhost:8000",
    ]

    @field_validator("BACKEND_CORS_ORIGINS", mode="before")
    @classmethod
    def assemble_cors_origins(cls, v: Union[str, List[str]]) -> List[str]:
        if isinstance(v, str):
            if v.startswith("[") and v.endswith("]"):
                import json
                try:
                    return json.loads(v)
                except Exception:
                    pass
            return [i.strip() for i in v.split(",") if i.strip()]
        elif isinstance(v, list):
            return v
        return []

    model_config = SettingsConfigDict(
        env_file=tuple(_env_files),
        env_file_encoding="utf-8",
        case_sensitive=True,
        extra="ignore"
    )

settings = Settings()

