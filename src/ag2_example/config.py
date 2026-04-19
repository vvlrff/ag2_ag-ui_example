from pydantic import Field, SecretStr
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file_encoding="utf-8",
        env_nested_delimiter="__",
        env_prefix="AG2EX__",
        extra="ignore",
    )

    app_name: str = "ag2-ag-ui-example"

    openai_api_key: SecretStr = Field(default=SecretStr("sk-placeholder"))
    openai_model: str = "gpt-4o-mini"
    openai_proxy_url: str | None = None

    database_url: str = "postgresql+psycopg://user:password@localhost:5432/note_db"

    log_level: str = "INFO"
    log_json: bool = False
