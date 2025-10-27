# Feature Specification: Dream Job Ally Deduction

**Feature Branch**: `002-dream-job-ally-deduction`  
**Created**: October 26, 2025  
**Status**: Draft  
**Input**: User description: "instead of the user supplying a list of ally types, the user will supply a description of their dream job and the ally types will be deduced from that and their resume"

## Clarifications

### Session 2025-10-26

- Q: The spec mentions resume parsing and dream job analysis but doesn't specify how the system deduces ally types from this data. What algorithm or approach should drive the core deduction logic? → A: LLM-based reasoning: Large language model analyzes resume+dream job and generates ally types with natural language explanations
- Q: The spec mentions "confidence scores above 0.8" and "relevance score (0.0-1.0)" but doesn't clarify what specifically determines these scores. What factors should influence the relevance/confidence scoring? → A: Pure LLM confidence: Score reflects only the LLM's internal confidence in its reasoning for each ally type
- Q: The spec mentions searching "GitHub issues, Twitter/X posts, and LinkedIn profiles" but doesn't specify the search strategy. How should the system construct search queries from deduced ally types? → A: LLM-generated search terms: Ask LLM to generate platform-specific search queries based on each ally type
- Q: When resume parsing fails or dream job descriptions are vague (mentioned in edge cases), what should the system's fallback behavior be? → A: Interactive clarification: Prompt user with specific questions to fill information gaps identified by the LLM
- Q: The spec mentions maintaining "99% uptime during business hours" but doesn't define which hours constitute "business hours" for a potentially global user base. What timezone/hours should this target? → A: US business hours: 9 AM - 6 PM Eastern Time as primary market focus

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Dream Job Analysis and Resume Processing (Priority: P1)

A job seeker uploads their resume and provides a detailed description of their dream job. The system analyzes both documents to extract relevant skills, experience, and career aspirations, then intelligently deduces the types of professional allies that would be most valuable for achieving their career goals.

**Why this priority**: Foundation functionality that eliminates the manual burden of defining ally types - users often don't know which ally types would be most beneficial, making this automated analysis essential for platform adoption and effectiveness.

**Independent Test**: Can be fully tested by uploading a resume and dream job description, then verifying that the system produces a ranked list of relevant ally types with explanations for why each was selected.

**Acceptance Scenarios**:

1. **Given** user uploads resume showing "Software Engineer with 3 years Python/ML experience" and dream job "AI Product Manager at tech startup", **When** system processes both documents, **Then** system deduces ally types including "AI/ML Technical Leaders", "Product Management Veterans", "Startup Founders" with confidence scores above 0.8
2. **Given** user's resume lacks direct experience in dream job field, **When** analysis completes, **Then** system identifies bridge ally types that connect current skills to target role (e.g., "Career Transition Mentors", "Skills Development Coaches")
3. **Given** dream job description is vague or generic, **When** processing occurs, **Then** system prompts user with LLM-generated clarification questions about industry preferences, company size, and role responsibilities to complete the analysis

---

### User Story 2 - Intelligent Ally Discovery and Matching (Priority: P2)

Using the deduced ally types from the user's dream job analysis, the system searches across GitHub, Twitter/X, and LinkedIn to discover professionals who match these ally categories, ranking results by relevance to both the user's background and career aspirations.

**Why this priority**: Provides immediate value by finding relevant connections without requiring users to understand complex search strategies or professional networking nuances.

**Independent Test**: Can be tested by taking deduced ally types and verifying that search results contain professionals whose expertise aligns with the user's career transition needs.

**Acceptance Scenarios**:

1. **Given** system deduced ally types "AI/ML Technical Leaders" and "Product Management Veterans" from dream job analysis, **When** ally discovery runs, **Then** search results include professionals with relevant titles, publications, and experience in both AI/ML and product management domains
2. **Given** user's current role as "Backend Developer" with dream job "DevOps Engineer", **When** matching occurs, **Then** results prioritize allies who successfully transitioned from development to DevOps roles
3. **Given** ally discovery completes, **When** user views results, **Then** each potential ally shows explanation of why they were selected and how they relate to the user's career goals

---

### User Story 3 - Personalized Career Transition Strategy (Priority: P3)

The system analyzes gaps between the user's current background and dream job requirements, then suggests specific ally types who can help bridge those gaps through mentorship, skill development, or strategic introductions.

**Why this priority**: Advanced feature that provides strategic career guidance by matching specific development needs with appropriate ally types, maximizing the value of professional networking efforts.

**Independent Test**: Can be tested by comparing current resume skills with dream job requirements, then verifying that suggested ally types address identified skill gaps and career advancement needs.

**Acceptance Scenarios**:

1. **Given** resume shows "Junior Frontend Developer" and dream job requires "Full-Stack Team Lead experience", **When** gap analysis runs, **Then** system suggests ally types like "Senior Full-Stack Engineers", "Engineering Managers", "Leadership Development Coaches"
2. **Given** significant skill gaps exist between current role and dream job, **When** strategy generation occurs, **Then** system provides timeline suggestions for engaging different ally types (e.g., "Connect with Senior Engineers first, then approach Engineering Managers after 6 months")
3. **Given** user has strong technical skills but dream job requires business acumen, **When** analysis completes, **Then** system prioritizes ally types like "Technical Product Managers", "Engineering-to-Business Career Coaches", "Startup CTOs"

---

### User Story 4 - Dynamic Career Goal Refinement (Priority: P4)

As users interact with discovered allies and gain insights, they can update their dream job descriptions, and the system automatically refines ally type recommendations based on new career clarity and networking feedback.

**Why this priority**: Iterative improvement feature that acknowledges career goals evolve through networking conversations, ensuring ally recommendations remain relevant as users gain career clarity.

**Independent Test**: Can be tested by updating dream job descriptions and verifying that ally type recommendations adjust appropriately while maintaining continuity with previous networking efforts.

**Acceptance Scenarios**:

1. **Given** user initially wanted "AI Product Manager" but updates to "AI Ethics Researcher" after ally conversations, **When** re-analysis occurs, **Then** system shifts ally types from "Product Management" focus to "AI Ethics", "Research Community", "Academic Partnerships"
2. **Given** user has established connections with certain ally types, **When** dream job refinement happens, **Then** system suggests expanding network in complementary ally categories rather than duplicating existing connections
3. **Given** multiple dream job updates over time, **When** user views ally history, **Then** system shows evolution of ally type recommendations with explanations for each change

---

### Edge Cases

- When resume parsing fails to extract meaningful skills or experience data, system prompts user with interactive clarification questions to gather missing information
- When dream job descriptions are vague or generic, system uses LLM to generate specific clarification questions about career goals
- What occurs when deduced ally types yield no search results across all platforms?
- How does system respond when user's current background is completely unrelated to their dream job aspirations?
- What happens when dream job description contains conflicting or contradictory requirements?
- How does system handle resumes with extensive experience that could lead to multiple valid career paths?
- What occurs when external APIs (LinkedIn, GitHub, Twitter) are unavailable during ally discovery?
- How does system manage when dream job market conditions change significantly between analysis sessions?

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: Users MUST be able to upload resume documents in standard formats (PDF, Word, plain text) for analysis
- **FR-002**: Users MUST be able to provide detailed dream job descriptions through text input or structured forms
- **FR-003**: System MUST parse resume documents to extract skills, experience levels, job titles, companies, education, and achievements
- **FR-003a**: When resume parsing fails or dream job description is insufficient, system MUST prompt users with LLM-generated clarification questions to gather missing information before ally type deduction
- **FR-004**: System MUST analyze dream job descriptions to identify required skills, experience, industry, company type, and role responsibilities
- **FR-005**: System MUST deduce relevant ally types using LLM-based reasoning that analyzes both resume and dream job description to generate appropriate professional categories with natural language explanations for each selection
- **FR-006**: System MUST rank deduced ally types by confidence score (0.0-1.0) reflecting the LLM's internal confidence in its reasoning for each ally type recommendation
- **FR-007**: System MUST provide clear explanations for why each ally type was selected and how it relates to the user's career goals
- **FR-008**: System MUST generate platform-specific search queries using LLM to translate each deduced ally type into appropriate search terms for GitHub, Twitter/X, and LinkedIn
- **FR-009**: System MUST rank discovered allies by relevance to user's background and career aspirations
- **FR-010**: System MUST identify skill gaps between current background and dream job requirements
- **FR-011**: System MUST suggest timeline strategies for engaging different ally types based on career transition complexity
- **FR-012**: Users MUST be able to update dream job descriptions and receive refined ally type recommendations
- **FR-013**: System MUST maintain history of ally type evolution as career goals change over time
- **FR-014**: System MUST respect rate limits and terms of service for all external APIs (GitHub, Twitter, LinkedIn)
- **FR-015**: System MUST provide web interface for resume upload, dream job input, and ally discovery results visualization

### Key Entities *(include if feature involves data)*

- **User Profile**: Individual user account containing uploaded resume data, parsed skills and experience, current role information, and career history
- **Dream Job Description**: User-provided text describing target career goals including desired role, industry, company type, responsibilities, and required skills
- **Parsed Resume**: Structured data extracted from resume including skills, experience levels, job titles, companies, education, achievements, and career timeline
- **Career Gap Analysis**: Comparison between current background and dream job requirements identifying skill deficiencies, experience gaps, and bridging opportunities
- **Deduced Ally Type**: System-generated professional category relevant to user's career transition including type name, confidence score, selection rationale, LLM-generated platform-specific search queries, and engagement strategy
- **Ally Confidence Score**: LLM-generated metric (0.0-1.0) reflecting the model's confidence in its reasoning for recommending a specific ally type based on resume and dream job analysis
- **Professional Ally**: Individual discovered through search with profile information, expertise areas, career background, contact details, and match explanation
- **Career Transition Strategy**: Generated roadmap suggesting sequence and timing for engaging different ally types based on career complexity and goals
- **Skill Gap**: Identified deficiency between current capabilities and dream job requirements including gap severity, learning resources, and ally types who can provide guidance
- **Dream Job Evolution**: Historical record of how user's career goals have changed over time with corresponding ally type recommendation adjustments

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: Users can upload resume and provide dream job description within 3 minutes of platform access
- **SC-002**: System deduces relevant ally types within 30 seconds of receiving resume and dream job inputs
- **SC-003**: Resume parsing successfully extracts meaningful skills and experience from 95% of uploaded documents
- **SC-004**: Users rate deduced ally types as "relevant" or "highly relevant" in 85% of cases based on career goals alignment
- **SC-005**: System identifies at least 3 distinct ally types for 90% of career transition scenarios
- **SC-006**: Discovered allies match deduced ally type criteria with 80% accuracy as measured by user feedback
- **SC-007**: Career gap analysis identifies skill deficiencies that users confirm as accurate in 85% of assessments
- **SC-008**: Users find at least 5 relevant potential allies within their deduced ally types within 2 minutes of ally discovery
- **SC-009**: System processes dream job description updates and provides refined ally recommendations within 15 seconds
- **SC-010**: Platform maintains career goal evolution history for 100% of users who update dream job descriptions
- **SC-011**: 75% of users successfully connect with at least one ally within 30 days of using deduced ally type recommendations
- **SC-012**: System maintains 99% uptime during US business hours (9 AM - 6 PM Eastern Time) for resume processing and ally deduction functionality

## Assumptions

- Users will provide detailed and honest dream job descriptions that accurately reflect their career aspirations
- Resume documents contain sufficient relevant information to enable meaningful skill and experience extraction
- Users understand the value of professional networking and are willing to engage with suggested allies
- Dream job market conditions and requirements remain relatively stable during the analysis and networking period
- Users can articulate their career goals clearly enough for the system to derive actionable ally types
- Professional allies discovered through public platforms are open to networking and career mentorship conversations
- The combination of resume analysis and dream job description provides sufficient context for accurate ally type deduction
- Users will update their dream job descriptions as their career goals evolve through networking interactions
- Industry-standard career transition patterns exist that can be analyzed and leveraged for ally type suggestions
- External platforms (GitHub, Twitter/X, LinkedIn) maintain stable APIs and accessible public data
- Natural language processing technology can accurately extract career-relevant information from unstructured text
- Users prefer automated ally type suggestions over manually defining professional networking categories

## Dependencies

- External APIs: GitHub API for developer profiles, Twitter/X API for professional content, LinkedIn public data access
- AI/ML Services: Large language model (LLM) API for ally type deduction with reasoning, natural language processing for resume parsing, semantic analysis for dream job description interpretation
- Document Processing: PDF and Word document parsing libraries, text extraction capabilities, structured data conversion tools
- Infrastructure: Vector database for career profile matching, web framework for user interface, secure file storage for resume documents
- User-provided Data: Resume documents in standard formats, detailed dream job descriptions, career goal updates and refinements
- Career Intelligence: Industry knowledge bases for skill requirements, professional role taxonomies, career transition pattern databases
- Authentication: Secure API key management for external service access, user session management, data privacy compliance