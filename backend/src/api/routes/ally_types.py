"""
Ally type API routes - supports both user-defined (001-civic-ally-hunter) and deduced (002-dream-job-ally-deduction) ally types.
"""

from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks, Query
from sqlalchemy.orm import Session
from pydantic import BaseModel, Field
from typing import Dict, Any, List, Optional
import logging
import uuid
from datetime import datetime

from src.core.database import get_db
from src.core.security import UserContext, get_current_user
from src.models.ally_type import AllyType, DeducedAllyType
from src.services.ally_deduction import ally_deduction_service

logger = logging.getLogger(__name__)

router = APIRouter()

# In-memory storage for analysis status (in production, use Redis or database)
analysis_jobs = {}


# ==================== User-Defined Ally Types (001-civic-ally-hunter) ====================

class CreateAllyTypeRequest(BaseModel):
    """Request model for creating user-defined ally type."""
    name: str = Field(..., min_length=1, max_length=100,
                      description="Ally type name (e.g., 'AI Researchers')")
    keywords: List[str] = Field(
        ..., description="List of keywords for matching (e.g., ['machine learning', 'NLP'])")
    criteria: str = Field(..., min_length=1,
                          description="User-defined criteria for this ally type")
    search_parameters: Optional[Dict[str, Any]] = Field(
        default=None, description="Platform-specific search parameters")


class UpdateAllyTypeRequest(BaseModel):
    """Request model for updating ally type."""
    name: Optional[str] = Field(None, min_length=1, max_length=100)
    keywords: Optional[List[str]] = None
    criteria: Optional[str] = None
    search_parameters: Optional[Dict[str, Any]] = None
    is_active: Optional[bool] = None


class AllyTypeResponse(BaseModel):
    """Response model for ally type."""
    id: str
    user_profile_id: str
    name: str
    keywords: List[str]
    criteria: str
    search_parameters: Optional[Dict[str, Any]]
    created_at: str
    is_active: bool


@router.post("/ally-types", response_model=AllyTypeResponse, status_code=201)
async def create_ally_type(
    request: CreateAllyTypeRequest,
    user: UserContext = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> AllyTypeResponse:
    """
    Create a new user-defined ally type.

    The ally type defines a category of professionals to search for.
    """
    # Check for duplicate name for this user
    existing = db.query(AllyType).filter(
        AllyType.user_profile_id == user.user_id,
        AllyType.name == request.name,
        AllyType.is_active == True
    ).first()

    if existing:
        raise HTTPException(
            status_code=400,
            detail=f"Ally type with name '{request.name}' already exists"
        )

    # Create new ally type
    ally_type = AllyType(
        id=str(uuid.uuid4()),
        user_profile_id=user.user_id,
        name=request.name,
        keywords=request.keywords,
        criteria=request.criteria,
        search_parameters=request.search_parameters or {},
        created_at=datetime.utcnow(),
        is_active=True,
    )

    db.add(ally_type)
    db.commit()
    db.refresh(ally_type)

    logger.info(f"Created ally type '{request.name}' for user {user.user_id}")

    return AllyTypeResponse(
        id=str(ally_type.id),
        user_profile_id=str(ally_type.user_profile_id),
        name=ally_type.name,
        keywords=ally_type.keywords or [],
        criteria=ally_type.criteria or "",
        search_parameters=ally_type.search_parameters,
        created_at=ally_type.created_at.isoformat(),
        is_active=ally_type.is_active,
    )


@router.get("/ally-types", response_model=List[AllyTypeResponse])
async def list_ally_types(
    is_active: Optional[bool] = Query(
        None, description="Filter by active status"),
    page: int = Query(1, ge=1, description="Page number (1-indexed)"),
    per_page: int = Query(20, ge=1, le=100, description="Results per page"),
    user: UserContext = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> List[AllyTypeResponse]:
    """
    List user's ally types with optional filtering and pagination.
    """
    query = db.query(AllyType).filter(AllyType.user_profile_id == user.user_id)

    if is_active is not None:
        query = query.filter(AllyType.is_active == is_active)

    # Order by created_at descending (newest first)
    query = query.order_by(AllyType.created_at.desc())

    # Pagination
    offset = (page - 1) * per_page
    ally_types = query.offset(offset).limit(per_page).all()

    return [
        AllyTypeResponse(
            id=str(at.id),
            user_profile_id=str(at.user_profile_id),
            name=at.name,
            keywords=at.keywords or [],
            criteria=at.criteria or "",
            search_parameters=at.search_parameters,
            created_at=at.created_at.isoformat(),
            is_active=at.is_active,
        )
        for at in ally_types
    ]


# Export/Import routes MUST be defined BEFORE /{ally_type_id} routes
# to prevent FastAPI from treating "export"/"import" as ally_type_id values
@router.get("/ally-types/export")
async def export_ally_types(
    user: UserContext = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> Dict[str, Any]:
    """
    Export all user's ally types as JSON.

    Supports saving ally type configurations for backup or transfer.
    """
    ally_types = db.query(AllyType).filter(
        AllyType.user_profile_id == user.user_id,
        AllyType.is_active == True
    ).order_by(AllyType.created_at.desc()).all()

    export_data = {
        "version": "1.0",
        "exported_at": datetime.utcnow().isoformat(),
        "user_id": str(user.user_id),
        "ally_types": [
            {
                "name": at.name,
                "keywords": at.keywords or [],
                "criteria": at.criteria or "",
                "search_parameters": at.search_parameters,
                "created_at": at.created_at.isoformat(),
            }
            for at in ally_types
        ],
    }

    logger.info(
        f"Exported {len(ally_types)} ally types for user {user.user_id}")

    return export_data


@router.post("/ally-types/import")
async def import_ally_types(
    data: Dict[str, Any],
    user: UserContext = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> Dict[str, Any]:
    """
    Import ally types from JSON payload.

    Skips duplicates (same name already exists).
    """
    if "ally_types" not in data or not isinstance(data["ally_types"], list):
        raise HTTPException(
            status_code=400, detail="Invalid import data format")

    imported_count = 0
    skipped_count = 0

    for item in data["ally_types"]:
        # Validate required fields
        if "name" not in item or "keywords" not in item:
            logger.warning(f"Skipping import item with missing fields: {item}")
            skipped_count += 1
            continue

        # Check for duplicate
        existing = db.query(AllyType).filter(
            AllyType.user_profile_id == user.user_id,
            AllyType.name == item["name"],
            AllyType.is_active == True
        ).first()

        if existing:
            logger.info(f"Skipping duplicate ally type: {item['name']}")
            skipped_count += 1
            continue

        # Create new ally type
        ally_type = AllyType(
            id=str(uuid.uuid4()),
            user_profile_id=user.user_id,
            name=item["name"],
            keywords=item["keywords"],
            criteria=item.get("criteria", ""),
            search_parameters=item.get("search_parameters", {}),
            created_at=datetime.utcnow(),
            is_active=True,
        )

        db.add(ally_type)
        imported_count += 1

    db.commit()

    logger.info(
        f"Imported {imported_count} ally types for user {user.user_id} ({skipped_count} skipped)")

    return {
        "imported": imported_count,
        "skipped": skipped_count,
        "total": imported_count + skipped_count,
    }


@router.get("/ally-types/{ally_type_id}", response_model=AllyTypeResponse)
async def get_ally_type(
    ally_type_id: str,
    user: UserContext = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> AllyTypeResponse:
    """Get a specific ally type by ID."""
    ally_type = db.query(AllyType).filter(
        AllyType.id == ally_type_id,
        AllyType.user_profile_id == user.user_id,
    ).first()

    if not ally_type:
        raise HTTPException(status_code=404, detail="Ally type not found")

    return AllyTypeResponse(
        id=str(ally_type.id),
        user_profile_id=str(ally_type.user_profile_id),
        name=ally_type.name,
        keywords=ally_type.keywords or [],
        criteria=ally_type.criteria or "",
        search_parameters=ally_type.search_parameters,
        created_at=ally_type.created_at.isoformat(),
        is_active=ally_type.is_active,
    )


@router.put("/ally-types/{ally_type_id}", response_model=AllyTypeResponse)
async def update_ally_type(
    ally_type_id: str,
    request: UpdateAllyTypeRequest,
    user: UserContext = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> AllyTypeResponse:
    """
    Update an ally type.

    Only the owner can update their ally types.
    """
    # Validate ownership
    ally_type = db.query(AllyType).filter(
        AllyType.id == ally_type_id,
        AllyType.user_profile_id == user.user_id,
    ).first()

    if not ally_type:
        raise HTTPException(status_code=404, detail="Ally type not found")

    # Check for name conflict if name is being changed
    if request.name and request.name != ally_type.name:
        existing = db.query(AllyType).filter(
            AllyType.user_profile_id == user.user_id,
            AllyType.name == request.name,
            AllyType.is_active == True,
            AllyType.id != ally_type_id
        ).first()

        if existing:
            raise HTTPException(
                status_code=400,
                detail=f"Ally type with name '{request.name}' already exists"
            )

    # Update fields
    if request.name is not None:
        ally_type.name = request.name
    if request.keywords is not None:
        ally_type.keywords = request.keywords
    if request.criteria is not None:
        ally_type.criteria = request.criteria
    if request.search_parameters is not None:
        ally_type.search_parameters = request.search_parameters
    if request.is_active is not None:
        ally_type.is_active = request.is_active

    db.commit()
    db.refresh(ally_type)

    logger.info(f"Updated ally type {ally_type_id} for user {user.user_id}")

    return AllyTypeResponse(
        id=str(ally_type.id),
        user_profile_id=str(ally_type.user_profile_id),
        name=ally_type.name,
        keywords=ally_type.keywords or [],
        criteria=ally_type.criteria or "",
        search_parameters=ally_type.search_parameters,
        created_at=ally_type.created_at.isoformat(),
        is_active=ally_type.is_active,
    )


@router.delete("/ally-types/{ally_type_id}", status_code=204)
async def delete_ally_type(
    ally_type_id: str,
    user: UserContext = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Soft delete an ally type (set is_active=False).

    This will cascade to associated contacts.
    """
    # Validate ownership
    ally_type = db.query(AllyType).filter(
        AllyType.id == ally_type_id,
        AllyType.user_profile_id == user.user_id,
    ).first()

    if not ally_type:
        raise HTTPException(status_code=404, detail="Ally type not found")

    # Soft delete
    ally_type.is_active = False
    db.commit()

    logger.info(
        f"Soft deleted ally type {ally_type_id} for user {user.user_id}")

    return None  # 204 No Content


# ==================== Deduced Ally Types (002-dream-job-ally-deduction - Legacy) ====================


class AllyDeductionRequest(BaseModel):
    """Request model for ally deduction analysis."""
    resume_id: str
    dream_job_id: str


async def run_ally_deduction_background(
    analysis_id: str,
    resume_id: str,
    dream_job_id: str,
    db_session: Session,
):
    """Background task for ally deduction."""
    try:
        analysis_jobs[analysis_id] = {"status": "processing", "progress": 50}

        result = await ally_deduction_service.analyze_resume_and_dream_job(
            db_session, resume_id, dream_job_id
        )

        analysis_jobs[analysis_id] = {
            "status": "completed",
            "progress": 100,
            "result": result,
        }

        logger.info(f"Ally deduction {analysis_id} completed successfully")

    except Exception as e:
        logger.error(f"Ally deduction {analysis_id} failed: {e}")
        analysis_jobs[analysis_id] = {
            "status": "failed",
            "progress": 0,
            "error": str(e),
        }


@router.post("/ally-deduction/analyze")
async def analyze_ally_types(
    request: AllyDeductionRequest,
    background_tasks: BackgroundTasks,
    user: UserContext = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> Dict[str, Any]:
    """
    Start ally type deduction analysis.

    Returns analysis_id for tracking progress.
    """
    # Generate analysis ID
    analysis_id = str(uuid.uuid4())

    # Initialize job status
    analysis_jobs[analysis_id] = {"status": "queued", "progress": 0}

    # Schedule background task
    background_tasks.add_task(
        run_ally_deduction_background,
        analysis_id,
        request.resume_id,
        request.dream_job_id,
        db,
    )

    logger.info(f"Started ally deduction analysis {analysis_id}")

    return {
        "analysis_id": analysis_id,
        "status": "queued",
        "message": "Analysis started. Use GET /ally-deduction/{analysis_id}/status to check progress.",
    }


@router.get("/ally-deduction/{analysis_id}/status")
async def get_analysis_status(
    analysis_id: str,
    user: UserContext = Depends(get_current_user),
) -> Dict[str, Any]:
    """Get status of ally deduction analysis."""
    if analysis_id not in analysis_jobs:
        raise HTTPException(status_code=404, detail="Analysis not found")

    job = analysis_jobs[analysis_id]

    return {
        "analysis_id": analysis_id,
        "status": job["status"],
        "progress": job["progress"],
    }


@router.get("/ally-deduction/{analysis_id}/results")
async def get_analysis_results(
    analysis_id: str,
    min_confidence: Optional[float] = 0.5,
    user: UserContext = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> Dict[str, Any]:
    """
    Get results of ally deduction analysis.

    Can filter by minimum confidence score.
    """
    if analysis_id not in analysis_jobs:
        raise HTTPException(status_code=404, detail="Analysis not found")

    job = analysis_jobs[analysis_id]

    if job["status"] != "completed":
        return {
            "analysis_id": analysis_id,
            "status": job["status"],
            "message": "Analysis not yet completed",
        }

    # Get dream job ID from result
    dream_job_id = job["result"]["dream_job_id"]

    # Fetch ally types from database
    query = db.query(DeducedAllyType).filter(
        DeducedAllyType.dream_job_id == dream_job_id
    )

    if min_confidence:
        query = query.filter(
            DeducedAllyType.confidence_score >= min_confidence)

    ally_types = query.order_by(DeducedAllyType.rank).all()

    return {
        "analysis_id": analysis_id,
        "status": "completed",
        "resume_id": job["result"]["resume_id"],
        "dream_job_id": dream_job_id,
        "ally_types": [
            {
                "id": ally.id,
                "ally_type_name": ally.ally_type_name,
                "confidence_score": ally.confidence_score,
                "selection_rationale": ally.selection_rationale,
                "search_queries": ally.search_queries,
                "engagement_strategy": ally.engagement_strategy,
                "rank": ally.rank,
            }
            for ally in ally_types
        ],
    }
