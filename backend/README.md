# Dream Job Ally Deduction - Backend

FastAPI backend service for analyzing resumes and dream jobs to deduce professional ally types using Claude 3 Sonnet.

## Setup

### Prerequisites

- Python 3.12+
- PostgreSQL (for production) or SQLite (for development)
- Anthropic API key for Claude 3 Sonnet

### Installation

1. **Create virtual environment:**
   ```bash
   python -m venv .venv
   source .venv/bin/activate  # On Windows: .venv\Scripts\activate
   ```

2. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

3. **Configure environment:**
   ```bash
   cp .env.example .env
   # Edit .env and add your ANTHROPIC_API_KEY
   ```

4. **Run database migrations:**
   ```bash
   alembic upgrade head
   ```

### Running the Server

**Development mode:**
```bash
cd src
python main.py
```

Or with uvicorn directly:
```bash
uvicorn src.main:app --reload --host 0.0.0.0 --port 8000
```

**Access API documentation:**
- Swagger UI: http://localhost:8000/api/docs
- ReDoc: http://localhost:8000/api/redoc

## Project Structure

```
backend/
├── src/
│   ├── models/          # SQLAlchemy database models
│   ├── services/        # Business logic services
│   ├── api/             # FastAPI route handlers
│   │   ├── routes/      # API endpoint definitions
│   │   └── dependencies/ # Dependency injection
│   ├── core/            # Core configuration
│   │   ├── config.py    # Environment settings
│   │   ├── database.py  # Database connection
│   │   ├── rate_limiter.py  # Rate limiting
│   │   └── security.py  # Authentication
│   ├── integrations/    # External API clients
│   │   ├── anthropic_client.py  # Claude 3 Sonnet
│   │   ├── github_client.py     # GitHub API
│   │   ├── twitter_client.py    # Twitter/X API
│   │   └── linkedin_client.py   # LinkedIn (placeholder)
│   └── main.py          # Application entry point
├── tests/               # Test suites
├── alembic/             # Database migrations
├── requirements.txt     # Python dependencies
├── .env.example         # Environment variables template
├── .pylintrc            # Linting configuration
└── pytest.ini           # Testing configuration
```

## Environment Variables

Required variables (see `.env.example`):

- `ANTHROPIC_API_KEY` - Claude 3 Sonnet API key (required)
- `DATABASE_URL` - Database connection string
- `SECRET_KEY` - Secret key for JWT signing
- `GITHUB_API_TOKEN` - GitHub API token (optional, for ally discovery)
- `TWITTER_API_KEY` - Twitter API key (optional, for ally discovery)
- `LINKEDIN_API_KEY` - LinkedIn API key (optional, for ally discovery)

## Database Migrations

**Create new migration:**
```bash
alembic revision --autogenerate -m "Description of changes"
```

**Apply migrations:**
```bash
alembic upgrade head
```

**Rollback one migration:**
```bash
alembic downgrade -1
```

## Testing

**Run all tests:**
```bash
pytest
```

**Run with coverage:**
```bash
pytest --cov=src --cov-report=html
```

**Run specific test types:**
```bash
pytest tests/unit/           # Unit tests only
pytest tests/integration/    # Integration tests only
pytest tests/contract/       # Contract tests only
```

## Code Quality

**Run linting:**
```bash
pylint src/
```

**Format code:**
```bash
black src/
```

## API Endpoints

### Health Check
- `GET /api/v1/health` - Service health status

### Resume Analysis (User Story 1)
- `POST /api/v1/resumes/upload` - Upload resume file
- `GET /api/v1/resumes/{id}/status` - Get parsing status
- `GET /api/v1/resumes/{id}` - Get parsed resume data

### Dream Job & Ally Deduction (User Story 1)
- `POST /api/v1/dream-jobs` - Create dream job description
- `GET /api/v1/dream-jobs/{id}` - Get dream job details
- `POST /api/v1/ally-deduction/analyze` - Analyze resume + dream job
- `GET /api/v1/ally-deduction/{id}/results` - Get deduced ally types

### Ally Discovery (User Story 2)
- `POST /api/v1/ally-discovery/search` - Search for professional allies
- `GET /api/v1/ally-discovery/{id}/results` - Get discovered allies

### Career Strategy (User Story 3)
- `POST /api/v1/career-gaps/analyze` - Analyze career gaps
- `POST /api/v1/career-strategy` - Generate transition strategy

### Goal Refinement (User Story 4)
- `PUT /api/v1/dream-jobs/{id}` - Update dream job description
- `GET /api/v1/dream-job-evolution/{id}` - Get evolution history

## Architecture

### Core Components

1. **LLM Integration**: Claude 3 Sonnet via Anthropic API
   - Rate limiting: 50 requests/minute
   - Automatic retry with exponential backoff
   - Response caching (24 hours)

2. **Document Processing**: PyPDF2 + pdfplumber fallback
   - Supports PDF, DOCX, TXT formats
   - Max file size: 10MB

3. **Vector Store**: FAISS with HuggingFace embeddings
   - Model: sentence-transformers/all-MiniLM-L6-v2
   - Dimension: 384

4. **External APIs**: GitHub, Twitter/X, LinkedIn
   - Circuit breaker pattern for resilience
   - Per-service rate limiting
   - Graceful degradation

## Development

### Adding New Endpoints

1. Create route handler in `src/api/routes/`
2. Define models in `src/models/`
3. Implement business logic in `src/services/`
4. Add tests in `tests/`
5. Update this README

### Adding New Dependencies

1. Add to `requirements.txt`
2. Run `pip install -r requirements.txt`
3. Update `.devcontainer/devcontainer.json` if needed

## Troubleshooting

**Import errors:**
- Ensure you're in the `backend/` directory
- Activate virtual environment
- Install all dependencies

**Database connection errors:**
- Check `DATABASE_URL` in `.env`
- Verify PostgreSQL is running (if using PostgreSQL)
- Run migrations: `alembic upgrade head`

**Anthropic API errors:**
- Verify `ANTHROPIC_API_KEY` in `.env`
- Check API rate limits and quotas
- Review API usage at https://console.anthropic.com/

**Rate limiting issues:**
- Adjust rate limiter settings in `core/rate_limiter.py`
- Implement caching to reduce API calls

## License

See LICENSE file in repository root.
