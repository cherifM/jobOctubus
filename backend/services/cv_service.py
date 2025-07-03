import os
import shutil
from typing import Optional, List, Dict, Any
from fastapi import UploadFile, HTTPException
from sqlalchemy.orm import Session
import PyPDF2
import json

from models.models import CV, Job, User
from services.llm_service import LLMService
from config import settings

class CVService:
    def __init__(self, db: Session):
        self.db = db
        self.llm_service = LLMService()
        
    async def parse_pdf_cv(self, file: UploadFile, title: str, language: str, user_id: int) -> CV:
        if not file.filename.endswith('.pdf'):
            raise HTTPException(status_code=400, detail="Only PDF files are supported")
        
        upload_dir = "data/cvs"
        os.makedirs(upload_dir, exist_ok=True)
        
        file_path = os.path.join(upload_dir, f"{user_id}_{file.filename}")
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
        
        try:
            pdf_text = self._extract_text_from_pdf(file_path)
            parsed_cv = await self._parse_cv_content(pdf_text, language)
            
            db_cv = CV(
                title=title,
                language=language,
                content=parsed_cv,
                original_pdf_path=file_path,
                skills=parsed_cv.get("skills", []),
                experience=parsed_cv.get("experience", []),
                education=parsed_cv.get("education", []),
                personal_info=parsed_cv.get("personal_info", {}),
                is_base_cv=True,
                owner_id=user_id
            )
            
            self.db.add(db_cv)
            self.db.commit()
            self.db.refresh(db_cv)
            
            return db_cv
            
        except Exception as e:
            if os.path.exists(file_path):
                os.remove(file_path)
            raise HTTPException(status_code=500, detail=f"Error parsing CV: {str(e)}")
    
    def _extract_text_from_pdf(self, file_path: str) -> str:
        text = ""
        with open(file_path, 'rb') as file:
            pdf_reader = PyPDF2.PdfReader(file)
            for page in pdf_reader.pages:
                text += page.extract_text()
        return text
    
    async def _parse_cv_content(self, text: str, language: str) -> Dict[str, Any]:
        prompt = f"""
        Parse the following CV text and extract structured information in JSON format.
        The CV is in {language} language.
        
        Extract the following information:
        - personal_info: {{name, email, phone, address, linkedin, github}}
        - experience: [{{company, position, start_date, end_date, description, achievements}}]
        - education: [{{institution, degree, field, start_date, end_date, gpa}}]
        - skills: [list of technical and soft skills]
        - certifications: [list of certifications]
        - languages: [{{language, proficiency}}]
        - summary: brief professional summary
        
        CV Text:
        {text}
        
        Return only valid JSON without any additional text or formatting.
        """
        
        response = await self.llm_service.generate_response(prompt)
        
        try:
            return json.loads(response)
        except json.JSONDecodeError:
            cleaned_response = response.strip()
            if cleaned_response.startswith('```json'):
                cleaned_response = cleaned_response[7:-3]
            elif cleaned_response.startswith('```'):
                cleaned_response = cleaned_response[3:-3]
            return json.loads(cleaned_response)
    
    async def adapt_cv_for_job(self, cv_id: int, job_id: int, user_id: int, focus_areas: Optional[List[str]] = None) -> CV:
        original_cv = self.db.query(CV).filter(CV.id == cv_id, CV.owner_id == user_id).first()
        if not original_cv:
            raise HTTPException(status_code=404, detail="CV not found")
        
        job = self.db.query(Job).filter(Job.id == job_id).first()
        if not job:
            raise HTTPException(status_code=404, detail="Job not found")
        
        adapted_content = await self._adapt_cv_content(original_cv, job, focus_areas)
        
        adapted_cv = CV(
            title=f"{original_cv.title} - Adapted for {job.title}",
            language=original_cv.language,
            content=adapted_content,
            original_pdf_path=original_cv.original_pdf_path,
            skills=adapted_content.get("skills", []),
            experience=adapted_content.get("experience", []),
            education=adapted_content.get("education", []),
            personal_info=adapted_content.get("personal_info", {}),
            is_base_cv=False,
            owner_id=user_id
        )
        
        self.db.add(adapted_cv)
        self.db.commit()
        self.db.refresh(adapted_cv)
        
        return adapted_cv
    
    async def _adapt_cv_content(self, cv: CV, job: Job, focus_areas: Optional[List[str]]) -> Dict[str, Any]:
        focus_text = f"Focus especially on: {', '.join(focus_areas)}" if focus_areas else ""
        
        prompt = f"""
        Adapt the following CV content for a specific job application.
        
        Job Title: {job.title}
        Company: {job.company}
        Job Description: {job.description}
        Requirements: {job.requirements}
        Skills Required: {', '.join(job.skills_required)}
        
        Current CV Content:
        {json.dumps(cv.content, indent=2)}
        
        {focus_text}
        
        Instructions:
        1. Reorder and emphasize experience that matches the job requirements
        2. Highlight relevant skills that match the job requirements
        3. Adjust the professional summary to align with the position
        4. Quantify achievements where possible
        5. Use keywords from the job description
        6. Maintain truthfulness - don't add false information
        7. Keep the same structure but optimize content relevance
        
        Return the adapted CV content in the same JSON format.
        """
        
        response = await self.llm_service.generate_response(prompt)
        
        try:
            return json.loads(response)
        except json.JSONDecodeError:
            cleaned_response = response.strip()
            if cleaned_response.startswith('```json'):
                cleaned_response = cleaned_response[7:-3]
            elif cleaned_response.startswith('```'):
                cleaned_response = cleaned_response[3:-3]
            return json.loads(cleaned_response)
    
    async def initialize_user_cvs(self, user_id: int) -> List[CV]:
        """Initialize CVs from the user's personal website folder"""
        cv_paths = [
            "/home/cherif/dev/personal-website/assets/cv/Mihoubi_Med_Cherif_CV_EN.pdf",
            "/home/cherif/dev/personal-website/assets/cv/Mihoubi_Med_Cherif_CV_DE.pdf"
        ]
        
        cvs = []
        for cv_path in cv_paths:
            if os.path.exists(cv_path):
                language = "en" if "EN" in cv_path else "de"
                title = f"Base CV ({language.upper()})"
                
                try:
                    pdf_text = self._extract_text_from_pdf(cv_path)
                    parsed_cv = await self._parse_cv_content(pdf_text, language)
                    
                    db_cv = CV(
                        title=title,
                        language=language,
                        content=parsed_cv,
                        original_pdf_path=cv_path,
                        skills=parsed_cv.get("skills", []),
                        experience=parsed_cv.get("experience", []),
                        education=parsed_cv.get("education", []),
                        personal_info=parsed_cv.get("personal_info", {}),
                        is_base_cv=True,
                        owner_id=user_id
                    )
                    
                    self.db.add(db_cv)
                    cvs.append(db_cv)
                    
                except Exception as e:
                    print(f"Error parsing CV {cv_path}: {e}")
                    continue
        
        if cvs:
            self.db.commit()
            for cv in cvs:
                self.db.refresh(cv)
        
        return cvs