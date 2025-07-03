from fastapi import APIRouter, Depends, HTTPException, UploadFile, File
from sqlalchemy.orm import Session
from typing import List

from database import get_db
from models.models import CV, User
from schemas.schemas import CV as CVSchema, CVCreate, CVUpdate, CVAdaptationRequest
from api.auth import get_current_user
from services.cv_service import CVService

router = APIRouter()

@router.get("/", response_model=List[CVSchema])
async def get_cvs(
    skip: int = 0,
    limit: int = 10,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    cvs = db.query(CV).filter(CV.owner_id == current_user.id).offset(skip).limit(limit).all()
    return cvs

@router.get("/{cv_id}", response_model=CVSchema)
async def get_cv(
    cv_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    cv = db.query(CV).filter(CV.id == cv_id, CV.owner_id == current_user.id).first()
    if not cv:
        raise HTTPException(status_code=404, detail="CV not found")
    return cv

@router.post("/", response_model=CVSchema)
async def create_cv(
    cv: CVCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    db_cv = CV(**cv.dict(), owner_id=current_user.id)
    db.add(db_cv)
    db.commit()
    db.refresh(db_cv)
    return db_cv

@router.post("/upload", response_model=CVSchema)
async def upload_cv(
    file: UploadFile = File(...),
    title: str = "Uploaded CV",
    language: str = "en",
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    cv_service = CVService(db)
    cv = await cv_service.parse_pdf_cv(file, title, language, current_user.id)
    return cv

@router.put("/{cv_id}", response_model=CVSchema)
async def update_cv(
    cv_id: int,
    cv_update: CVUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    db_cv = db.query(CV).filter(CV.id == cv_id, CV.owner_id == current_user.id).first()
    if not db_cv:
        raise HTTPException(status_code=404, detail="CV not found")
    
    for key, value in cv_update.dict(exclude_unset=True).items():
        setattr(db_cv, key, value)
    
    db.commit()
    db.refresh(db_cv)
    return db_cv

@router.post("/{cv_id}/adapt", response_model=CVSchema)
async def adapt_cv(
    cv_id: int,
    adaptation_request: CVAdaptationRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    cv_service = CVService(db)
    adapted_cv = await cv_service.adapt_cv_for_job(
        cv_id, adaptation_request.job_id, current_user.id, adaptation_request.focus_areas
    )
    return adapted_cv

@router.post("/initialize-from-website", response_model=List[CVSchema])
async def initialize_cvs_from_website(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Initialize user's CVs from personal website folder"""
    cv_service = CVService(db)
    cvs = await cv_service.initialize_user_cvs(current_user.id)
    return cvs

@router.delete("/{cv_id}")
async def delete_cv(
    cv_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    db_cv = db.query(CV).filter(CV.id == cv_id, CV.owner_id == current_user.id).first()
    if not db_cv:
        raise HTTPException(status_code=404, detail="CV not found")
    
    db.delete(db_cv)
    db.commit()
    return {"message": "CV deleted successfully"}