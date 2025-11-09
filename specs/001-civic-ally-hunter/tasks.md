# Implementation Tasks: Professional Ally-Hunting Platform

**Feature**: 001-civic-ally-hunter  
**Created**: November 8, 2025  
**Total Tasks**: 103  
**Estimated Effort**: 12-16 weeks (1-2 developers)

## Task Legend

- `[P]` = Can be parallelized with other [P] tasks in same phase
- `[S]` = Sequential dependency (must wait for prior task completion)
- `[US#]` = Maps to User Story number from spec.md

---

## Phase 1: Foundation & Resume Processing (23 tasks) - Weeks 1-3

**Goal**: P1 MVP Core - Profile Setup and Ally Type Configuration (includes authentication)

### Project Setup (5 tasks)

- [X] T001 [P] Initialize Dev Container: .devcontainer/devcontainer.json with Python 3.12, Node.js 18, PostgreSQL 15
- [X] T002 [P] Create backend/requirements.txt: FastAPI 0.104.1, anthropic 0.8.1, langchain 0.1.0, faiss-cpu 1.7.4, sentence-transformers 2.2.2, PyPDF2 3.0.1, python-docx 1.1.0, httpx 0.25.2, circuitbreaker 1.4.0, tenacity 8.2.3, NetworkX 3.2.0, SQLAlchemy 2.0.23, Alembic 1.13.1, redis 5.0.1, hiredis 2.2.3, pytest 7.4.3, pylint 3.0.3, bcrypt 4.1.2, python-jose 3.3.0
- [X] T003 [P] Create frontend/package.json: Next.js 14.0.4, React 18, TypeScript 5.3.3, D3.js 7.8+, Tailwind CSS 3.3.6
- [X] T004 [P] Setup FastAPI application scaffold: backend/src/main.py with CORS, health check endpoint, OpenAPI docs
- [X] T005 [P] Create backend/.env.example: ANTHROPIC_API_KEY, GITHUB_API_TOKEN, TWITTER_API_KEY, APOLLO_API_KEY, DATABASE_URL, SECRET_KEY, JWT_SECRET_KEY, JWT_ALGORITHM, environment variables with documentation

### Authentication & Security (3 tasks)

- [X] T006 [S] [US1] Create backend/src/core/security.py: JWT authentication with HTTPBearer scheme, generate_token(user_id), validate_token(token), hash_password(password) with bcrypt, verify_password(plain, hashed)
- [X] T007 [P] [US1] Create backend/src/api/routes/auth.py: POST /auth/register (email, password) creates UserProfile, POST /auth/login returns JWT token, POST /auth/refresh refreshes token, GET /auth/me returns current user
- [X] T008 [P] [US1] Add authentication middleware: protect all routes except /auth/*, /health, /docs, extract user_id from JWT, inject into request.state.user_id

### Database Schema (4 tasks)

- [X] T009 [S] Initialize Alembic: alembic init, configure alembic.ini with DATABASE_URL
- [X] T010 [P] [US1] Create backend/src/models/user_profile.py: UserProfile model (id, user_id, email unique indexed, password_hash, resume_file_path, parsed_resume_id FK, created_at, updated_at)
- [X] T011 [P] [US1] Create backend/src/models/parsed_resume.py: ParsedResume model (id, user_profile_id FK, raw_text, skills JSON, achievements JSON, work_history JSON, education JSON, companies JSON, keywords JSON, parsing_confidence float, parsed_at, parser_version)
- [X] T012 [P] [US1] Create backend/src/models/ally_type.py: AllyType model (id, user_profile_id FK, name, keywords JSON, criteria Text, search_parameters JSON, created_at, is_active)

### Resume Upload & Parsing (5 tasks)

- [X] T013 [S] [US1] Create backend/src/api/routes/resume.py: POST /resumes/upload endpoint with multipart/form-data handling, 10MB size limit validation, file extension check (pdf, docx, doc, txt), save to file storage
- [X] T014 [P] [US1] Create backend/src/services/resume_parser.py: ResumeParser class with extract_text_from_pdf (PyPDF2), extract_text_from_docx (python-docx), extract_text_from_txt, parse_resume method
- [X] T015 [S] [US1] Implement resume field extraction in resume_parser.py: extract skills (pattern matching + NER fallback), extract achievements (bullet points with metrics), extract work_history (company, title, dates, description), extract education, calculate parsing_confidence (0-1 based on extraction success rate)
- [X] T016 [S] [US1] Add resume parsing background task: parse_resume_background using FastAPI BackgroundTasks, update ParsedResume record, handle parsing errors with retry logic
- [X] T017 [S] [US1] Add resume retrieval endpoints: GET /resumes/{id} (return parsed resume), GET /resumes/{id}/status (parsing progress tracking)

### Ally Type CRUD (5 tasks)

- [X] T018 [P] [US1] Create backend/src/api/routes/ally_types.py: POST /ally-types endpoint (create with name, keywords JSON, criteria, search_parameters), validate name uniqueness per user
- [X] T019 [P] [US1] Add GET /ally-types endpoint: list user's ally types with pagination, filter by is_active
- [X] T020 [P] [US1] Add PUT /ally-types/{id} endpoint: update ally type (name, keywords, criteria), validate ownership
- [X] T021 [P] [US1] Add DELETE /ally-types/{id} endpoint: soft delete (set is_active=False), cascade to associated contacts
- [X] T022 [P] [US1] Add GET /ally-types/export, POST /ally-types/import endpoints: export all user's ally types as JSON, import from JSON payload (FR-014 save/load requirement)

---

## Phase 2: Multi-Platform Search Integration (22 tasks) - Weeks 4-6

**Goal**: P1 Continuation - Semantic search across GitHub, Twitter/X, LinkedIn

### External API Clients (8 tasks)

- [ ] T023 [P] [US1] Create backend/src/integrations/github_client.py: GitHubClient class with search_users(query, per_page, page), get_user_profile(username), get_user_issues(username), rate_limiter (5000 req/hour), circuit breaker (failure_threshold=5, recovery_timeout=60s)
- [ ] T024 [P] [US1] Create backend/src/integrations/twitter_client.py: TwitterClient class with search_tweets(query, max_results), get_user_profile(username), rate_limiter (300 req/15min), exponential backoff (1-10s delays)
- [ ] T025 [P] [US1] Create backend/src/integrations/linkedin_client.py: LinkedInClient class with search_profiles(query) using public endpoints only, ToS-compliant scraping, manual URL input fallback, aggressive caching (24hr TTL)
- [ ] T026 [P] [US1] Create backend/src/integrations/apollo_client.py: ApolloClient class with enrich_contact(name, company), search_people(query, filters), rate_limiter (TBD based on tier)
- [ ] T027 [S] Create backend/src/core/rate_limiter.py: TokenBucketRateLimiter class with acquire(tokens=1), wait_and_acquire(timeout=60), thread-safe implementation
- [ ] T028 [S] Create backend/src/core/circuit_breaker.py: CircuitBreakerManager using circuitbreaker library, failure_threshold=5, recovery_timeout=60s, half_open state logic
- [ ] T029 [P] Add retry logic to all API clients: tenacity @retry decorator with exponential backoff, stop_after_attempt=3, wait_exponential(min=1, max=10)
- [ ] T030 [P] Implement API response caching: Redis cache with TTL (GitHub: 1hr, Twitter: 15min, LinkedIn: 24hr), cache key = hash(endpoint + params)

### Contact & Content Models (3 tasks)

- [ ] T031 [P] [US1] Create backend/src/models/contact.py: Contact model (id, ally_type_id FK, name, title, company, location, email, phone, github_url, twitter_url, linkedin_url, relevance_score float, matched_keywords JSON, source_platform, profile_data JSON, enrichment_data JSON, created_at, last_updated)
- [ ] T032 [P] [US1] Create backend/src/models/content.py: Content model (id, contact_id FK, text Text, source_platform, url, metadata JSON, posted_at, embedding_vector bytes, ally_type_classification JSON, created_at)
- [ ] T033 [P] [US1] Create backend/src/models/search_query.py: SearchQuery model (id, user_profile_id FK, original_query, ally_type_filters JSON, counter_queries JSON, results_count, executed_at)

### FAISS Vector Store (4 tasks)

- [ ] T034 [S] [US1] Create backend/src/services/embedding_service.py: EmbeddingService class with encode(texts: List[str]) using sentence-transformers (all-MiniLM-L6-v2, 384 dims), encode_single(text: str), cosine_similarity(emb1, emb2)
- [ ] T035 [S] [US1] Create backend/src/services/faiss_service.py: FAISSService class with create_index(dimension=384), add_vectors(ids, vectors), search(query_vector, k=10), save_index(path), load_index(path)
- [ ] T036 [S] [US1] Implement resume indexing: index_resume(parsed_resume) aggregates all sections, generates single 384-dim vector, stores in user-specific FAISS index with resume_id as key
- [ ] T037 [S] [US1] Implement content indexing: index_content(content) generates vector from text, stores in global FAISS index with content_id as key, periodic batch indexing for new content

### Search Orchestration (7 tasks)

- [ ] T038 [S] [US1] Create backend/src/services/search_orchestrator.py: SearchOrchestrator class with execute_search(query, ally_type_ids), fan-out to GitHub/Twitter/LinkedIn in parallel using asyncio.gather
- [ ] T039 [S] [US1] Implement search result aggregation: merge results from all platforms, deduplicate by name+company, calculate relevance_score (0-1) using cosine similarity between query embedding and content embeddings
- [ ] T040 [S] [US1] Implement ally type filtering: filter results by matched_keywords in ally_type.keywords, boost relevance_score if keywords present, tag with matched ally_type_id
- [ ] T041 [P] [US1] Create backend/src/api/routes/search.py: POST /search endpoint (query, ally_type_ids) triggers background task, returns search_query_id, status="processing"
- [ ] T042 [P] [US1] Add GET /search/{query_id} endpoint: return SearchQuery with results (paginated, 20 per page), status (processing/completed/failed), results_count
- [ ] T043 [S] [US1] Implement search background task: execute_search_background calls search_orchestrator, indexes content, enriches contacts via Apollo API, stores results, updates SearchQuery status
- [ ] T044 [P] [US1] Add contact enrichment: for each Contact, call apollo_client.enrich_contact if email missing, store in enrichment_data JSON, track success rate

---

## Phase 3: Shadow Sequence Amplifier (16 tasks) - Weeks 7-9

**Goal**: P2 - Counter-query generation + bridge pitches

### LangChain & Claude 3 Sonnet Setup (4 tasks)

- [ ] T045 [P] [US2] Create backend/src/services/llm_service.py: LLMService class with anthropic.Anthropic client initialization, API key from settings.ANTHROPIC_API_KEY
- [ ] T046 [S] [US2] Implement LLM call wrapper: create_message(prompt, system_message, max_tokens=1024, temperature=0.7) using Claude 3 Sonnet (claude-3-sonnet-20240229), retry with tenacity (3 attempts), track token usage
- [ ] T047 [P] [US2] Add LLM cost tracking: track_api_usage(input_tokens, output_tokens), calculate cost ($3/million input, $15/million output), store in usage logs, per-user quota enforcement
- [ ] T048 [P] [US2] Implement response caching: cache LLM responses with TTL=24hr, cache key = hash(prompt + system_message + model), reduce API costs by ~70%

### Counter-Query Generation (5 tasks)

- [ ] T049 [S] [US2] Create backend/src/services/shadow_sequence_generator.py: ShadowSequenceGenerator class with generate_counter_queries(query, ally_types)
- [ ] T050 [S] [US2] Implement counter-query LLM prompt: system message = "Generate 3-5 opposing viewpoints to the following query within the context of {ally_type.name} ({ally_type.keywords})", user message = query, parse JSON response [{counter_query, rationale}]
- [ ] T051 [S] [US2] Add counter-query quality validation: check if counter_queries are meaningfully different from original (cosine similarity <0.7), validate relevance to ally_type, retry if quality <90% (max 2 retries)
- [ ] T052 [S] [US2] Store counter-queries: update SearchQuery.counter_queries JSON field, timestamp generation
- [ ] T053 [S] [US2] Execute counter-query searches: for each counter_query, call search_orchestrator, tag results with "skeptic" perspective, merge with original results (deduplicate), mark as shadow_sequence=True in Contact metadata

### Bridge Pitch Generation (7 tasks)

- [ ] T054 [P] [US2] Create backend/src/models/bridge_pitch.py: BridgePitch model (id, user_profile_id FK, target_contact_id FK, resume_achievements_referenced JSON, ally_type_context, generated_message Text, collaboration_proposal Text, llm_model, llm_prompt_version, created_at)
- [ ] T055 [S] [US2] Create backend/src/services/bridge_pitch_generator.py: BridgePitchGenerator class with generate_pitch(contact, parsed_resume, ally_type)
- [ ] T056 [S] [US2] Implement bridge pitch LLM prompt: system message = "Create professional outreach message acknowledging {contact_concerns} from their content while highlighting {resume_achievements} relevant to {ally_type}", user message = formatted data, parse JSON response {message, collaboration_proposal, achievements_used}
- [ ] T057 [S] [US2] Extract target concerns: analyze Contact.profile_data + associated Content records, identify key interests/concerns using LLM or keyword extraction
- [ ] T058 [S] [US2] Match resume achievements: find ParsedResume.achievements with keywords matching contact's interests, prioritize quantified achievements (e.g., "30% improvement"), return top 3 relevant achievements
- [ ] T059 [S] [US2] Validate resume achievement inclusion: verify at least 1 achievement from achievements_used appears in generated_message, fail if 0 (SC-005: 100% requirement), retry up to 2 times
- [ ] T060 [P] [US2] Create backend/src/api/routes/bridge_pitches.py: POST /bridge-pitches endpoint (contact_id), GET /bridge-pitches/{id}, GET /bridge-pitches (list user's pitches with pagination)

---

## Phase 4: Organization Network Mapping (18 tasks) - Weeks 10-12

**Goal**: P3 - Visualize connection paths

### Organization Data (5 tasks)

- [ ] T061 [P] [US3] Create backend/src/models/organization.py: Organization model (id, name indexed, domain, revenue, employee_count, technologies JSON, industry, ally_type_relevance JSON, created_at)
- [ ] T062 [S] [US3] Create backend/src/services/organization_service.py: OrganizationService class with extract_companies_from_resume(parsed_resume), create_or_update_organization(name, data)
- [ ] T063 [S] [US3] Implement company extraction: parse ParsedResume.work_history for company names, normalize (lowercase, remove Inc/Ltd), store in ParsedResume.companies JSON + create Organization records
- [ ] T064 [P] [US3] Integrate Apollo API for org data: enrich_organization(name) fetches revenue, employee_count, technologies from Apollo, store in Organization record, cache for 30 days
- [ ] T065 [P] [US3] Add organization-contact linking: when Contact created, extract company from title/profile, link to Organization.id, backfill existing contacts

### Network Graph Building (6 tasks)

- [ ] T066 [P] [US3] Create backend/src/models/network_connection.py: NetworkConnection model (id, user_profile_id FK, source_contact_id FK, target_contact_id FK, connection_type, shared_organizations JSON, connection_strength float, path_metadata JSON, created_at)
- [ ] T067 [S] [US3] Create backend/src/services/network_mapper.py: NetworkMapper class with build_graph(user_profile, target_contacts), uses NetworkX for graph construction
- [ ] T068 [S] [US3] Implement network node creation: add user's resume contacts as nodes (from ParsedResume.work_history), add target contacts as nodes, add organizations as nodes
- [ ] T069 [S] [US3] Implement network edge creation: add edges for employment (person → company), add edges for shared employment (person ↔ person via company), add edges for investor/acquisition relationships (company ↔ company)
- [ ] T070 [S] [US3] Calculate connection paths: use NetworkX shortest_path(user_node, target_node), limit to paths ≤3 degrees, calculate connection_strength (1.0 / path_length, weighted by recency)
- [ ] T071 [S] [US3] Store network connections: for each path found, create NetworkConnection record with path_metadata = {nodes, edges, connection_type}, deduplicate by source+target

### Network Visualization (4 tasks)

- [ ] T072 [P] [US3] Create backend/src/api/routes/network_map.py: GET /network-map endpoint (user_id, target_contact_ids[]) returns graph JSON {nodes: [{id, label, type}], edges: [{source, target, label, strength}]}
- [ ] T073 [P] [US3] Add GET /network-map/connections endpoint: return NetworkConnection records for user, filter by target_contact_id, include warm intro suggestions
- [ ] T074 [S] [US3] Generate warm intro suggestions: for each NetworkConnection, create suggestion text = "Ask {source_contact.name} for intro to {target_contact.name} (shared {connection_type})", store in path_metadata.intro_suggestion
- [ ] T075 [P] [US3] Handle no connections case: when no paths found, return alternative_strategies = ["Join {ally_type} professional association", "Attend {industry} conferences", "Engage in {ally_type} online communities"], store in SearchQuery.metadata

### Frontend Network Visualization (3 tasks)

- [ ] T076 [P] [US3] Create frontend/src/components/NetworkGraph.tsx: D3.js force-directed graph, nodes sized by importance, edges colored by connection_type, interactive (click node → show details, click edge → show path)
- [ ] T077 [P] [US3] Add network graph controls: zoom/pan, filter by connection_type, highlight paths to specific target, toggle organization vs. people view
- [ ] T078 [P] [US3] Add connection details panel: when user clicks path, show: source contact, target contact, shared organizations, connection_strength, warm intro suggestion with "Copy Message" button

---

## Phase 5: Outreach Template Generator (12 tasks) - Weeks 13-14

**Goal**: P4 - Personalized outreach messages

### Outreach Template Generation (6 tasks)

- [ ] T079 [S] [US4] Extend BridgePitch model: add template_type field ("bridge_pitch" | "outreach_template"), add target_content_ids JSON (FK to Content)
- [ ] T080 [S] [US4] Create backend/src/services/outreach_template_generator.py: OutreachTemplateGenerator class with generate_template(contact, target_content, parsed_resume)
- [ ] T081 [S] [US4] Implement content interest extraction: analyze target's Content records (posts/issues), extract key topics using LLM or TF-IDF, identify primary interests/expertise areas
- [ ] T082 [S] [US4] Implement resume-interest matching: find ParsedResume achievements/skills matching target's interests, calculate match_score (0-1) using cosine similarity between embeddings, return top 3 matches
- [ ] T083 [S] [US4] Implement outreach LLM prompt: system message = "Create authentic outreach message connecting {resume_achievements} to {target_interests} from {target_content}, propose collaboration on {shared_topic}", parse JSON response {message, collaboration_proposal, authenticity_score}
- [ ] T084 [S] [US4] Validate authenticity: check if message references specific content from target (URL, quote, topic), verify resume achievement connection, retry if authenticity_score <0.7 (up to 2 retries)

### Export Functionality (6 tasks)

- [ ] T085 [P] [US4] Create backend/src/api/routes/export.py: GET /export/search-results/{query_id} endpoint returns markdown file with search results, ally type matches, relevance scores
- [ ] T086 [P] [US4] Add GET /export/network-map/{user_id} endpoint: returns markdown + PNG (NetworkX graph visualization), includes connection paths, warm intro suggestions
- [ ] T087 [P] [US4] Add GET /export/outreach-templates endpoint: returns markdown with all user's templates, grouped by target ally_type, includes copy-paste ready messages
- [ ] T088 [S] [US4] Implement markdown formatting: for search results, format as table (Name | Title | Company | Relevance | Ally Type | Platform), include metadata (query, timestamp, results_count)
- [ ] T089 [S] [US4] Implement graph export: use NetworkX to_png() for network map visualization, include legend, optimize for 1920x1080 resolution, deliver within 10s (SC-009)
- [ ] T090 [S] [US4] Add batch export: GET /export/all endpoint returns ZIP file with search results + network maps + outreach templates, stream response for large files

---

## Phase 6: Polish & Production Readiness (15 tasks) - Weeks 15-17

**Goal**: Production deployment with 99.5% uptime (includes testing and infrastructure)

### Frontend UI Polish (4 tasks)

- [ ] T091 [P] Create frontend/src/pages/onboarding.tsx: guided flow (1. Upload resume → 2. Define ally types → 3. First search), progress indicators, tooltips, complete within 5min (SC-001)
- [ ] T092 [P] Create frontend/src/components/ResumeUploader.tsx: drag-drop zone, file validation (PDF/DOCX/TXT, ≤10MB), upload progress bar, parsing status polling, display parsing_confidence
- [ ] T093 [P] Create frontend/src/components/AllyTypeManager.tsx: CRUD UI for ally types, keyword chip input, criteria textarea, search parameter toggles (GitHub/Twitter/LinkedIn), is_active toggle
- [ ] T094 [P] Create frontend/src/components/SearchResults.tsx: card layout for contacts, relevance score badges, ally type tags, filter by platform/ally_type, sort by relevance, pagination (20/page)

### Performance Optimization (3 tasks)

- [ ] T095 [S] Implement Redis caching: cache search results (TTL=1hr), cache LLM responses (TTL=24hr), cache API responses per client TTLs, track cache hit rate (target >70%)
- [ ] T096 [S] Optimize FAISS queries: implement index sharding by user (user_id → index_file), periodic index optimization (rebuild after 1000 additions), consider Pinecone for production scale
- [ ] T097 [P] Optimize database queries: add indexes (user_id, created_at, ally_type_id, relevance_score), use SELECT DISTINCT for deduplication, implement query result caching in PostgreSQL

### Security & Monitoring (8 tasks)

- [ ] T098 [P] Implement API key encryption: encrypt ANTHROPIC_API_KEY, GITHUB_API_TOKEN, TWITTER_API_KEY in database using Fernet symmetric encryption, decrypt at runtime
- [ ] T099 [P] Add input validation: sanitize all user inputs (query, ally_type.name, criteria), prevent SQL injection, prevent XSS in markdown export, max length limits
- [ ] T100 [P] Setup logging: structured logging (JSON format), log levels (DEBUG/INFO/WARNING/ERROR), log API calls, search queries, LLM token usage, errors with stack traces
- [ ] T101 [P] Setup monitoring: Prometheus metrics (API response times, error rates, cache hit rates, LLM costs), Grafana dashboards, alerting for uptime <99.5% (SC-008)
- [ ] T102 [P] [US1] Implement resume parsing accuracy testing (SC-004): pytest suite with 100+ sample resumes (PDF/DOCX/TXT from diverse formats/industries), measure skill/achievement/company extraction success rates, validate ≥95% parsing_confidence target, generate test report with failure analysis
- [ ] T103 [S] Setup production deployment infrastructure (SC-008): select cloud platform (Heroku/Render/Railway), configure load balancer, auto-scaling (2-10 instances based on CPU/memory), health checks (/health endpoint polling), SSL/TLS certificates, environment variable management, database connection pooling
- [ ] T104 [P] Create deployment documentation: README.md with setup instructions, .env.example with all variables, Docker Compose for local dev, deployment guide for cloud platforms (Heroku/Render/Railway)
- [ ] T105 [P] Create database migration guide: Alembic migration scripts for all schema changes, rollback procedures, data migration scripts for existing users (if any)
- [ ] T106 [P] Final end-to-end testing: complete user journey from registration → resume upload → ally type creation → search → network mapping → outreach generation → export, verify all success criteria (SC-001 through SC-010), load testing with 100+ concurrent users

---

## Task Summary by Phase

| Phase | Tasks | Focus | Target User Story |
|-------|-------|-------|-------------------|
| 1 | 22 (T001-T022) | Foundation, Auth & Resume Processing | US1 (P1) |
| 2 | 22 (T023-T044) | Multi-Platform Search | US1 (P1) |
| 3 | 16 (T045-T060) | Shadow Sequence Amplifier | US2 (P2) |
| 4 | 18 (T061-T078) | Organization Network Mapping | US3 (P3) |
| 5 | 12 (T079-T090) | Outreach Template Generator | US4 (P4) |
| 6 | 16 (T091-T106) | Polish, Testing & Production | All |
| **Total** | **106** | | |

## Critical Path

Sequential dependencies (must execute in order):
1. T001-T005 (setup) → T006-T008 (auth) → T009-T012 (models) → T013-T017 (resume parsing)
2. T023-T029 (API clients + models) → T037-T043 (search orchestration)
3. T044-T047 (LLM setup) → T048-T052 (counter-queries) → T053-T059 (bridge pitches)
4. T060-T064 (org data) → T065-T070 (network graph) → T071-T077 (visualization)
5. T078-T083 (outreach templates) → T084-T089 (export)
6. T090-T103 (production readiness, testing, deployment)

**Parallelizable**: Within each phase, [P] tasks can run simultaneously across multiple developers.

## Success Criteria Mapping

| SC | Description | Tasks |
|----|-------------|-------|
| SC-001 | Upload + define ally types <5min | T001-T022, T090-T092 |
| SC-002 | Search results <30s | T037-T043, T094-T096 |
| SC-003 | Relevance ≥80% | T038-T039, T093 |
| SC-004 | Resume parsing ≥95% | T014-T016, T101 |
| SC-005 | Bridge pitch resume refs 100% | T057-T058 |
| SC-006 | Network connections ≥60% | T066-T070, T073-T074 |
| SC-007 | Multi-platform indexing 100% | T023-T026, T037-T043 |
| SC-008 | Uptime ≥99.5% | T097-T103 |
| SC-009 | Export <10s for 50 results | T084-T089 |
| SC-010 | Counter-query quality ≥90% | T049-T050 |
| FR-015 | Secure authentication | T006-T008 |
