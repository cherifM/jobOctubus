from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List

from database import get_db
from models.models import Application, User, Job, CV
from schemas.schemas import (
    Application as ApplicationSchema, 
    ApplicationCreate, 
    ApplicationUpdate,
    CoverLetterRequest
)
from api.auth import get_current_user
from services.application_service import ApplicationService

router = APIRouter()

@router.get("/", response_model=List[ApplicationSchema])
async def get_applications(
    skip: int = 0,
    limit: int = 20,
    status: str = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    query = db.query(Application).filter(Application.user_id == current_user.id)
    
    if status:
        query = query.filter(Application.status == status)
    
    applications = query.offset(skip).limit(limit).all()
    return applications

@router.get("/{application_id}", response_model=ApplicationSchema)
async def get_application(
    application_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    application = db.query(Application).filter(
        Application.id == application_id,
        Application.user_id == current_user.id
    ).first()
    if not application:
        raise HTTPException(status_code=404, detail="Application not found")
    return application

@router.post("/", response_model=ApplicationSchema)
async def create_application(
    application: ApplicationCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    job = db.query(Job).filter(Job.id == application.job_id).first()
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")
    
    cv = db.query(CV).filter(
        CV.id == application.cv_id,
        CV.owner_id == current_user.id
    ).first()
    if not cv:
        raise HTTPException(status_code=404, detail="CV not found")
    
    db_application = Application(
        **application.dict(),
        user_id=current_user.id
    )
    db.add(db_application)
    db.commit()
    db.refresh(db_application)
    return db_application

@router.put("/{application_id}", response_model=ApplicationSchema)
async def update_application(
    application_id: int,
    application_update: ApplicationUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    db_application = db.query(Application).filter(
        Application.id == application_id,
        Application.user_id == current_user.id
    ).first()
    if not db_application:
        raise HTTPException(status_code=404, detail="Application not found")
    
    for key, value in application_update.dict(exclude_unset=True).items():
        setattr(db_application, key, value)
    
    db.commit()
    db.refresh(db_application)
    return db_application

@router.post("/{application_id}/cover-letter")
async def generate_cover_letter(
    application_id: int,
    cover_letter_request: CoverLetterRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    application = db.query(Application).filter(
        Application.id == application_id,
        Application.user_id == current_user.id
    ).first()
    if not application:
        raise HTTPException(status_code=404, detail="Application not found")
    
    application_service = ApplicationService(db)
    cover_letter = await application_service.generate_cover_letter(
        cover_letter_request.job_id,
        cover_letter_request.cv_id,
        current_user.id,
        cover_letter_request.tone,
        cover_letter_request.length,
        cover_letter_request.custom_points
    )
    
    application.cover_letter = cover_letter
    db.commit()
    
    return {"cover_letter": cover_letter}

@router.delete("/{application_id}")
async def delete_application(
    application_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    db_application = db.query(Application).filter(
        Application.id == application_id,
        Application.user_id == current_user.id
    ).first()
    if not db_application:
        raise HTTPException(status_code=404, detail="Application not found")
    
    db.delete(db_application)
    db.commit()
    return {"message": "Application deleted successfully"}