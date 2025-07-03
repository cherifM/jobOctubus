import httpx
from typing import List, Optional
from sqlalchemy.orm import Session
from datetime import datetime, timedelta
import json
from bs4 import BeautifulSoup
import re

from models.models import Job, JobSearch
from schemas.schemas import JobSearchRequest, Job as JobSchema
from config import settings

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
            # Placeholder for actual API integrations
            # For now, we'll simulate with some mock data
            mock_jobs = await self._get_mock_jobs(search_request)
            jobs.extend(mock_jobs)
            
            # Store search in database
            if user_id:
                self._store_search_history(search_request, len(jobs), user_id)
            
            # Filter and sort results
            filtered_jobs = self._filter_jobs(jobs, search_request)
            sorted_jobs = self._sort_jobs(filtered_jobs)
            
            return sorted_jobs[:search_request.max_results]
            
        except Exception as e:
            print(f"Error in job search: {e}")
            return []
    
    async def _get_mock_jobs(self, search_request: JobSearchRequest) -> List[JobSchema]:
        """
        Mock job data for testing - replace with actual API calls
        """
        mock_jobs = [
            Job(
                external_id="job_1",
                title="Senior CFD Engineer",
                company="Siemens Energy",
                location="Hamburg, Germany",
                description="We are looking for a Senior CFD Engineer to join our wind energy division. The ideal candidate will have extensive experience with OpenFOAM and computational fluid dynamics.",
                requirements="PhD in Engineering, 5+ years CFD experience, OpenFOAM expertise, wind energy background",
                job_type="Full-time",
                remote_option=True,
                posted_date=datetime.now() - timedelta(days=2),
                source="linkedin",
                url="https://linkedin.com/jobs/1",
                skills_required=["CFD", "OpenFOAM", "Wind Energy", "Python", "C++", "HPC"],
                experience_level="Senior",
                salary_range="€80,000 - €120,000"
            ),
            Job(
                external_id="job_2", 
                title="Computational Fluid Dynamics Specialist",
                company="Airbus",
                location="Hamburg, Germany",
                description="Join our aerodynamics team working on next-generation aircraft. We need a CFD specialist with strong background in high-performance computing.",
                requirements="Master's degree in Aerospace Engineering, CFD experience, HPC knowledge, programming skills",
                job_type="Full-time",
                remote_option=False,
                posted_date=datetime.now() - timedelta(days=1),
                source="indeed",
                url="https://indeed.com/jobs/2",
                skills_required=["CFD", "Aerodynamics", "HPC", "ANSYS", "Python", "Fortran"],
                experience_level="Mid-level",
                salary_range="€70,000 - €100,000"
            ),
            Job(
                external_id="job_3",
                title="Research Scientist - Wind Energy",
                company="Fraunhofer Institute",
                location="Oldenburg, Germany", 
                description="Research position focusing on wind turbine aerodynamics and computational modeling. Experience with Lattice Boltzmann Methods preferred.",
                requirements="PhD in relevant field, research experience, wind energy background, LBM knowledge",
                job_type="Full-time",
                remote_option=True,
                posted_date=datetime.now() - timedelta(days=5),
                source="glassdoor",
                url="https://glassdoor.com/jobs/3",
                skills_required=["Wind Energy", "LBM", "Research", "OpenFOAM", "Python", "Supercomputing"],
                experience_level="Senior",
                salary_range="€60,000 - €90,000"
            )
        ]
        
        # Store jobs in database
        for job_data in mock_jobs:
            existing_job = self.db.query(Job).filter(Job.external_id == job_data.external_id).first()
            if not existing_job:
                self.db.add(job_data)
        
        self.db.commit()
        
        # Return as schemas
        return [JobSchema.from_orm(job) for job in mock_jobs]
    
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