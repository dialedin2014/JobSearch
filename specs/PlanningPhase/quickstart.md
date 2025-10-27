# Quickstart Guide: Dream Job Ally Deduction

**Feature**: 002-dream-job-ally-deduction  
**Branch**: `002-dream-job-ally-deduction`  
**Last Updated**: 2025-10-26

## Prerequisites

- Docker Desktop installed and running
- VS Code with Dev Containers extension
- Git configured with access to repository
- Anthropic API key for Claude 3 Sonnet (obtain from [Anthropic Console](https://console.anthropic.com/))

---

## Local Development Setup

### 1. Clone Repository & Checkout Feature Branch

```powershell
# Clone repository
git clone https://github.com/dialedin2014/JobSearch.git
cd JobSearch

# Checkout feature branch
git checkout 002-dream-job-ally-deduction
```

### 2. Environment Variables

Create `.env` file in repository root:

```bash
# Anthropic API
ANTHROPIC_API_KEY=sk-ant-api03-...  # Your Anthropic API key

# Database
DATABASE_URL=postgresql://jobsearch:jobsearch@localhost:5432/jobsearch_dev
# For SQLite (dev/testing): DATABASE_URL=sqlite:///./jobsearch.db

# External APIs (optional for MVP)
GITHUB_API_TOKEN=ghp_...  # GitHub personal access token
TWITTER_API_KEY=...       # Twitter API key
TWITTER_API_SECRET=...    # Twitter API secret
LINKEDIN_API_KEY=...      # LinkedIn API key (if available)

# Application Settings
ENVIRONMENT=development
DEBUG=true
LOG_LEVEL=INFO
MAX_UPLOAD_SIZE_MB=10
```

### 3. Open in Dev Container

1. Open VS Code in repository directory
2. Press `Ctrl+Shift+P` (or `Cmd+Shift+P` on Mac)
3. Select **"Dev Containers: Reopen in Container"**
4. Wait for container build (first time: ~5-10 minutes)

The `.devcontainer/devcontainer.json` will automatically:
- Install Python 3.12
- Install all dependencies from `requirements.txt`
- Setup PostgreSQL database container
- Configure VS Code extensions (Python, Pylint, GitHub Copilot)

### 4. Initialize Database

```bash
# Inside Dev Container terminal

# Run Alembic migrations
cd backend
alembic upgrade head

# (Optional) Seed test data
python scripts/seed_test_data.py
```

### 5. Start Backend Server

```bash
# Inside backend/ directory
uvicorn src.main:app --reload --host 0.0.0.0 --port 8000
```

Backend will be available at: `http://localhost:8000`

API documentation (auto-generated): `http://localhost:8000/docs`

### 6. Start Frontend (Optional for Full-Stack Development)

```bash
# Open new terminal
cd frontend

# Install dependencies (first time only)
npm install

# Start development server
npm run dev
```

Frontend will be available at: `http://localhost:3000`

---

## Project Structure

```
JobSearch/
├── .devcontainer/
│   ├── devcontainer.json       # Dev container configuration
│   └── Dockerfile              # Container image definition
├── backend/
│   ├── src/
│   │   ├── main.py             # FastAPI application entry point
│   │   ├── models/             # SQLAlchemy ORM models
│   │   │   ├── user_profile.py
│   │   │   ├── resume.py
│   │   │   ├── dream_job.py
│   │   │   └── ally_type.py
│   │   ├── services/           # Business logic
│   │   │   ├── resume_parser.py
│   │   │   ├── llm_service.py
│   │   │   ├── ally_deduction.py
│   │   │   └── ally_discovery.py
│   │   ├── api/
│   │   │   └── routes/         # API endpoints
│   │   │       ├── resume.py
│   │   │       ├── dream_job.py
│   │   │       └── ally_types.py
│   │   ├── core/
│   │   │   ├── config.py       # Configuration management
│   │   │   └── security.py     # Auth/security helpers
│   │   └── integrations/
│   │       ├── anthropic_client.py  # Claude 3 Sonnet client
│   │       ├── github_client.py
│   │       └── twitter_client.py
│   ├── tests/
│   │   ├── unit/
│   │   ├── integration/
│   │   └── contract/
│   ├── alembic/                # Database migrations
│   ├── requirements.txt        # Python dependencies
│   └── pytest.ini              # Test configuration
├── frontend/                    # React/Next.js frontend
│   ├── src/
│   │   ├── components/
│   │   ├── pages/
│   │   └── services/
│   ├── package.json
│   └── next.config.js
├── specs/
│   └── 002-dream-job-ally-deduction/
│       ├── spec.md             # Feature specification
│       ├── plan.md             # Implementation plan
│       ├── research.md         # Technical research
│       ├── data-model.md       # Database schema
│       ├── contracts/          # API contracts (OpenAPI)
│       └── tasks.md            # Task breakdown (to be generated)
└── .env                        # Environment variables (not committed)
```

---

## Running Tests

### Backend Tests

```bash
cd backend

# Run all tests
pytest

# Run specific test file
pytest tests/unit/test_resume_parser.py

# Run with coverage
pytest --cov=src --cov-report=html

# Run only contract tests
pytest tests/contract/

# Run with verbose output
pytest -v
```

### Frontend Tests

```bash
cd frontend

# Run all tests
npm test

# Run tests in watch mode
npm test -- --watch

# Run with coverage
npm test -- --coverage
```

---

## API Usage Examples

### 1. Upload Resume

```bash
curl -X POST http://localhost:8000/api/v1/resumes/upload \
  -F "file=@/path/to/resume.pdf" \
  -F "user_id=550e8400-e29b-41d4-a716-446655440000"
```

Response:
```json
{
  "resume_id": "123e4567-e89b-12d3-a456-426614174000",
  "status": "parsing",
  "message": "Resume uploaded successfully. Parsing in progress.",
  "estimated_completion": "2025-10-26T14:35:00Z"
}
```

### 2. Check Resume Parsing Status

```bash
curl http://localhost:8000/api/v1/resumes/123e4567-e89b-12d3-a456-426614174000/status
```

### 3. Deduce Ally Types

```bash
curl -X POST http://localhost:8000/api/v1/ally-deduction/analyze \
  -H "Content-Type: application/json" \
  -d '{
    "user_id": "550e8400-e29b-41d4-a716-446655440000",
    "resume_id": "123e4567-e89b-12d3-a456-426614174000",
    "dream_job_description": "I want to transition from ML Engineer to AI Product Manager at a tech startup, focusing on B2B SaaS products in the healthcare space."
  }'
```

Response:
```json
{
  "analysis_id": "789e0123-e89b-12d3-a456-426614174999",
  "status": "processing",
  "estimated_completion": "2025-10-26T14:36:00Z",
  "message": "Ally type deduction started. Expected completion in 20-30 seconds."
}
```

### 4. Get Deduced Ally Types

```bash
curl http://localhost:8000/api/v1/ally-deduction/789e0123-e89b-12d3-a456-426614174999/results?min_confidence=0.7
```

Response:
```json
{
  "analysis_id": "789e0123-e89b-12d3-a456-426614174999",
  "user_id": "550e8400-e29b-41d4-a716-446655440000",
  "ally_types": [
    {
      "id": "abc12345-...",
      "ally_type_name": "AI/ML Technical Leaders",
      "confidence_score": 0.85,
      "selection_rationale": "Given your ML engineering background...",
      "search_queries": {
        "github": "machine learning language:python followers:>1000",
        "twitter": "#MachineLearning #ProductManagement",
        "linkedin": "AI Product Manager OR ML Product Lead"
      },
      "rank": 1
    }
  ],
  "total_ally_types": 5,
  "analyzed_at": "2025-10-26T14:35:45Z"
}
```

### 5. Search for Allies

```bash
curl -X POST http://localhost:8000/api/v1/ally-discovery/search \
  -H "Content-Type: application/json" \
  -d '{
    "user_id": "550e8400-e29b-41d4-a716-446655440000",
    "ally_type_ids": ["abc12345-..."],
    "platforms": ["github", "linkedin"]
  }'
```

---

## Database Management

### View Database

```bash
# PostgreSQL CLI
psql postgresql://jobsearch:jobsearch@localhost:5432/jobsearch_dev

# List tables
\dt

# Query user profiles
SELECT * FROM user_profiles;

# Exit
\q
```

### Create New Migration

```bash
cd backend

# Generate migration after model changes
alembic revision --autogenerate -m "Add new field to ally_type"

# Review generated migration in alembic/versions/

# Apply migration
alembic upgrade head
```

### Reset Database

```bash
# Drop all tables and recreate
alembic downgrade base
alembic upgrade head

# Re-seed test data
python scripts/seed_test_data.py
```

---

## Development Workflow

### 1. Create Feature Branch (Already Done)

```powershell
git checkout -b 002-dream-job-ally-deduction
```

### 2. Implement User Story (Priority Order)

Follow task breakdown in `specs/002-dream-job-ally-deduction/tasks.md`:

1. **Phase 1**: Setup (T001-T007) - Project structure, dependencies
2. **Phase 2**: Foundation (T008-T013) - RAG pipeline, LLM integration
3. **Phase 3**: User Story 1 (P1) - Resume analysis & ally deduction
4. **Phase 4**: User Story 2 (P2) - Ally discovery
5. **Phase 5**: User Story 3 (P3) - Gap analysis
6. **Phase 6**: User Story 4 (P4) - Goal refinement

### 3. Test-Driven Development

For each task:

1. Write failing test first
2. Implement minimal code to pass test
3. Refactor
4. Commit

```bash
# Example TDD cycle
pytest tests/unit/test_resume_parser.py::test_extract_skills  # FAIL
# ... implement extract_skills() ...
pytest tests/unit/test_resume_parser.py::test_extract_skills  # PASS
git add .
git commit -m "feat: implement skill extraction from resumes"
```

### 4. Code Quality Checks

```bash
# Run pylint
pylint src/

# Format code
black src/ tests/

# Type checking
mypy src/

# Security checks
bandit -r src/
```

### 5. Commit & Push

```bash
git add .
git commit -m "feat(ally-deduction): implement Claude 3 Sonnet integration"
git push origin 002-dream-job-ally-deduction
```

---

## Troubleshooting

### Issue: Dev Container Build Fails

**Solution**: Clear Docker cache and rebuild
```powershell
docker system prune -a
# In VS Code: Dev Containers: Rebuild Container
```

### Issue: Anthropic API Key Invalid

**Solution**: Verify key in `.env` and restart container
```bash
# Check if key is loaded
echo $ANTHROPIC_API_KEY

# Restart FastAPI server
# Ctrl+C, then: uvicorn src.main:app --reload
```

### Issue: Database Connection Failed

**Solution**: Ensure PostgreSQL container is running
```bash
docker ps | grep postgres

# If not running, start it:
docker-compose up -d postgres
```

### Issue: Resume Parsing Returns Empty Skills

**Solution**: Check parsing confidence and fallback to manual input
```python
if parsed_resume.parsing_confidence < 0.5:
    # Prompt user for manual skill entry (FR-003a)
    pass
```

### Issue: Tests Fail with "ModuleNotFoundError"

**Solution**: Ensure PYTHONPATH is set correctly
```bash
export PYTHONPATH="${PYTHONPATH}:$(pwd)/backend/src"
pytest
```

---

## Key Configuration Files

### `backend/requirements.txt`

```txt
fastapi==0.104.1
uvicorn[standard]==0.24.0
anthropic==0.8.1
langchain==0.1.0
langchain-community==0.1.0
faiss-cpu==1.7.4
sentence-transformers==2.2.2
PyPDF2==3.0.1
pdfplumber==0.10.3
python-docx==1.1.0
httpx==0.25.2
sqlalchemy==2.0.23
alembic==1.13.1
psycopg2-binary==2.9.9
pydantic==2.5.2
pydantic-settings==2.1.0
python-multipart==0.0.6
tenacity==8.2.3
circuitbreaker==1.4.0
pytest==7.4.3
pytest-asyncio==0.21.1
pytest-cov==4.1.0
pylint==3.0.3
black==23.12.1
mypy==1.7.1
```

### `.devcontainer/devcontainer.json`

```json
{
  "name": "JobSearch Dev",
  "dockerComposeFile": "docker-compose.yml",
  "service": "app",
  "workspaceFolder": "/workspace",
  "customizations": {
    "vscode": {
      "extensions": [
        "ms-python.python",
        "ms-python.vscode-pylance",
        "ms-toolsai.jupyter",
        "github.copilot",
        "ms-azuretools.vscode-docker"
      ],
      "settings": {
        "python.defaultInterpreterPath": "/usr/local/bin/python",
        "python.linting.enabled": true,
        "python.linting.pylintEnabled": true,
        "python.formatting.provider": "black"
      }
    }
  },
  "postCreateCommand": "pip install -r backend/requirements.txt"
}
```

---

## Next Steps

1. ✅ Setup complete - Dev environment ready
2. 🔄 Implement Phase 1: Setup tasks (T001-T007)
3. ⏳ Implement Phase 2: Foundation (T008-T013)
4. ⏳ Implement User Story 1 (P1) - Resume & Ally Deduction
5. ⏳ Deploy to staging environment
6. ⏳ User acceptance testing

---

## Resources

- **Feature Spec**: `specs/002-dream-job-ally-deduction/spec.md`
- **Data Model**: `specs/002-dream-job-ally-deduction/data-model.md`
- **API Contracts**: `specs/002-dream-job-ally-deduction/contracts/`
- **Anthropic Docs**: https://docs.anthropic.com/claude/reference/
- **FastAPI Docs**: https://fastapi.tiangolo.com/
- **LangChain Docs**: https://python.langchain.com/docs/

---

## Support

For questions or issues:
- Check `specs/002-dream-job-ally-deduction/research.md` for technical decisions
- Review constitution at `.specify/memory/constitution.md` for project standards
- Open issue in GitHub repository
