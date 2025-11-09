# Constitution Amendment Summary - v2.1.0

**Date**: November 9, 2025  
**Version Change**: 2.0.0 → 2.1.0  
**Amendment Type**: MINOR (New principle + non-breaking technology upgrade)

---

## Changes Made

### 🆕 New Principle Added: VI. Test-Driven Phase Completion

**Content**:

> A development phase is NOT complete until automated tests are written and passing; Manual validation alone is insufficient; All API endpoints MUST have pytest integration tests; All service layer logic MUST have pytest unit tests; Test coverage MUST be measured and reported; Phases cannot proceed to "validated" status without a passing automated test suite.

**Rationale**: Your observation was correct - Phase 1 was validated manually but lacks automated tests. This principle now makes it explicit: **a phase is not complete without passing automated tests**.

### 🔄 Updated Principle: I. RAG-First AI Architecture

**Change**: Claude 3 Sonnet → Claude Sonnet 4.5 (claude-sonnet-4-5-20250929)

**Rationale**: Upgraded to latest model for enhanced reasoning capabilities and performance improvements (already in use per copilot-instructions.md).

### 📚 Technology Stack Updates

- **AI/ML Stack**: Updated to Claude Sonnet 4.5 specification
- **Testing**: Added `pytest-cov` for coverage reporting
- **Linting**: Changed from `pylint` to `ruff check` (modern, faster Python linter)

### 🔧 Development Workflow Updates

**Testing Gates** now explicitly state:

> Constitution compliance check → Unit tests (pytest) → Integration tests (pytest) → Manual feature validation → **Phase complete only when automated tests pass**

---

## Templates Updated

### ✅ Completed Updates

1. **constitution.md** (this file)

   - Added Principle VI
   - Updated Principle I
   - Updated Technology Stack Standards
   - Updated Development Workflow

2. **plan-template.md**

   - Added "Test-Driven Phase Completion" to Constitution Check
   - Updated Claude 3 Sonnet → Claude Sonnet 4.5

3. **tasks-template.md**

   - Updated T010: Claude 3 Sonnet → Claude Sonnet 4.5
   - Added T014: Setup pytest test infrastructure with coverage reporting

4. **checklist-template.md**

   - Added "Automated Testing (Required for Phase Completion)" section
   - 7 test verification items (TEST001-TEST007)

5. **spec-template.md**
   - No changes needed (already has strong testing guidance in acceptance scenarios)

---

## Impact on Current Project

### ⚠️ Phase 1 (001-civic-ally-hunter) Status

**Current State**:

- ✅ Manual validation complete (all 60+ items checked)
- ✅ All endpoints working correctly
- ✅ Performance benchmarks exceeded
- ❌ **No automated pytest tests exist**

**Required Action**:
According to new Principle VI, **Phase 1 is NOT complete** until automated tests are written and passing.

**Next Steps**:

1. Create `backend/tests/unit/` tests for:

   - Authentication service (register, login, token validation)
   - Resume parser service
   - Ally type service

2. Create `backend/tests/integration/` tests for:

   - `/api/v1/auth/*` endpoints
   - `/api/v1/resumes/*` endpoints
   - `/api/v1/ally-types/*` endpoints

3. Setup pytest configuration:

   - Install `pytest-cov`
   - Configure `pytest.ini` for coverage reporting
   - Add test fixtures for database, test users, etc.

4. Achieve passing test suite before marking Phase 1 as "validated"

---

## Version Bump Justification

**MINOR (2.1.0)** because:

- ✅ New principle added (Principle VI) - requires MINOR
- ✅ Non-breaking technology upgrade (Claude model version)
- ✅ No removal of existing principles
- ✅ No backward-incompatible governance changes

**Not MAJOR** because:

- Existing code continues to work
- No principles removed or fundamentally redefined
- Model upgrade is transparent to application code

**Not PATCH** because:

- New principle added (material governance expansion)
- New testing requirements impose new quality gates

---

## Suggested Commit Message

```
docs: amend constitution to v2.1.0 (test-driven phase completion + Claude Sonnet 4.5)

- Add Principle VI: Test-Driven Phase Completion
- Upgrade to Claude Sonnet 4.5 (claude-sonnet-4-5-20250929)
- Update templates: plan, tasks, checklist
- Phase 1 requires automated tests before completion

BREAKING CHANGE: Phases cannot be marked complete without passing pytest suite
```

---

## Files Modified

1. `.specify/memory/constitution.md` - Constitution v2.1.0
2. `.specify/templates/plan-template.md` - Updated Constitution Check
3. `.specify/templates/tasks-template.md` - Updated foundational tasks
4. `.specify/templates/checklist-template.md` - Added testing section

---

## Follow-Up Actions Required

### Immediate (Phase 1 Completion)

- [ ] Install `pytest-cov` in backend requirements.txt
- [ ] Create pytest test suite for Phase 1 functionality
- [ ] Achieve passing test suite
- [ ] Measure and document test coverage
- [ ] Update Phase 1 validation checklist to include automated tests

### Future Phases

- [ ] All new phases must include automated tests from the start
- [ ] Test coverage targets should be defined per phase
- [ ] CI/CD pipeline should enforce test passing before merge

---

## Constitution Validation

✅ No remaining unexplained bracket tokens  
✅ Version line matches report (2.1.0)  
✅ Dates in ISO format (YYYY-MM-DD)  
✅ Principles are declarative and testable  
✅ All templates updated consistently

---

**Constitution amendment complete and ready for use.**
