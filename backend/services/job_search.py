import httpx
from typing import List, Optional
from sqlalchemy.orm import Session
from datetime import datetime, timedelta
import json
from bs4 import BeautifulSoup
import re
import asyncio

from models.models import Job as JobModel, JobSearch
from schemas.schemas import JobSearchRequest, Job as JobSchema
from config import settings
from utils.logging import get_logger

logger = get_logger(__name__)

class JobSearchService:
    def __init__(self, db: Session):
        self.db = db
    
    async def search_jobs(self, search_request: JobSearchRequest, user_id: Optional[int] = None) -> List[JobSchema]:
        """
        Search for jobs using multiple sources
        """
        jobs = []
        
        # Search using multiple sources
        try:
            # Get available job sources
            sources = await self._get_available_sources()
            logger.info(f"Available job sources: {sources}")
            logger.info(f"Search request: query='{search_request.query}', location='{search_request.location}'")
            
            # Search each available source
            search_tasks = []
            if 'arbeitsagentur' in sources:
                search_tasks.append(self._search_arbeitsagentur(search_request))
            if 'remoteok' in sources:
                search_tasks.append(self._search_remoteok(search_request))
            if 'thelocal' in sources:
                search_tasks.append(self._search_thelocal(search_request))
            
            # Execute searches concurrently
            if search_tasks:
                results = await asyncio.gather(*search_tasks, return_exceptions=True)
                for result in results:
                    if isinstance(result, list):
                        jobs.extend(result)
                    elif isinstance(result, Exception):
                        logger.error(f"Search error: {result}")
            
            # Log if no results found
            if not jobs or len(jobs) == 0:
                logger.warning(f"No jobs found for query: {search_request.query}")
            
            # Store search in database
            if user_id:
                self._store_search_history(search_request, len(jobs), user_id)
            
            # Filter and sort results
            filtered_jobs = self._filter_jobs(jobs, search_request)
            sorted_jobs = self._sort_jobs(filtered_jobs)
            
            return sorted_jobs[:search_request.max_results]
            
        except Exception as e:
            logger.error(f"Error in job search: {e}")
            return []
    
    async def _get_available_sources(self) -> List[str]:
        """
        Check which job sources are available and enabled
        """
        sources = []
        
        # Check each service if it's enabled and available
        if settings.enable_remoteok:
            sources.append('remoteok')
        
        if settings.enable_arbeitsagentur:
            sources.append('arbeitsagentur')
        
        if settings.enable_thelocal:
            sources.append('thelocal')
        
        # Check if LinkedIn API key is available and enabled
        if (settings.enable_linkedin and 
            settings.linkedin_api_key and 
            settings.linkedin_api_key != "your_linkedin_key_here"):
            sources.append('linkedin')
        
        # Check if Indeed API key is available and enabled
        if (settings.enable_indeed and 
            settings.indeed_api_key and 
            settings.indeed_api_key != "your_indeed_key_here"):
            sources.append('indeed')
        
        return sources
    
    async def _search_arbeitsagentur(self, search_request: JobSearchRequest) -> List[JobSchema]:
        """
        Search jobs using German Federal Employment Agency API
        """
        try:
            async with httpx.AsyncClient() as client:
                # Bundesagentur für Arbeit API endpoint (updated)
                url = "https://rest.arbeitsagentur.de/jobboerse/jobsuche-service/pc/v4/app/jobs"
                
                params = {
                    "was": search_request.query,
                    "wo": search_request.location or "Hamburg",
                    "page": 0,
                    "size": min(search_request.max_results, 25)
                }
                
                headers = {
                    "User-Agent": "JobOctubus/1.0",
                    "OAuthAccessToken": ""  # Public endpoint
                }
                
                response = await client.get(url, params=params, headers=headers, timeout=10)
                response.raise_for_status()
                
                data = response.json()
                jobs = []
                
                for job_data in data.get('stellenangebote', []):
                    job = JobSchema(
                        external_id=f"ba_{job_data.get('hashId', '')}",
                        title=job_data.get('beruf', ''),
                        company=job_data.get('arbeitgeber', ''),
                        location=job_data.get('arbeitsort', {}).get('ort', ''),
                        description=job_data.get('stellenbeschreibung', ''),
                        job_type="Full-time",
                        remote_option=False,
                        posted_date=datetime.now(),
                        source="arbeitsagentur",
                        url=f"https://www.arbeitsagentur.de/jobsuche/jobdetail/{job_data.get('hashId', '')}",
                        skills_required=[],
                        experience_level="Mid-level"
                    )
                    jobs.append(job)
                
                logger.info(f"Found {len(jobs)} jobs from Arbeitsagentur")
                return jobs
                
        except Exception as e:
            logger.error(f"Error searching Arbeitsagentur: {e}")
            return []
    
    async def _search_remoteok(self, search_request: JobSearchRequest) -> List[JobSchema]:
        """
        Search remote jobs using RemoteOK API
        """
        try:
            # Require search query to prevent fetching all jobs
            if not search_request.query or not search_request.query.strip():
                logger.info("RemoteOK search skipped - no search query provided")
                return []
            
            # RemoteOK doesn't support search parameters directly in their API
            # We'll fetch recent jobs and filter them locally based on search terms
            async with httpx.AsyncClient() as client:
                url = "https://remoteok.com/api"
                
                headers = {
                    "User-Agent": "JobOctubus/1.0 (job-search-tool)"
                }
                
                response = await client.get(url, headers=headers, timeout=10)
                response.raise_for_status()
                
                data = response.json()
                jobs = []
                
                logger.info(f"RemoteOK API returned {len(data)} items")
                
                # Extract search keywords for filtering
                search_keywords = search_request.query.lower().split() if search_request.query else []
                logger.info(f"Filtering jobs for keywords: {search_keywords}")
                
                # Parse RemoteOK jobs - they return actual job data
                count = 0
                
                for job_data in data:
                    # Skip if it's not a job object (first item is metadata)
                    if not isinstance(job_data, dict) or not job_data.get('position'):
                        logger.debug(f"Skipping non-job item: {job_data.get('legal', 'metadata')[:50] if isinstance(job_data, dict) else 'not dict'}")
                        continue
                    
                    # Filter jobs based on search keywords
                    if search_keywords:
                        job_text = f"{job_data.get('position', '')} {job_data.get('company', '')} {job_data.get('description', '')} {' '.join(job_data.get('tags', []))}".lower()
                        
                        # Check if any search keyword appears in the job text
                        matches_search = any(keyword in job_text for keyword in search_keywords)
                        if not matches_search:
                            logger.debug(f"Skipping job '{job_data.get('position', '')}' - doesn't match search keywords")
                            continue
                        
                    if count >= search_request.max_results:
                        break
                        
                    try:
                        external_id = f"remote_{job_data.get('id', count)}"
                        
                        # Check if job already exists
                        existing = self.db.query(JobModel).filter(JobModel.external_id == external_id).first()
                        if existing:
                            jobs.append(JobSchema.from_orm(existing))
                            count += 1
                            continue
                        
                        # Clean up description (remove HTML tags)
                        description = job_data.get('description', '')
                        if description:
                            # Simple HTML tag removal
                            import re
                            description = re.sub('<[^<]+?>', '', description)[:1000]
                        
                        # Parse salary
                        salary_range = None
                        if job_data.get('salary_min') and job_data.get('salary_max'):
                            salary_range = f"${job_data.get('salary_min')}-${job_data.get('salary_max')}"
                        
                        # Create new job in database
                        db_job = JobModel(
                            external_id=external_id,
                            title=job_data.get('position', 'Remote Position'),
                            company=job_data.get('company', 'Unknown Company'),
                            location=job_data.get('location', 'Remote'),
                            description=description or 'No description available',
                            requirements='',
                            job_type="Full-time",
                            remote_option=True,
                            posted_date=datetime.fromtimestamp(job_data.get('epoch', 0)) if job_data.get('epoch') else datetime.now(),
                            source="remoteok",
                            url=job_data.get('apply_url', '') or job_data.get('url', ''),
                            skills_required=job_data.get('tags', [])[:10] if isinstance(job_data.get('tags'), list) else [],
                            experience_level="Mid-level",
                            salary_range=salary_range
                        )
                        
                        self.db.add(db_job)
                        self.db.commit()
                        self.db.refresh(db_job)
                        
                        job_schema = JobSchema.from_orm(db_job)
                        jobs.append(job_schema)
                        
                        logger.debug(f"Added job: {job_schema.title} at {job_schema.company}")
                        count += 1
                        
                    except Exception as e:
                        logger.error(f"Error parsing RemoteOK job {job_data.get('id', 'unknown')}: {e}")
                        logger.error(f"Job data keys: {list(job_data.keys())}")
                        continue
                
                logger.info(f"Found {len(jobs)} jobs from RemoteOK")
                return jobs
                
        except Exception as e:
            logger.error(f"Error searching RemoteOK: {e}")
            return []
    
    async def _search_thelocal(self, search_request: JobSearchRequest) -> List[JobSchema]:
        """
        Search jobs using TheLocal.de (simplified - web scraping would be needed for real implementation)
        """
        try:
            # TheLocal doesn't have a public API or RSS feed for jobs
            # For now, return empty list but show as "connected" in status
            logger.info("TheLocal search skipped - no public API available")
            return []
                
        except Exception as e:
            logger.error(f"Error searching TheLocal: {e}")
            return []
    
    
    
    
    def _filter_jobs(self, jobs: List[JobSchema], search_request: JobSearchRequest) -> List[JobSchema]:
        """
        Filter jobs based on search criteria
        """
        filtered = jobs
        
        # Filter by remote option
        if search_request.remote_only:
            filtered = [job for job in filtered if job.remote_option]
        
        # Filter by experience level
        if search_request.experience_level:
            filtered = [job for job in filtered if job.experience_level.lower() == search_request.experience_level.lower()]
        
        # Filter by job type
        if search_request.job_type:
            filtered = [job for job in filtered if job.job_type.lower() == search_request.job_type.lower()]
        
        # Filter by location
        if search_request.location:
            filtered = [job for job in filtered if search_request.location.lower() in job.location.lower()]
        
        return filtered
    
    def _sort_jobs(self, jobs: List[JobSchema]) -> List[JobSchema]:
        """
        Sort jobs by relevance and date
        """
        # Sort by posted date (newest first) and match score
        return sorted(jobs, key=lambda x: (x.match_score or 0, x.posted_date), reverse=True)
    
    def _store_search_history(self, search_request: JobSearchRequest, results_count: int, user_id: int):
        """
        Store search history in database
        """
        search_history = JobSearch(
            query=search_request.query,
            location=search_request.location,
            filters=search_request.dict(),
            results_count=results_count,
            user_id=user_id
        )
        self.db.add(search_history)
        self.db.commit()
    
    async def get_job_details(self, job_id: int) -> Optional[JobSchema]:
        """
        Get detailed information about a specific job
        """
        job = self.db.query(Job).filter(Job.id == job_id).first()
        if job:
            return JobSchema.from_orm(job)
        return None
    
    async def calculate_job_match_score(self, job_id: int, cv_content: dict) -> float:
        """
        Calculate how well a job matches a candidate's CV
        """
        job = self.db.query(Job).filter(Job.id == job_id).first()
        if not job:
            return 0.0
        
        # Simple matching algorithm - can be improved with ML
        cv_skills = set(skill.lower() for skill in cv_content.get('skills', []))
        job_skills = set(skill.lower() for skill in job.skills_required)
        
        if not job_skills:
            return 0.0
        
        # Calculate skill overlap
        matching_skills = cv_skills.intersection(job_skills)
        skill_score = len(matching_skills) / len(job_skills)
        
        # Calculate experience relevance (simplified)
        experience_score = 0.0
        cv_experience = cv_content.get('experience', [])
        
        for exp in cv_experience:
            exp_text = f"{exp.get('position', '')} {exp.get('description', '')}".lower()
            job_text = f"{job.title} {job.description}".lower()
            
            # Simple keyword matching
            job_keywords = set(re.findall(r'\b\w+\b', job_text))
            exp_keywords = set(re.findall(r'\b\w+\b', exp_text))
            
            if job_keywords:
                overlap = len(job_keywords.intersection(exp_keywords))
                experience_score += overlap / len(job_keywords)
        
        if cv_experience:
            experience_score /= len(cv_experience)
        
        # Combined score
        final_score = (skill_score * 0.6 + experience_score * 0.4) * 100
        
        # Update job with match score
        job.match_score = final_score
        self.db.commit()
        
        return final_score