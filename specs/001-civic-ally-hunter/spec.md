# Feature Specification: Professional Ally-Hunting Platform

**Feature Branch**: `001-civic-ally-hunter`  
**Created**: October 26, 2025  
**Status**: ✅ Phase 1 Complete - Automated Tests Passing (Constitution v2.1.0 Principle VI Satisfied)  
**Input**: User description: "Professional Ally-Hunting Platform - A RAG-powered application that discovers and connects with professional allies across user-defined domains by analyzing GitHub issues, X/Twitter threads, and public LinkedIn data, featuring shadow sequence amplification and org mirage mapping for strategic networking based on user's resume and target ally types"

**✅ Constitution Compliance Achieved**: Phase 1 complete with 85.11% test coverage (exceeds 80% requirement). All 7 automated test tasks (T022a-T022g) implemented successfully with 89 passing tests. Constitution v2.1.0 Principle VI (Test-Driven Phase Completion) is now satisfied.

## Terminology Glossary

**Core Concepts**:

- **Ally Type**: User-defined professional category for targeting (e.g., "AI Researchers", "Fintech Investors"). Used to filter and classify search results.
- **Counter-Query** (technical term) / **Shadow Sequence** (user-facing term): Opposing viewpoints generated from original search query to discover skeptics and diverse perspectives. Backend code, API responses, and technical documentation use "counter-query". User-facing UI and marketing materials may use "shadow sequence" for clarity. Both refer to the same functionality described in User Story 2.
- **Bridge Pitch**: Personalized outreach message that acknowledges a target's skeptical concerns (from counter-query results) while highlighting relevant resume achievements.
- **Outreach Template**: Personalized collaboration message that connects user's resume achievements to target's demonstrated interests (from their posts/content).

## User Scenarios & Testing _(mandatory)_

### User Story 1 - Profile Setup and Ally Type Configuration (Priority: P1)

A professional uploads their resume and defines their target ally types (e.g., "AI researchers", "sustainability consultants", "fintech investors") with associated keywords, then searches for potential collaborators using semantic queries tailored to their specified domains.

**Why this priority**: Foundation functionality that personalizes the entire platform experience - without user context and ally definitions, search results lack relevance and personalization.

**Independent Test**: Can be fully tested by uploading a resume, defining ally types, and verifying that search results are filtered and ranked according to the specified criteria.

**Acceptance Scenarios**:

1. **Given** user uploads resume and defines ally types "AI researchers, sustainability experts", **When** user searches "machine learning climate solutions", **Then** system returns ranked results filtered to AI and sustainability professionals with relevance scores above 0.7
2. **Given** user has defined ally types, **When** viewing search results, **Then** each result shows which ally type category it matches and why (based on user's resume keywords)
3. **Given** no results found for query within specified ally types, **When** search completes, **Then** system suggests expanding ally type definitions or alternative search terms based on resume content
4. **Given** user wants to add LinkedIn profile to search results, **When** automated LinkedIn parsing is unavailable or rate-limited, **Then** system displays "Add LinkedIn Profile" input field where user can manually paste profile URL (e.g., linkedin.com/in/username), and system extracts name, title, company, and headline from public profile page (addressing Edge Case 6: LinkedIn rate limits)

---

### User Story 2 - Resume-Powered Counter-Query Generator (Priority: P2)

A user generates counter-arguments (opposing viewpoints) to their search query based on their defined ally types to find potential skeptics, then creates collaborative bridge pitches that reference specific resume achievements while acknowledging concerns and proposing mutual value opportunities.

**Terminology Note**: The technical term "counter-query" is used in backend implementation and API responses. User-facing documentation may refer to this feature as "Shadow Sequence Amplifier" for marketing purposes, but both terms refer to the same functionality: generating opposing viewpoints to discover diverse perspectives.

**Why this priority**: Differentiates from basic search by finding diverse perspectives and creating highly personalized outreach strategies based on user's actual background.

**Independent Test**: Can be tested by generating counter-queries from ally type searches and creating bridge pitches that incorporate resume elements and demonstrate understanding of opposing viewpoints.

**Acceptance Scenarios**:

1. **Given** user searches for "AI researchers" with query "machine learning optimization", **When** counter-query is generated, **Then** system produces skeptical perspectives like "AI bias concerns" or "ML interpretability challenges" relevant to the ally type
2. **Given** skeptic results are found within defined ally types, **When** bridge pitch is generated, **Then** outreach message references specific resume achievements that address the skeptical concerns
3. **Given** user's resume contains "Led 30% efficiency improvement via ML optimization", **When** bridge pitch targets ML skeptic, **Then** message acknowledges their concerns while highlighting relevant personal success metrics as potential collaboration value

---

### User Story 3 - Resume-Enhanced Organization Network Mapping (Priority: P3)

A user visualizes connection paths between themselves and target organizations within their defined ally types, leveraging resume-derived company connections and discovering warm introduction opportunities via network analysis and second-degree connections.

**Why this priority**: Advanced networking feature that provides strategic value by combining user's professional history with ally type targeting.

**Independent Test**: Can be tested by creating network graphs showing connections between resume-derived contacts and target organizations from ally type searches.

**Acceptance Scenarios**:

1. **Given** user's resume shows previous employment at Company X and search results include contacts at Partner Company Y, **When** network mapping is requested, **Then** visual graph shows potential paths through Company X alumni networks
2. **Given** network graph displays connection through former colleague, **When** user clicks on connection path, **Then** system shows mutual connection details and suggests introduction approach referencing shared work experience
3. **Given** no direct connections found via resume history, **When** network analysis runs within ally types, **Then** system suggests alternative strategies like industry events or professional associations relevant to the ally categories

---

### User Story 4 - Resume-Driven Outreach Templates (Priority: P4)

A user generates highly personalized outreach messages that reference specific resume achievements matching the target person's interests within defined ally types, creating contextually relevant collaboration proposals.

**Why this priority**: Maximizes response rates by creating authentic connections between user's demonstrated expertise and target ally's interests, but requires complete ally type configuration and resume analysis.

**Independent Test**: Can be tested by generating outreach templates that match specific resume elements to target ally profiles and interests within defined categories.

**Acceptance Scenarios**:

1. **Given** target "AI researcher" posts about neural networks and user's resume shows "Implemented CNN for 40% accuracy improvement", **When** outreach template is generated, **Then** message connects user's CNN experience to target's neural network interests
2. **Given** user defines "fintech investors" as ally type and resume shows "Led $2M cost reduction in financial systems", **When** template targets fintech investor, **Then** message highlights relevant financial impact metrics and suggests investment discussion
3. **Given** generated template for any ally type, **When** user reviews it, **Then** message authentically connects resume achievements to target's professional interests without appearing generic or automated

---

### Edge Cases & Resolution Strategies

1. **Resume with no extractable keywords or achievements**

   - **Detection**: parsing_confidence score <0.5 triggers warning
   - **Resolution**: Prompt user to manually enter key skills and achievements; offer guided form with common resume elements; allow skip with reduced matching accuracy warning

2. **Ally type definitions too broad or too narrow**

   - **Too Broad**: If search returns >500 results, suggest keyword refinement; show most common terms from results to help narrow focus
   - **Too Narrow**: If search returns <5 results, suggest expanding keywords; recommend related terms using semantic similarity from successful ally types

3. **No network connections found between resume history and ally types**

   - **Resolution**: Return alternative_strategies in SearchQuery.metadata: "Join {ally_type} professional associations", "Attend {industry} conferences", "Engage in {ally_type} online communities"; cite User Story 3 Acceptance Scenario 3

4. **Counter-query generation produces unrelated content**

   - **Detection**: Cosine similarity between counter_query and original query >0.7 indicates insufficient divergence
   - **Resolution**: Retry LLM call with stronger prompt (max 2 retries); if still fails, skip counter-query for that ally type; track quality metric (target 90% per SC-010)

5. **Resume parsing fails to identify skills or company connections**

   - **Detection**: Empty or very short fields in ParsedResume (skills, companies, achievements)
   - **Resolution**: Phase 1 stores raw text for manual review; Phase 2 enhancement with advanced NER models; user can edit extracted fields via UI

6. **LinkedIn rate limits during data collection**

   - **Scope**: LinkedIn integration uses **public profile viewing only** (no API access); allowed operations: manual URL input, public profile page parsing (name, title, company, headline); forbidden operations: automated scraping, bulk profile access, private data collection
   - **Detection**: Rate limiting errors, CAPTCHA challenges, or access denials during LinkedIn data collection
   - **Resolution**: Aggressive caching (24hr TTL per T025); **manual URL input as primary method** (user provides LinkedIn profile URLs); automated public page parsing as secondary option with strict rate limiting (max 10 profiles/hour); prioritize GitHub/Twitter data; display "LinkedIn data unavailable - please provide profile URL manually" message; circuit breaker prevents repeated failures (5 failures → 60s timeout)
   - **Compliance**: FR-012 requires ToS compliance - T029a validates that LinkedIn integration never uses private APIs, respects robots.txt, implements minimum 5-second delays between requests, and provides clear user disclosure about limitations

7. **Conflicting or overlapping ally types producing redundant results**
   - **Detection**: Same contact matched to multiple ally types with similar keywords
   - **Resolution**: Deduplicate by Contact.name + Contact.company; show all matched ally_types in UI; allow user to merge similar ally types via suggestions

## Requirements _(mandatory)_

### Functional Requirements

- **FR-001 Resume Upload & Parsing**: Users MUST be able to upload and parse resume documents to extract content
  - **Phase 1 (Current - COMPLETE)**: Simplified schema implemented in backend/src/models/resume.py with fields: id, user_id (FK), content (raw text), filename, file_type, created_at. Basic text extraction functional for TXT/PDF/DOCX formats. Parsing confidence: 72.5% on test data. Status: ✅ Working (validated Nov 9, 2025)
  - **Phase 2 (Planned - Tasks T014-T016 enhancement)**: Will extend ParsedResume model to add structured field extraction: skills (JSON), achievements (JSON), work_history (JSON), education (JSON), companies (JSON), keywords (JSON), parsing_confidence (float 0.0-1.0), parser_version (string). Advanced NER/pattern matching for entity extraction.
  - **Rationale**: Simplified Phase 1 schema enables faster P1 MVP delivery while deferring complex field extraction to Phase 2 when multi-platform search integration can validate extraction quality against real ally type searches
- **FR-002**: Users MUST be able to define custom ally types with associated keywords and criteria (e.g., "AI researchers: machine learning, neural networks, computer vision")
- **FR-003**: System MUST search GitHub issues, X/Twitter threads, and public LinkedIn profiles using semantic queries filtered by user-defined ally types; LinkedIn integration uses manual URL input as primary method with optional public profile parsing (rate-limited to 10 profiles/hour, 5-second delays, ToS-compliant per FR-012)
- **FR-003a**: System MUST accept LinkedIn profile URLs via text input field (format: linkedin.com/in/username or full URL) and parse publicly accessible profile HTML to extract: name (required), current title (required), company (required), headline/summary (optional); parsing failures MUST display user-friendly error message with retry option; extracted data stored in Contact.profile_data JSON with source="linkedin_manual_input"
- **FR-004**: System MUST rank search results by relevance score (0.0-1.0) calculated using cosine similarity between query embedding and content embeddings (sentence-transformers/all-MiniLM-L6-v2, 384-dim vectors); contacts with similarity ≥0.6 are considered matches; results sorted by descending match score; **keyword boost applied as: final_score = base_cosine_similarity × 1.2 when ≥2 ally_type keywords found in contact's content, capped at 1.0 maximum**
- **FR-005**: System MUST enrich contact information using Apollo API, filtered by ally type criteria
- **FR-006**: System MUST generate 3-5 counter-queries within ally type contexts that present opposing viewpoints to initial search terms
- **FR-007**: System MUST generate two types of personalized messages: (1) **Bridge Pitches** that reference specific resume achievements while addressing concerns from counter-query results (skeptical perspectives), and (2) **Outreach Templates** that connect resume achievements to target's demonstrated interests from their content; both types stored as template variants with discriminator field distinguishing their purpose
- **FR-008**: System MUST visualize network connections between user's resume-derived contacts and target ally organizations
- **FR-009**: System MUST match resume elements to ally profiles to identify collaboration opportunities
- **FR-010**: System MUST export search results, ally type mappings, and generated content in markdown format
- **FR-011**: System MUST respect rate limits for all external APIs (GitHub, X/Twitter, LinkedIn, Apollo)
- **FR-012**: System MUST use only public data sources and comply with platform terms of service
- **FR-013**: System MUST provide web interface for ally type management, resume upload, and result visualization
- **FR-014**: Users MUST be able to save and load ally type definitions and search configurations
- **FR-015**: System MUST implement JWT authentication with bcrypt password hashing and secure token validation

### Non-Functional Requirements

- **NFR-001 Performance - Search Response Time**: System MUST return search results within 30 seconds of query submission (SC-002)
- **NFR-002 Performance - Export Speed**: System MUST generate and deliver export files within 10 seconds for queries returning up to 50 results (SC-009)
- **NFR-003 Performance - Onboarding Flow**: User onboarding (resume upload + ally type definition) MUST complete within 5 minutes (SC-001)
- **NFR-004 Availability**: System MUST maintain 99.5% uptime during normal business hours (9 AM - 6 PM EST) (SC-008)
- **NFR-005 Scalability**: System MUST support 100+ concurrent users with consistent performance under load testing; **baseline performance at 10 concurrent users = 30s average search response time (TARGET to be established in Phase 6 via task T105a before load testing)** (per NFR-001); **performance degradation MUST NOT exceed 20% increase when scaling from 10 to 100 concurrent users** (max acceptable average at 100 users: 36s, calculated as 30s × 1.2); p95 latency MUST remain below 45 seconds at 100 concurrent users; measured via k6 load test script (see tasks.md T105a prerequisite + T106 main load test)
- **NFR-006 Security - Authentication**: System MUST use JWT tokens with secure HTTPBearer scheme and bcrypt password hashing (minimum 12 rounds)
- **NFR-007 Security - API Keys**: System MUST encrypt stored API keys using Fernet symmetric encryption and decrypt only at runtime
- **NFR-008 Security - Input Validation**: System MUST sanitize all user inputs to prevent SQL injection and XSS attacks with maximum length limits enforced
- **NFR-009 Data Privacy**: All data collection MUST comply with Constitution Principle II (public sources only, explicit ToS compliance, no private scraping)
- **NFR-010 Accuracy - Resume Parsing**: System MUST successfully extract resume content in 95% of uploaded documents (SC-004)
- **NFR-011 Accuracy - Relevance**: System MUST achieve 80% or higher relevance accuracy measured by user ratings of top 5 search results within ally categories; users rate results on 1-5 star scale; accuracy = percentage of results rated ≥4 stars; ratings stored in SearchResultRating table (search_query_id FK, contact_id FK, rating int 1-5, created_at); see plan.md API Design section for rating endpoints (SC-003)
- **NFR-012 Reliability - API Rate Limiting**: System MUST implement circuit breakers (failure_threshold=5, recovery_timeout=60s) and exponential backoff (1-10s delays) for all external API calls
- **NFR-013 Maintainability**: All Python code MUST pass ruff linting checks and maintain ≥80% test coverage per Constitution Principle VI

### Key Entities _(include if feature involves data)_

- **User Resume**: Parsed resume document containing skills, achievements, work history, education, and extractable keywords for ally matching
- **Ally Type**: User-defined professional category with name, keywords, criteria, and search parameters (e.g., "Fintech Investors", "AI Researchers", "Sustainability Consultants")
- **Contact**: Person identified from search results with name, title, company, location, email, phone, social profiles, relevance score, and matched ally type
- **Content**: Posts, issues, or threads from various platforms with text content, author, source platform, URL, metadata, and ally type classification
- **Organization**: Companies or institutions associated with contacts, including revenue, employee count, technologies used, industry classification, and ally type relevance
- **Network Connection**: Relationship between user's resume contacts and target allies showing connection type, shared organizations, and connection strength
- **Search Query**: User input with original query text, ally type filters, generated counter-queries, timestamp, and associated results
- **Bridge Pitch / Outreach Template**: Generated message templates stored with template_type discriminator; "bridge_pitch" addresses skeptical concerns from counter-queries with resume achievements; "outreach_template" connects resume achievements to target's demonstrated interests from their content; both include collaboration proposal
- **Ally Match Score**: Calculated relevance between contact and user's ally type definitions based on keywords, skills, and resume alignment

## Success Criteria _(mandatory)_

### Measurable Outcomes

- **SC-001**: Users can upload resume and define ally types within 5 minutes of platform access
- **SC-002**: Users can discover relevant contacts within their defined ally types within 30 seconds of entering a search query
- **SC-003**: System achieves 80% or higher relevance accuracy as measured by user rating of top 5 results within their ally categories
- **SC-004**: Resume parsing successfully extracts skills and achievements in 95% of uploaded documents
- **SC-005**: Bridge pitch generation incorporates specific resume elements in 100% of generated templates
- **SC-006**: Network mapping identifies at least one potential connection path (≤3 degrees of separation, connection_strength ≥0.4) for 60% of search queries that return ≥1 contact result within ally type filters; calculation excludes searches with zero results; measured as (queries_with_connection_path / queries_with_results) × 100; connection_strength calculated as weighted score combining path_length and relationship_recency (see plan.md Network Graph Building section)
- **SC-007**: System processes and indexes data from all three platforms for each ally type search query
- **SC-008**: Platform maintains 99.5% uptime during normal business hours (9 AM - 6 PM EST)
- **SC-009**: Export functionality delivers complete search results in under 10 seconds for queries returning up to 50 results
- **SC-010**: Counter-query generation produces meaningfully different perspectives from original query in 90% of attempts within ally type contexts

## Assumptions

- Users have access to required API keys (GitHub PAT, Apollo API key, Anthropic API key) for enhanced functionality
- Public LinkedIn data collection remains within platform terms of service limits
- Users will provide resume documents in standard formats (PDF, Word, plain text) for parsing
- Users can clearly define their target ally types with appropriate keywords and criteria
- Professionals across various industries value diverse perspectives and are open to collaborative approaches
- Resume parsing technology can accurately extract relevant skills, achievements, and company history
- Network effect increases as more users contribute ally type definitions and connection data
- Claude Sonnet 4.5 (claude-sonnet-4-5-20250929 via Anthropic API) provides sufficient quality for counter-query and bridge pitch generation across different professional domains with superior reasoning compared to previous models (Constitution v2.1.0 requirement)
- Users prefer web-based interface over command-line tools for this type of discovery work

## Dependencies

- External APIs: GitHub API, X/Twitter API, Apollo API, public LinkedIn endpoints, Anthropic API (Claude Sonnet 4.5)
- AI/ML Services: Claude Sonnet 4.5 (claude-sonnet-4-5-20250929) via Anthropic API for LLM reasoning, HuggingFace embeddings for semantic search (sentence-transformers/all-MiniLM-L6-v2), resume parsing libraries
- Infrastructure: FAISS vector database for search indexing, Next.js for web interface, PostgreSQL for data storage, file storage for resume documents
- User-provided data: Resume documents, ally type definitions, API keys (GitHub, Apollo, Anthropic), existing network contacts
- Document Processing: PyPDF2 for PDF parsing, python-docx for Word documents, text extraction and NLP for resume analysis
