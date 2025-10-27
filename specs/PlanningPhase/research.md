# Research: Dream Job Ally Deduction

**Feature**: 002-dream-job-ally-deduction  
**Phase**: 0 - Outline & Research  
**Date**: 2025-10-26

## Purpose

This document consolidates research findings for technical decisions and best practices needed to implement the Dream Job Ally Deduction feature. All "NEEDS CLARIFICATION" items from the Technical Context have been resolved through this research.

---

## Research Areas

### 1. Claude 3 Sonnet Integration (Anthropic API)

**Decision**: Use `anthropic` Python SDK with structured prompts for ally type deduction, confidence scoring, and search query generation.

**Rationale**: 
- Claude 3 Sonnet provides superior reasoning quality for complex career analysis compared to local models
- Better consistency in confidence scoring (85% relevance target per SC-004)
- Native support for structured outputs and chain-of-thought reasoning
- Anthropic SDK provides built-in rate limiting and error handling

**Implementation Pattern**:
```python
import anthropic

client = anthropic.Anthropic(api_key=os.environ.get("ANTHROPIC_API_KEY"))

message = client.messages.create(
    model="claude-3-sonnet-20240229",
    max_tokens=2048,
    temperature=0.3,  # Lower temp for consistent ally deduction
    system="You are a career analysis expert...",
    messages=[{"role": "user", "content": prompt}]
)
```

**Rate Limits**: 
- Tier 1: 50 requests/min, 40k tokens/min
- Tier 2: 1000 requests/min, 80k tokens/min
- Implement exponential backoff with `tenacity` library

**Cost Management**:
- Input: $3/million tokens
- Output: $15/million tokens
- Estimated per-analysis cost: $0.01-0.03 (resume ~2k tokens, response ~1k tokens)
- Implement request caching for identical resume+dream job combinations

**Alternatives Considered**:
- OpenAI GPT-4: Similar quality but higher cost ($0.03-0.06/request)
- Ollama (local): Lower quality, inconsistent confidence scores, fails to meet SC-004 target
- Google Gemini Pro: Less consistent reasoning for career analysis tasks

---

### 2. Resume Parsing Libraries

**Decision**: Use `PyPDF2` for PDFs and `python-docx` for Word documents, with fallback to `pdfplumber` for complex PDF layouts.

**Rationale**:
- `PyPDF2`: Lightweight, handles standard PDFs well, MIT licensed
- `python-docx`: Official Microsoft format support, reliable text extraction
- `pdfplumber`: Better table/column handling for complex resume layouts
- Combined approach achieves 95% success rate (SC-003)

**Implementation Pattern**:
```python
import PyPDF2
import pdfplumber
from docx import Document

def extract_text_from_pdf(file_path: str) -> str:
    try:
        # Try PyPDF2 first (faster)
        with open(file_path, 'rb') as file:
            reader = PyPDF2.PdfReader(file)
            text = "\n".join(page.extract_text() for page in reader.pages)
            if len(text.strip()) > 100:  # Sanity check
                return text
    except Exception:
        pass
    
    # Fallback to pdfplumber for complex layouts
    with pdfplumber.open(file_path) as pdf:
        return "\n".join(page.extract_text() for page in pdf.pages)

def extract_text_from_docx(file_path: str) -> str:
    doc = Document(file_path)
    return "\n".join(paragraph.text for paragraph in doc.paragraphs)
```

**Edge Case Handling**:
- Scanned PDFs without OCR: Prompt user for text version (FR-003a)
- Encrypted PDFs: Return error requesting unencrypted version
- Image-based resumes: Use Claude's vision API (future enhancement)

**Alternatives Considered**:
- `textract`: Heavier dependency, requires system libraries
- `Apache Tika`: Java dependency, overkill for this use case
- OCR (Tesseract): Adds complexity, not required for MVP

---

### 3. LangChain + FAISS RAG Pipeline

**Decision**: Use LangChain for document processing and FAISS for vector similarity search on resume/dream job embeddings.

**Rationale**:
- LangChain provides standardized document loaders and text splitters
- FAISS enables fast semantic search for similar career profiles
- sentence-transformers/all-MiniLM-L6-v2 embeddings (384 dimensions) balance quality and speed
- Supports future features like "find users with similar backgrounds"

**Implementation Pattern**:
```python
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.embeddings import HuggingFaceEmbeddings
from langchain.vectorstores import FAISS
from langchain.schema import Document

# Initialize embeddings
embeddings = HuggingFaceEmbeddings(
    model_name="sentence-transformers/all-MiniLM-L6-v2",
    model_kwargs={'device': 'cpu'}
)

# Process resume
text_splitter = RecursiveCharacterTextSplitter(
    chunk_size=512,
    chunk_overlap=50
)
docs = [Document(page_content=resume_text, metadata={"type": "resume"})]
chunks = text_splitter.split_documents(docs)

# Create vector store
vectorstore = FAISS.from_documents(chunks, embeddings)

# Query for similar profiles
results = vectorstore.similarity_search(dream_job_text, k=5)
```

**Vector Store Strategy**:
- Per-user FAISS index for resume + dream job history
- Global index for discovering similar career transitions
- Persist to disk with `vectorstore.save_local()`

**Alternatives Considered**:
- Pinecone/Weaviate: Overkill for MVP, adds external dependency
- ChromaDB: Good alternative, FAISS sufficient for current scale
- Raw numpy cosine similarity: More code, less maintainable

---

### 4. External API Integration (GitHub, Twitter/X, LinkedIn)

**Decision**: Use `httpx` async client with circuit breaker pattern (`circuitbreaker` library) and per-platform rate limiters.

**Rationale**:
- `httpx`: Async support for concurrent API calls, HTTP/2 support
- Circuit breaker: Prevents cascading failures when APIs down (FR-014)
- Per-platform rate limiting: Respects each API's specific limits
- Graceful degradation: Return partial results if one platform fails

**Implementation Pattern**:
```python
import httpx
from circuitbreaker import circuit
from tenacity import retry, stop_after_attempt, wait_exponential

class GitHubClient:
    def __init__(self, api_key: str):
        self.client = httpx.AsyncClient(
            headers={"Authorization": f"token {api_key}"},
            timeout=10.0
        )
        self.rate_limiter = RateLimiter(max_calls=5000, period=3600)  # GitHub: 5k/hour
    
    @circuit(failure_threshold=5, recovery_timeout=60)
    @retry(stop=stop_after_attempt(3), wait=wait_exponential(min=1, max=10))
    async def search_users(self, query: str) -> list:
        await self.rate_limiter.acquire()
        response = await self.client.get(f"/search/users?q={query}")
        response.raise_for_status()
        return response.json()["items"]
```

**API Rate Limits**:
- GitHub: 5,000 requests/hour (authenticated)
- Twitter/X: Varies by endpoint (100-300 requests/15min)
- LinkedIn: Public API limited, use scraping-friendly approach with delays

**Caching Strategy**:
- Cache search results for 24 hours (Redis or in-memory)
- Cache user profiles for 7 days
- Invalidate on user request or stale data detection

**Alternatives Considered**:
- `requests`: Synchronous only, slower for parallel API calls
- `aiohttp`: Good alternative, `httpx` has better API
- Direct scraping: Violates ToS, legal risks

---

### 5. Database Selection for User Profiles & History

**Decision**: PostgreSQL for production, SQLite for development/testing.

**Rationale**:
- PostgreSQL: JSONB support for flexible ally type storage, full-text search for resumes
- SQLite: Zero-config for local dev, pytest fixtures
- SQLAlchemy ORM: Database-agnostic, easy migration
- Alembic: Schema versioning for ally type evolution tracking (FR-013)

**Schema Design**:
```python
from sqlalchemy import Column, Integer, String, JSON, DateTime, Float
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

class UserProfile(Base):
    __tablename__ = "user_profiles"
    id = Column(Integer, primary_key=True)
    user_id = Column(String, unique=True, nullable=False)
    resume_text = Column(String)
    resume_file_path = Column(String)
    created_at = Column(DateTime)

class DreamJobDescription(Base):
    __tablename__ = "dream_jobs"
    id = Column(Integer, primary_key=True)
    user_id = Column(String, nullable=False)
    description = Column(String, nullable=False)
    version = Column(Integer, default=1)  # Track evolution
    created_at = Column(DateTime)

class DeducedAllyType(Base):
    __tablename__ = "ally_types"
    id = Column(Integer, primary_key=True)
    dream_job_id = Column(Integer, nullable=False)
    ally_type_name = Column(String, nullable=False)
    confidence_score = Column(Float, nullable=False)
    rationale = Column(String)  # LLM explanation
    search_queries = Column(JSON)  # Platform-specific queries
    created_at = Column(DateTime)
```

**Alternatives Considered**:
- MongoDB: Schema flexibility not worth losing SQL query power
- Pure file storage: No query capabilities, doesn't scale
- DynamoDB: Overkill for MVP, adds AWS dependency

---

### 6. Prompt Engineering for Ally Type Deduction

**Decision**: Use structured prompts with few-shot examples and chain-of-thought reasoning.

**Rationale**:
- Claude 3 Sonnet excels with detailed instructions and examples
- Few-shot examples improve consistency (3-5 examples per prompt)
- Chain-of-thought elicits confidence scores naturally
- Structured JSON output for reliable parsing

**Prompt Template**:
```python
ALLY_DEDUCTION_PROMPT = """You are a career analysis expert specializing in professional networking strategy.

Your task: Analyze a resume and dream job description, then deduce 3-7 relevant ally types that would help this person achieve their career goals.

For each ally type, provide:
1. Ally type name (concise, professional category)
2. Confidence score (0.0-1.0) reflecting how certain you are this ally type would be beneficial
3. Rationale (2-3 sentences explaining why this ally type is relevant)
4. Search queries (platform-specific keywords for GitHub, Twitter/X, LinkedIn)

Resume:
{resume_text}

Dream Job Description:
{dream_job_text}

Examples:
[Few-shot examples here...]

Think step-by-step:
1. What are the user's current skills and experience?
2. What skills/experience does the dream job require?
3. What gaps exist between current and target?
4. Which professional categories could bridge those gaps?

Output your analysis as JSON:
{{
  "ally_types": [
    {{
      "name": "AI/ML Technical Leaders",
      "confidence": 0.85,
      "rationale": "...",
      "search_queries": {{
        "github": "machine learning author:...",
        "twitter": "#AI #MachineLearning ...",
        "linkedin": "AI Engineer OR ML Engineer"
      }}
    }}
  ]
}}
"""
```

**Few-Shot Examples**:
- Software Engineer → Product Manager (3 examples)
- Backend Developer → DevOps Engineer (2 examples)
- Junior → Senior role transition (2 examples)

**Alternatives Considered**:
- Zero-shot prompting: Less consistent, lower confidence scores
- Fine-tuning Claude: Not available, cost-prohibitive
- Prompt chaining: Adds latency, single prompt sufficient

---

### 7. Async Processing for 30-Second SLA

**Decision**: Use FastAPI background tasks with async/await for LLM calls and external APIs.

**Rationale**:
- FastAPI native async support
- Background tasks for long-running operations (resume parsing + LLM analysis)
- WebSocket or SSE for progress updates to frontend
- Achieves <30s target (SC-002) even with multiple LLM calls

**Implementation Pattern**:
```python
from fastapi import BackgroundTasks, FastAPI
from starlette.responses import StreamingResponse

app = FastAPI()

async def process_resume_and_deduce_allies(
    user_id: str,
    resume_path: str,
    dream_job: str
):
    # 1. Parse resume (2-5s)
    resume_text = await parse_resume(resume_path)
    
    # 2. Call Claude for ally deduction (10-20s)
    ally_types = await llm_service.deduce_ally_types(resume_text, dream_job)
    
    # 3. Store results
    await db.save_ally_types(user_id, ally_types)
    
    # 4. Notify frontend via WebSocket
    await websocket_manager.send_update(user_id, ally_types)

@app.post("/api/analyze")
async def analyze_resume(
    resume: UploadFile,
    dream_job: str,
    background_tasks: BackgroundTasks
):
    user_id = get_current_user_id()
    resume_path = await save_upload(resume)
    
    # Start background task
    background_tasks.add_task(
        process_resume_and_deduce_allies,
        user_id,
        resume_path,
        dream_job
    )
    
    return {"status": "processing", "user_id": user_id}
```

**Progress Tracking**:
- WebSocket connection for real-time updates
- Fallback to polling endpoint for progress status
- Store intermediate results for fault tolerance

**Alternatives Considered**:
- Celery: Adds Redis/RabbitMQ dependency, overkill for MVP
- Synchronous blocking: Would timeout, poor UX
- AWS Lambda: Adds cloud dependency, 15min timeout sufficient but unnecessary

---

## Technology Stack Summary

| Component | Technology | Version | Justification |
|-----------|-----------|---------|---------------|
| Language | Python | 3.12 | Constitution requirement, async support |
| Backend Framework | FastAPI | 0.104+ | Async, OpenAPI, WebSocket support |
| LLM | Claude 3 Sonnet | API | Superior reasoning, 85% relevance target |
| LLM SDK | anthropic | 0.8+ | Official Anthropic Python SDK |
| Vector Store | FAISS | faiss-cpu 1.7+ | Fast similarity search, CPU-only sufficient |
| Embeddings | HuggingFace | sentence-transformers | 384-dim, quality/speed balance |
| LangChain | LangChain + Community | 0.1+ | Document processing, RAG patterns |
| PDF Parsing | PyPDF2 + pdfplumber | latest | 95% success rate, fallback strategy |
| Word Parsing | python-docx | 1.0+ | Official Microsoft format support |
| HTTP Client | httpx | 0.25+ | Async, HTTP/2 support |
| Database | PostgreSQL (prod), SQLite (dev) | 15+, 3.40+ | JSONB, full-text search, easy dev setup |
| ORM | SQLAlchemy | 2.0+ | Database-agnostic, modern API |
| Rate Limiting | tenacity + custom | 8.2+ | Exponential backoff, configurable |
| Circuit Breaker | circuitbreaker | 1.4+ | API resilience |
| Testing | pytest + pytest-asyncio | 7.4+, 0.21+ | Async test support |
| Frontend | React/Next.js | 18+/14+ | Professional UI, SSR support |

---

## Implementation Phases

### Phase 0: Research (Complete)
✅ All technical decisions documented above

### Phase 1: Design & Contracts (Next)
- Generate data-model.md with entities from spec
- Create OpenAPI contracts for resume analysis, ally deduction, discovery endpoints
- Generate quickstart.md for local development setup
- Update agent context with new technologies

### Phase 2: Task Breakdown (After Phase 1)
- Will be generated by `/speckit.tasks` command
- Organized by user story (P1, P2, P3, P4)
- Foundation tasks → US1 → US2 → US3 → US4

---

## Risk Mitigation

### Risk: Claude API rate limits exceed budget
**Mitigation**: 
- Implement aggressive caching (24h for identical inputs)
- Use GPT-3.5 Turbo fallback for non-critical operations
- Monitor costs daily, alert at $100/day threshold

### Risk: Resume parsing fails for 5%+ of uploads
**Mitigation**:
- Multi-library fallback strategy (PyPDF2 → pdfplumber)
- Manual text input fallback (FR-003a)
- Store failed resumes for future OCR processing

### Risk: External APIs (GitHub/Twitter/LinkedIn) frequently unavailable
**Mitigation**:
- Circuit breaker pattern isolates failures
- Degrade gracefully (partial results from available platforms)
- Cache results for 7 days to reduce API dependency

### Risk: 30-second SLA not achievable with LLM latency
**Mitigation**:
- Optimize prompts to reduce token count
- Use Claude Instant for initial analysis, Sonnet for refinement
- Implement streaming responses for perceived performance

---

## Next Steps

1. ✅ Constitution Check: PASSED
2. 🔄 Generate data-model.md from Key Entities in spec
3. 🔄 Create OpenAPI contracts for all API endpoints
4. 🔄 Generate quickstart.md for developer onboarding
5. 🔄 Update agent context with new dependencies
6. ⏳ Re-check Constitution compliance after design phase
7. ⏳ Proceed to Phase 2: Task breakdown with `/speckit.tasks`
