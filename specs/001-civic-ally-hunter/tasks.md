# Implementation Tasks: Professional Ally-Hunting Platform

**Feature**: 001-civic-ally-hunter  
**Created**: November 8, 2025  
**Total Tasks**: 139  
**Estimated Effort**: 12-16 weeks (1-2 developers)

## Task Legend

- `[P]` = Can be parallelized with other [P] tasks in same phase
- `[S]` = Sequential dependency (must wait for prior task completion)
- `[US#]` = Maps to User Story number from spec.md

---

## Phase 1: Foundation & Resume Processing (30 tasks) - Weeks 1-3

**Goal**: P1 MVP Core - Profile Setup and Ally Type Configuration (includes authentication + automated tests)

### Project Setup (5 tasks)

- [x] T001 [P] Initialize Dev Container: .devcontainer/devcontainer.json with Python 3.12, Node.js 18, PostgreSQL 15
- [x] T002 [P] Create backend/requirements.txt: FastAPI 0.104.1, anthropic 0.8.1, langchain 0.1.0, faiss-cpu 1.7.4, sentence-transformers 2.2.2, PyPDF2 3.0.1, python-docx 1.1.0, httpx 0.25.2, circuitbreaker 1.4.0, tenacity 8.2.3, NetworkX 3.2.0, SQLAlchemy 2.0.23, Alembic 1.13.1, redis 5.0.1, hiredis 2.2.3, pytest 7.4.3, pylint 3.0.3, bcrypt 4.1.2, python-jose 3.3.0
- [x] T003 [P] Create frontend/package.json: Next.js 14.0.4, React 18, TypeScript 5.3.3, D3.js 7.8+, Tailwind CSS 3.3.6
- [x] T004 [P] Setup FastAPI application scaffold: backend/src/main.py with CORS, health check endpoint, OpenAPI docs
- [x] T005 [P] Create backend/.env.example: ANTHROPIC_API_KEY, GITHUB_API_TOKEN, TWITTER_API_KEY, APOLLO_API_KEY, DATABASE_URL, SECRET_KEY, JWT_SECRET_KEY, JWT_ALGORITHM, environment variables with documentation

### Authentication & Security (3 tasks)

- [x] T006 [S] [US1] Create backend/src/core/security.py: JWT authentication with HTTPBearer scheme, generate_token(user_id), validate_token(token), hash_password(password) with bcrypt (minimum 12 rounds: bcrypt.gensalt(rounds=12)), verify_password(plain, hashed)
- [x] T007 [P] [US1] Create backend/src/api/routes/auth.py: POST /auth/register (email, password) creates UserProfile, POST /auth/login returns JWT token, POST /auth/refresh refreshes token, GET /auth/me returns current user
- [x] T008 [P] [US1] Add authentication middleware: protect all routes except /auth/\*, /health, /docs, extract user_id from JWT, inject into request.state.user_id

### Database Schema (4 tasks)

- [x] T009 [S] Initialize Alembic: alembic init, configure alembic.ini with DATABASE_URL
- [x] T010 [P] [US1] Create backend/src/models/user_profile.py: UserProfile model (id, user_id, email unique indexed, password_hash, resume_file_path, parsed_resume_id FK, created_at, updated_at)
- [x] T011 [P] [US1] Create backend/src/models/parsed_resume.py: ParsedResume model (id, user_profile_id FK, raw_text, skills JSON, achievements JSON, work_history JSON, education JSON, companies JSON, keywords JSON, parsing_confidence float, parsed_at, parser_version)
- [x] T012 [P] [US1] Create backend/src/models/ally_type.py: AllyType model (id, user_profile_id FK, name, keywords JSON, criteria Text, search_parameters JSON, created_at, is_active)

### Resume Upload & Parsing (5 tasks)

- [x] T013 [S] [US1] Create backend/src/api/routes/resume.py: POST /resumes/upload endpoint with multipart/form-data handling, 10MB size limit validation, file extension check (pdf, docx, doc, txt), save to file storage
- [x] T014 [P] [US1] Create backend/src/services/resume_parser.py: ResumeParser class with extract_text_from_pdf (PyPDF2), extract_text_from_docx (python-docx), extract_text_from_txt, parse_resume method
- [x] T015 [S] [US1] Implement resume field extraction in resume_parser.py: extract skills (pattern matching + NER fallback), extract achievements (bullet points with metrics), extract work_history (company, title, dates, description), extract education, calculate parsing_confidence (0-1 based on extraction success rate)
- [x] T016 [S] [US1] Add resume parsing background task: parse_resume_background using FastAPI BackgroundTasks, update ParsedResume record, handle parsing errors with retry logic
- [x] T017 [S] [US1] Add resume retrieval endpoints: GET /resumes/{id} (return parsed resume), GET /resumes/{id}/status (parsing progress tracking)

### Ally Type CRUD (5 tasks)

- [x] T018 [P] [US1] Create backend/src/api/routes/ally_types.py: POST /ally-types endpoint (create with name, keywords JSON, criteria, search_parameters), validate name uniqueness per user
- [x] T019 [P] [US1] Add GET /ally-types endpoint: list user's ally types with pagination, filter by is_active
- [x] T020 [P] [US1] Add PUT /ally-types/{id} endpoint: update ally type (name, keywords, criteria), validate ownership
- [x] T021 [P] [US1] Add DELETE /ally-types/{id} endpoint: soft delete (set is_active=False), cascade to associated contacts
- [x] T022 [P] [US1] Add GET /ally-types/export, POST /ally-types/import endpoints: export all user's ally types as JSON, import from JSON payload (FR-014 save/load requirement)

### Automated Testing (7 tasks)

- [x] T022a [S] [US1] Create pytest configuration: backend/pytest.ini with coverage settings (--cov=src, --cov-report=html/term-missing), test discovery patterns, markers for unit/integration/auth/resume/ally_type
- [x] T022b [P] [US1] Write unit tests for security.py: test_hash_password, test_verify_password, test_generate_token, test_validate_token, test_token_expiration, test_bcrypt_rounds_minimum_12 (verify bcrypt.gensalt(rounds=12) configuration per NFR-006) (≥90% coverage target)
- [x] T022c [P] [US1] Write unit tests for resume_parser.py: test_extract_text_pdf/docx/txt, test_extract_skills, test_extract_achievements, test_calculate_confidence (≥85% coverage target)
- [x] T022d [S] [US1] Write integration tests for auth endpoints: test_register_success/duplicate, test_login_valid/invalid, test_get_me_authenticated/unauthenticated, test_refresh_token (backend/tests/integration/test_auth_api.py)
- [x] T022e [S] [US1] Write integration tests for resume endpoints: test_upload_resume_txt/pdf, test_upload_invalid_format, test_get_resume_status, test_get_parsed_resume, test_multi_user_isolation (backend/tests/integration/test_resume_api.py)
- [x] T022f [S] [US1] Write integration tests for ally type endpoints: test_create_ally_type, test_list_ally_types_filter, test_update_ally_type, test_delete_soft, test_export_import, test_ownership_validation (backend/tests/integration/test_ally_type_api.py)
- [x] T022g [S] [US1] Achieve ≥80% test coverage for Phase 1 code: run pytest --cov=src --cov-report=html, fix uncovered branches, document coverage report in htmlcov/index.html, verify all critical paths tested (ACHIEVED: 85.11% coverage with 89 passing tests)

**Constitution Principle VI Compliance**: ✅ Phase 1 NOW complete with T022a-g finished and 85.11% test coverage achieved (exceeds 80% requirement). All automated tests passing.

---

## Phase 2: Multi-Platform Search Integration (29 tasks) - Weeks 4-6

**Goal**: P1 Continuation - Semantic search across GitHub, Twitter/X, LinkedIn

### External API Clients (8 tasks)

- [ ] T023 [P] [US1] Create backend/src/integrations/github_client.py: GitHubClient class with search_users(query, per_page, page), get_user_profile(username), get_user_issues(username), rate_limiter (5000 req/hour), circuit breaker (failure_threshold=5, recovery_timeout=60s)
- [ ] T024 [P] [US1] Create backend/src/integrations/twitter_client.py: TwitterClient class with search_tweets(query, max_results), get_user_profile(username), rate_limiter (300 req/15min), exponential backoff (1-10s delays)
- [ ] T025 [P] [US1] Create backend/src/integrations/linkedin_client.py: LinkedInClient class with search_profiles(query) using public endpoints only, ToS-compliant scraping, **manual URL input as fallback**, aggressive caching (24hr TTL)
- [ ] T025a [P] [US1] **PRIMARY METHOD** Create backend/src/api/routes/linkedin.py: POST /linkedin/manual-add endpoint accepting LinkedIn profile URL (linkedin.com/in/username format), validate URL format with regex ^https?://(www\.)?linkedin\.com/in/[a-zA-Z0-9_-]+/?$, parse public profile HTML to extract name (required), title (required), company (required), headline (optional), store in Contact with source="linkedin_manual_input", return Contact record with parsing_success boolean and parsed_fields array; **Parsing Success Criteria**: FULL SUCCESS = all 3 required fields extracted (name + title + company), PARTIAL SUCCESS = 2/3 required fields extracted (return parsed_fields list + warning message "Missing: [field_name]"), FAILURE = <2 required fields extracted (return error "Unable to extract sufficient profile data. Please verify profile is public and try again. Missing required fields: [field_names]"); headline is always optional and doesn't affect success status; handle parsing errors with user-friendly messages (addresses FR-003a requirement - manual URL input is the primary LinkedIn integration method)
- [ ] T026 [P] [US1] Create backend/src/integrations/apollo_client.py: ApolloClient class with enrich_contact(name, company), search_people(query, filters), rate_limiter (TBD based on tier)
- [ ] T027 [S] Create backend/src/core/rate_limiter.py: TokenBucketRateLimiter class with acquire(tokens=1), wait_and_acquire(timeout=60), thread-safe implementation
- [ ] T028 [S] Create backend/src/core/circuit_breaker.py: CircuitBreakerManager using circuitbreaker library, failure_threshold=5, recovery_timeout=60s, half_open state logic
- [ ] T029 [P] Add retry logic to all API clients: tenacity @retry decorator with exponential backoff, stop_after_attempt=3, wait_exponential(min=1, max=10)
- [ ] T029a [P] Create API ToS compliance validation: backend/src/integrations/compliance.py with check_github_tos(), check_twitter_tos(), check_linkedin_tos() documenting rate limits, allowed endpoints, forbidden scraping patterns; raise ComplianceError if violations detected; unit tests for each API's compliance rules (FR-012 requirement)
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
- [ ] T043a [P] [US1] Create backend/src/models/search_result_rating.py: SearchResultRating model (id, search_query_id FK, contact_id FK, rating int 1-5, created_at); Create backend/src/api/routes/search.py rating endpoints: POST /search/results/{contact_id}/rate (rating: int), GET /search/{query_id}/ratings (returns avg rating, count, % rated ≥4); validate rating in range 1-5
- [ ] T043b [P] [US1] Implement ally type deduplication UI: display all matched_ally_types for contacts matching multiple categories in SearchResults component, provide "Merge Ally Types" suggestion button with keyword consolidation preview, addresses Edge Case 7 (conflicting/overlapping ally types)
- [ ] T044 [P] [US1] Add contact enrichment: for each Contact, call apollo_client.enrich_contact if email missing, store in enrichment_data JSON, track success rate

### Automated Testing - Phase 2 (7 tasks)

- [ ] T044a [P] [US1] Write unit tests for API clients: test_github_client (rate limiting, circuit breaker, retry logic), test_twitter_client (rate limiting, exponential backoff), test_linkedin_client (caching, ToS compliance), test_apollo_client (enrichment, rate limiting) - ≥85% coverage target
- [ ] T044b [P] [US1] Write unit tests for rate_limiter.py: test_token_bucket_acquire, test_wait_and_acquire, test_thread_safety, test_timeout_handling - ≥90% coverage target
- [ ] T044c [P] [US1] Write unit tests for circuit_breaker.py and resilience patterns: test_failure_threshold, test_recovery_timeout, test_half_open_state, test_success_reset, test_circuit_breaker_integration_with_api_clients (verify CircuitBreakerManager from T028 prevents cascading failures across GitHub/Twitter/LinkedIn clients per NFR-012) - ≥90% coverage target
- [ ] T044d [S] [US1] Write integration tests for search orchestration: test_execute_search_multi_platform, test_result_aggregation, test_deduplication, test_ally_type_filtering, test_relevance_scoring - backend/tests/integration/test_search_api.py
- [ ] T044e [S] [US1] Write integration tests for FAISS indexing: test_index_resume, test_index_content, test_vector_search_accuracy, test_cosine_similarity_threshold - backend/tests/integration/test_faiss_service.py
- [ ] T044f [S] [US1] Write integration tests for embedding service: test_encode_single, test_encode_batch, test_embedding_dimensions, test_similarity_calculation - backend/tests/integration/test_embedding_service.py
- [ ] T044g [S] [US1] Achieve ≥80% test coverage for Phase 2 code: run pytest --cov=src --cov-report=html, verify API client resilience, validate search orchestration, document coverage in htmlcov/index.html
- [ ] T044h [P] [US1] Write unit tests for ToS compliance validation (FR-012): test_check_github_tos (validates rate limits, allowed endpoints), test_check_twitter_tos (validates 15min window, max_results limits), test_check_linkedin_tos (validates public-only access, robots.txt compliance, manual URL input requirement), test_compliance_error_raising - backend/tests/unit/test_compliance.py - ≥90% coverage target
- [x] T044i [P] [US1] Write live GitHub API integration test: test_github_search_real_api in backend/tests/integration/test_github_live_api.py that makes actual API call to GitHub Users Search API (e.g., search for 'torvalds' or 'guido'), validates response structure (login, id, avatar_url, html_url fields present), verifies rate limit headers (X-RateLimit-Remaining, X-RateLimit-Reset), confirms data quality (results match search term), requires GITHUB_API_TOKEN in test environment, marked with @pytest.mark.live_api decorator for optional execution, skipped if token not configured

**Constitution Principle VI Compliance**: Phase 2 NOT complete until T044a-i finished with ≥80% coverage and all tests passing.

---

## Phase 3: Shadow Sequence Amplifier (21 tasks) - Weeks 7-9

**Goal**: P2 - Counter-query generation + bridge pitches

### LangChain & Claude Sonnet 4.5 Setup (4 tasks)

- [ ] T045 [P] [US2] Create backend/src/services/llm_service.py: LLMService class with anthropic.Anthropic client initialization, API key from settings.ANTHROPIC_API_KEY
- [ ] T046 [S] [US2] Implement LLM call wrapper: create_message(prompt, system_message, max_tokens=1024, temperature=0.7) using Claude Sonnet 4.5 (claude-sonnet-4-5-20250929), retry with tenacity (3 attempts), track token usage
- [ ] T047 [P] [US2] Add LLM cost tracking: track_api_usage(input_tokens, output_tokens), calculate cost ($3/million input, $15/million output), store in usage logs, per-user quota enforcement
- [ ] T048 [P] [US2] Implement response caching: cache LLM responses with TTL=24hr, cache key = hash(prompt + system_message + model), reduce API costs by ~70%

### Counter-Query Generation (5 tasks)

- [ ] T049 [S] [US2] Create backend/src/services/counter_query_generator.py: CounterQueryGenerator class with generate_counter_queries(query, ally_types) - **Note: Backend code uses "counter_query" terminology consistently; frontend UI may display as "Shadow Sequence" for user-facing context per spec.md Terminology Glossary**
- [ ] T050 [S] [US2] Implement counter-query LLM prompt: system message = "Generate 3-5 opposing viewpoints to the following query within the context of {ally_type.name} ({ally_type.keywords})", user message = query, parse JSON response [{counter_query, rationale}]
- [ ] T051 [S] [US2] Add counter-query quality validation: check if counter_queries are meaningfully different from original using cosine similarity between text embeddings (generate embeddings with sentence-transformers all-MiniLM-L6-v2 model from T034); **Validation**: for each counter_query, calculate `similarity = cosine_similarity(encode(counter_query), encode(original_query))`; PASS if similarity <0.7 (sufficiently divergent), FAIL if ≥0.7 (too similar); additionally validate relevance to ally_type keywords using keyword overlap (≥2 ally_type keywords must appear in counter_query or its context); retry if quality <90% (max 2 retries); track metric: percentage of counter_queries passing validation (target ≥90% per SC-010)
- [ ] T052 [S] [US2] Store counter-queries: update SearchQuery.counter_queries JSON field, timestamp generation
- [ ] T053 [S] [US2] Execute counter-query searches: for each counter_query, call search_orchestrator, tag results with "skeptic" perspective, merge with original results (deduplicate), mark as shadow_sequence=True in Contact metadata

### Bridge Pitch Generation (7 tasks)

- [ ] T054 [P] [US2] Create backend/src/models/bridge_pitch.py: BridgePitch model (id, user_profile_id FK, target_contact_id FK, template_type="bridge_pitch"|"outreach_template", resume_achievements_referenced JSON, ally_type_context, target_concerns Text nullable, target_interests JSON nullable, generated_message Text, collaboration_proposal Text, llm_model, llm_prompt_version, created_at)
- [ ] T055 [S] [US2] Create backend/src/services/bridge_pitch_generator.py: BridgePitchGenerator class with generate_pitch(contact, parsed_resume, ally_type)
- [ ] T056 [S] [US2] Implement bridge pitch LLM prompt: system message = "Create professional outreach message acknowledging {contact_concerns} from their content while highlighting {resume_achievements} relevant to {ally_type}", user message = formatted data, parse JSON response {message, collaboration_proposal, achievements_used}
- [ ] T057 [S] [US2] Extract target concerns: analyze Contact.profile_data + associated Content records, identify key interests/concerns using LLM or keyword extraction
- [ ] T058 [S] [US2] Match resume achievements: find ParsedResume.achievements with keywords matching contact's interests, calculate cosine similarity between resume embedding and contact content embeddings, filter matches with similarity ≥0.6, prioritize quantified achievements (e.g., "30% improvement"), return top 3 relevant achievements with match_scores, store in Contact.profile_data
- [ ] T059 [S] [US2] Validate resume achievement inclusion: verify at least 1 achievement from achievements_used appears in generated_message, fail if 0 (SC-005: 100% requirement), retry up to 2 times
- [ ] T060 [P] [US2] Create backend/src/api/routes/bridge_pitches.py: POST /bridge-pitches endpoint (contact_id), GET /bridge-pitches/{id}, GET /bridge-pitches (list user's pitches with pagination)

### Automated Testing - Phase 3 (5 tasks)

- [ ] T060a [P] [US2] Write unit tests for llm_service.py: test_create_message, test_retry_logic, test_token_usage_tracking, test_response_caching, test_cost_calculation - ≥85% coverage target
- [ ] T060b [P] [US2] Write unit tests for shadow_sequence_generator.py: test_generate_counter_queries, test_quality_validation (cosine_similarity <0.7), test_retry_on_low_quality, test_ally_type_context - ≥85% coverage target
- [ ] T060c [P] [US2] Write unit tests for bridge_pitch_generator.py: test_generate_pitch, test_extract_target_concerns, test_match_resume_achievements, test_achievement_inclusion_validation (SC-005: 100% requirement) - ≥85% coverage target
- [ ] T060d [S] [US2] Write integration tests for counter-query endpoints: test_generate_counter_queries, test_counter_query_search_execution, test_skeptic_perspective_tagging, test_result_merging - backend/tests/integration/test_shadow_sequence_api.py
- [ ] T060e [S] [US2] Achieve ≥80% test coverage for Phase 3 code: run pytest --cov=src --cov-report=html, verify LLM integration, validate counter-query quality (≥90% per SC-010), verify bridge pitch resume references (100% per SC-005), document coverage

**Constitution Principle VI Compliance**: Phase 3 NOT complete until T060a-e finished with ≥80% coverage and all tests passing.

---

## Phase 4: Organization Network Mapping (22 tasks) - Weeks 10-12

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
- [ ] T070 [S] [US3] Calculate connection paths: use NetworkX shortest_path(user_node, target_node), limit to paths ≤3 degrees, calculate connection_strength using formula: **connection_strength = (1.0 / path_length) × recency_factor** where recency_factor is determined by most recent shared connection date: 1.0 if connection <1 year old, 0.8 if 1-3 years old, 0.6 if 3-5 years old, 0.4 if >5 years old, 0.3 if date unknown (use ParsedResume.work_history dates or Contact.last_updated for recency calculation); example: 2-degree path with 6-month-old connection = (1.0/2) × 1.0 = 0.5 strength; 3-degree path with 4-year-old connection = (1.0/3) × 0.6 = 0.2 strength; paths with strength <0.4 filtered out per SC-006 requirement
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

### Automated Testing - Phase 4 (4 tasks)

- [ ] T078a [P] [US3] Write unit tests for organization_service.py: test_extract_companies_from_resume, test_create_or_update_organization, test_company_normalization - ≥85% coverage target
- [ ] T078b [P] [US3] Write unit tests for network_mapper.py: test_build_graph, test_node_creation, test_edge_creation, test_calculate_connection_paths, test_connection_strength_calculation - ≥85% coverage target
- [ ] T078c [S] [US3] Write integration tests for network mapping: test_network_graph_endpoint, test_connections_endpoint, test_warm_intro_suggestions, test_no_connections_alternative_strategies (US3 Acceptance Scenario 3) - backend/tests/integration/test_network_map_api.py
- [ ] T078d [S] [US3] Achieve ≥80% test coverage for Phase 4 code: run pytest --cov=src --cov-report=html, verify NetworkX graph algorithms, validate connection discovery (≥60% success per SC-006), document coverage

**Constitution Principle VI Compliance**: Phase 4 NOT complete until T078a-d finished with ≥80% coverage and all tests passing.

---

## Phase 5: Outreach Template Generator (15 tasks) - Weeks 13-14

**Goal**: P4 - Personalized outreach messages

### Outreach Template Generation (6 tasks)

- [ ] T079 [S] [US4] Update BridgePitch usage for outreach templates: set template_type="outreach_template", populate target_interests instead of target_concerns
- [ ] T080 [S] [US4] Create backend/src/services/outreach_template_generator.py: OutreachTemplateGenerator class with generate_template(contact, target_content, parsed_resume)
- [ ] T081 [S] [US4] Implement content interest extraction: analyze target's Content records (posts/issues), extract key topics using LLM or TF-IDF, identify primary interests/expertise areas
- [ ] T082 [S] [US4] Implement resume-interest matching: find ParsedResume achievements/skills matching target's interests, calculate match_score (0-1) using cosine similarity ≥0.6 between embeddings, return top 3 matches
- [ ] T083 [S] [US4] Implement outreach LLM prompt: system message = "Create authentic outreach message connecting {resume_achievements} to {target_interests} from {target_content}, propose collaboration on {shared_topic}", parse JSON response {message, collaboration_proposal, authenticity_score}
- [ ] T084 [S] [US4] Validate authenticity: check if message references specific content from target (URL, quote, topic), verify resume achievement connection, retry if authenticity_score <0.7 (up to 2 retries)

### Export Functionality (6 tasks)

- [ ] T085 [P] [US4] Create backend/src/api/routes/export.py: GET /export/search-results/{query_id} endpoint returns markdown file with search results, ally type matches, relevance scores
- [ ] T086 [P] [US4] Add GET /export/network-map/{user_id} endpoint: returns markdown + PNG (NetworkX graph visualization), includes connection paths, warm intro suggestions
- [ ] T087 [P] [US4] Add GET /export/outreach-templates endpoint: returns markdown with all user's templates, grouped by target ally_type, includes copy-paste ready messages
- [ ] T088 [S] [US4] Implement markdown formatting: for search results, format as table (Name | Title | Company | Relevance | Ally Type | Platform), include metadata (query, timestamp, results_count)
- [ ] T089 [S] [US4] Implement graph export: use NetworkX to_png() for network map visualization, include legend, optimize for 1920x1080 resolution, deliver within 10s (SC-009)
- [ ] T090 [S] [US4] Add batch export: GET /export/all endpoint returns ZIP file with search results + network maps + outreach templates, stream response for large files

### Automated Testing - Phase 5 (3 tasks)

- [ ] T090a [P] [US4] Write unit tests for outreach_template_generator.py: test_generate_template, test_content_interest_extraction, test_resume_interest_matching, test_authenticity_validation - ≥85% coverage target
- [ ] T090b [S] [US4] Write integration tests for export functionality: test_export_search_results, test_export_network_map, test_export_outreach_templates, test_batch_export_zip, test_export_speed_10s (SC-009) - backend/tests/integration/test_export_api.py
- [ ] T090c [S] [US4] Achieve ≥80% test coverage for Phase 5 code: run pytest --cov=src --cov-report=html, verify outreach template quality, validate export performance (<10s for 50 results per SC-009), document coverage

**Constitution Principle VI Compliance**: Phase 5 NOT complete until T090a-c finished with ≥80% coverage and all tests passing.

---

## Phase 6: Polish & Production Readiness (15 tasks) - Weeks 15-17

**Goal**: Production deployment with 99.5% uptime (includes testing and infrastructure)

### Frontend UI Polish (4 tasks)

- [ ] T091 [P] Create frontend/src/pages/onboarding.tsx: guided flow (1. Upload resume → 2. Define ally types → 3. First search), progress indicators, tooltips, complete within 5min (SC-001)
- [ ] T092 [P] Create frontend/src/components/ResumeUploader.tsx: drag-drop zone, file validation (PDF/DOCX/TXT, ≤10MB), upload progress bar, parsing status polling, display parsing_confidence
- [ ] T093 [P] Create frontend/src/components/AllyTypeManager.tsx: CRUD UI for ally types, keyword chip input, criteria textarea, search parameter toggles (GitHub/Twitter/LinkedIn), is_active toggle
- [ ] T094 [P] Create frontend/src/components/SearchResults.tsx: card layout for contacts, relevance score badges, ally type tags, filter by platform/ally_type, sort by relevance, pagination (20/page)
- [ ] T094a [P] [US1] Create frontend/src/components/ResultRatingWidget.tsx: 5-star rating component integrated into SearchResults cards, POST to /api/v1/search/results/{contact_id}/rate endpoint (from T043a), display average rating + rating count fetched from GET /api/v1/search/{query_id}/ratings, visual feedback on submit, validates rating 1-5, supports NFR-011 accuracy measurement (≥80% relevance via user ratings ≥4 stars)

### Performance Optimization (3 tasks)

- [ ] T095 [S] Implement Redis caching: cache search results (TTL=1hr), cache LLM responses (TTL=24hr), cache API responses per client TTLs, track cache hit rate (target >70%)
- [ ] T096 [S] Optimize FAISS queries: implement index sharding by user (user_id → index_file), periodic index optimization (rebuild after 1000 additions), consider Pinecone for production scale
- [ ] T097 [P] Optimize database queries: add indexes (user_id, created_at, ally_type_id, relevance_score), use SELECT DISTINCT for deduplication, implement query result caching in PostgreSQL

### Security & Monitoring (10 tasks)

- [ ] T098 [P] Implement API key encryption: encrypt ANTHROPIC_API_KEY, GITHUB_API_TOKEN, TWITTER_API_KEY in database using Fernet symmetric encryption, decrypt at runtime **Note: NFR-007 security requirement deferred to Phase 6 per risk acceptance - Phase 1-5 use environment variables only; production deployment in Phase 6 implements database encryption**
- [ ] T098a [P] Write unit tests for API key encryption: test_encrypt_api_key, test_decrypt_api_key, test_fernet_key_rotation, test_encryption_key_validation - ≥90% coverage target (NFR-007)
- [ ] T099 [P] Add input validation: sanitize all user inputs (query, ally_type.name, criteria), prevent SQL injection, prevent XSS in markdown export, max length limits
- [ ] T099a [P] Write unit tests for input validation: test_sanitize_query, test_prevent_sql_injection, test_prevent_xss, test_max_length_enforcement, test_special_character_handling - ≥90% coverage target (NFR-008)
- [ ] T100 [P] Setup logging: structured logging (JSON format), log levels (DEBUG/INFO/WARNING/ERROR), log API calls, search queries, LLM token usage, errors with stack traces
- [ ] T101 [P] Setup monitoring: Prometheus metrics (API response times, error rates, cache hit rates, LLM costs), Grafana dashboards, alerting for uptime <99.5% (SC-008)
- [ ] T102 [S] Run comprehensive integration tests across all phases: end-to-end user journey (registration → resume upload → ally type creation → search → counter-queries → network mapping → outreach generation → export), cross-phase integration validation, verify all Success Criteria (SC-001 through SC-010), generate final combined coverage report showing ≥80% across entire codebase
- [ ] T103 [S] Setup production deployment infrastructure (SC-008): **Platform Decision Matrix** (score 0-10 each criterion, select highest total): (1) Cost: PostgreSQL add-on + 2 instances <$50/mo, (2) Auto-scaling: supports 2-10 instances with CPU/memory triggers, (3) PostgreSQL: managed service ≥15GB storage, (4) Health checks: native /health endpoint monitoring with auto-restart, (5) Uptime SLA: ≥99.5% guarantee. **Recommended**: Railway (score ~42/50) for dev-friendly pricing + PostgreSQL + auto-scaling. **Note**: Platform selection requires project lead approval before proceeding with configuration. After platform selection approval: configure load balancer, auto-scaling (2-10 instances), health checks (/health polling every 30s), SSL/TLS certificates (Let's Encrypt), environment variable management (platform secrets), database connection pooling (SQLAlchemy pool_size=10, max_overflow=20)
- [ ] T104 [P] Create deployment documentation: README.md with setup instructions, .env.example with all variables, Docker Compose for local dev, deployment guide for cloud platforms (Heroku/Render/Railway)
- [ ] T105 [P] Create database migration guide: Alembic migration scripts for all schema changes, rollback procedures, data migration scripts for existing users (if any)
- [ ] T105a [S] **PREREQUISITE FOR T106** Establish 10-user baseline performance: Run k6 load test with 10 concurrent users (5 min duration, 1 min ramp-up) against POST /api/v1/search endpoint, measure average response time and p95 latency, document actual baseline (target: ≤30s average per NFR-001, but measure real performance), results inform NFR-005 degradation calculations (max acceptable at 100 users = baseline × 1.2), store baseline metrics in performance-baseline.md for comparison during T106 and T106a
- [ ] T106 [P] Final end-to-end testing: complete user journey from registration → resume upload → ally type creation → search → network mapping → outreach generation → export, verify all success criteria (SC-001 through SC-010), **load testing with 100 concurrent users** (test duration: 10 minutes, ramp-up: 0→100 users over 2 minutes, target endpoint: POST /api/v1/search, success threshold: p95 latency <45s at 100 concurrent users per NFR-005, compare against T105a measured baseline, measure performance degradation must not exceed 20% increase from T105a baseline), performance benchmarks using k6 load testing tool with script reusable from T105a
- [ ] T106a [S] Intermediate load testing for NFR-005 validation: **REQUIRES T105a baseline completion first** - progressive load tests at 25, 50, 75 concurrent users (5 min duration each, same ramp-up pattern as T106), measure average search response time at each level, verify performance degradation ≤20% from T105a measured 10-user baseline to each intermediate level, document performance curve to validate linear scaling assumption before 100-user test, use k6 load testing tool with script reusable from T105a/T106, generates performance report showing: baseline (10 users: T105a measured avg), intermediate levels (25/50/75 users: measure avg response time), validates degradation threshold before final 100-user test
- [ ] T107 [P] Quarterly ToS compliance review: Create backend/src/integrations/compliance_review.py with check_platform_tos_updates() function that documents ToS versions checked (GitHub, Twitter, LinkedIn, Apollo) with review_date timestamp; scheduled task runs quarterly to validate rate limits, allowed endpoints, forbidden patterns haven't changed; updates ComplianceError rules if platform ToS updated; stores review results in compliance_audit_log table (platform, tos_version, review_date, changes_detected, action_taken); addresses FR-012 periodic compliance validation requirement

---

## Task Summary by Phase

| Phase     | Tasks           | Focus                                        | Target User Story |
| --------- | --------------- | -------------------------------------------- | ----------------- |
| 1         | 30 (T001-T022g) | Foundation, Auth, Resume, Ally Types + Tests | US1 (P1)          |
| 2         | 31 (T023-T044i) | Multi-Platform Search + Tests                | US1 (P1)          |
| 3         | 21 (T045-T060e) | Shadow Sequence Amplifier + Tests            | US2 (P2)          |
| 4         | 22 (T061-T078d) | Organization Network Mapping + Tests         | US3 (P3)          |
| 5         | 15 (T079-T090c) | Outreach Template Generator + Tests          | US4 (P4)          |
| 6         | 20 (T091-T107)  | Polish, Integration Testing & Production     | All               |
| **Total** | **139**         |                                              |                   |

## Critical Path

Sequential dependencies (must execute in order):

1. T001-T005 (setup) → T006-T008 (auth) → T009-T012 (models) → T013-T017 (resume parsing) → T018-T022 (ally types) → **T022a-T022g (automated tests - COMPLETE ✅)**
2. T023-T029 (API clients + models) → T034-T037 (FAISS setup) → T038-T044 (search orchestration) → **T044a-T044i (Phase 2 automated tests - required before Phase 3)**
3. T045-T048 (LLM setup) → T049-T053 (counter-queries) → T054-T060 (bridge pitches) → **T060a-T060e (Phase 3 automated tests - required before Phase 4)**
4. T061-T065 (org data) → T066-T071 (network graph) → T072-T078 (visualization) → **T078a-T078d (Phase 4 automated tests - required before Phase 5)**
5. T079-T084 (outreach templates) → T085-T090 (export) → **T090a-T090c (Phase 5 automated tests - required before Phase 6)**
6. T091-T094 (UI polish) → T095-T097 (performance) → T098-T101 (security/monitoring) → T102 (integration tests) → T103-T106 (production deployment)

**Constitution Principle VI**: Each phase MUST complete its automated test tasks (T0XXa-T0XXg pattern) with ≥80% coverage before proceeding to next phase. Phase-specific tests ensure quality gates at each development milestone.

**Parallelizable**: Within each phase, [P] tasks can run simultaneously across multiple developers.

## Success Criteria Mapping

| SC     | Description                      | Tasks                  |
| ------ | -------------------------------- | ---------------------- |
| SC-001 | Upload + define ally types <5min | T001-T022, T090-T092   |
| SC-002 | Search results <30s              | T037-T043, T094-T096   |
| SC-003 | Relevance ≥80%                   | T038-T039, T093        |
| SC-004 | Resume parsing ≥95%              | T014-T016, T022c, T102 |
| SC-005 | Bridge pitch resume refs 100%    | T057-T058, T059        |
| SC-006 | Network connections ≥60%         | T066-T070, T073-T074   |
| SC-007 | Multi-platform indexing 100%     | T023-T026, T037-T043   |
| SC-008 | Uptime ≥99.5%                    | T097-T103              |
| SC-009 | Export <10s for 50 results       | T084-T089              |
| SC-010 | Counter-query quality ≥90%       | T049-T050              |
| FR-015 | Secure authentication            | T006-T008, T022d       |

**Note**: Constitution v2.1.0 Principle VI requires automated tests for all phases. Phase 1 tests are T022a-T022g.
