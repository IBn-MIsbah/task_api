from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    DATABASE_URL: str
    ACCESS_TOKEN_SECRET_KEY: str
    REFRESH_TOKEN_SECRET_KEY: str
    ALGORITHM: str = "HS256"
    ENVIRONMENT: str = "development"
    ACCESS_TOKEN_EXPIRE_MINUTES: float = 30
    REFRESH_TOKEN_EXPIRE_MINUTES: int = 10080

    @property
    def COOKIE_SECURE(self)-> bool:
        self.ENVIRONMENT == "production"

    model_config = SettingsConfigDict(env_file=".env")


settings = Settings()
