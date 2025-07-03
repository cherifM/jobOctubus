import os
from pydantic_settings import BaseSettings
from typing import List

class Settings(BaseSettings):
    database_url: str = "sqlite:///./joboctubus.db"
    
    openrouter_api_key: str
    openrouter_base_url: str = "https://openrouter.ai/api/v1"
    
    linkedin_api_key: str = ""
    indeed_api_key: str = ""
    
    secret_key: str
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 30
    
    redis_url: str = "redis://localhost:6379/0"
    
    debug: bool = True
    cors_origins: str = "http://localhost:3000,http://localhost:8000"
    
    model_config = {"env_file": "../.env"}
    
    def get_cors_origins(self) -> List[str]:
        return self.cors_origins.split(",")

settings = Settings()