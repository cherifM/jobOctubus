from sqlalchemy import Boolean, Column, Integer, String, Text, DateTime, Float, ForeignKey, JSON
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from database import Base

class User(Base):
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True)
    hashed_password = Column(String)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    cvs = relationship("CV", back_populates="owner")
    applications = relationship("Application", back_populates="user")

class CV(Base):
    __tablename__ = "cvs"
    
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, index=True)
    language = Column(String, default="en")
    content = Column(JSON)
    original_pdf_path = Column(String)
    skills = Column(JSON)
    experience = Column(JSON)
    education = Column(JSON)
    personal_info = Column(JSON)
    is_base_cv = Column(Boolean, default=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    owner_id = Column(Integer, ForeignKey("users.id"))
    owner = relationship("User", back_populates="cvs")
    applications = relationship("Application", back_populates="cv")

class Job(Base):
    __tablename__ = "jobs"
    
    id = Column(Integer, primary_key=True, index=True)
    external_id = Column(String, unique=True, index=True)
    title = Column(String, index=True)
    company = Column(String, index=True)
    location = Column(String)
    description = Column(Text)
    requirements = Column(Text)
    salary_range = Column(String)
    job_type = Column(String)
    remote_option = Column(Boolean, default=False)
    posted_date = Column(DateTime(timezone=True))
    deadline = Column(DateTime(timezone=True))
    source = Column(String)
    url = Column(String)
    skills_required = Column(JSON)
    experience_level = Column(String)
    match_score = Column(Float)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    applications = relationship("Application", back_populates="job")

class Application(Base):
    __tablename__ = "applications"
    
    id = Column(Integer, primary_key=True, index=True)
    status = Column(String, default="pending")
    cover_letter = Column(Text)
    adapted_cv_content = Column(JSON)
    notes = Column(Text)
    applied_date = Column(DateTime(timezone=True))
    response_date = Column(DateTime(timezone=True))
    interview_date = Column(DateTime(timezone=True))
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    user_id = Column(Integer, ForeignKey("users.id"))
    job_id = Column(Integer, ForeignKey("jobs.id"))
    cv_id = Column(Integer, ForeignKey("cvs.id"))
    
    user = relationship("User", back_populates="applications")
    job = relationship("Job", back_populates="applications")
    cv = relationship("CV", back_populates="applications")

class JobSearch(Base):
    __tablename__ = "job_searches"
    
    id = Column(Integer, primary_key=True, index=True)
    query = Column(String)
    location = Column(String)
    filters = Column(JSON)
    results_count = Column(Integer)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    user_id = Column(Integer, ForeignKey("users.id"))

class Template(Base):
    __tablename__ = "templates"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
    type = Column(String)
    content = Column(Text)
    variables = Column(JSON)
    language = Column(String, default="en")
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    user_id = Column(Integer, ForeignKey("users.id"))