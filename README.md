# JobOctubus

An intelligent agentic job search tool that automates the entire job application process. Simply search for jobs, select multiple positions, and let the system automatically adapt your CV and generate personalized cover letters for each selected job.

## Features

- **Agentic Workflow**: Batch process multiple job applications at once
- **AI-Powered Job Search**: Search across multiple job platforms with intelligent matching
- **Automatic CV Adaptation**: Automatically adapt your CV content to match specific job requirements
- **Smart Cover Letter Generation**: Generate personalized cover letters using OpenRouter LLM APIs
- **Application Tracking**: Track all your job applications in one place
- **Personal Website Integration**: Automatically loads CVs from your personal website directory
- **Multi-language Support**: Support for English and German CVs and applications

## Tech Stack

### Backend
- **FastAPI**: Modern Python web framework with async support
- **SQLAlchemy 2.0**: Database ORM with modern declarative style
- **OpenRouter**: LLM API integration for CV adaptation and cover letter generation
- **PyPDF2**: PDF parsing for CV extraction
- **BeautifulSoup**: Web scraping for job data
- **Structured Logging**: JSON-formatted logs with rotation

### Frontend
- **React**: Modern JavaScript framework
- **TypeScript**: Type-safe development
- **Tailwind CSS**: Utility-first CSS framework
- **Heroicons**: Beautiful SVG icons

## Setup

### Prerequisites
- Python 3.9+ (compatible with older versions)
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

Edit `.env` and add your configuration:
```
OPENROUTER_API_KEY=your_openrouter_key_here
SECRET_KEY=your_secret_key_here_min_32_chars
PERSONAL_WEBSITE_CV_EN_PATH=/path/to/your/english/cv.pdf
PERSONAL_WEBSITE_CV_DE_PATH=/path/to/your/german/cv.pdf
DEBUG=false  # Set to true for development
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

### Agentic Workflow (Recommended)
1. **Initialize CVs**: The system automatically loads CVs from your personal website directory
2. **Search Jobs**: Enter keywords or job descriptions to find matching positions
3. **Batch Select**: Select multiple jobs from the search results
4. **Automated Processing**: The system will:
   - Adapt your CV for each selected job
   - Generate personalized cover letters
   - Create application records for tracking
5. **Review & Apply**: Review the generated materials and submit applications

### Manual Workflow (Alternative)
1. **Upload Your CV**: Upload your existing CV (PDF format) in English or German
2. **Search for Jobs**: Use the job search interface to find relevant positions
3. **Apply Individually**: Select jobs one by one for CV adaptation and cover letter generation

### 4. Manage Applications
- View all your applications in one dashboard
- Update application status as you hear back from employers
- Add notes and track interview dates

## API Documentation

Once the backend is running, visit `http://localhost:8000/docs` to view the interactive API documentation.

## Technical Improvements

### Recent Updates
- **Async Operations**: Converted to async OpenAI client for better performance
- **Database Optimizations**: Added connection pooling and cascade constraints
- **Error Handling**: Specific exception handling for different error scenarios
- **Environment Validation**: Automatic validation of required settings on startup
- **Logging System**: Structured JSON logging with automatic rotation
- **Python Compatibility**: Fixed compatibility issues for Python 3.9+

## Key Endpoints

- `POST /api/auth/register` - User registration
- `POST /api/auth/login` - User login
- `POST /api/jobs/search` - Search for jobs
- `POST /api/cvs/upload` - Upload and parse CV
- `POST /api/cvs/{cv_id}/adapt` - Adapt CV for specific job
- `POST /api/applications/{id}/cover-letter` - Generate cover letter

## Development

### Environment Setup
```bash
# Create and activate virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

### Running Tests
```bash
# Backend tests
cd backend
pytest

# Frontend tests
npm test
```

### Logs
Logs are stored in the `logs/` directory:
- `joboctubus.log`: General application logs
- `joboctubus_errors.log`: Error-level logs only

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