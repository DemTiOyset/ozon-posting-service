from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    DATABASE_URL: str
    CLIENT_ID: str
    API_KEY: str
    GOOGLE_SHEET_ID: str
    GOOGLE_SHEET_NAME: str
    GOOGLE_SHEETS_PATH: str

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )


settings = Settings()
