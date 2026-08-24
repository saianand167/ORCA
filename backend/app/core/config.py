import os
from pathlib import Path
from pydantic import BaseModel
from dotenv import load_dotenv

# Load .env or root sai.env if exists
env_paths = [
    Path(__file__).resolve().parent.parent.parent / ".env",
    Path(__file__).resolve().parent.parent.parent.parent / "sai.env"
]
for p in env_paths:
    if p.exists():
        load_dotenv(p)

class Settings(BaseModel):
    PROJECT_NAME: str = "ORCA - Marine Ecosystem Reasoning with Collaborative Agents"
    VERSION: str = "1.0.0"
    API_V1_PREFIX: str = "/api"
    
    # Environment credentials
    GROQ_API_KEY: str = os.getenv("GROQ_API_KEY", os.getenv("groq_api_key", ""))
    IMD_API_KEY: str = os.getenv("IMD_API_KEY", "")
    WEATHER_API_KEY: str = os.getenv("WEATHER_API_KEY", "")
    MOSDAC_USERNAME: str = os.getenv("MOSDAC_USERNAME", "")
    MOSDAC_PASSWORD: str = os.getenv("MOSDAC_PASSWORD", "")
    
    # SQLite DB
    DATABASE_URL: str = os.getenv("DATABASE_URL", "sqlite:///./orca.db")
    
    # Cache duration in seconds (15 minutes default)
    CACHE_TTL_SECONDS: int = 900
    
    # Base dir
    BASE_DIR: Path = Path(__file__).resolve().parent.parent

settings = Settings()

