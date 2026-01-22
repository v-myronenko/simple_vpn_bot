from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    APP_NAME: str = "svpn-backend"
    ENV: str = "dev"
    DEBUG: bool = True

    HOST: str = "0.0.0.0"
    PORT: int = 8000

    SECRET_KEY: str = "change_me"

    DATABASE_URL: str = "sqlite:///./svpn.db"
    TZ: str = "Europe/Warsaw"


settings = Settings()
