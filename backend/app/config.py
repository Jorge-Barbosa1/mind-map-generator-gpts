from pydantic_settings import BaseSettings
from pathlib import Path

# Get the backend directory (parent of app directory)
BASE_DIR = Path(__file__).resolve().parent.parent
ENV_FILE = BASE_DIR / ".env"

class Settings(BaseSettings):
    openrouter_api_key: str

    class Config:
        env_file = str(ENV_FILE)

settings = Settings()
