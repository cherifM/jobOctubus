from fastapi import APIRouter
import httpx
from typing import Dict, Any
import asyncio
from config import settings
from utils.logging import get_logger

logger = get_logger(__name__)
router = APIRouter()

@router.get("/health")
async def get_system_status() -> Dict[str, Any]:
    """
    Check the health status of all external services
    """
    status = {
        "openrouter": {"status": "unknown", "message": "", "response_time": 0, "enabled": True},
        "arbeitsagentur": {"status": "unknown", "message": "", "response_time": 0, "enabled": settings.enable_arbeitsagentur},
        "remoteok": {"status": "unknown", "message": "", "response_time": 0, "enabled": settings.enable_remoteok},
        "adzuna": {"status": "unknown", "message": "", "response_time": 0, "enabled": False},  # Not implemented
        "overall": "checking"
    }
    
    # Check only enabled services concurrently
    tasks = [check_openrouter_status()]  # OpenRouter is always checked
    service_names = ["openrouter"]
    
    if settings.enable_arbeitsagentur:
        tasks.append(check_arbeitsagentur_status())
        service_names.append("arbeitsagentur")
    
    if settings.enable_remoteok:
        tasks.append(check_remoteok_status())
        service_names.append("remoteok")
    
    # Adzuna is always disabled for now
    service_names.append("adzuna")
    
    try:
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        # Update status with results (only for enabled services)
        for i, result in enumerate(results):
            service_name = service_names[i]
            if isinstance(result, dict):
                status[service_name].update(result)
            else:
                status[service_name].update({
                    "status": "error", 
                    "message": str(result), 
                    "response_time": 0
                })
        
        # Mark disabled services as such
        for service_name in ["arbeitsagentur", "remoteok"]:
            if not status[service_name]["enabled"]:
                status[service_name].update({
                    "status": "disabled",
                    "message": "Service disabled in configuration",
                    "response_time": 0
                })
        
        # Determine overall status (only consider enabled services)
        enabled_statuses = [status[service]["status"] for service in service_names if status[service]["enabled"]]
        if all(s == "connected" for s in enabled_statuses):
            status["overall"] = "healthy"
        elif any(s == "connected" for s in enabled_statuses):
            status["overall"] = "partial"
        else:
            status["overall"] = "unhealthy"
            
    except Exception as e:
        logger.error(f"Error checking system status: {e}")
        status["overall"] = "error"
    
    return status

async def check_openrouter_status() -> Dict[str, Any]:
    """Check OpenRouter API status"""
    import time
    start_time = time.time()
    
    try:
        async with httpx.AsyncClient() as client:
            # Simple test request to OpenRouter
            headers = {
                "Authorization": f"Bearer {settings.openrouter_api_key}",
                "Content-Type": "application/json"
            }
            
            # Use a minimal request to check connectivity
            response = await client.get(
                f"{settings.openrouter_base_url}/models",
                headers=headers,
                timeout=5.0
            )
            
            response_time = round((time.time() - start_time) * 1000)
            
            if response.status_code == 200:
                return {
                    "status": "connected",
                    "message": "OpenRouter API accessible",
                    "response_time": response_time
                }
            else:
                return {
                    "status": "error",
                    "message": f"HTTP {response.status_code}",
                    "response_time": response_time
                }
                
    except httpx.TimeoutException:
        return {
            "status": "timeout",
            "message": "Request timeout (>5s)",
            "response_time": 5000
        }
    except Exception as e:
        return {
            "status": "error",
            "message": str(e)[:100],
            "response_time": round((time.time() - start_time) * 1000)
        }

async def check_arbeitsagentur_status() -> Dict[str, Any]:
    """Check German Federal Employment Agency API status"""
    import time
    start_time = time.time()
    
    try:
        async with httpx.AsyncClient() as client:
            # Check if the Arbeitsagentur website is accessible
            url = "https://www.arbeitsagentur.de/jobsuche/"
            headers = {
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
            }
            
            response = await client.get(url, headers=headers, timeout=5.0, follow_redirects=True)
            response_time = round((time.time() - start_time) * 1000)
            
            if response.status_code == 200:
                return {
                    "status": "connected",
                    "message": "Arbeitsagentur website accessible",
                    "response_time": response_time
                }
            else:
                return {
                    "status": "error",
                    "message": f"HTTP {response.status_code}",
                    "response_time": response_time
                }
                
    except httpx.TimeoutException:
        return {
            "status": "timeout",
            "message": "Request timeout (>5s)",
            "response_time": 5000
        }
    except Exception as e:
        return {
            "status": "error",
            "message": str(e)[:100],
            "response_time": round((time.time() - start_time) * 1000)
        }

async def check_remoteok_status() -> Dict[str, Any]:
    """Check RemoteOK API status"""
    import time
    start_time = time.time()
    
    try:
        async with httpx.AsyncClient() as client:
            headers = {"User-Agent": "JobOctubus/1.0 (job-search-tool)"}
            
            # Use GET instead of HEAD and follow redirects
            response = await client.get("https://remoteok.com/api", headers=headers, timeout=5.0, follow_redirects=True)
            response_time = round((time.time() - start_time) * 1000)
            
            if response.status_code == 200:
                return {
                    "status": "connected",
                    "message": "RemoteOK API accessible",
                    "response_time": response_time
                }
            else:
                return {
                    "status": "error",
                    "message": f"HTTP {response.status_code}",
                    "response_time": response_time
                }
                
    except httpx.TimeoutException:
        return {
            "status": "timeout",
            "message": "Request timeout (>5s)",
            "response_time": 5000
        }
    except Exception as e:
        return {
            "status": "error",
            "message": str(e)[:100],
            "response_time": round((time.time() - start_time) * 1000)
        }

async def check_adzuna_status() -> Dict[str, Any]:
    """Check Adzuna API status"""
    import time
    start_time = time.time()
    
    try:
        async with httpx.AsyncClient() as client:
            url = "https://api.adzuna.com/v1/api/jobs/de/search/1"
            params = {
                "app_id": "demo",
                "app_key": "demo",
                "results_per_page": 1,
                "what": "test"
            }
            
            response = await client.get(url, params=params, timeout=5.0)
            response_time = round((time.time() - start_time) * 1000)
            
            if response.status_code == 200:
                return {
                    "status": "connected",
                    "message": "Adzuna API accessible",
                    "response_time": response_time
                }
            else:
                return {
                    "status": "error",
                    "message": f"HTTP {response.status_code}",
                    "response_time": response_time
                }
                
    except httpx.TimeoutException:
        return {
            "status": "timeout",
            "message": "Request timeout (>5s)",
            "response_time": 5000
        }
    except Exception as e:
        return {
            "status": "error",
            "message": str(e)[:100],
            "response_time": round((time.time() - start_time) * 1000)
        }

async def check_thelocal_status() -> Dict[str, Any]:
    """Check TheLocal.de RSS feed status"""
    import time
    start_time = time.time()
    
    try:
        async with httpx.AsyncClient() as client:
            # TheLocal jobs page (RSS feed might not exist)
            response = await client.get("https://www.thelocal.de/tag/jobs", timeout=5.0, follow_redirects=True)
            response_time = round((time.time() - start_time) * 1000)
            
            if response.status_code == 200:
                return {
                    "status": "connected",
                    "message": "TheLocal jobs page accessible",
                    "response_time": response_time
                }
            else:
                return {
                    "status": "error",
                    "message": f"HTTP {response.status_code}",
                    "response_time": response_time
                }
                
    except httpx.TimeoutException:
        return {
            "status": "timeout",
            "message": "Request timeout (>5s)",
            "response_time": 5000
        }
    except Exception as e:
        return {
            "status": "error",
            "message": str(e)[:100],
            "response_time": round((time.time() - start_time) * 1000)
        }