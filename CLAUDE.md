# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

JobOctubus is an intelligent job search and application management system that automatically adapts CVs and generates personalized cover letters. It integrates with OpenRouter for LLM capabilities and parses existing CVs from the user's personal website directory.

## Development Commands

### Backend (FastAPI)
```bash
# Install dependencies
pip install -r requirements.txt

# Run development server (from backend directory)
cd backend
python -m uvicorn main:app --reload

# Or from project root
python -m uvicorn backend.main:app --reload

# Run tests (when implemented)
cd backend
pytest

# Type checking (when mypy is configured)
mypy backend/
```

### Frontend (React/TypeScript)
```bash
# Install dependencies
npm install

# Run development server
npm start

# Build for production
npm run build

# Run tests
npm test

# Run single test file
npm test -- --testPathPattern=<filename>
```

### Environment Setup
```bash
# Create environment file
cp .env.example .env

# Required environment variables:
# - OPENROUTER_API_KEY (for LLM operations)
# - SECRET_KEY (for JWT authentication)
# - DATABASE_URL (defaults to SQLite)
```

## Architecture Overview

### Backend Architecture

The backend follows a layered architecture:

1. **API Layer** (`backend/api/`): FastAPI routers handling HTTP requests
   - `auth.py`: JWT-based authentication endpoints
   - `jobs.py`: Job search and management endpoints
   - `cvs.py`: CV upload, parsing, and adaptation endpoints
   - `applications.py`: Application tracking and cover letter generation

2. **Service Layer** (`backend/services/`): Business logic implementation
   - `cv_service.py`: PDF parsing, CV adaptation logic, connects to user's personal CVs
   - `llm_service.py`: OpenRouter integration for AI-powered features
   - `job_search.py`: Job matching and scoring algorithms
   - `application_service.py`: Application workflow management

3. **Data Layer** (`backend/models/`): SQLAlchemy models and database schema
   - User, CV, Job, Application, JobSearch, Template models
   - Relationships: User → CVs → Applications ← Jobs

4. **Integration Points**:
   - Personal website CVs at `/home/cherif/dev/personal-website/assets/cv/`
   - OpenRouter API for LLM operations (CV adaptation, cover letter generation)

### Frontend Architecture

React application with TypeScript:

1. **Context** (`src/contexts/`): Global state management
   - `AuthContext`: User authentication state and methods

2. **Services** (`src/services/`): API client layer
   - Axios-based services for auth, jobs, CVs, and applications
   - Automatic token injection via interceptors

3. **Pages** (`src/pages/`): Main application views
   - Dashboard, Jobs, CVs, Applications, Login
   - Each page manages its own state and API calls

4. **Components** (`src/components/`): Reusable UI components
   - Layout, ProtectedRoute for navigation and access control

### Key Workflows

1. **Agentic Job Search Workflow** (Primary):
   - User enters keywords/job description OR loads CVs from personal website
   - System searches multiple job platforms and returns matching jobs
   - User selects multiple jobs from the list (batch selection)
   - System automatically adapts CV for each selected job using LLM
   - System generates personalized cover letters for each job
   - All applications are created and ready for submission
   - User can review and submit from Applications page

2. **CV Processing Flow**:
   - User uploads PDF or system reads from personal website folder
   - `CVService._extract_text_from_pdf()` extracts text
   - `LLMService` parses text into structured JSON
   - Stored in database with searchable fields

3. **Individual Job Application Flow** (Alternative):
   - Job search returns matches with scoring
   - User selects single job → system adapts CV using LLM
   - Cover letter generated based on job + CV content
   - Application tracked through status lifecycle

4. **Authentication Flow**:
   - JWT tokens with 30-minute expiration
   - Token stored in localStorage
   - Automatic injection on API requests
   - Protected routes redirect to login

### Database Schema

SQLite database with following key relationships:
- Users own multiple CVs
- Jobs can have multiple Applications
- Applications link Users, Jobs, and CVs
- CVs marked as `is_base_cv` are original uploads
- Adapted CVs reference the same `original_pdf_path`

### External Dependencies

- **OpenRouter API**: All LLM operations (CV parsing, adaptation, cover letter generation)
- **Personal Website**: Source for user's existing CV files
- **Mock Job Data**: Currently returns simulated jobs, designed for easy API integration

### Development Notes

- Frontend runs on port 3000, backend on port 8000
- CORS configured for local development
- Database auto-creates on startup via SQLAlchemy
- API documentation available at http://localhost:8000/docs
- All file paths use absolute paths, not relative


### Claude rules

1. First think through the problem, read the codebase for relevant files, and write a plan to tasks/todo.md.
2. The plan should have a list of todo items that you can check off as you complete them
3. Before you begin working, check in with me and I will verify the plan.
4. Then, begin working on the todo items, marking them as complete as you go.
5. Please every step of the way just give me a high level explanation of what changes you made
6. Make every task and code change you do as simple as possible. We want to avoid making any massive or complex changes. Every change should impact as little code as possible. Everything is about simplicity.
7. Finally, add a review section to the [todo.md](http://todo.md/) file with a summary of the changes you made and any other relevant information.
