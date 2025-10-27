# Data Model: Dream Job Ally Deduction

**Feature**: 002-dream-job-ally-deduction  
**Phase**: 1 - Design & Contracts  
**Date**: 2025-10-26

## Purpose

This document defines the core entities, relationships, validation rules, and state transitions for the Dream Job Ally Deduction feature, derived from the Key Entities section in the feature specification.

---

## Entity Relationship Diagram

```
┌─────────────────┐
│  UserProfile    │
└────────┬────────┘
         │ 1:N
         │
┌────────▼───────────────┐
│ DreamJobDescription    │
└────────┬───────────────┘
         │ 1:N
         │
┌────────▼──────────────┐       ┌──────────────────────┐
│  DeducedAllyType      │ N:M   │  ProfessionalAlly    │
└────────┬──────────────┘◄─────►└──────────────────────┘
         │ 1:1                   
         │                       
┌────────▼──────────────┐
│ AllyConfidenceScore   │
└───────────────────────┘

┌────────────────────────┐
│  ParsedResume          │◄───── Embedded in UserProfile
└────────────────────────┘

┌────────────────────────┐
│  CareerGapAnalysis     │◄───── Derived from UserProfile + DreamJob
└────────────────────────┘

┌──────────────────────────┐
│  CareerTransitionStrategy│◄── Generated from DeducedAllyTypes
└──────────────────────────┘

┌────────────────────────┐
│  SkillGap              │◄───── Component of CareerGapAnalysis
└────────────────────────┘

┌────────────────────────┐
│  DreamJobEvolution     │◄───── History tracking for DreamJob versions
└────────────────────────┘
```

---

## Entities

### 1. UserProfile

**Description**: Individual user account containing uploaded resume data, parsed skills and experience, current role information, and career history.

**Fields**:

| Field | Type | Constraints | Description |
|-------|------|-------------|-------------|
| `id` | UUID | PK, Required | Unique identifier |
| `user_id` | String | Unique, Required, FK | External auth system user ID |
| `email` | String | Unique, Required | User email for notifications |
| `created_at` | DateTime | Required | Account creation timestamp |
| `updated_at` | DateTime | Required | Last update timestamp |
| `resume_file_path` | String | Optional | S3/local path to uploaded resume |
| `resume_file_name` | String | Optional | Original filename |
| `resume_file_size` | Integer | Optional | File size in bytes (max 10MB) |
| `resume_upload_date` | DateTime | Optional | When resume was uploaded |
| `parsed_resume_id` | UUID | FK, Optional | Reference to ParsedResume |

**Validation Rules**:
- `email` must be valid email format (RFC 5322)
- `resume_file_size` ≤ 10,485,760 bytes (10MB)
- `resume_file_path` must be non-empty if `parsed_resume_id` exists

**Relationships**:
- 1:N with `DreamJobDescription` (one user, many dream job versions)
- 1:1 with `ParsedResume` (embedded/referenced)

---

### 2. ParsedResume

**Description**: Structured data extracted from resume including skills, experience levels, job titles, companies, education, achievements, and career timeline.

**Fields**:

| Field | Type | Constraints | Description |
|-------|------|-------------|-------------|
| `id` | UUID | PK, Required | Unique identifier |
| `user_id` | UUID | FK, Required | Reference to UserProfile |
| `raw_text` | Text | Required | Full extracted text from resume |
| `skills` | JSON Array | Required | List of identified skills ["Python", "ML", ...] |
| `experience_years` | Float | Optional | Total years of experience |
| `job_titles` | JSON Array | Required | List of held positions with dates |
| `companies` | JSON Array | Required | List of companies with dates |
| `education` | JSON Array | Optional | Degrees, institutions, years |
| `achievements` | JSON Array | Optional | Notable accomplishments |
| `career_timeline` | JSON Array | Required | Chronological work history |
| `current_role` | String | Optional | Most recent job title |
| `current_company` | String | Optional | Most recent employer |
| `parsing_confidence` | Float | Required | 0.0-1.0 quality score |
| `parsed_at` | DateTime | Required | When parsing occurred |
| `parser_version` | String | Required | Parsing algorithm version |

**Validation Rules**:
- `skills` must contain at least 1 skill
- `parsing_confidence` must be 0.0 ≤ x ≤ 1.0
- `experience_years` must be ≥ 0 if present
- `career_timeline` must be chronologically ordered

**State Transitions**:
```
UPLOADED → PARSING → PARSED_SUCCESS
                  ↘ PARSING_FAILED
```

**Example JSON Structure**:
```json
{
  "skills": ["Python", "Machine Learning", "FastAPI"],
  "job_titles": [
    {"title": "Software Engineer", "start": "2020-01", "end": "2023-06"},
    {"title": "ML Engineer", "start": "2023-07", "end": "present"}
  ],
  "companies": [
    {"name": "TechCorp", "start": "2020-01", "end": "2023-06"},
    {"name": "AI Startup", "start": "2023-07", "end": "present"}
  ],
  "education": [
    {"degree": "BS Computer Science", "institution": "State University", "year": 2019}
  ],
  "career_timeline": [
    {"date": "2020-01", "event": "Joined TechCorp as Software Engineer"},
    {"date": "2023-07", "event": "Promoted to ML Engineer at AI Startup"}
  ]
}
```

---

### 3. DreamJobDescription

**Description**: User-provided text describing target career goals including desired role, industry, company type, responsibilities, and required skills.

**Fields**:

| Field | Type | Constraints | Description |
|-------|------|-------------|-------------|
| `id` | UUID | PK, Required | Unique identifier |
| `user_id` | UUID | FK, Required | Reference to UserProfile |
| `description` | Text | Required, Min 50 chars | Full dream job description |
| `version` | Integer | Required, ≥1 | Evolution tracking (starts at 1) |
| `desired_role` | String | Optional | Extracted job title |
| `desired_industry` | String | Optional | Target industry |
| `desired_company_type` | String | Optional | Startup, Enterprise, etc. |
| `required_skills` | JSON Array | Optional | LLM-extracted required skills |
| `responsibilities` | JSON Array | Optional | Key responsibilities |
| `created_at` | DateTime | Required | When version created |
| `is_active` | Boolean | Required | Current version flag |
| `previous_version_id` | UUID | FK, Optional | Link to previous version |

**Validation Rules**:
- `description` must be ≥ 50 characters (force detailed input)
- Only one `is_active=true` per user
- `version` must increment monotonically per user
- `previous_version_id` must reference same user's older version

**State Transitions**:
```
DRAFT → ACTIVE → SUPERSEDED (when new version created)
```

---

### 4. DeducedAllyType

**Description**: System-generated professional category relevant to user's career transition including type name, confidence score, selection rationale, LLM-generated platform-specific search queries, and engagement strategy.

**Fields**:

| Field | Type | Constraints | Description |
|-------|------|-------------|-------------|
| `id` | UUID | PK, Required | Unique identifier |
| `dream_job_id` | UUID | FK, Required | Reference to DreamJobDescription |
| `ally_type_name` | String | Required | E.g., "AI/ML Technical Leaders" |
| `confidence_score` | Float | Required, 0.0-1.0 | LLM confidence in recommendation |
| `selection_rationale` | Text | Required | Why this ally type was chosen |
| `search_queries` | JSON Object | Required | Platform-specific search terms |
| `engagement_strategy` | Text | Optional | When/how to engage this ally type |
| `rank` | Integer | Required, ≥1 | Ordering by relevance (1=highest) |
| `created_at` | DateTime | Required | When deduced |
| `llm_model` | String | Required | E.g., "claude-3-sonnet-20240229" |
| `llm_prompt_version` | String | Required | Prompt version for reproducibility |

**Validation Rules**:
- `confidence_score` must be 0.0 ≤ x ≤ 1.0
- `ally_type_name` must be 3-50 characters
- `search_queries` must contain keys: "github", "twitter", "linkedin"
- `rank` must be unique per `dream_job_id`

**Example JSON Structure**:
```json
{
  "ally_type_name": "AI/ML Technical Leaders",
  "confidence_score": 0.85,
  "selection_rationale": "Given your ML engineering background and goal of becoming an AI Product Manager, connecting with technical leaders who transitioned from engineering to product roles will provide valuable insights on skill gaps and career positioning.",
  "search_queries": {
    "github": "machine learning language:python followers:>1000",
    "twitter": "#MachineLearning #ProductManagement (AI OR ML) -job",
    "linkedin": "AI Product Manager OR ML Product Lead"
  },
  "engagement_strategy": "Reach out within first 2 weeks of analysis. Start with GitHub contributions, then LinkedIn connections.",
  "rank": 1
}
```

---

### 5. AllyConfidenceScore

**Description**: LLM-generated metric (0.0-1.0) reflecting the model's confidence in its reasoning for recommending a specific ally type based on resume and dream job analysis.

**Fields**:

| Field | Type | Constraints | Description |
|-------|------|-------------|-------------|
| `id` | UUID | PK, Required | Unique identifier |
| `ally_type_id` | UUID | FK, Required | Reference to DeducedAllyType |
| `score` | Float | Required, 0.0-1.0 | Confidence value |
| `score_components` | JSON Object | Optional | Breakdown of score factors |
| `calculated_at` | DateTime | Required | Timestamp |

**Validation Rules**:
- `score` must be 0.0 ≤ x ≤ 1.0
- Each `ally_type_id` has exactly one AllyConfidenceScore

**Note**: This is often embedded in `DeducedAllyType.confidence_score` rather than a separate table. Separate entity provided for extensibility if scoring becomes more complex.

---

### 6. ProfessionalAlly

**Description**: Individual discovered through search with profile information, expertise areas, career background, contact details, and match explanation.

**Fields**:

| Field | Type | Constraints | Description |
|-------|------|-------------|-------------|
| `id` | UUID | PK, Required | Unique identifier |
| `ally_type_id` | UUID | FK, Required | Which ally type this person matches |
| `name` | String | Required | Full name |
| `current_title` | String | Optional | Current job title |
| `current_company` | String | Optional | Current employer |
| `platform` | String | Required | "github", "twitter", "linkedin" |
| `profile_url` | String | Required, URL | Link to profile |
| `expertise_areas` | JSON Array | Optional | Skills/domains |
| `career_background` | Text | Optional | Summary of experience |
| `match_explanation` | Text | Required | Why this person matches ally type |
| `relevance_score` | Float | Required, 0.0-1.0 | How well they match |
| `discovered_at` | DateTime | Required | When found |
| `last_updated` | DateTime | Required | Profile data freshness |

**Validation Rules**:
- `platform` must be one of: "github", "twitter", "linkedin"
- `profile_url` must be valid URL for specified platform
- `relevance_score` must be 0.0 ≤ x ≤ 1.0
- `match_explanation` must be ≥ 50 characters

**Relationships**:
- N:M with `DeducedAllyType` (one ally may match multiple types)

---

### 7. CareerGapAnalysis

**Description**: Comparison between current background and dream job requirements identifying skill deficiencies, experience gaps, and bridging opportunities.

**Fields**:

| Field | Type | Constraints | Description |
|-------|------|-------------|-------------|
| `id` | UUID | PK, Required | Unique identifier |
| `user_id` | UUID | FK, Required | Reference to UserProfile |
| `dream_job_id` | UUID | FK, Required | Reference to DreamJobDescription |
| `skill_gaps` | JSON Array | Required | List of SkillGap objects |
| `experience_gaps` | JSON Array | Optional | Missing experience types |
| `bridge_opportunities` | JSON Array | Optional | How to close gaps |
| `gap_severity` | String | Required | "low", "medium", "high" |
| `estimated_time_to_close` | String | Optional | E.g., "6-12 months" |
| `recommended_ally_types` | JSON Array | Required | Which ally types help with gaps |
| `analyzed_at` | DateTime | Required | When analysis performed |
| `llm_model` | String | Required | Model used for analysis |

**Validation Rules**:
- `skill_gaps` must contain at least 1 gap
- `gap_severity` must be one of: "low", "medium", "high"
- Each gap in `skill_gaps` must reference a valid SkillGap structure

---

### 8. SkillGap

**Description**: Identified deficiency between current capabilities and dream job requirements including gap severity, learning resources, and ally types who can provide guidance.

**Fields** (typically embedded in CareerGapAnalysis):

| Field | Type | Constraints | Description |
|-------|------|-------------|-------------|
| `skill_name` | String | Required | Missing skill |
| `current_level` | String | Required | "none", "beginner", "intermediate", "advanced" |
| `required_level` | String | Required | Target proficiency level |
| `gap_severity` | String | Required | "low", "medium", "high", "critical" |
| `learning_resources` | JSON Array | Optional | Courses, books, projects |
| `relevant_ally_types` | JSON Array | Required | Which ally types can help |
| `estimated_learning_time` | String | Optional | E.g., "3-6 months" |

**Validation Rules**:
- `current_level` and `required_level` must be one of: "none", "beginner", "intermediate", "advanced"
- `gap_severity` must be one of: "low", "medium", "high", "critical"

**Example JSON**:
```json
{
  "skill_name": "Product Strategy",
  "current_level": "none",
  "required_level": "intermediate",
  "gap_severity": "high",
  "learning_resources": [
    "Cracking the PM Interview",
    "Product Management course (Udemy)"
  ],
  "relevant_ally_types": ["Product Management Veterans", "Product Coaches"],
  "estimated_learning_time": "6-9 months"
}
```

---

### 9. CareerTransitionStrategy

**Description**: Generated roadmap suggesting sequence and timing for engaging different ally types based on career complexity and goals.

**Fields**:

| Field | Type | Constraints | Description |
|-------|------|-------------|-------------|
| `id` | UUID | PK, Required | Unique identifier |
| `user_id` | UUID | FK, Required | Reference to UserProfile |
| `dream_job_id` | UUID | FK, Required | Reference to DreamJobDescription |
| `gap_analysis_id` | UUID | FK, Required | Reference to CareerGapAnalysis |
| `strategy_phases` | JSON Array | Required | Timeline of ally engagement |
| `total_estimated_duration` | String | Required | E.g., "12-18 months" |
| `priority_ally_types` | JSON Array | Required | Ordered list by urgency |
| `success_metrics` | JSON Array | Optional | How to measure progress |
| `generated_at` | DateTime | Required | When strategy created |

**Example JSON Structure**:
```json
{
  "strategy_phases": [
    {
      "phase": 1,
      "duration": "0-3 months",
      "ally_types": ["AI/ML Technical Leaders"],
      "goals": ["Learn product mindset from technical perspective"],
      "actions": ["Follow on GitHub", "Engage with blog posts", "Attend meetups"]
    },
    {
      "phase": 2,
      "duration": "3-6 months",
      "ally_types": ["Product Management Veterans", "Career Transition Mentors"],
      "goals": ["Build product skills", "Understand PM workflows"],
      "actions": ["LinkedIn outreach", "Informational interviews", "Find mentor"]
    }
  ],
  "priority_ally_types": [
    "AI/ML Technical Leaders",
    "Product Management Veterans",
    "Career Transition Mentors"
  ]
}
```

---

### 10. DreamJobEvolution

**Description**: Historical record of how user's career goals have changed over time with corresponding ally type recommendation adjustments.

**Fields**:

| Field | Type | Constraints | Description |
|-------|------|-------------|-------------|
| `id` | UUID | PK, Required | Unique identifier |
| `user_id` | UUID | FK, Required | Reference to UserProfile |
| `from_dream_job_id` | UUID | FK, Optional | Previous version |
| `to_dream_job_id` | UUID | FK, Required | New version |
| `change_summary` | Text | Required | What changed |
| `ally_type_changes` | JSON Object | Required | Added/removed/modified ally types |
| `rationale` | Text | Optional | Why goals evolved |
| `changed_at` | DateTime | Required | When evolution occurred |

**Example JSON Structure**:
```json
{
  "change_summary": "Shifted focus from AI Product Manager to AI Ethics Researcher",
  "ally_type_changes": {
    "removed": ["Product Management Veterans", "Startup Founders"],
    "added": ["AI Ethics Researchers", "Academic AI Researchers", "Policy Advisors"],
    "retained": ["AI/ML Technical Leaders"]
  },
  "rationale": "After conversations with allies, realized passion lies in ethical implications rather than commercial product development"
}
```

---

## Database Schema (SQLAlchemy Models)

```python
from sqlalchemy import Column, Integer, String, Text, Float, Boolean, DateTime, JSON, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from datetime import datetime
import uuid

class UserProfile(Base):
    __tablename__ = "user_profiles"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(String(255), unique=True, nullable=False, index=True)
    email = Column(String(255), unique=True, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    resume_file_path = Column(String(512))
    resume_file_name = Column(String(255))
    resume_file_size = Column(Integer)
    resume_upload_date = Column(DateTime)
    parsed_resume_id = Column(UUID(as_uuid=True), ForeignKey("parsed_resumes.id"))
    
    # Relationships
    dream_jobs = relationship("DreamJobDescription", back_populates="user")
    parsed_resume = relationship("ParsedResume", uselist=False, back_populates="user")

class ParsedResume(Base):
    __tablename__ = "parsed_resumes"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("user_profiles.id"), nullable=False)
    raw_text = Column(Text, nullable=False)
    skills = Column(JSON, nullable=False)
    experience_years = Column(Float)
    job_titles = Column(JSON, nullable=False)
    companies = Column(JSON, nullable=False)
    education = Column(JSON)
    achievements = Column(JSON)
    career_timeline = Column(JSON, nullable=False)
    current_role = Column(String(255))
    current_company = Column(String(255))
    parsing_confidence = Column(Float, nullable=False)
    parsed_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    parser_version = Column(String(50), nullable=False)
    
    # Relationships
    user = relationship("UserProfile", back_populates="parsed_resume")

class DreamJobDescription(Base):
    __tablename__ = "dream_job_descriptions"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("user_profiles.id"), nullable=False, index=True)
    description = Column(Text, nullable=False)
    version = Column(Integer, nullable=False, default=1)
    desired_role = Column(String(255))
    desired_industry = Column(String(255))
    desired_company_type = Column(String(100))
    required_skills = Column(JSON)
    responsibilities = Column(JSON)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    is_active = Column(Boolean, default=True, nullable=False, index=True)
    previous_version_id = Column(UUID(as_uuid=True), ForeignKey("dream_job_descriptions.id"))
    
    # Relationships
    user = relationship("UserProfile", back_populates="dream_jobs")
    ally_types = relationship("DeducedAllyType", back_populates="dream_job")

class DeducedAllyType(Base):
    __tablename__ = "deduced_ally_types"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    dream_job_id = Column(UUID(as_uuid=True), ForeignKey("dream_job_descriptions.id"), nullable=False, index=True)
    ally_type_name = Column(String(100), nullable=False)
    confidence_score = Column(Float, nullable=False)
    selection_rationale = Column(Text, nullable=False)
    search_queries = Column(JSON, nullable=False)
    engagement_strategy = Column(Text)
    rank = Column(Integer, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    llm_model = Column(String(100), nullable=False)
    llm_prompt_version = Column(String(50), nullable=False)
    
    # Relationships
    dream_job = relationship("DreamJobDescription", back_populates="ally_types")
    professional_allies = relationship("ProfessionalAlly", back_populates="ally_type")

class ProfessionalAlly(Base):
    __tablename__ = "professional_allies"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    ally_type_id = Column(UUID(as_uuid=True), ForeignKey("deduced_ally_types.id"), nullable=False, index=True)
    name = Column(String(255), nullable=False)
    current_title = Column(String(255))
    current_company = Column(String(255))
    platform = Column(String(50), nullable=False)
    profile_url = Column(String(512), nullable=False)
    expertise_areas = Column(JSON)
    career_background = Column(Text)
    match_explanation = Column(Text, nullable=False)
    relevance_score = Column(Float, nullable=False)
    discovered_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    last_updated = Column(DateTime, default=datetime.utcnow, nullable=False)
    
    # Relationships
    ally_type = relationship("DeducedAllyType", back_populates="professional_allies")

class CareerGapAnalysis(Base):
    __tablename__ = "career_gap_analyses"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("user_profiles.id"), nullable=False, index=True)
    dream_job_id = Column(UUID(as_uuid=True), ForeignKey("dream_job_descriptions.id"), nullable=False)
    skill_gaps = Column(JSON, nullable=False)
    experience_gaps = Column(JSON)
    bridge_opportunities = Column(JSON)
    gap_severity = Column(String(20), nullable=False)
    estimated_time_to_close = Column(String(50))
    recommended_ally_types = Column(JSON, nullable=False)
    analyzed_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    llm_model = Column(String(100), nullable=False)

class CareerTransitionStrategy(Base):
    __tablename__ = "career_transition_strategies"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("user_profiles.id"), nullable=False, index=True)
    dream_job_id = Column(UUID(as_uuid=True), ForeignKey("dream_job_descriptions.id"), nullable=False)
    gap_analysis_id = Column(UUID(as_uuid=True), ForeignKey("career_gap_analyses.id"), nullable=False)
    strategy_phases = Column(JSON, nullable=False)
    total_estimated_duration = Column(String(50), nullable=False)
    priority_ally_types = Column(JSON, nullable=False)
    success_metrics = Column(JSON)
    generated_at = Column(DateTime, default=datetime.utcnow, nullable=False)

class DreamJobEvolution(Base):
    __tablename__ = "dream_job_evolutions"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("user_profiles.id"), nullable=False, index=True)
    from_dream_job_id = Column(UUID(as_uuid=True), ForeignKey("dream_job_descriptions.id"))
    to_dream_job_id = Column(UUID(as_uuid=True), ForeignKey("dream_job_descriptions.id"), nullable=False)
    change_summary = Column(Text, nullable=False)
    ally_type_changes = Column(JSON, nullable=False)
    rationale = Column(Text)
    changed_at = Column(DateTime, default=datetime.utcnow, nullable=False)
```

---

## Indexes

For optimal query performance:

```sql
-- User lookups
CREATE INDEX idx_user_profiles_user_id ON user_profiles(user_id);
CREATE INDEX idx_user_profiles_email ON user_profiles(email);

-- Dream job queries
CREATE INDEX idx_dream_jobs_user_active ON dream_job_descriptions(user_id, is_active);
CREATE INDEX idx_dream_jobs_created ON dream_job_descriptions(created_at DESC);

-- Ally type lookups
CREATE INDEX idx_ally_types_dream_job ON deduced_ally_types(dream_job_id);
CREATE INDEX idx_ally_types_confidence ON deduced_ally_types(confidence_score DESC);

-- Professional ally searches
CREATE INDEX idx_allies_type_relevance ON professional_allies(ally_type_id, relevance_score DESC);
CREATE INDEX idx_allies_platform ON professional_allies(platform);

-- Full-text search on resumes (PostgreSQL)
CREATE INDEX idx_parsed_resumes_text ON parsed_resumes USING gin(to_tsvector('english', raw_text));
```

---

## Next Steps

1. ✅ Data model defined with all entities from spec
2. 🔄 Generate OpenAPI contracts for API endpoints
3. 🔄 Generate quickstart.md for database setup
4. ⏳ Implement SQLAlchemy models in backend/src/models/
5. ⏳ Create Alembic migrations for schema versioning
