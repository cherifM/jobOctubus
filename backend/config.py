import os
from pydantic_settings import BaseSettings
from pydantic import validator
from typing import List

class Settings(BaseSettings):
    database_url: str = "sqlite:///./joboctubus.db"
    
    openrouter_api_key: str
    openrouter_base_url: str = "https://openrouter.ai/api/v1"
    
    linkedin_api_key: str = ""
    indeed_api_key: str = ""
    
    personal_website_cv_en_path: str = "/home/cherif/dev/personal-website/assets/cv/Mihoubi_Med_Cherif_CV_EN.pdf"
    personal_website_cv_de_path: str = "/home/cherif/dev/personal-website/assets/cv/Mihoubi_Med_Cherif_CV_DE.pdf"
    
    secret_key: str
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 30
    
    redis_url: str = "redis://localhost:6379/0"
    
    debug: bool = False
    cors_origins: str = "http://localhost:3000,http://localhost:8000"
    
    model_config = {"env_file": "../.env"}
    
    def get_cors_origins(self) -> List[str]:
        return self.cors_origins.split(",")
    
    @validator('openrouter_api_key')
    def validate_openrouter_key(cls, v):
        if not v or v == "your_openrouter_key_here" or len(v) < 10:
            raise ValueError("Valid OpenRouter API key required. Please set OPENROUTER_API_KEY in your .env file")
        return v
    
    @validator('secret_key')
    def validate_secret_key(cls, v):
        if not v or v == "your_secret_key_here" or len(v) < 32:
            raise ValueError("Valid secret key required (min 32 chars). Please set SECRET_KEY in your .env file")
        return v
    
    @validator('personal_website_cv_en_path', 'personal_website_cv_de_path')
    def validate_cv_paths(cls, v):
        if not os.path.exists(v):
            print(f"Warning: CV path does not exist: {v}")
        return v

settings = Settings()