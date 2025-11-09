# Phase 1 Validation Checklist: Foundation & Resume Processing

**Feature**: 001-civic-ally-hunter  
**Phase**: Phase 1 (T001-T022)  
**Created**: November 8, 2025  
**Status**: Code Complete - Awaiting Validation

## Purpose

Validate that Phase 1 implementation is functional before proceeding to Phase 2. All code has been written, but requires installation, migration, and testing.

---

## Pre-Validation Setup

### Package Installation

- [ ] **Backend**: Run `pip install -r backend/requirements.txt`
  - Expected packages: FastAPI, anthropic, langchain, faiss-cpu, sentence-transformers, PyPDF2, python-docx, httpx, networkx, redis, bcrypt, python-jose, SQLAlchemy, Alembic, pytest
  - Verify no dependency conflicts
  - Check for import errors in Python files

- [ ] **Frontend**: Run `npm install` in `frontend/`
  - Expected packages: Next.js, React, TypeScript, D3.js, Tailwind CSS
  - Verify no dependency conflicts

### Database Setup

- [ ] **Create Database**: Ensure PostgreSQL 15 is running (or SQLite for dev)
  - Verify DATABASE_URL in `.env` is correct
  - Test database connection

- [ ] **Run Migrations**: Create and apply Alembic migrations
  - [ ] Generate migration: `alembic revision --autogenerate -m "Phase 1: Initial schema"`
  - [ ] Review migration file for correctness
  - [ ] Apply migration: `alembic upgrade head`
  - [ ] Verify tables created: `user_profiles`, `parsed_resumes`, `ally_types`
  - [ ] Verify indexes on `user_profiles.email`, `user_profiles.user_id`

### Environment Configuration

- [ ] **Create `.env` file**: Copy from `.env.example`
  - [ ] Set `JWT_SECRET_KEY` (generate with `openssl rand -hex 32`)
  - [ ] Set `JWT_ALGORITHM=HS256`
  - [ ] Set `DATABASE_URL` (PostgreSQL or SQLite)
  - [ ] Set `SECRET_KEY` for FastAPI
  - [ ] Optional: Set `ANTHROPIC_API_KEY`, `GITHUB_API_TOKEN`, etc. (not needed for Phase 1)

---

## Validation Tests

### T001-T005: Project Setup

- [ ] **Dev Container**: `docker-compose up` starts all services without errors
- [ ] **FastAPI Server**: `uvicorn src.main:app --reload` starts successfully
  - [ ] Health check: GET `http://localhost:8000/api/v1/health` returns 200
  - [ ] OpenAPI docs: `http://localhost:8000/docs` loads
  - [ ] CORS configured for `localhost:3000`

### T006-T008: Authentication & Security

- [ ] **User Registration**: POST `/api/v1/auth/register`
  ```json
  {
    "email": "test@example.com",
    "password": "testpassword123"
  }
  ```
  - [ ] Returns 201 with access_token and refresh_token
  - [ ] Password is hashed with bcrypt in database
  - [ ] UserProfile created in database

- [ ] **User Login**: POST `/api/v1/auth/login`
  ```json
  {
    "email": "test@example.com",
    "password": "testpassword123"
  }
  ```
  - [ ] Returns 200 with tokens
  - [ ] Invalid password returns 401

- [ ] **Token Refresh**: POST `/api/v1/auth/refresh`
  ```json
  {
    "refresh_token": "<refresh_token>"
  }
  ```
  - [ ] Returns new access_token and refresh_token
  - [ ] Invalid/expired token returns 401

- [ ] **Get Current User**: GET `/api/v1/auth/me`
  - [ ] With valid token: Returns 200 with user profile
  - [ ] Without token: Returns 401
  - [ ] With invalid token: Returns 401

- [ ] **Auth Middleware**: Protected endpoints require JWT
  - [ ] Public routes work without auth: `/`, `/api/v1/health`, `/docs`
  - [ ] Protected routes return 401 without token

### T009-T012: Database Schema

- [ ] **UserProfile Model**:
  - [ ] Contains fields: id, user_id, email, password_hash, resume_file_path, parsed_resume_id, created_at, updated_at
  - [ ] email is unique and indexed
  - [ ] password_hash is bcrypt hashed
  - [ ] Relationship to ParsedResume works
  - [ ] Relationship to AllyType works (one-to-many)

- [ ] **ParsedResume Model**:
  - [ ] Contains fields: id, user_profile_id, raw_text, skills, achievements, work_history, education, companies, keywords, parsing_confidence, parsed_at, parser_version
  - [ ] user_profile_id FK references user_profiles.id
  - [ ] JSON fields (skills, achievements, work_history, education, companies, keywords) store arrays/objects

- [ ] **AllyType Model**:
  - [ ] Contains fields: id, user_profile_id, name, keywords, criteria, search_parameters, created_at, is_active
  - [ ] user_profile_id FK references user_profiles.id
  - [ ] keywords stored as JSON array
  - [ ] search_parameters stored as JSON object

### T013-T017: Resume Upload & Parsing

- [ ] **Resume Upload**: POST `/api/v1/resumes/upload`
  - [ ] Upload PDF resume (< 10MB): Returns 200 with resume_id
  - [ ] Upload DOCX resume: Returns 200 with resume_id
  - [ ] Upload TXT resume: Returns 200 with resume_id
  - [ ] Upload > 10MB file: Returns 400
  - [ ] Upload invalid file type (.exe): Returns 400
  - [ ] File saved to disk with unique filename
  - [ ] ParsedResume record created with parsing_confidence=0.0

- [ ] **Resume Parsing Background Task**:
  - [ ] Background task executes after upload
  - [ ] ParsedResume updated with extracted fields
  - [ ] skills extracted (non-empty array)
  - [ ] achievements extracted (bullet points with metrics)
  - [ ] work_history extracted (array of job objects)
  - [ ] education extracted
  - [ ] companies extracted
  - [ ] keywords extracted
  - [ ] parsing_confidence calculated (0.0-1.0)

- [ ] **Resume Status**: GET `/api/v1/resumes/{resume_id}/status`
  - [ ] Before parsing: Returns "parsing" status
  - [ ] After parsing: Returns "parsed_success" status
  - [ ] Includes parsing_confidence

- [ ] **Resume Retrieval**: GET `/api/v1/resumes/{resume_id}`
  - [ ] Returns complete parsed resume data
  - [ ] Includes all fields: skills, achievements, work_history, education, companies, keywords
  - [ ] User can only access their own resumes (ownership validation)

### T018-T022: Ally Type CRUD

- [ ] **Create Ally Type**: POST `/api/v1/ally-types`
  ```json
  {
    "name": "AI Researchers",
    "keywords": ["machine learning", "NLP", "computer vision"],
    "criteria": "Researchers working on AI/ML technologies",
    "search_parameters": {"platforms": ["github", "twitter"]}
  }
  ```
  - [ ] Returns 201 with created ally type
  - [ ] Duplicate name returns 400
  - [ ] AllyType created in database with is_active=true

- [ ] **List Ally Types**: GET `/api/v1/ally-types`
  - [ ] Returns user's ally types (not other users')
  - [ ] Pagination works: `?page=1&per_page=10`
  - [ ] Filter by is_active: `?is_active=true`
  - [ ] Ordered by created_at DESC (newest first)

- [ ] **Get Ally Type**: GET `/api/v1/ally-types/{id}`
  - [ ] Returns ally type details
  - [ ] User can only access their own ally types (ownership validation)
  - [ ] Non-existent ID returns 404

- [ ] **Update Ally Type**: PUT `/api/v1/ally-types/{id}`
  ```json
  {
    "name": "AI Researchers Updated",
    "keywords": ["deep learning", "reinforcement learning"]
  }
  ```
  - [ ] Updates ally type successfully
  - [ ] User can only update their own ally types
  - [ ] Duplicate name (different ally type) returns 400
  - [ ] Partial updates work (only name, only keywords, etc.)

- [ ] **Delete Ally Type**: DELETE `/api/v1/ally-types/{id}`
  - [ ] Soft deletes (sets is_active=false)
  - [ ] Returns 204 No Content
  - [ ] User can only delete their own ally types
  - [ ] Deleted ally types don't appear in list (unless filtered by is_active=false)

- [ ] **Export Ally Types**: GET `/api/v1/ally-types/export`
  - [ ] Returns JSON with all user's active ally types
  - [ ] Includes version, exported_at timestamp
  - [ ] Export format matches import schema

- [ ] **Import Ally Types**: POST `/api/v1/ally-types/import`
  ```json
  {
    "version": "1.0",
    "ally_types": [
      {
        "name": "Fintech Founders",
        "keywords": ["fintech", "payments", "banking"],
        "criteria": "Founders in fintech space"
      }
    ]
  }
  ```
  - [ ] Creates ally types from import data
  - [ ] Skips duplicates (same name already exists)
  - [ ] Returns count of imported and skipped items
  - [ ] Invalid format returns 400

---

## Integration Tests

- [ ] **Complete User Flow**:
  1. [ ] Register new user
  2. [ ] Login and get JWT token
  3. [ ] Upload resume
  4. [ ] Wait for parsing to complete (check status)
  5. [ ] Retrieve parsed resume
  6. [ ] Create ally type
  7. [ ] List ally types
  8. [ ] Update ally type
  9. [ ] Export ally types
  10. [ ] Import ally types
  11. [ ] Delete ally type
  12. [ ] Verify deleted ally type is inactive

- [ ] **Multi-User Isolation**:
  - [ ] User A cannot access User B's resumes
  - [ ] User A cannot access User B's ally types
  - [ ] User A cannot update/delete User B's ally types

- [ ] **Error Handling**:
  - [ ] Invalid JWT returns 401
  - [ ] Expired JWT returns 401
  - [ ] Missing required fields return 422
  - [ ] Invalid file types return 400
  - [ ] Database errors are logged (not exposed to user)

---

## Performance Checks

- [ ] **Resume Parsing**:
  - [ ] Small resume (1 page): Parses in < 5 seconds
  - [ ] Large resume (5 pages): Parses in < 15 seconds
  - [ ] PDF with scanned images: Falls back to pdfplumber

- [ ] **API Response Times**:
  - [ ] Authentication endpoints: < 500ms
  - [ ] List ally types: < 200ms
  - [ ] Resume upload: < 1s (excluding parsing)

---

## Security Validation

- [ ] **Password Security**:
  - [ ] Passwords hashed with bcrypt (not plaintext)
  - [ ] Password hash cost factor ≥ 12
  - [ ] Minimum password length enforced (8 chars)

- [ ] **JWT Security**:
  - [ ] JWT_SECRET_KEY is strong (32+ random bytes)
  - [ ] Access tokens expire (30 minutes)
  - [ ] Refresh tokens expire (7 days)
  - [ ] Token signature validated on every request

- [ ] **Input Validation**:
  - [ ] SQL injection prevented (SQLAlchemy parameterized queries)
  - [ ] File upload validation (type, size)
  - [ ] Email format validated
  - [ ] JSON schema validation on all POST/PUT endpoints

---

## Code Quality

- [ ] **Linting**: Run `ruff check backend/src`
  - [ ] No critical errors
  - [ ] Type hints present on functions

- [ ] **Import Errors**: All files import successfully
  - [ ] No missing dependencies
  - [ ] No circular imports

- [ ] **Database Consistency**:
  - [ ] All models have __tablename__
  - [ ] All FKs have proper relationships
  - [ ] All indexes defined

---

## Documentation

- [ ] **API Documentation**:
  - [ ] OpenAPI docs at `/docs` are complete
  - [ ] All endpoints have descriptions
  - [ ] Request/response schemas documented

- [ ] **Environment Variables**:
  - [ ] `.env.example` contains all required variables
  - [ ] Variables have descriptions/comments

---

## Success Criteria

✅ **Phase 1 is validated when:**
1. All checklist items above are marked complete
2. Complete user flow works end-to-end
3. No critical errors in logs
4. Security requirements met
5. Performance benchmarks met
6. Multi-user isolation verified

**Next Steps After Validation:**
- Proceed to Phase 2: Multi-Platform Search Integration (T023-T044)
- Or address any issues found during validation

---

## Notes

- Import errors expected until packages installed
- Database migrations must be created and applied
- Some extraction methods in resume_parser.py are simplified (work_history extraction is placeholder)
- Legacy DeducedAllyType model preserved for backward compatibility with 002-dream-job-ally-deduction
