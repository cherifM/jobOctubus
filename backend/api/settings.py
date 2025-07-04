from fastapi import APIRouter, Depends
from typing import Dict, Any
from config import settings
from utils.logging import get_logger
from schemas.schemas import User
from api.auth import get_current_user

logger = get_logger(__name__)
router = APIRouter()

@router.get("/job-search-services")
async def get_job_search_services(current_user: User = Depends(get_current_user)) -> Dict[str, Any]:
    """
    Get current job search service configuration
    """
    return {
        "services": {
            "remoteok": {
                "enabled": settings.enable_remoteok,
                "name": "RemoteOK",
                "description": "Remote job listings",
                "requires_api_key": False
            },
            "arbeitsagentur": {
                "enabled": settings.enable_arbeitsagentur,
                "name": "Arbeitsagentur",
                "description": "German Federal Employment Agency",
                "requires_api_key": False
            },
            "thelocal": {
                "enabled": settings.enable_thelocal,
                "name": "TheLocal.de",
                "description": "Jobs in Germany for expats",
                "requires_api_key": False
            },
            "linkedin": {
                "enabled": settings.enable_linkedin,
                "name": "LinkedIn",
                "description": "Professional network jobs",
                "requires_api_key": True,
                "has_api_key": bool(settings.linkedin_api_key and settings.linkedin_api_key != "your_linkedin_key_here")
            },
            "indeed": {
                "enabled": settings.enable_indeed,
                "name": "Indeed",
                "description": "General job search engine",
                "requires_api_key": True,
                "has_api_key": bool(settings.indeed_api_key and settings.indeed_api_key != "your_indeed_key_here")
            }
        }
    }