# JobOctubus

An intelligent job search and application management system that automatically adapts your CV and generates personalized cover letters for each job application.

## Features

- **AI-Powered Job Search**: Search across multiple job platforms with intelligent matching
- **CV Adaptation**: Automatically adapt your CV content to match specific job requirements
- **Cover Letter Generation**: Generate personalized cover letters using OpenRouter LLM APIs
- **Application Tracking**: Track all your job applications in one place
- **Multi-language Support**: Support for English and German CVs and applications

## Tech Stack

### Backend
- **FastAPI**: Modern Python web framework
- **SQLAlchemy**: Database ORM
- **OpenRouter**: LLM API integration for CV adaptation and cover letter generation
- **PyPDF2**: PDF parsing for CV extraction
- **BeautifulSoup**: Web scraping for job data

### Frontend
- **React**: Modern JavaScript framework
- **TypeScript**: Type-safe development
- **Tailwind CSS**: Utility-first CSS framework
- **Heroicons**: Beautiful SVG icons

## Setup

### Prerequisites
- Python 3.8+
- Node.js 16+
- OpenRouter API key

### Backend Setup

1. Install Python dependencies:
```bash
pip install -r requirements.txt
```

2. Set up environment variables:
```bash
cp .env.example .env
```

Edit `.env` and add your API keys:
```
OPENROUTER_API_KEY=your_openrouter_key_here
SECRET_KEY=your_secret_key_here
```

3. Run the backend:
```bash
cd backend
python -m uvicorn main:app --reload
```

The API will be available at `http://localhost:8000`

### Frontend Setup

1. Install Node.js dependencies:
```bash
npm install
```

2. Start the development server:
```bash
npm start
```

The frontend will be available at `http://localhost:3000`

## Usage

### 1. Upload Your CV
- Upload your existing CV (PDF format) in English or German
- The system will automatically parse and extract structured information
- Your base CVs will be stored for future job applications

### 2. Search for Jobs
- Use the job search interface to find relevant positions
- Filter by location, experience level, job type, and more
- View match scores based on your CV content

### 3. Apply to Jobs
- Select jobs you're interested in
- The system will automatically adapt your CV to highlight relevant experience
- Generate personalized cover letters tailored to each job
- Track your application status

### 4. Manage Applications
- View all your applications in one dashboard
- Update application status as you hear back from employers
- Add notes and track interview dates

## API Documentation

Once the backend is running, visit `http://localhost:8000/docs` to view the interactive API documentation.

## Key Endpoints

- `POST /api/auth/register` - User registration
- `POST /api/auth/login` - User login
- `POST /api/jobs/search` - Search for jobs
- `POST /api/cvs/upload` - Upload and parse CV
- `POST /api/cvs/{cv_id}/adapt` - Adapt CV for specific job
- `POST /api/applications/{id}/cover-letter` - Generate cover letter

## Development

### Running Tests
```bash
# Backend tests
cd backend
pytest

# Frontend tests
npm test
```

### Code Style
- Backend: Follow PEP 8 guidelines
- Frontend: Use Prettier and ESLint configurations

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests for new functionality
5. Submit a pull request

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Support

For support or questions, please open an issue on GitHub.