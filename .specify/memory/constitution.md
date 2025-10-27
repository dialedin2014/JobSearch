<!--
Sync Impact Report:
- Version change: 1.1.0 → 2.0.0
- Modified principles: 
  - I. RAG-First AI Architecture: Ollama → Claude 3 Sonnet (Anthropic API)
- Modified sections: Technology Stack Standards (AI/ML Stack updated)
- Changed: Ollama (Llama3) → Claude 3 Sonnet via Anthropic API
- Rationale: Claude 3 Sonnet provides superior reasoning quality for complex career analysis, better confidence scoring consistency, and higher reliability for meeting success criteria (85% relevance ratings). External API dependency accepted for quality gains.
- Version bump justification: MAJOR (2.0.0) - Backward incompatible architectural change from local LLM to external API dependency
- Templates requiring updates:
  ✅ Updated constitution.md Principle I and Technology Stack Standards
  ✅ Updated plan-template.md Constitution Check (Ollama → Claude 3 Sonnet)
  ✅ Updated tasks-template.md foundational tasks (LLM connection setup)
- Follow-up TODOs: 
  - Configure Anthropic API key management in .devcontainer.json
  - Update requirements.txt to include anthropic Python SDK
  - Implement API rate limiting and cost monitoring for Anthropic API calls
-->

# JobSearch Platform Constitution

## Core Principles

### I. RAG-First AI Architecture
Every AI-powered feature MUST use Retrieval-Augmented Generation (RAG) patterns with proper vector indexing; LangChain components are required for document loading, processing, and chain orchestration; FAISS vector search MUST be implemented for semantic similarity; Claude 3 Sonnet (Anthropic API) MUST be used for all LLM reasoning tasks requiring high-quality analysis, explanations, and confidence scoring.

**Rationale**: Ensures consistent, maintainable AI architecture while providing semantic search capabilities essential for professional networking and job search functionality. Claude 3 Sonnet provides superior reasoning quality for complex career analysis and better meets success criteria targets (85% relevance ratings) compared to local models.

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

## Technology Stack Standards

**Core Languages**: Python 3.12 exclusively for all business logic and backend services  
**AI/ML Stack**: LangChain + LangChain Community + Claude 3 Sonnet (Anthropic API) + Hugging Face Embeddings (sentence-transformers/all-MiniLM-L6-v2)  
**Vector Search**: FAISS (faiss-cpu) for all similarity search and document indexing  
**Backend Framework**: FastAPI for REST API services with automatic OpenAPI documentation  
**Frontend Framework**: React or Next.js for professional UI components and user experience  
**Development Environment**: VS Code + Dev Containers + GitHub Copilot  
**Testing**: pytest + pylint (backend) with GitHub Actions CI/CD; frontend testing per framework standards  
**Version Control**: GitHub Enterprise with Pull Request workflows  
**External APIs**: Apollo (enrichment), GitHub API, Twitter API, LinkedIn public API  
**Visualization**: NetworkX + Matplotlib for relationship mapping  

All Python dependencies MUST be pinned to specific versions in requirements.txt. Frontend dependencies MUST be pinned in package.json. No runtime pip installs are permitted.

## Development Workflow

**Branch Strategy**: Feature branches following `###-feature-name` pattern with corresponding spec directories  
**Code Review**: All changes require PR approval with automated pylint and pytest validation for backend; frontend linting per framework standards  
**Testing Gates**: Constitution compliance check → Unit tests → Integration tests → Manual feature validation  
**Deployment**: Backend and frontend deployment strategy per hosting platform requirements  
**Documentation**: Each feature requires spec.md, plan.md, and tasks.md following established templates  

## Governance

This constitution supersedes all other development practices and coding standards. All feature specifications, implementation plans, and code reviews MUST verify compliance with these principles. Complexity must be justified against user value and aligned with priority-driven development. 

Amendment Process: Changes require documented rationale, impact analysis, and migration plan. Breaking changes require MAJOR version increment. New principles or expanded guidance require MINOR version increment.

**Version**: 2.0.0 | **Ratified**: 2025-10-26 | **Last Amended**: 2025-10-26
