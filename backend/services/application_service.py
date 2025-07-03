from typing import Optional, List
from sqlalchemy.orm import Session
from datetime import datetime

from models.models import Application, Job, CV, User
from services.llm_service import LLMService
from services.job_search import JobSearchService

class ApplicationService:
    def __init__(self, db: Session):
        self.db = db
        self.llm_service = LLMService()
        self.job_search_service = JobSearchService(db)
    
    async def create_application(
        self,
        user_id: int,
        job_id: int,
        cv_id: int,
        generate_cover_letter: bool = True
    ) -> Application:
        """
        Create a new job application with optional cover letter generation
        """
        job = self.db.query(Job).filter(Job.id == job_id).first()
        if not job:
            raise ValueError("Job not found")
        
        cv = self.db.query(CV).filter(CV.id == cv_id, CV.owner_id == user_id).first()
        if not cv:
            raise ValueError("CV not found")
        
        application = Application(
            user_id=user_id,
            job_id=job_id,
            cv_id=cv_id,
            status="draft"
        )
        
        if generate_cover_letter:
            cover_letter = await self.generate_cover_letter(
                job_id, cv_id, user_id
            )
            application.cover_letter = cover_letter
        
        self.db.add(application)
        self.db.commit()
        self.db.refresh(application)
        
        return application
    
    async def generate_cover_letter(
        self,
        job_id: int,
        cv_id: int,
        user_id: int,
        tone: str = "professional",
        length: str = "medium",
        custom_points: Optional[List[str]] = None
    ) -> str:
        """
        Generate a personalized cover letter for a job application
        """
        job = self.db.query(Job).filter(Job.id == job_id).first()
        if not job:
            raise ValueError("Job not found")
        
        cv = self.db.query(CV).filter(CV.id == cv_id, CV.owner_id == user_id).first()
        if not cv:
            raise ValueError("CV not found")
        
        cover_letter = await self.llm_service.generate_cover_letter(
            cv_content=cv.content,
            job_title=job.title,
            company=job.company,
            job_description=job.description,
            job_requirements=job.requirements,
            tone=tone,
            length=length,
            custom_points=custom_points
        )
        
        return cover_letter
    
    async def analyze_application_strength(
        self,
        application_id: int,
        user_id: int
    ) -> dict:
        """
        Analyze how strong an application is for a specific job
        """
        application = self.db.query(Application).filter(
            Application.id == application_id,
            Application.user_id == user_id
        ).first()
        
        if not application:
            raise ValueError("Application not found")
        
        job = application.job
        cv = application.cv
        
        analysis = await self.llm_service.analyze_job_cv_match(
            cv_content=cv.content,
            job_description=job.description,
            job_requirements=job.requirements,
            skills_required=job.skills_required
        )
        
        # Calculate match score if not already done
        if not job.match_score:
            match_score = await self.job_search_service.calculate_job_match_score(
                job.id, cv.content
            )
            analysis["match_score"] = match_score
        else:
            analysis["match_score"] = job.match_score
        
        return analysis
    
    async def update_application_status(
        self,
        application_id: int,
        user_id: int,
        status: str,
        notes: Optional[str] = None
    ) -> Application:
        """
        Update application status and add notes
        """
        application = self.db.query(Application).filter(
            Application.id == application_id,
            Application.user_id == user_id
        ).first()
        
        if not application:
            raise ValueError("Application not found")
        
        application.status = status
        if notes:
            application.notes = notes
        
        # Update timestamps based on status
        if status == "applied":
            application.applied_date = datetime.now()
        elif status == "responded":
            application.response_date = datetime.now()
        elif status == "interview_scheduled":
            application.interview_date = datetime.now()
        
        self.db.commit()
        self.db.refresh(application)
        
        return application
    
    async def get_application_recommendations(
        self,
        user_id: int,
        limit: int = 5
    ) -> List[dict]:
        """
        Get personalized job recommendations based on user's CVs and application history
        """
        user = self.db.query(User).filter(User.id == user_id).first()
        if not user:
            raise ValueError("User not found")
        
        # Get user's base CVs
        base_cvs = self.db.query(CV).filter(
            CV.owner_id == user_id,
            CV.is_base_cv == True
        ).all()
        
        if not base_cvs:
            return []
        
        # Get recent applications to avoid duplicates
        recent_applications = self.db.query(Application).filter(
            Application.user_id == user_id
        ).limit(20).all()
        
        applied_job_ids = [app.job_id for app in recent_applications]
        
        # Get available jobs
        available_jobs = self.db.query(Job).filter(
            ~Job.id.in_(applied_job_ids)
        ).order_by(Job.posted_date.desc()).limit(50).all()
        
        recommendations = []
        
        # Calculate match scores for each CV-job combination
        for cv in base_cvs:
            for job in available_jobs:
                match_score = await self.job_search_service.calculate_job_match_score(
                    job.id, cv.content
                )
                
                if match_score > 50:  # Only recommend jobs with >50% match
                    recommendations.append({
                        "job": job,
                        "cv": cv,
                        "match_score": match_score,
                        "recommended_cv_id": cv.id
                    })
        
        # Sort by match score and return top recommendations
        recommendations.sort(key=lambda x: x["match_score"], reverse=True)
        
        return recommendations[:limit]
    
    async def get_application_analytics(self, user_id: int) -> dict:
        """
        Get analytics about user's job applications
        """
        applications = self.db.query(Application).filter(
            Application.user_id == user_id
        ).all()
        
        if not applications:
            return {
                "total_applications": 0,
                "status_breakdown": {},
                "response_rate": 0.0,
                "average_match_score": 0.0
            }
        
        # Status breakdown
        status_counts = {}
        for app in applications:
            status = app.status
            status_counts[status] = status_counts.get(status, 0) + 1
        
        # Response rate
        applied_count = status_counts.get("applied", 0)
        responded_count = sum(status_counts.get(status, 0) for status in ["responded", "interview_scheduled", "offer"])
        response_rate = (responded_count / applied_count * 100) if applied_count > 0 else 0.0
        
        # Average match score
        match_scores = [app.job.match_score for app in applications if app.job.match_score]
        avg_match_score = sum(match_scores) / len(match_scores) if match_scores else 0.0
        
        return {
            "total_applications": len(applications),
            "status_breakdown": status_counts,
            "response_rate": response_rate,
            "average_match_score": avg_match_score,
            "applications_this_month": len([
                app for app in applications 
                if app.created_at.month == datetime.now().month
            ])
        }