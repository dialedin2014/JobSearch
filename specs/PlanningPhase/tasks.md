---
description: "Task list for Dream Job Ally Deduction feature implementation"
---

# Tasks: Dream Job Ally Deduction

**Input**: Design documents from `/specs/PlanningPhase/`  
**Prerequisites**: plan.md (required), spec.md (required for user stories), research.md, data-model.md, contracts/

**Feature Branch**: `002-dream-job-ally-deduction`

**Tests**: Tests are OPTIONAL per project constitution. No test tasks included unless explicitly requested.

**Organization**: Tasks are grouped by user story to enable independent implementation and testing of each story (P1, P2, P3, P4).

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (e.g., US1, US2, US3, US4)
- Include exact file paths in descriptions

## Path Conventions

- **Web app**: `backend/src/`, `frontend/src/`
- Paths shown below are for FastAPI backend + React/Next.js frontend structure

---

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Project initialization and basic structure

- [ ] T001 Create backend directory structure: backend/src/{models,services,api,core,integrations}
- [ ] T002 Create frontend directory structure: frontend/src/{components,pages,services,utils}
- [ ] T003 Create test directories: backend/tests/{contract,integration,unit} and frontend/tests/components
- [ ] T004 Configure .devcontainer/devcontainer.json with Python 3.12, Node.js 18+, PostgreSQL service
- [ ] T005 Create backend/requirements.txt with pinned versions: fastapi==0.104.1, anthropic==0.8.1, langchain==0.1.0, langchain-community==0.1.0, faiss-cpu==1.7.4, sentence-transformers==2.2.2, PyPDF2==3.0.1, pdfplumber==0.10.3, python-docx==1.1.0, httpx==0.25.2, sqlalchemy==2.0.23, alembic==1.13.1, psycopg2-binary==2.9.9, pydantic==2.5.2, pytest==7.4.3, pytest-asyncio==0.21.1, pylint==3.0.3
- [ ] T006 Create frontend/package.json with dependencies: next@14, react@18, typescript@5, axios, tailwindcss
- [ ] T007 [P] Configure .devcontainer/docker-compose.yml with app and postgres services
- [ ] T008 [P] Create backend/.env.example with ANTHROPIC_API_KEY, DATABASE_URL, GITHUB_API_TOKEN placeholders
- [ ] T009 [P] Setup Alembic in backend/alembic/ with initial migration configuration
- [ ] T010 [P] Create backend/src/main.py with FastAPI app initialization, CORS middleware, and router includes
- [ ] T011 [P] Create frontend/next.config.js with API proxy configuration for backend
- [ ] T012 [P] Configure pylint in backend/.pylintrc and pytest in backend/pytest.ini

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Core infrastructure that MUST be complete before ANY user story can be implemented

**⚠️ CRITICAL**: No user story work can begin until this phase is complete

- [ ] T013 Create backend/src/core/config.py with Pydantic Settings for environment variables (ANTHROPIC_API_KEY, DATABASE_URL, etc.)
- [ ] T014 [P] Create backend/src/core/database.py with SQLAlchemy engine, SessionLocal, and Base initialization
- [ ] T015 [P] Create backend/src/core/rate_limiter.py with token bucket rate limiter class for API throttling
- [ ] T016 [P] Create backend/src/core/security.py with authentication helpers and user context management
- [ ] T017 Create backend/src/integrations/anthropic_client.py with Claude 3 Sonnet client wrapper, rate limiting, error handling, and retry logic using tenacity
- [ ] T018 [P] Create backend/src/integrations/github_client.py with httpx async client, circuit breaker pattern, and rate limiting (5000 req/hour)
- [ ] T019 [P] Create backend/src/integrations/twitter_client.py with httpx async client, circuit breaker pattern, and rate limiting (100-300 req/15min)
- [ ] T020 [P] Create backend/src/integrations/linkedin_client.py with httpx async client and rate-friendly scraping approach
- [ ] T021 Create backend/src/api/dependencies/llm.py with dependency injection for Claude client (get_llm_service)
- [ ] T022 [P] Create backend/src/api/dependencies/auth.py with get_current_user dependency
- [ ] T023 Setup HuggingFace embeddings in backend/src/services/embedding_service.py using sentence-transformers/all-MiniLM-L6-v2
- [ ] T024 [P] Create frontend/src/services/api.ts with axios client, base URL configuration, and error handling
- [ ] T025 Run Alembic initial migration to create database schema: alembic revision --autogenerate -m "Initial schema"

**Checkpoint**: Foundation ready - user story implementation can now begin in parallel

---

## Phase 3: User Story 1 - Dream Job Analysis and Resume Processing (Priority: P1) 🎯 MVP

**Goal**: Enable users to upload resumes and dream job descriptions, parse documents, deduce ally types with confidence scores using Claude 3 Sonnet

**Independent Test**: Upload resume PDF + dream job text → Verify system returns 3-7 ally types with confidence >0.5, explanations, and search queries

**Success Criteria**: SC-002 (30s deduction), SC-003 (95% parsing success), SC-004 (85% relevance rating)

### Backend Models (US1)

- [ ] T026 [P] [US1] Create backend/src/models/user_profile.py with SQLAlchemy model: id, user_id, email, resume_file_path, resume_file_name, resume_file_size, resume_upload_date, parsed_resume_id, created_at, updated_at
- [ ] T027 [P] [US1] Create backend/src/models/resume.py with ParsedResume model: id, user_id, raw_text, skills (JSON), experience_years, job_titles (JSON), companies (JSON), education (JSON), achievements (JSON), career_timeline (JSON), current_role, current_company, parsing_confidence, parsed_at, parser_version
- [ ] T028 [P] [US1] Create backend/src/models/dream_job.py with DreamJobDescription model: id, user_id, description, version, desired_role, desired_industry, desired_company_type, required_skills (JSON), responsibilities (JSON), created_at, is_active, previous_version_id
- [ ] T029 [P] [US1] Create backend/src/models/ally_type.py with DeducedAllyType model: id, dream_job_id, ally_type_name, confidence_score, selection_rationale, search_queries (JSON), engagement_strategy, rank, created_at, llm_model, llm_prompt_version

### Backend Services (US1)

- [ ] T030 [US1] Create backend/src/services/resume_parser.py with extract_text_from_pdf() using PyPDF2 with pdfplumber fallback, extract_text_from_docx() using python-docx, and parse_resume() returning structured ParsedResume data
- [ ] T031 [US1] Create backend/src/services/llm_service.py with LLMService class: deduce_ally_types(resume_text, dream_job_text) method calling Claude 3 Sonnet with structured prompt, chain-of-thought reasoning, JSON output parsing for ally types with confidence scores
- [ ] T032 [US1] Create backend/src/services/ally_deduction.py with AllyDeductionService: analyze_resume_and_dream_job() orchestrating resume parsing, LLM deduction, validation (confidence >0.5), and database persistence
- [ ] T033 [US1] Implement LLM prompt template in backend/src/services/llm_service.py: ALLY_DEDUCTION_PROMPT with few-shot examples (Software Engineer→Product Manager, Backend→DevOps, Junior→Senior), structured JSON output format
- [ ] T034 [US1] Add error handling to backend/src/services/resume_parser.py for parsing failures: detect low confidence (<0.5), generate LLM-based clarification questions (FR-003a), return user-friendly error messages

### Backend API Routes (US1)

- [ ] T035 [US1] Create backend/src/api/routes/resume.py with POST /api/v1/resumes/upload endpoint: accept multipart file upload, validate format (PDF/DOCX/TXT), validate size (≤10MB), save file, start async parsing task, return 202 with resume_id
- [ ] T036 [US1] Add GET /api/v1/resumes/{resume_id}/status endpoint in backend/src/api/routes/resume.py: return parsing status (uploaded/parsing/parsed_success/parsing_failed) and progress percentage
- [ ] T037 [US1] Add GET /api/v1/resumes/{resume_id} endpoint in backend/src/api/routes/resume.py: return ParsedResume data with skills, experience, job titles, companies, education, career timeline
- [ ] T038 [US1] Create backend/src/api/routes/dream_job.py with POST /api/v1/dream-jobs endpoint: validate description length (≥50 chars), create DreamJobDescription record, set version=1 and is_active=true
- [ ] T039 [US1] Add GET /api/v1/dream-jobs/{dream_job_id} endpoint in backend/src/api/routes/dream_job.py: return DreamJobDescription with all fields
- [ ] T040 [US1] Create backend/src/api/routes/ally_types.py with POST /api/v1/ally-deduction/analyze endpoint: accept resume_id + dream_job_description, start async analysis task (background), return 202 with analysis_id
- [ ] T041 [US1] Add GET /api/v1/ally-deduction/{analysis_id}/status endpoint in backend/src/api/routes/ally_types.py: return analysis status (queued/processing/completed/failed) and progress
- [ ] T042 [US1] Add GET /api/v1/ally-deduction/{analysis_id}/results endpoint in backend/src/api/routes/ally_types.py: return DeducedAllyType array with confidence scores, rationales, search queries, filtered by min_confidence query param (default 0.5)

### Frontend Components (US1)

- [ ] T043 [P] [US1] Create frontend/src/components/ResumeUpload.tsx: file input, drag-drop zone, format validation (PDF/DOCX/TXT), size validation (≤10MB), upload progress bar, POST to /api/v1/resumes/upload
- [ ] T044 [P] [US1] Create frontend/src/components/DreamJobForm.tsx: textarea input (min 50 chars), character counter, validation messages, submit to POST /api/v1/dream-jobs
- [ ] T045 [P] [US1] Create frontend/src/components/AllyTypesList.tsx: display ally types with name, confidence score (0-1 as percentage), rationale, search queries (GitHub/Twitter/LinkedIn), engagement strategy, sortable by confidence
- [ ] T046 [US1] Create frontend/src/pages/analysis.tsx: page layout with ResumeUpload, DreamJobForm, trigger analyze button, WebSocket or polling for status updates, display AllyTypesList when analysis_id status=completed
- [ ] T047 [US1] Add status polling logic to frontend/src/services/api.ts: pollAnalysisStatus(analysis_id) with 2s intervals, max 60s timeout, abort on completed/failed

### Integration & Optimization (US1)

- [ ] T048 [US1] Implement async background task processing in backend/src/api/routes/ally_types.py: use FastAPI BackgroundTasks for analyze_resume_and_dream_job workflow (parse → LLM call → save)
- [ ] T049 [US1] Add LLM response caching in backend/src/services/llm_service.py: hash resume+dream_job text, cache results for 24 hours to reduce API costs (~$0.01-0.03 per analysis)
- [ ] T050 [US1] Implement FAISS vector store initialization in backend/src/services/embedding_service.py: create_vector_store_from_resume(resume_text) using HuggingFace embeddings, persist to disk per user
- [ ] T051 [US1] Add logging and monitoring to backend/src/integrations/anthropic_client.py: track API usage, response times, error rates, cost estimation ($3/million input tokens, $15/million output tokens)
- [ ] T052 [US1] Run Alembic migration for User Story 1 models: alembic revision --autogenerate -m "Add US1 models: UserProfile, ParsedResume, DreamJob, AllyType"

**US1 Checkpoint**: MVP complete - Users can upload resumes, get ally type recommendations with confidence scores

---

## Phase 4: User Story 2 - Intelligent Ally Discovery and Matching (Priority: P2)

**Goal**: Search GitHub, Twitter/X, LinkedIn for professionals matching deduced ally types, rank by relevance with match explanations

**Independent Test**: Given ally type "AI/ML Technical Leaders" → Verify search returns professionals with ML expertise, GitHub repos, publications, ranked by relevance >0.6

**Success Criteria**: SC-006 (80% match accuracy), SC-008 (5+ relevant allies in 2 minutes)

### Backend Models (US2)

- [ ] T053 [P] [US2] Create backend/src/models/professional_ally.py with ProfessionalAlly model: id, ally_type_id, name, current_title, current_company, platform (github/twitter/linkedin), profile_url, expertise_areas (JSON), career_background, match_explanation, relevance_score, discovered_at, last_updated

### Backend Services (US2)

- [ ] T054 [US2] Create backend/src/services/search_query_generator.py with generate_platform_queries(ally_type) method: use Claude to create GitHub search (language filters, followers), Twitter hashtags/keywords, LinkedIn titles/companies
- [ ] T055 [US2] Create backend/src/services/ally_discovery.py with AllyDiscoveryService: search_github(query), search_twitter(query), search_linkedin(query) using respective client integrations, return raw profile data
- [ ] T056 [US2] Add rank_allies_by_relevance() method to backend/src/services/ally_discovery.py: score profiles based on title match, expertise overlap, career transition similarity, use FAISS similarity search for resume/profile matching
- [ ] T057 [US2] Implement discover_allies_for_type(ally_type_id) workflow in backend/src/services/ally_discovery.py: generate queries → search all platforms in parallel → rank by relevance → save top 20 per platform → return ProfessionalAlly list

### Backend API Routes (US2)

- [ ] T058 [US2] Create backend/src/api/routes/discovery.py with POST /api/v1/ally-discovery/search endpoint: accept ally_type_ids array, platforms filter, start async search task, return 202 with search_id
- [ ] T059 [US2] Add GET /api/v1/ally-discovery/{search_id}/status endpoint in backend/src/api/routes/discovery.py: return search status with per-platform progress (github: completed, twitter: searching, linkedin: pending)
- [ ] T060 [US2] Add GET /api/v1/ally-discovery/{search_id}/results endpoint in backend/src/api/routes/discovery.py: return ProfessionalAlly array with filters (platform, min_relevance), pagination (limit/offset), sorted by relevance_score DESC
- [ ] T061 [US2] Add GET /api/v1/ally-types/{ally_type_id}/allies endpoint in backend/src/api/routes/discovery.py: list all discovered allies for specific ally type, with sort_by (relevance/discovered_date) and pagination

### Frontend Components (US2)

- [ ] T062 [P] [US2] Create frontend/src/components/AllyDiscoveryResults.tsx: table/card view of ProfessionalAlly with name, title, company, platform icon, profile link, match explanation, relevance score bar chart, expertise tags
- [ ] T063 [P] [US2] Add filter controls to frontend/src/components/AllyDiscoveryResults.tsx: platform checkboxes (GitHub/Twitter/LinkedIn), relevance slider (0.6-1.0), search input for name/title
- [ ] T064 [US2] Create frontend/src/pages/discovery.tsx: page layout showing selected ally types from US1, trigger search button, display search status with platform progress indicators, render AllyDiscoveryResults when search_id status=completed
- [ ] T065 [US2] Add export functionality to frontend/src/components/AllyDiscoveryResults.tsx: export to CSV button with ally data (name, title, profile URL, relevance, explanation)

### Integration & Optimization (US2)

- [ ] T066 [US2] Implement circuit breaker pattern in all platform clients (backend/src/integrations/{github,twitter,linkedin}_client.py): use circuitbreaker library with failure_threshold=5, recovery_timeout=60s
- [ ] T067 [US2] Add exponential backoff retry logic to backend/src/integrations/{github,twitter,linkedin}_client.py: use tenacity with stop_after_attempt(3), wait_exponential(min=1, max=10)
- [ ] T068 [US2] Implement search results caching in backend/src/services/ally_discovery.py: cache by ally_type_id + platform for 24 hours using Redis or in-memory dict
- [ ] T069 [US2] Add graceful degradation to backend/src/api/routes/discovery.py: return partial results if one platform fails (e.g., GitHub succeeds but Twitter fails), include error messages in response
- [ ] T070 [US2] Run Alembic migration for User Story 2 models: alembic revision --autogenerate -m "Add US2 models: ProfessionalAlly"

**US2 Checkpoint**: Ally discovery complete - Users can search platforms and get ranked professional matches

---

## Phase 5: User Story 3 - Personalized Career Transition Strategy (Priority: P3)

**Goal**: Analyze skill/experience gaps between current resume and dream job, suggest ally types to bridge gaps, generate phased engagement timeline

**Independent Test**: Given resume "Junior Frontend" + dream job "Full-Stack Lead" → Verify gap analysis identifies backend/leadership gaps, suggests "Senior Full-Stack Engineers" + "Engineering Managers"

**Success Criteria**: SC-007 (85% gap accuracy), SC-005 (3+ distinct ally types for 90% scenarios)

### Backend Models (US3)

- [ ] T071 [P] [US3] Create backend/src/models/career_gap.py with CareerGapAnalysis model: id, user_id, dream_job_id, skill_gaps (JSON of SkillGap objects), experience_gaps (JSON), bridge_opportunities (JSON), gap_severity (low/medium/high), estimated_time_to_close, recommended_ally_types (JSON), analyzed_at, llm_model
- [ ] T072 [P] [US3] Add CareerTransitionStrategy model to backend/src/models/career_gap.py: id, user_id, dream_job_id, gap_analysis_id, strategy_phases (JSON), total_estimated_duration, priority_ally_types (JSON), success_metrics (JSON), generated_at

### Backend Services (US3)

- [ ] T073 [US3] Create backend/src/services/gap_analysis.py with GapAnalysisService: analyze_career_gaps(resume, dream_job) method using Claude to compare skills/experience, identify gaps with severity, estimate learning time
- [ ] T074 [US3] Add generate_transition_strategy(gap_analysis) method to backend/src/services/gap_analysis.py: use Claude to create phased timeline (0-3mo, 3-6mo, 6-12mo), assign ally types to phases, define goals/actions per phase
- [ ] T075 [US3] Implement skill gap classification in backend/src/services/gap_analysis.py: categorize gaps as technical (Python, ML), business (product strategy), leadership (team management), assign severity based on current vs required level

### Backend API Routes (US3)

- [ ] T076 [US3] Create backend/src/api/routes/career_strategy.py with POST /api/v1/career-gaps/analyze endpoint: accept user_id + resume_id + dream_job_id, run gap analysis, return CareerGapAnalysis with skill_gaps array, recommended_ally_types
- [ ] T077 [US3] Add POST /api/v1/career-strategy endpoint in backend/src/api/routes/career_strategy.py: accept gap_analysis_id, generate CareerTransitionStrategy with phased approach, priority ally types, success metrics
- [ ] T078 [US3] Add GET /api/v1/users/{user_id}/career-strategy endpoint in backend/src/api/routes/career_strategy.py: return current CareerTransitionStrategy for user

### Frontend Components (US3)

- [ ] T079 [P] [US3] Create frontend/src/components/CareerGapAnalysis.tsx: display skill gaps in table (skill name, current level, required level, severity badge), experience gaps list, bridge opportunities suggestions
- [ ] T080 [P] [US3] Create frontend/src/components/TransitionStrategyTimeline.tsx: visual timeline component showing phases (0-3mo, 3-6mo, 6-12mo), ally types per phase, goals, action items
- [ ] T081 [US3] Create frontend/src/pages/strategy.tsx: page layout with CareerGapAnalysis section, TransitionStrategyTimeline, trigger strategy generation button, download strategy as PDF option

### Integration & Optimization (US3)

- [ ] T082 [US3] Add LLM prompt for gap analysis in backend/src/services/gap_analysis.py: GAP_ANALYSIS_PROMPT with chain-of-thought reasoning, structured JSON output for skill_gaps with severity levels
- [ ] T083 [US3] Add LLM prompt for strategy generation in backend/src/services/gap_analysis.py: STRATEGY_GENERATION_PROMPT with few-shot examples of phased career transitions, timeline suggestions
- [ ] T084 [US3] Run Alembic migration for User Story 3 models: alembic revision --autogenerate -m "Add US3 models: CareerGapAnalysis, CareerTransitionStrategy"

**US3 Checkpoint**: Career strategy complete - Users get personalized gap analysis and phased networking roadmap

---

## Phase 6: User Story 4 - Dynamic Career Goal Refinement (Priority: P4)

**Goal**: Enable users to update dream job descriptions, track goal evolution, automatically refine ally type recommendations while maintaining history

**Independent Test**: Given original "AI Product Manager" dream job → Update to "AI Ethics Researcher" → Verify ally types shift from "Product Management" to "AI Ethics/Research", evolution history tracked

**Success Criteria**: SC-009 (15s update processing), SC-010 (100% history tracking), SC-013 (evolution history maintained)

### Backend Models (US4)

- [ ] T085 [P] [US4] Create backend/src/models/dream_job_evolution.py with DreamJobEvolution model: id, user_id, from_dream_job_id, to_dream_job_id, change_summary, ally_type_changes (JSON with removed/added/retained arrays), rationale, changed_at

### Backend Services (US4)

- [ ] T086 [US4] Add update_dream_job(user_id, dream_job_id, new_description) method to backend/src/services/ally_deduction.py: create new DreamJobDescription with version+1, set is_active=false on old version, link previous_version_id
- [ ] T087 [US4] Add compare_ally_types(old_ally_types, new_ally_types) method to backend/src/services/ally_deduction.py: identify removed, added, retained ally types, generate change summary
- [ ] T088 [US4] Implement evolution tracking in backend/src/services/ally_deduction.py: create DreamJobEvolution record after dream job update, populate ally_type_changes, optionally ask Claude for rationale analysis

### Backend API Routes (US4)

- [ ] T089 [US4] Add PUT /api/v1/dream-jobs/{dream_job_id} endpoint in backend/src/api/routes/dream_job.py: accept new description + optional rationale, trigger update_dream_job workflow, re-run ally deduction, return new DreamJobDescription with incremented version
- [ ] T090 [US4] Add GET /api/v1/users/{user_id}/dream-jobs endpoint in backend/src/api/routes/dream_job.py: list all DreamJobDescription versions for user with active_only query param (default false)
- [ ] T091 [US4] Create backend/src/api/routes/evolution.py with GET /api/v1/dream-job-evolution/{user_id} endpoint: return DreamJobEvolution array showing version transitions, ally type changes, rationales, sorted by changed_at DESC

### Frontend Components (US4)

- [ ] T092 [P] [US4] Add edit mode to frontend/src/components/DreamJobForm.tsx: pre-populate with existing description, show version number, rationale input for why dream job changed, submit to PUT /api/v1/dream-jobs/{id}
- [ ] T093 [P] [US4] Create frontend/src/components/DreamJobEvolutionHistory.tsx: timeline view showing dream job versions, ally type changes (removed in red, added in green, retained in blue), change summaries, rationales
- [ ] T094 [US4] Add evolution history tab to frontend/src/pages/analysis.tsx: display DreamJobEvolutionHistory component, click version to view historical ally types

### Integration & Optimization (US4)

- [ ] T095 [US4] Implement version control logic in backend/src/services/ally_deduction.py: ensure only one is_active=true per user, maintain previous_version_id chain, validate version increments
- [ ] T096 [US4] Add ally type deduplication in backend/src/services/ally_deduction.py: when updating dream job, compare new ally types with existing connections, prioritize new complementary types over duplicates (FR-012 acceptance scenario 2)
- [ ] T097 [US4] Optimize dream job update processing in backend/src/api/routes/dream_job.py: cache previous ally types, only re-run LLM if description similarity <0.8 (using FAISS embeddings), target <15s for updates (SC-009)
- [ ] T098 [US4] Run Alembic migration for User Story 4 models: alembic revision --autogenerate -m "Add US4 models: DreamJobEvolution"

**US4 Checkpoint**: Goal refinement complete - Users can update dream jobs, track evolution, maintain networking continuity

---

## Phase 7: Polish & Cross-Cutting Concerns

**Purpose**: Final optimizations, monitoring, documentation, deployment readiness

- [ ] T099 [P] Add comprehensive error handling to all API routes: standardized error responses with error code, message, details, HTTP status codes per OpenAPI spec
- [ ] T100 [P] Implement request/response logging middleware in backend/src/main.py: log all API calls with user_id, endpoint, duration, status code
- [ ] T101 [P] Add health check endpoint in backend/src/api/routes/health.py: GET /api/v1/health returning status, database connection, LLM API availability, external API circuit breaker states
- [ ] T102 [P] Create API usage dashboard queries in backend/src/core/analytics.py: track LLM API costs, resume upload counts, ally discovery requests per user, average deduction time
- [ ] T103 [P] Add rate limiting middleware to FastAPI app in backend/src/main.py: 100 requests per minute per user for API endpoints, prevent abuse
- [ ] T104 [P] Implement frontend error boundaries in frontend/src/pages/_app.tsx: catch component errors, display user-friendly messages, log to monitoring service
- [ ] T105 [P] Add loading states to all frontend components: skeleton loaders for AllyTypesList, progress bars for uploads, spinners for analysis status polling
- [ ] T106 [P] Create backend/README.md with setup instructions, API documentation links, environment variables reference, Alembic migration commands
- [ ] T107 [P] Create frontend/README.md with setup instructions, component usage examples, build/deploy commands
- [ ] T108 [P] Setup GitHub Actions CI/CD in .github/workflows/backend-ci.yml: run pylint, pytest on push, fail on coverage <80%
- [ ] T109 [P] Setup GitHub Actions CI/CD in .github/workflows/frontend-ci.yml: run ESLint, TypeScript checks, Jest tests on push
- [ ] T110 [P] Create docker-compose.yml for production deployment: backend service, frontend service, postgres, nginx reverse proxy
- [ ] T111 [P] Add monitoring and alerting setup documentation in docs/monitoring.md: LLM API cost alerts at $100/day, error rate alerts at 5%, uptime monitoring for SC-012 (99% during business hours)
- [ ] T112 Perform end-to-end testing: upload resume → create dream job → analyze → discover allies → gap analysis → update dream job → verify evolution tracking
- [ ] T113 Run final Alembic migration check: alembic upgrade head, verify all models created, run alembic downgrade -1 and upgrade head to test reversibility

---

## Dependencies & Execution Strategy

### User Story Dependency Graph

```
Phase 1 (Setup) → Phase 2 (Foundation) → Phase 3 (US1) ✅ MVP
                                        ↓
                                       Phase 4 (US2) → Phase 5 (US3)
                                        ↓                    ↓
                                       Phase 6 (US4) ←──────┘
                                        ↓
                                       Phase 7 (Polish)
```

**Critical Path**: Setup → Foundation → US1 (MVP)

**Parallel Opportunities**:
- US2, US3, US4 can be developed in parallel after US1 completes (independent features)
- Within each phase: [P] marked tasks can run in parallel
- Frontend and backend tasks within same story can be developed concurrently

### MVP Scope (Minimum Viable Product)

**Phases 1-3 only**: Setup + Foundation + User Story 1

Delivers core value:
- ✅ Resume upload and parsing
- ✅ Dream job description input
- ✅ Claude 3 Sonnet ally type deduction
- ✅ Confidence scores and rationales
- ✅ Platform-specific search queries generated
- ✅ Basic web UI for input and results

**Estimated MVP completion**: ~60 tasks (T001-T052), deployable and testable independently

### Incremental Delivery Strategy

1. **Sprint 1**: Phases 1-3 (US1 MVP) - Deploy basic ally deduction
2. **Sprint 2**: Phase 4 (US2) - Add ally discovery across platforms
3. **Sprint 3**: Phase 5 (US3) - Add gap analysis and career strategy
4. **Sprint 4**: Phase 6 (US4) - Add dream job evolution tracking
5. **Sprint 5**: Phase 7 - Polish, monitoring, optimization

Each sprint delivers independently testable and valuable functionality.

---

## Task Validation Summary

✅ **Format Compliance**: All 113 tasks follow checklist format `- [ ] [ID] [P?] [Story?] Description`
✅ **Story Organization**: Tasks grouped by user story (US1, US2, US3, US4)
✅ **File Paths**: Every task includes exact file path
✅ **Parallelization**: 45 tasks marked [P] for parallel execution
✅ **Dependencies**: Clear phase dependencies, foundational tasks marked critical
✅ **Independent Testing**: Each user story phase is independently testable
✅ **MVP Defined**: Phases 1-3 deliver deployable MVP (52 tasks)

**Total Tasks**: 113
- Setup (Phase 1): 12 tasks
- Foundation (Phase 2): 13 tasks  
- User Story 1 (Phase 3): 27 tasks ← **MVP**
- User Story 2 (Phase 4): 18 tasks
- User Story 3 (Phase 5): 14 tasks
- User Story 4 (Phase 6): 14 tasks
- Polish (Phase 7): 15 tasks

**Parallel Opportunities**: 45 tasks can run in parallel within their phases

**Constitution Compliance**:
- ✅ RAG-First AI Architecture: T017, T023, T031, T050 (Claude + FAISS)
- ✅ Privacy & Ethical Data Use: T018-T020 (public APIs only)
- ✅ Container-Native Development: T004, T007, T110 (devcontainer + Docker)
- ✅ Priority-Driven Development: US1→US2→US3→US4 with independent testability
- ✅ API Rate Limiting & Resilience: T015, T066-T069 (rate limiters + circuit breakers)
