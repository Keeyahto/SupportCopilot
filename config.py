import os
from typing import Optional

class Config:
    # Database
    DATABASE_URL: str = os.getenv("DATABASE_URL", "postgresql://user:password@localhost:5432/supportcopilot")
    
    # Redis
    REDIS_URL: str = os.getenv("REDIS_URL", "redis://localhost:6379")
    
    # OpenAI
    OPENAI_API_KEY: Optional[str] = os.getenv("OPENAI_API_KEY")
    
    # Bot
    BOT_TOKEN: Optional[str] = os.getenv("BOT_TOKEN")
    
    # API
    API_HOST: str = os.getenv("API_HOST", "0.0.0.0")
    API_PORT: int = int(os.getenv("API_PORT", "8000"))
    
    # Tools API
    TOOLS_API_HOST: str = os.getenv("TOOLS_API_HOST", "0.0.0.0")
    TOOLS_API_PORT: int = int(os.getenv("TOOLS_API_PORT", "8001"))
    
    # Environment
    ENVIRONMENT: str = os.getenv("ENVIRONMENT", "development")
    DEBUG: bool = os.getenv("DEBUG", "true").lower() == "true"

config = Config()
