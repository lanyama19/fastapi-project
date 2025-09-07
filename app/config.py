from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import SecretStr


class Settings(BaseSettings):
    database_hostname: str
    database_port: int
    database_password: str
    database_name: str
    database_username: str
    secret_key: str
    algorithm: str
    access_token_expire_minutes: int

    # pydantic-settings v2 style config
    model_config = SettingsConfigDict(env_file=(".env",), env_file_encoding="utf-8")

settings = Settings()
