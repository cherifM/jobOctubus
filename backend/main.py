from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from contextlib import asynccontextmanager
import os
from dotenv import load_dotenv

from database import engine, Base, get_db
from api import jobs, cvs, applications, auth, status, settings as settings_api
from config import settings
from utils.logging import setup_logging, get_logger

load_dotenv()

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Setup logging
    setup_logging(log_level="INFO" if not settings.debug else "DEBUG")
    logger = get_logger(__name__)
    logger.info("Starting JobOctubus application")
    
    # Create database tables
    Base.metadata.create_all(bind=engine)
    logger.info("Database tables created/verified")
    
    yield
    
    logger.info("Shutting down JobOctubus application")

app = FastAPI(
    title="JobOctubus",
    description="Agentic Job Search Tool with CV Adaptation and Cover Letter Generation",
    version="1.0.0",
    lifespan=lifespan
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.get_cors_origins(),
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router, prefix="/api/auth", tags=["authentication"])
app.include_router(jobs.router, prefix="/api/jobs", tags=["jobs"])
app.include_router(cvs.router, prefix="/api/cvs", tags=["cvs"])
app.include_router(applications.router, prefix="/api/applications", tags=["applications"])
app.include_router(status.router, prefix="/api/status", tags=["status"])
app.include_router(settings_api.router, prefix="/api/settings", tags=["settings"])

@app.get("/")
async def root():
    return {"message": "JobOctubus API is running"}

@app.get("/health")
async def health_check():
    return {"status": "healthy"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000, reload=True)