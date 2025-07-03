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
        "openrouter": {"status": "unknown", "message": "", "response_time": 0},
        "arbeitsagentur": {"status": "unknown", "message": "", "response_time": 0},
        "remoteok": {"status": "unknown", "message": "", "response_time": 0},
        "thelocal": {"status": "unknown", "message": "", "response_time": 0},
        "overall": "checking"
    }
    
    # Check all services concurrently
    tasks = [
        check_openrouter_status(),
        check_arbeitsagentur_status(),
        check_remoteok_status(),
        check_thelocal_status()
    ]
    
    try:
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        # Update status with results
        service_names = ["openrouter", "arbeitsagentur", "remoteok", "thelocal"]
        for i, result in enumerate(results):
            service_name = service_names[i]
            if isinstance(result, dict):
                status[service_name] = result
            else:
                status[service_name] = {
                    "status": "error", 
                    "message": str(result), 
                    "response_time": 0
                }
        
        # Determine overall status
        all_statuses = [status[service]["status"] for service in service_names]
        if all(s == "connected" for s in all_statuses):
            status["overall"] = "healthy"
        elif any(s == "connected" for s in all_statuses):
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
            url = "https://rest.arbeitsagentur.de/jobboerse/jobsuche-service/pc/v4/jobs"
            params = {"was": "test", "wo": "Hamburg", "size": 1}
            headers = {"User-Agent": "JobOctubus/1.0 (job-search-tool)"}
            
            response = await client.get(url, params=params, headers=headers, timeout=5.0)
            response_time = round((time.time() - start_time) * 1000)
            
            if response.status_code == 200:
                return {
                    "status": "connected",
                    "message": "Arbeitsagentur API accessible",
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
            
            response = await client.head("https://remoteok.io/api", headers=headers, timeout=5.0)
            response_time = round((time.time() - start_time) * 1000)
            
            if response.status_code in [200, 405]:  # 405 is also ok for HEAD request
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

async def check_thelocal_status() -> Dict[str, Any]:
    """Check TheLocal.de RSS feed status"""
    import time
    start_time = time.time()
    
    try:
        async with httpx.AsyncClient() as client:
            response = await client.head("https://www.thelocal.de/jobs/feed/", timeout=5.0)
            response_time = round((time.time() - start_time) * 1000)
            
            if response.status_code in [200, 405]:  # 405 is also ok for HEAD request
                return {
                    "status": "connected",
                    "message": "TheLocal RSS feed accessible",
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