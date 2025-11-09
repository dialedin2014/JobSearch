"""
Dream job description management API routes.
"""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel, Field
from typing import Dict, Any, Optional
import logging

from src.core.database import get_db
from src.core.security import UserContext, get_current_user
from src.models.dream_job import DreamJobDescription

logger = logging.getLogger(__name__)

router = APIRouter()


class DreamJobCreate(BaseModel):
    """Request model for creating dream job."""
    description: str = Field(..., min_length=50, description="Dream job description (min 50 characters)")
    desired_role: Optional[str] = None
    desired_industry: Optional[str] = None
    desired_company_type: Optional[str] = None


@router.post("/dream-jobs")
async def create_dream_job(
    dream_job_data: DreamJobCreate,
    user: UserContext = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> Dict[str, Any]:
    """
    Create new dream job description.
    
    Sets version=1 and is_active=true for first dream job.
    """
    # Check if user has existing dream jobs
    existing_count = db.query(DreamJobDescription).filter(
        DreamJobDescription.user_id == user.user_id
    ).count()
    
    version = existing_count + 1
    
    # Create dream job
    dream_job = DreamJobDescription(
        user_id=user.user_id,
        description=dream_job_data.description,
        version=version,
        desired_role=dream_job_data.desired_role,
        desired_industry=dream_job_data.desired_industry,
        desired_company_type=dream_job_data.desired_company_type,
        is_active=True,
    )
    
    # Deactivate previous versions if any
    if version > 1:
        db.query(DreamJobDescription).filter(
            DreamJobDescription.user_id == user.user_id,
            DreamJobDescription.is_active == True
        ).update({"is_active": False})
    
    db.add(dream_job)
    db.commit()
    db.refresh(dream_job)
    
    logger.info(f"Created dream job {dream_job.id} for user {user.user_id} (version {version})")
    
    return {
        "id": dream_job.id,
        "user_id": dream_job.user_id,
        "description": dream_job.description,
        "version": dream_job.version,
        "desired_role": dream_job.desired_role,
        "desired_industry": dream_job.desired_industry,
        "desired_company_type": dream_job.desired_company_type,
        "is_active": dream_job.is_active,
        "created_at": dream_job.created_at.isoformat(),
    }


@router.get("/dream-jobs/{dream_job_id}")
async def get_dream_job(
    dream_job_id: str,
    user: UserContext = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> Dict[str, Any]:
    """Get dream job description by ID."""
    dream_job = db.query(DreamJobDescription).filter(
        DreamJobDescription.id == dream_job_id,
        DreamJobDescription.user_id == user.user_id,
    ).first()
    
    if not dream_job:
        raise HTTPException(status_code=404, detail="Dream job not found")
    
    return {
        "id": dream_job.id,
        "user_id": dream_job.user_id,
        "description": dream_job.description,
        "version": dream_job.version,
        "desired_role": dream_job.desired_role,
        "desired_industry": dream_job.desired_industry,
        "desired_company_type": dream_job.desired_company_type,
        "required_skills": dream_job.required_skills,
        "responsibilities": dream_job.responsibilities,
        "is_active": dream_job.is_active,
        "created_at": dream_job.created_at.isoformat(),
        "previous_version_id": dream_job.previous_version_id,
    }
