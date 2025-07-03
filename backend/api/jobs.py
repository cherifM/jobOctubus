from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List, Optional

from database import get_db
from models.models import Job, User
from schemas.schemas import Job as JobSchema, JobCreate, JobUpdate, JobSearchRequest
from api.auth import get_current_user
from services.job_search import JobSearchService

router = APIRouter()

@router.post("/search", response_model=List[JobSchema])
async def search_jobs(
    search_request: JobSearchRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    job_search_service = JobSearchService(db)
    jobs = await job_search_service.search_jobs(search_request)
    return jobs

@router.get("/", response_model=List[JobSchema])
async def get_jobs(
    skip: int = 0,
    limit: int = 20,
    location: Optional[str] = None,
    company: Optional[str] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    query = db.query(Job)
    
    if location:
        query = query.filter(Job.location.contains(location))
    if company:
        query = query.filter(Job.company.contains(company))
    
    jobs = query.offset(skip).limit(limit).all()
    return jobs

@router.get("/{job_id}", response_model=JobSchema)
async def get_job(
    job_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    job = db.query(Job).filter(Job.id == job_id).first()
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")
    return job

@router.post("/", response_model=JobSchema)
async def create_job(
    job: JobCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    db_job = Job(**job.dict())
    db.add(db_job)
    db.commit()
    db.refresh(db_job)
    return db_job

@router.put("/{job_id}", response_model=JobSchema)
async def update_job(
    job_id: int,
    job_update: JobUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    db_job = db.query(Job).filter(Job.id == job_id).first()
    if not db_job:
        raise HTTPException(status_code=404, detail="Job not found")
    
    for key, value in job_update.dict(exclude_unset=True).items():
        setattr(db_job, key, value)
    
    db.commit()
    db.refresh(db_job)
    return db_job

@router.delete("/{job_id}")
async def delete_job(
    job_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    db_job = db.query(Job).filter(Job.id == job_id).first()
    if not db_job:
        raise HTTPException(status_code=404, detail="Job not found")
    
    db.delete(db_job)
    db.commit()
    return {"message": "Job deleted successfully"}