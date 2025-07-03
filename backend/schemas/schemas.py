from pydantic import BaseModel, EmailStr
from typing import Optional, List, Dict, Any
from datetime import datetime

class UserBase(BaseModel):
    email: EmailStr

class UserCreate(UserBase):
    password: str

class UserLogin(BaseModel):
    email: EmailStr
    password: str

class User(UserBase):
    id: int
    is_active: bool
    created_at: datetime
    
    class Config:
        from_attributes = True

class CVBase(BaseModel):
    title: str
    language: str = "en"
    content: Dict[str, Any]
    skills: List[str]
    experience: List[Dict[str, Any]]
    education: List[Dict[str, Any]]
    personal_info: Dict[str, Any]
    is_base_cv: bool = False

class CVCreate(CVBase):
    pass

class CVUpdate(BaseModel):
    title: Optional[str] = None
    content: Optional[Dict[str, Any]] = None
    skills: Optional[List[str]] = None
    experience: Optional[List[Dict[str, Any]]] = None
    education: Optional[List[Dict[str, Any]]] = None
    personal_info: Optional[Dict[str, Any]] = None

class CV(CVBase):
    id: int
    owner_id: int
    created_at: datetime
    updated_at: Optional[datetime]
    
    class Config:
        from_attributes = True

class JobBase(BaseModel):
    title: str
    company: str
    location: str
    description: str
    requirements: str
    salary_range: Optional[str] = None
    job_type: str
    remote_option: bool = False
    source: str
    url: str
    skills_required: List[str]
    experience_level: str

class JobCreate(JobBase):
    external_id: str
    posted_date: datetime
    deadline: Optional[datetime] = None

class JobUpdate(BaseModel):
    match_score: Optional[float] = None

class Job(JobBase):
    id: int
    external_id: str
    posted_date: datetime
    deadline: Optional[datetime]
    match_score: Optional[float]
    created_at: datetime
    
    class Config:
        from_attributes = True

class JobSearchRequest(BaseModel):
    query: str
    location: Optional[str] = None
    remote_only: bool = False
    experience_level: Optional[str] = None
    job_type: Optional[str] = None
    salary_min: Optional[int] = None
    max_results: int = 50

class ApplicationBase(BaseModel):
    status: str = "pending"
    cover_letter: Optional[str] = None
    adapted_cv_content: Optional[Dict[str, Any]] = None
    notes: Optional[str] = None

class ApplicationCreate(ApplicationBase):
    job_id: int
    cv_id: int

class ApplicationUpdate(BaseModel):
    status: Optional[str] = None
    cover_letter: Optional[str] = None
    notes: Optional[str] = None
    applied_date: Optional[datetime] = None
    response_date: Optional[datetime] = None
    interview_date: Optional[datetime] = None

class Application(ApplicationBase):
    id: int
    user_id: int
    job_id: int
    cv_id: int
    created_at: datetime
    updated_at: Optional[datetime]
    applied_date: Optional[datetime]
    response_date: Optional[datetime]
    interview_date: Optional[datetime]
    
    job: Job
    cv: CV
    
    class Config:
        from_attributes = True

class CVAdaptationRequest(BaseModel):
    cv_id: int
    job_id: int
    focus_areas: Optional[List[str]] = None

class CoverLetterRequest(BaseModel):
    job_id: int
    cv_id: int
    tone: str = "professional"
    length: str = "medium"
    custom_points: Optional[List[str]] = None

class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    email: Optional[str] = None