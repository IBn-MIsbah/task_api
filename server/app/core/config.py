from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    DATABASE_URL: str
    ACCESS_TOKEN_SECRET_KEY: str
    REFRESH_TOKEN_SECRET_KEY: str
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: float = 0.5
    REFRESH_TOKEN_EXPIRE_MINUTES: int = 10

    model_config = SettingsConfigDict(env_file=".env")


settings = Settings()
