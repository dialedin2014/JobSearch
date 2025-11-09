<!--
Sync Impact Report:
- Version change: 2.0.0 → 2.1.0
- Modified principles:
  - I. RAG-First AI Architecture: Claude 3 Sonnet → Claude Sonnet 4.5 (model upgrade)
  - NEW VI. Test-Driven Phase Completion: Phases not complete without automated tests
- Modified sections: Technology Stack Standards (AI/ML Stack model version updated)
- Added sections: New Principle VI (Test-Driven Phase Completion)
- Changed: Claude 3 Sonnet → Claude Sonnet 4.5 (claude-sonnet-4-5-20250929)
- Rationale: Claude Sonnet 4.5 provides enhanced reasoning capabilities and performance improvements. New testing principle enforces quality gate: manual validation alone insufficient for phase completion.
- Version bump justification: MINOR (2.1.0) - New principle added (Test-Driven Phase Completion) + non-breaking model upgrade
- Templates requiring updates:
  ✅ Updated constitution.md Principle I and Technology Stack Standards
  ✅ Updated constitution.md with new Principle VI
  ✅ plan-template.md Constitution Check (added Test-Driven Phase Completion check)
  ✅ tasks-template.md foundational tasks (LLM model version updated + pytest setup added)
  ✅ checklist-template.md: Added automated test verification section
  ⚠ spec-template.md: Already has good testing guidance in acceptance scenarios (no changes needed)
- Follow-up TODOs:
  - Phase 1 (001-civic-ally-hunter) requires automated pytest tests before considered complete
  - Create pytest test suite covering auth, resume parsing, ally type CRUD
  - Update phase completion criteria in all active specs
-->

# JobSearch Platform Constitution

## Core Principles

### I. RAG-First AI Architecture

Every AI-powered feature MUST use Retrieval-Augmented Generation (RAG) patterns with proper vector indexing; LangChain components are required for document loading, processing, and chain orchestration; FAISS vector search MUST be implemented for semantic similarity; Claude Sonnet 4.5 (claude-sonnet-4-5-20250929 via Anthropic API) MUST be used for all LLM reasoning tasks requiring high-quality analysis, explanations, and confidence scoring.

**Rationale**: Ensures consistent, maintainable AI architecture while providing semantic search capabilities essential for professional networking and job search functionality. Claude Sonnet 4.5 provides superior reasoning quality, enhanced performance, and better meets success criteria targets (85% relevance ratings) compared to previous models.

### II. Privacy & Ethical Data Use

All data collection MUST use only public sources with explicit ToS compliance; Personal data processing requires user consent and clear value exchange; API rate limits MUST be strictly respected; Ethical filtering MUST be embedded in prompts and code to prevent harmful content generation; No private scraping or unauthorized data collection is permitted.

**Rationale**: Establishes trust with users and maintains legal compliance while enabling powerful networking capabilities. Protects both the platform and users from potential legal issues.

### III. Container-Native Development

All development MUST occur within Dev Container environments; Dependencies MUST be declared in requirements.txt or devcontainer.json; Local development environment consistency is enforced via .devcontainer configuration; Docker containerization ensures reproducible builds and deployments.

**Rationale**: Eliminates "works on my machine" issues and ensures consistent development environment across team members. Critical for complex AI/ML dependency management.

### IV. Priority-Driven Feature Development

Features MUST be broken into independently testable user stories with P1/P2/P3 priorities; P1 stories MUST deliver standalone value as MVPs; Each user story MUST be implementable, testable, and deployable independently; Feature specifications MUST include clear acceptance scenarios using Given/When/Then format.

**Rationale**: Enables incremental delivery of value and reduces integration risks. Allows for early user feedback and iterative improvement of AI-powered networking features.

### V. API Rate Limiting & Resilience

All external API integrations (GitHub, Twitter/X, LinkedIn, Apollo) MUST implement proper rate limiting and exponential backoff; Graceful degradation is required when APIs are unavailable; Circuit breaker patterns MUST be used for third-party dependencies; Local caching strategies are mandatory to minimize API calls.

**Rationale**: Ensures platform reliability and prevents service disruption due to external API limitations. Critical for maintaining user experience when processing large volumes of networking data.

### VI. Test-Driven Phase Completion

A development phase is NOT complete until automated tests are written and passing; Manual validation alone is insufficient; All API endpoints MUST have pytest integration tests; All service layer logic MUST have pytest unit tests; Test coverage MUST be measured and reported; Phases cannot proceed to "validated" status without a passing automated test suite.

**Rationale**: Ensures code quality, prevents regressions, and enables confident refactoring. Manual testing is error-prone and non-repeatable. Automated tests serve as executable documentation and catch bugs early in development cycle.

## Technology Stack Standards

**Core Languages**: Python 3.12 exclusively for all business logic and backend services  
**AI/ML Stack**: LangChain + LangChain Community + Claude Sonnet 4.5 (claude-sonnet-4-5-20250929 via Anthropic API) + Hugging Face Embeddings (sentence-transformers/all-MiniLM-L6-v2)  
**Vector Search**: FAISS (faiss-cpu) for all similarity search and document indexing  
**Backend Framework**: FastAPI for REST API services with automatic OpenAPI documentation  
**Frontend Framework**: React or Next.js for professional UI components and user experience  
**Development Environment**: VS Code + Dev Containers + GitHub Copilot  
**Testing**: pytest + pytest-cov (backend) with GitHub Actions CI/CD; frontend testing per framework standards  
**Linting**: ruff check (Python) for code quality enforcement  
**Version Control**: GitHub Enterprise with Pull Request workflows  
**External APIs**: Apollo (enrichment), GitHub API, Twitter API, LinkedIn public API  
**Visualization**: NetworkX + Matplotlib for relationship mapping

All Python dependencies MUST be pinned to specific versions in requirements.txt. Frontend dependencies MUST be pinned in package.json. No runtime pip installs are permitted.

## Development Workflow

**Branch Strategy**: Feature branches following `###-feature-name` pattern with corresponding spec directories  
**Code Review**: All changes require PR approval with automated ruff check and pytest validation for backend; frontend linting per framework standards  
**Testing Gates**: Constitution compliance check → Unit tests (pytest) → Integration tests (pytest) → Manual feature validation → Phase complete only when automated tests pass  
**Deployment**: Backend and frontend deployment strategy per hosting platform requirements  
**Documentation**: Each feature requires spec.md, plan.md, and tasks.md following established templates

## Governance

This constitution supersedes all other development practices and coding standards. All feature specifications, implementation plans, and code reviews MUST verify compliance with these principles. Complexity must be justified against user value and aligned with priority-driven development.

Amendment Process: Changes require documented rationale, impact analysis, and migration plan. Breaking changes require MAJOR version increment. New principles or expanded guidance require MINOR version increment.

**Version**: 2.1.0 | **Ratified**: 2025-10-26 | **Last Amended**: 2025-11-09
