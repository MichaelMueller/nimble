# builtin
from typing import Literal, Union
# 3rd party
from pydantic_settings import BaseSettings, SettingsConfigDict
# local


class ApiConfig(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",            # optional: load from .env file
        env_file_encoding="utf-8",
        env_nested_delimiter="_",
        extra="ignore",             # ignore extra vars instead of raising
    )

    # define your settings
    database_url: str = "sqlite+aiosqlite:///:memory:"
    echo_sql: bool = False
