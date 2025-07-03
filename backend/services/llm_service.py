import openai
from typing import Optional, List
from config import settings

class LLMService:
    def __init__(self):
        self.client = openai.OpenAI(
            api_key=settings.openrouter_api_key,
            base_url=settings.openrouter_base_url
        )
        self.default_model = "anthropic/claude-3-haiku"
        self.advanced_model = "anthropic/claude-3-sonnet"
    
    async def generate_response(
        self, 
        prompt: str, 
        model: Optional[str] = None,
        temperature: float = 0.7,
        max_tokens: int = 4000
    ) -> str:
        try:
            response = self.client.chat.completions.create(
                model=model or self.default_model,
                messages=[
                    {"role": "user", "content": prompt}
                ],
                temperature=temperature,
                max_tokens=max_tokens
            )
            return response.choices[0].message.content
        except Exception as e:
            raise Exception(f"LLM service error: {str(e)}")
    
    async def generate_cv_adaptation(
        self, 
        cv_content: dict, 
        job_description: str,
        job_requirements: str,
        focus_areas: Optional[List[str]] = None
    ) -> dict:
        focus_text = f"Focus especially on: {', '.join(focus_areas)}" if focus_areas else ""
        
        prompt = f"""
        You are an expert CV adaptation specialist. Adapt the following CV content for a specific job application.
        
        Job Description: {job_description}
        Job Requirements: {job_requirements}
        {focus_text}
        
        Current CV Content:
        {cv_content}
        
        Instructions:
        1. Reorder and emphasize experience that matches the job requirements
        2. Highlight relevant skills that match the job requirements
        3. Adjust the professional summary to align with the position
        4. Quantify achievements where possible
        5. Use keywords from the job description
        6. Maintain truthfulness - don't add false information
        7. Keep the same JSON structure but optimize content relevance
        
        Return the adapted CV content in the same JSON format.
        """
        
        response = await self.generate_response(prompt, model=self.advanced_model)
        
        try:
            import json
            return json.loads(response)
        except json.JSONDecodeError:
            cleaned_response = response.strip()
            if cleaned_response.startswith('```json'):
                cleaned_response = cleaned_response[7:-3]
            elif cleaned_response.startswith('```'):
                cleaned_response = cleaned_response[3:-3]
            return json.loads(cleaned_response)
    
    async def generate_cover_letter(
        self,
        cv_content: dict,
        job_title: str,
        company: str,
        job_description: str,
        job_requirements: str,
        tone: str = "professional",
        length: str = "medium",
        custom_points: Optional[List[str]] = None
    ) -> str:
        length_guide = {
            "short": "2-3 paragraphs, around 150-200 words",
            "medium": "3-4 paragraphs, around 250-350 words", 
            "long": "4-5 paragraphs, around 400-500 words"
        }
        
        tone_guide = {
            "professional": "formal, business-like tone",
            "enthusiastic": "energetic and passionate tone",
            "conversational": "friendly but professional tone"
        }
        
        custom_text = f"Include these specific points: {', '.join(custom_points)}" if custom_points else ""
        
        prompt = f"""
        You are an expert cover letter writer. Write a compelling cover letter for the following job application.
        
        Job Title: {job_title}
        Company: {company}
        Job Description: {job_description}
        Job Requirements: {job_requirements}
        
        Applicant's CV Summary:
        - Name: {cv_content.get('personal_info', {}).get('name', 'Applicant')}
        - Summary: {cv_content.get('summary', '')}
        - Key Skills: {', '.join(cv_content.get('skills', [])[:10])}
        - Recent Experience: {cv_content.get('experience', [{}])[0].get('position', '') if cv_content.get('experience') else ''}
        
        Style Requirements:
        - Length: {length_guide.get(length, 'medium')}
        - Tone: {tone_guide.get(tone, 'professional')}
        - {custom_text}
        
        Instructions:
        1. Start with a strong opening that mentions the specific position
        2. Highlight relevant experience and skills that match the job requirements
        3. Show knowledge of the company and why you want to work there
        4. Include specific examples of achievements
        5. End with a strong closing and call to action
        6. Use the applicant's actual experience and skills from their CV
        7. Make it personal and tailored to this specific job
        
        Write a complete cover letter without any placeholders.
        """
        
        return await self.generate_response(prompt, model=self.advanced_model, temperature=0.8)
    
    async def analyze_job_cv_match(
        self,
        cv_content: dict,
        job_description: str,
        job_requirements: str,
        skills_required: List[str]
    ) -> dict:
        prompt = f"""
        You are an expert recruiter. Analyze how well this CV matches the job requirements and provide a detailed assessment.
        
        Job Description: {job_description}
        Job Requirements: {job_requirements}
        Skills Required: {', '.join(skills_required)}
        
        CV Content:
        {cv_content}
        
        Provide a detailed analysis including:
        1. Overall match score (0-100)
        2. Matching skills
        3. Missing skills
        4. Relevant experience
        5. Strengths for this position
        6. Areas for improvement
        7. Specific recommendations
        
        Return as JSON with the following structure:
        {
            "match_score": number,
            "matching_skills": [array of skills],
            "missing_skills": [array of skills],
            "relevant_experience": [array of experience items],
            "strengths": [array of strengths],
            "improvements": [array of improvements],
            "recommendations": [array of recommendations]
        }
        """
        
        response = await self.generate_response(prompt, model=self.advanced_model)
        
        try:
            import json
            return json.loads(response)
        except json.JSONDecodeError:
            cleaned_response = response.strip()
            if cleaned_response.startswith('```json'):
                cleaned_response = cleaned_response[7:-3]
            elif cleaned_response.startswith('```'):
                cleaned_response = cleaned_response[3:-3]
            return json.loads(cleaned_response)