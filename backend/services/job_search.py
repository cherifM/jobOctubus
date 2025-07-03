import httpx
from typing import List, Optional
from sqlalchemy.orm import Session
from datetime import datetime, timedelta
import json
from bs4 import BeautifulSoup
import re
import asyncio

from models.models import Job, JobSearch
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
            if not jobs:
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
        Check which job sources are available (no API key required or valid API key)
        """
        sources = []
        
        # Always available (no API key required)
        sources.extend(['arbeitsagentur', 'remoteok', 'thelocal'])
        
        # Check if LinkedIn API key is available
        if settings.linkedin_api_key and settings.linkedin_api_key != "your_linkedin_key_here":
            sources.append('linkedin')
        
        # Check if Indeed API key is available
        if settings.indeed_api_key and settings.indeed_api_key != "your_indeed_key_here":
            sources.append('indeed')
        
        return sources
    
    async def _search_arbeitsagentur(self, search_request: JobSearchRequest) -> List[JobSchema]:
        """
        Search jobs using German Federal Employment Agency API
        """
        try:
            async with httpx.AsyncClient() as client:
                # Bundesagentur für Arbeit API endpoint
                url = "https://rest.arbeitsagentur.de/jobboerse/jobsuche-service/pc/v4/jobs"
                
                params = {
                    "was": search_request.query,
                    "wo": search_request.location or "Hamburg",
                    "page": 1,
                    "size": min(search_request.max_results, 25)
                }
                
                headers = {
                    "User-Agent": "JobOctubus/1.0 (job-search-tool)"
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
            async with httpx.AsyncClient() as client:
                url = "https://remoteok.io/api"
                
                headers = {
                    "User-Agent": "JobOctubus/1.0 (job-search-tool)"
                }
                
                response = await client.get(url, headers=headers, timeout=10)
                response.raise_for_status()
                
                data = response.json()
                jobs = []
                
                # Filter jobs by query
                query_lower = search_request.query.lower()
                count = 0
                
                for job_data in data[1:]:  # Skip first item (metadata)
                    if count >= search_request.max_results:
                        break
                    
                    # Simple keyword matching
                    job_text = f"{job_data.get('position', '')} {job_data.get('description', '')}".lower()
                    if query_lower in job_text:
                        job = JobSchema(
                            external_id=f"remote_{job_data.get('id', '')}",
                            title=job_data.get('position', ''),
                            company=job_data.get('company', ''),
                            location="Remote",
                            description=job_data.get('description', ''),
                            job_type="Full-time",
                            remote_option=True,
                            posted_date=datetime.fromtimestamp(job_data.get('date', 0)),
                            source="remoteok",
                            url=job_data.get('url', ''),
                            skills_required=job_data.get('tags', []),
                            experience_level="Mid-level",
                            salary_range=job_data.get('salary', '')
                        )
                        jobs.append(job)
                        count += 1
                
                logger.info(f"Found {len(jobs)} jobs from RemoteOK")
                return jobs
                
        except Exception as e:
            logger.error(f"Error searching RemoteOK: {e}")
            return []
    
    async def _search_thelocal(self, search_request: JobSearchRequest) -> List[JobSchema]:
        """
        Search jobs using TheLocal.de RSS feed
        """
        try:
            async with httpx.AsyncClient() as client:
                url = "https://www.thelocal.de/jobs/feed/"
                
                response = await client.get(url, timeout=10)
                response.raise_for_status()
                
                # Parse RSS feed
                soup = BeautifulSoup(response.text, 'xml')
                jobs = []
                
                query_lower = search_request.query.lower()
                
                for item in soup.find_all('item')[:search_request.max_results]:
                    title = item.find('title').text if item.find('title') else ''
                    description = item.find('description').text if item.find('description') else ''
                    
                    # Simple keyword matching
                    if query_lower in f"{title} {description}".lower():
                        job = JobSchema(
                            external_id=f"thelocal_{hash(item.find('link').text if item.find('link') else '')}",
                            title=title,
                            company="Various",
                            location="Germany",
                            description=description,
                            job_type="Full-time",
                            remote_option=False,
                            posted_date=datetime.now(),
                            source="thelocal",
                            url=item.find('link').text if item.find('link') else '',
                            skills_required=[],
                            experience_level="Mid-level"
                        )
                        jobs.append(job)
                
                logger.info(f"Found {len(jobs)} jobs from TheLocal")
                return jobs
                
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