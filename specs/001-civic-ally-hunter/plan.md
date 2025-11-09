# Implementation Plan: Professional Ally-Hunting Platform

**Feature**: 001-civic-ally-hunter  
**Created**: November 8, 2025  
**Constitution Version**: 2.0.0

## Constitution Compliance Check

✅ **I. RAG-First AI Architecture**: LangChain + Claude 3 Sonnet (Anthropic API) + FAISS vector search  
✅ **II. Privacy & Ethical Data Use**: Public APIs only, explicit ToS compliance, rate limiting  
✅ **III. Container-Native Development**: Dev Container with Python 3.12, pinned dependencies  
✅ **IV. Priority-Driven Feature Development**: P1-P4 user stories with acceptance scenarios  
✅ **V. API Rate Limiting & Resilience**: Circuit breakers, exponential backoff, caching for all external APIs  

⚠️ **Constitution Correction**: Spec references "Ollama with Llama3" but Constitution v2.0.0 mandates Claude 3 Sonnet (Anthropic API). This plan uses Claude 3 Sonnet.

## Architecture Overview

### System Components

```
┌─────────────────────────────────────────────────────────────┐
│                     Frontend (Next.js)                       │
│  - Resume Upload UI      - Ally Type Manager                │
│  - Search Interface      - Network Graph Visualizer         │
│  - Bridge Pitch Editor   - Export Dashboard                 │
└─────────────────┬───────────────────────────────────────────┘
                  │ REST API
┌─────────────────▼───────────────────────────────────────────┐
│               Backend (FastAPI + Python 3.12)               │
│                                                              │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐     │
│  │ Resume       │  │ Ally Type    │  │ Search       │     │
│  │ Parser       │  │ Manager      │  │ Orchestrator │     │
│  └──────────────┘  └──────────────┘  └──────────────┘     │
│                                                              │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐     │
│  │ Shadow       │  │ Bridge Pitch │  │ Network      │     │
│  │ Sequence Gen │  │ Generator    │  │ Mapper       │     │
│  └──────────────┘  └──────────────┘  └──────────────┘     │
└─────────────────┬───────────────────────────────────────────┘
                  │
┌─────────────────▼───────────────────────────────────────────┐
│                  Data & Integration Layer                    │
│                                                              │
│  ┌─────────────────┐  ┌─────────────────┐                  │
│  │ LangChain RAG   │  │ FAISS Vector DB │                  │
│  │ Pipeline        │  │ (Resume + Posts) │                  │
│  │ (Claude 3       │  │                 │                  │
│  │  Sonnet API)    │  │                 │                  │
│  └─────────────────┘  └─────────────────┘                  │
│                                                              │
│  ┌─────────────────────────────────────────────────────┐   │
│  │          External API Clients (Rate-Limited)        │   │
│  │  - GitHub API   - Twitter/X API                      │   │
│  │  - LinkedIn API - Apollo API                         │   │
│  │  (Circuit breakers, exponential backoff, caching)   │   │
│  └─────────────────────────────────────────────────────┘   │
│                                                              │
│  ┌─────────────────┐  ┌─────────────────┐                  │
│  │ PostgreSQL      │  │ File Storage    │                  │
│  │ (User/Ally Data)│  │ (Resume PDFs)   │                  │
│  └─────────────────┘  └─────────────────┘                  │
└──────────────────────────────────────────────────────────────┘
```

### Technology Stack

**Backend**:
- Python 3.12 (constitutional requirement)
- FastAPI 0.104+ for REST API
- LangChain 0.1.0+ for RAG orchestration
- LangChain Community 0.1.0+ for integrations
- anthropic 0.8.1+ for Claude 3 Sonnet API
- FAISS (faiss-cpu 1.7.4+) for vector search
- sentence-transformers 2.2.2+ (all-MiniLM-L6-v2 model, 384-dim embeddings)
- SQLAlchemy 2.0+ for ORM
- Alembic 1.13+ for migrations
- PyPDF2 3.0+ for resume parsing
- python-docx 1.1+ for Word documents
- httpx 0.25+ for async HTTP clients
- circuitbreaker 1.4+ for resilience
- tenacity 8.2+ for retry logic
- NetworkX 3.2+ for graph analysis
- redis 5.0+ for caching
- bcrypt 4.1+ for password hashing
- python-jose 3.3+ for JWT authentication

**Frontend**:
- Next.js 14.0+ with React 18
- TypeScript 5.3+
- Recharts or D3.js for network visualization
- Tailwind CSS 3.3+ for styling

**Infrastructure**:
- PostgreSQL 15+ (production)
- SQLite (development)
- Docker + Docker Compose
- VS Code Dev Container

**External APIs**:
- Anthropic API (Claude 3 Sonnet: claude-3-sonnet-20240229)
- GitHub API v3 (5000 req/hour authenticated)
- Twitter/X API v2 (300 req/15min basic tier)
- LinkedIn public endpoints (limited, may require manual URL input)
- Apollo API (contact enrichment, rate limits TBD)

## Data Model

### Core Entities

#### UserProfile
```python
class UserProfile(Base):
    id: UUID (PK)
    user_id: str (indexed, unique)
    email: str (indexed, unique)
    password_hash: str # bcrypt hashed
    resume_file_path: str
    parsed_resume_id: UUID (FK → ParsedResume)
    created_at: datetime
    updated_at: datetime
    # Relationships
    ally_types: List[AllyType]
    search_queries: List[SearchQuery]
```

#### ParsedResume
```python
class ParsedResume(Base):
    id: UUID (PK)
    user_profile_id: UUID (FK)
    raw_text: str (Text)
    skills: List[str] (JSON)
    achievements: List[str] (JSON)
    work_history: List[dict] (JSON)
      # [{company, title, start_date, end_date, description}]
    education: List[dict] (JSON)
      # [{institution, degree, field, graduation_year}]
    companies: List[str] (JSON) # Extracted for network mapping
    keywords: List[str] (JSON) # Extracted for matching
    parsing_confidence: float (0-1)
    parsed_at: datetime
    parser_version: str
```

#### AllyType
```python
class AllyType(Base):
    id: UUID (PK)
    user_profile_id: UUID (FK)
    name: str # "AI Researchers", "Fintech Investors"
    keywords: List[str] (JSON)
    criteria: str (Text) # User-defined criteria
    search_parameters: dict (JSON) # Platform filters
    created_at: datetime
    is_active: bool
    # Relationships
    contacts: List[Contact]
```

#### Contact
```python
class Contact(Base):
    id: UUID (PK)
    ally_type_id: UUID (FK, nullable) # Matched ally type
    name: str
    title: str (nullable)
    company: str (nullable)
    location: str (nullable)
    email: str (nullable)
    phone: str (nullable)
    github_url: str (nullable)
    twitter_url: str (nullable)
    linkedin_url: str (nullable)
    relevance_score: float (0-1)
    matched_keywords: List[str] (JSON)
    source_platform: str # "github", "twitter", "linkedin"
    profile_data: dict (JSON) # Platform-specific data
    enrichment_data: dict (JSON) # Apollo API data
    created_at: datetime
    last_updated: datetime
```

#### Content
```python
class Content(Base):
    id: UUID (PK)
    contact_id: UUID (FK)
    text: str (Text)
    source_platform: str
    url: str
    metadata: dict (JSON) # Platform-specific
    posted_at: datetime (nullable)
    embedding_vector: bytes # FAISS vector (384 dims)
    ally_type_classification: List[str] (JSON) # Matched ally types
    created_at: datetime
```

#### Organization
```python
class Organization(Base):
    id: UUID (PK)
    name: str (indexed)
    domain: str (nullable)
    revenue: int (nullable)
    employee_count: int (nullable)
    technologies: List[str] (JSON, nullable)
    industry: str (nullable)
    ally_type_relevance: dict (JSON) # {ally_type_id: score}
    created_at: datetime
    # Relationships
    contacts: List[Contact]
```

#### NetworkConnection
```python
class NetworkConnection(Base):
    id: UUID (PK)
    user_profile_id: UUID (FK)
    source_contact_id: UUID (FK) # User's resume contact
    target_contact_id: UUID (FK) # Ally search result
    connection_type: str # "alumni", "employer", "investor", "conference"
    shared_organizations: List[str] (JSON)
    connection_strength: float (0-1)
    path_metadata: dict (JSON) # Graph path details
    created_at: datetime
```

#### SearchQuery
```python
class SearchQuery(Base):
    id: UUID (PK)
    user_profile_id: UUID (FK)
    original_query: str
    ally_type_filters: List[UUID] (JSON) # FK to AllyType
    counter_queries: List[str] (JSON) # Shadow sequences
    results_count: int
    executed_at: datetime
    # Relationships
    results: List[Contact]
```

#### BridgePitch
```python
class BridgePitch(Base):
    id: UUID (PK)
    user_profile_id: UUID (FK)
    target_contact_id: UUID (FK)
    resume_achievements_referenced: List[str] (JSON)
    ally_type_context: str
    generated_message: str (Text)
    collaboration_proposal: str (Text)
    llm_model: str # "claude-3-sonnet-20240229"
    llm_prompt_version: str
    created_at: datetime
```

### FAISS Vector Indices

**Resume Index**: One vector per resume (aggregated from all sections)  
**Content Index**: One vector per post/issue/thread  
**Ally Type Index**: One vector per ally type definition (from keywords + criteria)

## Implementation Phases

### Phase 1: Foundation & Resume Processing (P1 - MVP Core)

**User Story 1 Support**: Profile Setup and Ally Type Configuration

**Tasks**:
1. Project setup (Dev Container, requirements.txt, FastAPI scaffold)
2. Database schema implementation (Alembic migrations)
3. Resume upload endpoint (multipart/form-data, 10MB limit)
4. Resume parser service (PyPDF2 + python-docx):
   - Extract text, skills, achievements, work history
   - Calculate parsing confidence (0-1 based on extraction success)
   - Store in PostgreSQL + generate FAISS embedding
5. Ally type CRUD API:
   - POST /ally-types (create with keywords)
   - GET /ally-types (list user's types)
   - PUT /ally-types/{id} (update)
   - DELETE /ally-types/{id}
6. FAISS vector store initialization:
   - Index resumes by user
   - Index ally types for semantic matching

**Deliverables**:
- Backend API endpoints for resume + ally types
- Resume parsing with 95% success rate (SC-004)
- Vector indexing operational
- Basic Next.js UI for upload + ally type management

**Testing**: Upload resume → verify parsed fields → define ally types → verify storage

---

### Phase 2: Multi-Platform Search Integration (P1 Continuation)

**User Story 1 Support**: Semantic search across platforms

**Tasks**:
1. External API client implementations:
   - GitHub API client (search users, issues, with rate limiting)
   - Twitter/X API client (search tweets, with 15min window limits)
   - LinkedIn scraper (public profiles, ToS-compliant, minimal)
   - Apollo API client (contact enrichment)
2. Rate limiter service:
   - Token bucket algorithm per API
   - Circuit breaker pattern (failure_threshold=5, recovery_timeout=60s)
   - Exponential backoff (1-10s delays)
3. Search orchestrator service:
   - Accept query + ally type filters
   - Fan-out to GitHub/Twitter/LinkedIn in parallel
   - Aggregate results with relevance scoring (0-1)
   - Filter by ally type keywords
4. Content indexing pipeline:
   - Fetch posts/issues from APIs
   - Generate embeddings (sentence-transformers)
   - Store in FAISS + PostgreSQL
5. Search API endpoint:
   - POST /search (query, ally_type_ids) → List[Contact]
   - GET /search/{query_id}/results (pagination)

**Deliverables**:
- Multi-platform search functional
- Relevance scoring ≥0.7 for matched ally types (SC-003: 80% accuracy target)
- Rate limiting preventing API bans
- Search completes within 30s (SC-002)

**Testing**: Search "machine learning" with "AI researchers" ally type → verify GitHub/Twitter/LinkedIn results → verify relevance scores

---

### Phase 3: Shadow Sequence Amplifier (P2)

**User Story 2 Support**: Counter-query generation + bridge pitches

**Tasks**:
1. LangChain setup:
   - Configure Anthropic API client (Claude 3 Sonnet)
   - Implement RAG chain for counter-query generation
   - System prompt: "Generate opposing viewpoints to: {query} within context of {ally_type}"
2. Shadow sequence generator service:
   - Input: original query + ally types
   - LLM call to generate 3-5 counter-arguments
   - Validate output quality (meaningfully different? SC-010: 90% target)
   - Store counter-queries in SearchQuery.counter_queries
3. Counter-query search execution:
   - Execute searches for each counter-query
   - Tag results as "skeptic" perspective
   - Merge with original results (deduplicate)
4. Bridge pitch generator service:
   - Input: target Contact + user ParsedResume
   - LLM prompt: "Create outreach message acknowledging {target_concerns} while highlighting {resume_achievements}"
   - Validate resume achievement references (SC-005: 100% inclusion)
   - Store in BridgePitch table
5. Bridge pitch API:
   - POST /bridge-pitches (contact_id) → BridgePitch
   - GET /bridge-pitches/{id}

**Deliverables**:
- Counter-query generation operational (90% quality, SC-010)
- Bridge pitches reference resume achievements (100%, SC-005)
- Claude 3 Sonnet integration with cost tracking

**Testing**: Search "ML optimization" → generate counter-queries → verify "AI bias concerns" result → generate bridge pitch → verify resume achievement reference

---

### Phase 4: Organization Network Mapping (P3)

**User Story 3 Support**: Visualize connection paths

**Tasks**:
1. Organization data extraction:
   - Parse companies from resume work history
   - Fetch organization data from Apollo API
   - Store in Organization table
2. Network graph builder service:
   - Extract user's professional network (resume companies)
   - Build graph: nodes = people/orgs, edges = relationships
   - Calculate connection paths (NetworkX shortest_path)
   - Assign connection strength (0-1 based on recency, shared time)
3. Network connection discovery:
   - Match user's companies to target contact's companies
   - Identify alumni networks, investor overlaps, acquisition paths
   - Store in NetworkConnection table
4. Network visualization API:
   - GET /network-map (user_id, target_contact_id) → Graph JSON
   - Format: nodes, edges, path metadata
5. Frontend graph visualization:
   - D3.js or Recharts network diagram
   - Interactive: click path → show connection details
   - Warm intro suggestions

**Deliverables**:
- Network mapping identifies connections (60% success rate, SC-006)
- Graph visualization functional
- Warm intro suggestions generated

**Testing**: Resume with "Microsoft" → target at "Google" → verify ex-Microsoft alumni path → verify warm intro suggestion

---

### Phase 5: Outreach Template Generator (P4)

**User Story 4 Support**: Personalized outreach messages

**Tasks**:
1. Outreach template generator service:
   - Input: Contact + target's Content (posts/issues)
   - LLM prompt: "Match {resume_achievements} to {target_interests} and create collaboration proposal"
   - Validate: authentic connection, not generic (manual review)
   - Store in BridgePitch (extended for outreach templates)
2. Template customization API:
   - POST /outreach-templates (contact_id) → Template
   - GET /outreach-templates/{id}
   - PUT /outreach-templates/{id} (user edits)
3. Export functionality:
   - GET /export/search-results/{query_id} (markdown)
   - GET /export/network-map/{user_id} (markdown + PNG)
   - GET /export/outreach-templates (markdown)
   - Deliver within 10s for 50 results (SC-009)

**Deliverables**:
- Outreach templates generated with resume-target matching
- Export functionality operational (10s for 50 results, SC-009)

**Testing**: Generate template for "AI researcher" posting about CNNs → verify user's CNN achievement referenced → verify collaboration proposal

---

### Phase 6: Polish & Production Readiness

**Tasks**:
1. Frontend UI polish:
   - Responsive design (mobile-friendly)
   - Loading states, error handling
   - User onboarding flow (SC-001: 5min to upload + define ally types)
2. Performance optimization:
   - Query caching (Redis)
   - FAISS index optimization
   - Database query optimization
3. Security hardening:
   - API key encryption
   - HTTPS enforcement
   - Input validation and sanitization
4. Monitoring & logging:
   - API usage tracking
   - Cost estimation (Anthropic API)
   - Error rate dashboards
5. Documentation:
   - API documentation (OpenAPI/Swagger)
   - User guide
   - Deployment guide

**Deliverables**:
- 99.5% uptime (SC-008)
- Production-ready deployment

---

## API Design

### Core Endpoints

#### Authentication
```
POST   /api/v1/auth/register           # Register new user
POST   /api/v1/auth/login              # Login and get JWT token
POST   /api/v1/auth/refresh            # Refresh JWT token
GET    /api/v1/auth/me                 # Get current user profile
```

#### Resume Management
```
POST   /api/v1/resumes/upload          # Upload resume file
GET    /api/v1/resumes/{id}            # Get parsed resume
GET    /api/v1/resumes/{id}/embedding  # Get FAISS vector
```

#### Ally Type Management
```
POST   /api/v1/ally-types              # Create ally type
GET    /api/v1/ally-types              # List user's ally types
GET    /api/v1/ally-types/{id}         # Get specific ally type
PUT    /api/v1/ally-types/{id}         # Update ally type
DELETE /api/v1/ally-types/{id}         # Delete ally type
GET    /api/v1/ally-types/export       # Export ally types as JSON
POST   /api/v1/ally-types/import       # Import ally types from JSON
```

#### Search
```
POST   /api/v1/search                  # Execute search with ally filters
GET    /api/v1/search/{query_id}       # Get search results (paginated)
POST   /api/v1/search/counter-queries  # Generate shadow sequences
```

#### Shadow Sequence & Bridge Pitches
```
POST   /api/v1/bridge-pitches          # Generate bridge pitch for contact
GET    /api/v1/bridge-pitches/{id}     # Get bridge pitch
GET    /api/v1/bridge-pitches          # List user's bridge pitches
```

#### Network Mapping
```
GET    /api/v1/network-map             # Get network graph (user → targets)
GET    /api/v1/network-map/connections # Get connection details
```

#### Outreach Templates
```
POST   /api/v1/outreach-templates      # Generate outreach message
GET    /api/v1/outreach-templates/{id} # Get template
PUT    /api/v1/outreach-templates/{id} # Edit template
```

#### Export
```
GET    /api/v1/export/search/{query_id}      # Export search results (markdown)
GET    /api/v1/export/network-map/{user_id}  # Export network graph
GET    /api/v1/export/outreach-templates     # Export all templates
```

## Risk Mitigation

### Technical Risks

| Risk | Likelihood | Impact | Mitigation |
|------|-----------|--------|------------|
| LinkedIn API rate limits | High | High | Implement aggressive caching, fallback to manual URL input, use Apollo API for enrichment |
| Resume parsing accuracy <95% | Medium | Medium | Multi-parser strategy (PyPDF2 → pdfplumber fallback), confidence scoring, manual review option |
| Claude 3 Sonnet API costs exceed budget | Medium | Medium | Implement response caching (24hr TTL), prompt optimization, usage caps per user |
| FAISS index performance degrades at scale | Low | Medium | Implement index sharding by user, periodic index optimization, consider Pinecone for production |
| Network mapping finds no connections (>40% cases) | Medium | Low | Provide alternative strategies (events, associations), expand org data sources |
| Counter-query quality <90% | Medium | Medium | Implement quality scoring, LLM prompt refinement, manual review option |

### Compliance Risks

| Risk | Mitigation |
|------|------------|
| LinkedIn ToS violation | Use only public endpoints, respect robots.txt, implement user-agent identification, consider manual URL input |
| GitHub API abuse | Implement strict rate limiting (5000/hr), cache aggressively, exponential backoff |
| Twitter API tier limits | Cache tweets for 24hrs, prioritize recent content, graceful degradation if quota exceeded |
| GDPR/CCPA compliance for contact data | Store only public data, provide data deletion, clear privacy policy, user consent for contact enrichment |

## Testing Strategy

### Unit Tests
- Resume parser (95% extraction accuracy)
- Ally type matching logic
- LLM prompt construction
- Network graph algorithms

### Integration Tests
- Multi-platform search orchestration
- FAISS vector search accuracy
- API rate limiting enforcement
- Database transactions

### Acceptance Tests
- User Story 1: Upload resume → define ally types → search → verify relevance ≥0.7
- User Story 2: Generate counter-queries → verify 90% quality → generate bridge pitch → verify resume references
- User Story 3: Network mapping → verify connection path → verify warm intro suggestion
- User Story 4: Generate outreach template → verify resume-target matching

### Performance Tests
- Search completion <30s (SC-002)
- Export <10s for 50 results (SC-009)
- Resume upload + parsing <5min (SC-001)

## Deployment Strategy

**Development**: Docker Compose (PostgreSQL + Backend + Frontend)  
**Staging**: Cloud platform (Heroku/Render/Railway) with PostgreSQL add-on  
**Production**: Cloud platform with:
- Load balancer
- Auto-scaling (2-10 instances)
- Managed PostgreSQL
- Redis cache
- CloudFlare CDN

**Environment Variables**:
```
ANTHROPIC_API_KEY=<secret>
GITHUB_API_TOKEN=<secret>
TWITTER_API_KEY=<secret>
TWITTER_API_SECRET=<secret>
APOLLO_API_KEY=<secret>
DATABASE_URL=postgresql://...
REDIS_URL=redis://...
SECRET_KEY=<secret>
JWT_SECRET_KEY=<secret>
JWT_ALGORITHM=HS256
ENVIRONMENT=production
```

## Success Metrics Dashboard

Track against Success Criteria:
- **SC-001**: Time to first search (target: <5min)
- **SC-002**: Search response time (target: <30s)
- **SC-003**: Relevance rating (target: ≥80%)
- **SC-004**: Resume parsing success (target: ≥95%)
- **SC-005**: Bridge pitch quality (target: 100% resume references)
- **SC-006**: Network connection discovery (target: ≥60%)
- **SC-007**: Multi-platform indexing (target: 100%)
- **SC-008**: Uptime (target: ≥99.5%)
- **SC-009**: Export speed (target: <10s)
- **SC-010**: Counter-query quality (target: ≥90%)

**Monitoring**:
- Anthropic API cost per user
- API rate limit violations
- Search result quality (user ratings)
- Network mapping success rate
