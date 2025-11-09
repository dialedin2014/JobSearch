# Implementation Plan: Dream Job Ally Deduction

**Branch**: `002-dream-job-ally-deduction` | **Date**: 2025-10-26 | **Spec**: [../002-dream-job-ally-deduction/spec.md](../002-dream-job-ally-deduction/spec.md)
**Input**: Feature specification from `/specs/002-dream-job-ally-deduction/spec.md`

**Note**: This template is filled in by the `/speckit.plan` command. See `.specify/templates/commands/plan.md` for the execution workflow.

## Summary

Enable job seekers to automatically discover relevant professional allies by analyzing their resume and dream job description using Claude Sonnet 4.5 LLM. The system will deduce appropriate ally types (e.g., "AI/ML Technical Leaders", "Career Transition Mentors"), generate platform-specific search queries, and discover matching professionals across GitHub, Twitter/X, and LinkedIn. Core technical approach: LangChain + FAISS RAG pipeline for document processing, Claude Sonnet 4.5 (Anthropic API) for ally type deduction and search query generation, FastAPI backend with React frontend for web interface.

## Technical Context

**Language/Version**: Python 3.12  
**Primary Dependencies**: FastAPI, LangChain, LangChain Community, anthropic (Claude Sonnet 4.5 API), FAISS (faiss-cpu), Hugging Face Transformers (sentence-transformers/all-MiniLM-L6-v2), PyPDF2 or pdfplumber (PDF parsing), python-docx (Word parsing), httpx (async HTTP client)  
**Storage**: FAISS vector store for resume/job description embeddings, local file storage for uploaded resumes, PostgreSQL or SQLite for user profiles and ally type history  
**Testing**: pytest for unit/integration tests, pytest-asyncio for async testing, pylint for code quality  
**Target Platform**: Linux server (containerized), web browser clients  
**Project Type**: Web application (FastAPI backend + React/Next.js frontend)  
**Performance Goals**: Resume parsing <5s, ally type deduction <30s (per SC-002), dream job updates <15s (per SC-009), handle concurrent uploads from 100+ users  
**Constraints**: Claude Sonnet 4.5 API rate limits (tier-dependent), <200ms p95 for API responses (excluding LLM calls), cost management for LLM API calls (~$0.01-0.03 per analysis)  
**Scale/Scope**: 10k users initially, 1k daily resume uploads, 5k daily ally discovery requests, support PDF/Word/text resume formats up to 10MB

## Constitution Check

_GATE: Must pass before Phase 0 research. Re-check after Phase 1 design._

- [x] **RAG-First AI Architecture**: Feature uses LangChain + FAISS + Claude Sonnet 4.5 (Anthropic API) for resume/dream job analysis and ally type deduction with vector embeddings
- [x] **Privacy & Ethical Data Use**: Only public APIs (GitHub, Twitter/X, LinkedIn) with ToS compliance, ethical prompts for ally recommendations, user consent for resume upload
- [x] **Container-Native Development**: .devcontainer.json with Python 3.12, requirements.txt with pinned versions, Docker deployment
- [x] **Priority-Driven Feature Development**: 4 user stories (P1: Resume/Dream Job Analysis, P2: Ally Discovery, P3: Gap Analysis, P4: Goal Refinement) with independent testability
- [x] **API Rate Limiting & Resilience**: Anthropic API rate limiting, exponential backoff for GitHub/Twitter/LinkedIn APIs, circuit breakers, caching for repeated queries

**Gate Status**: ✅ PASSED - All constitutional principles satisfied

## Project Structure

### Documentation (this feature)

```text
specs/002-dream-job-ally-deduction/
├── spec.md              # Feature specification (existing)
├── plan.md              # This file (/speckit.plan command output)
├── research.md          # Phase 0 output (/speckit.plan command)
├── data-model.md        # Phase 1 output (/speckit.plan command)
├── quickstart.md        # Phase 1 output (/speckit.plan command)
├── contracts/           # Phase 1 output (/speckit.plan command)
│   ├── resume-analysis.yaml
│   ├── ally-deduction.yaml
│   └── ally-discovery.yaml
└── tasks.md             # Phase 2 output (/speckit.tasks command - NOT created by /speckit.plan)
```

### Source Code (repository root)

```text
backend/
├── src/
│   ├── models/
│   │   ├── user_profile.py
│   │   ├── resume.py
│   │   ├── dream_job.py
│   │   ├── ally_type.py
│   │   └── professional_ally.py
│   ├── services/
│   │   ├── resume_parser.py
│   │   ├── llm_service.py           # Claude Sonnet 4.5 integration
│   │   ├── ally_deduction.py
│   │   ├── ally_discovery.py
│   │   ├── gap_analysis.py
│   │   └── search_query_generator.py
│   ├── api/
│   │   ├── routes/
│   │   │   ├── resume.py
│   │   │   ├── dream_job.py
│   │   │   ├── ally_types.py
│   │   │   └── discovery.py
│   │   └── dependencies/
│   │       ├── auth.py
│   │       └── llm.py
│   ├── core/
│   │   ├── config.py
│   │   ├── security.py
│   │   └── rate_limiter.py
│   └── integrations/
│       ├── anthropic_client.py
│       ├── github_client.py
│       ├── twitter_client.py
│       └── linkedin_client.py
├── tests/
│   ├── contract/
│   │   ├── test_resume_api.py
│   │   └── test_ally_deduction_api.py
│   ├── integration/
│   │   ├── test_resume_to_ally_flow.py
│   │   └── test_llm_integration.py
│   └── unit/
│       ├── test_resume_parser.py
│       ├── test_ally_deduction.py
│       └── test_gap_analysis.py
└── requirements.txt

frontend/
├── src/
│   ├── components/
│   │   ├── ResumeUpload.tsx
│   │   ├── DreamJobForm.tsx
│   │   ├── AllyTypesList.tsx
│   │   └── AllyDiscoveryResults.tsx
│   ├── pages/
│   │   ├── index.tsx
│   │   ├── analysis.tsx
│   │   └── discovery.tsx
│   ├── services/
│   │   └── api.ts
│   └── utils/
│       └── validation.ts
├── tests/
│   └── components/
│       ├── ResumeUpload.test.tsx
│       └── AllyTypesList.test.tsx
├── package.json
└── next.config.js
```

**Structure Decision**: Web application structure selected - FastAPI backend handles LLM integration, document parsing, and external API orchestration; React/Next.js frontend provides professional UI for resume upload, dream job input, and ally discovery visualization. This separation enables independent scaling of compute-intensive backend vs. user-facing frontend.

## Complexity Tracking

> **Fill ONLY if Constitution Check has violations that must be justified**

No violations - All constitutional principles satisfied. No complexity justification required.

---

## Phase Completion Summary

### Phase 0: Research ✅ COMPLETE

All technical unknowns resolved and documented in `research.md`:

- ✅ Claude Sonnet 4.5 integration strategy with Anthropic SDK
- ✅ Resume parsing approach (PyPDF2 + pdfplumber fallback)
- ✅ LangChain + FAISS RAG pipeline architecture
- ✅ External API integration patterns (httpx + circuit breakers)
- ✅ Database selection (PostgreSQL/SQLite)
- ✅ Prompt engineering for ally deduction
- ✅ Async processing strategy for 30s SLA

### Phase 1: Design & Contracts ✅ COMPLETE

All design artifacts generated:

- ✅ `data-model.md` - Complete entity definitions with SQLAlchemy models
- ✅ `contracts/resume-analysis.yaml` - Resume upload and parsing API
- ✅ `contracts/ally-deduction.yaml` - Ally type deduction and dream job API
- ✅ `contracts/ally-discovery.yaml` - Professional ally discovery API
- ✅ `quickstart.md` - Local development setup guide
- ✅ Agent context updated - GitHub Copilot instructions with new tech stack

### Constitution Re-Check ✅ PASSED

Post-design validation confirms all constitutional principles satisfied:

- ✅ RAG-First AI Architecture maintained throughout design
- ✅ Privacy & Ethical Data Use enforced in all APIs
- ✅ Container-Native Development properly configured
- ✅ Priority-Driven Feature Development with 4 independent user stories
- ✅ API Rate Limiting & Resilience built into all external integrations

### Artifacts Generated

```
specs/PlanningPhase/
├── plan.md ✅           # This file - implementation roadmap
├── research.md ✅       # Technical decisions and best practices
├── data-model.md ✅     # Database schema and entity relationships
├── quickstart.md ✅     # Developer onboarding guide
└── contracts/ ✅        # OpenAPI specifications
    ├── resume-analysis.yaml
    ├── ally-deduction.yaml
    └── ally-discovery.yaml

.github/
└── copilot-instructions.md ✅  # Updated with Python 3.12 + Claude Sonnet 4.5 stack
```

### Key Decisions Made

1. **LLM Provider**: Claude Sonnet 4.5 (Anthropic API) selected over Ollama for superior reasoning quality
2. **Architecture**: Web application (FastAPI + React/Next.js) for professional UI and API separation
3. **Database**: PostgreSQL for production, SQLite for development
4. **Resume Parsing**: Multi-library fallback strategy (PyPDF2 → pdfplumber)
5. **Vector Search**: FAISS with sentence-transformers embeddings
6. **API Integration**: httpx async client with circuit breaker pattern

### Next Steps

**Phase 2: Task Breakdown** - Run `/speckit.tasks` command to generate detailed implementation tasks organized by user story priority (P1, P2, P3, P4).

Expected task structure:

1. **Phase 1: Setup** (T001-T007) - Project initialization, dependencies
2. **Phase 2: Foundation** (T008-T013) - RAG pipeline, LLM integration, API clients
3. **Phase 3: User Story 1 (P1)** - Resume analysis & ally type deduction (MVP)
4. **Phase 4: User Story 2 (P2)** - Professional ally discovery
5. **Phase 5: User Story 3 (P3)** - Career gap analysis & transition strategy
6. **Phase 6: User Story 4 (P4)** - Dream job evolution tracking

### Success Criteria Alignment

All 12 success criteria from spec are achievable with this design:

- **SC-002**: 30s ally deduction ✅ (async processing with WebSocket updates)
- **SC-003**: 95% parsing success ✅ (multi-library fallback strategy)
- **SC-004**: 85% relevance rating ✅ (Claude 3 Sonnet reasoning quality)
- **SC-007**: 85% gap analysis accuracy ✅ (structured prompts with chain-of-thought)
- **SC-012**: 99% uptime ✅ (circuit breakers, graceful degradation, caching)

---

## Report

**Branch**: `002-dream-job-ally-deduction` (or `PlanningPhase` for current working branch)  
**Implementation Plan**: `D:\src\git\gh\di\JobSearch\specs\PlanningPhase\plan.md`

**Generated Artifacts**:

- ✅ `research.md` - 7 research areas with technical decisions
- ✅ `data-model.md` - 10 entities with complete SQLAlchemy models
- ✅ `quickstart.md` - Complete local development guide
- ✅ `contracts/` - 3 OpenAPI specifications (resume, ally-deduction, ally-discovery)
- ✅ Agent context updated - GitHub Copilot with Python 3.12 + Claude 3 Sonnet

**Status**: Phase 0 & 1 complete. Ready for Phase 2 task generation with `/speckit.tasks`.

**Constitution Compliance**: ✅ All principles satisfied, no violations to justify.
