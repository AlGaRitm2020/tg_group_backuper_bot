from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict

BASE_DIR = Path(__file__).parent.parent
ENV_FILE_PATH = BASE_DIR / ".env"


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=ENV_FILE_PATH,
        env_file_encoding="utf-8",
        extra="ignore",
    )

    TOKEN: str
    DEST_CHAT_ID: str
    SOURCE_CHAT_ID: str
    ADMINS: list[str]


settings = Settings()

if __name__ == "__main__":
    print(ENV_FILE_PATH)
    print(settings.model_dump())
