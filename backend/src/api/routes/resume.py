"""
Resume upload and management API routes.
"""

from fastapi import APIRouter, UploadFile, File, Depends, HTTPException, BackgroundTasks
from sqlalchemy.orm import Session
from typing import Dict, Any
import os
import uuid
from pathlib import Path
import logging

from src.core.database import get_db
from src.core.config import settings
from src.core.security import UserContext, get_current_user
from src.models.user_profile import UserProfile
from src.models.resume import ParsedResume
from src.services.resume_parser import resume_parser

logger = logging.getLogger(__name__)

router = APIRouter()

# Ensure upload directory exists
Path(settings.upload_dir).mkdir(parents=True, exist_ok=True)

# Allowed file extensions
ALLOWED_EXTENSIONS = {"pdf", "docx", "doc", "txt"}


def allowed_file(filename: str) -> bool:
    """Check if file extension is allowed."""
    return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS


async def parse_resume_background(
    file_path: str, file_type: str, resume_id: str, db_session: Session
):
    """Background task for parsing resume."""
    try:
        logger.info(f"Parsing resume {resume_id} in background")
        
        # Parse resume
        parsed_data = resume_parser.parse_resume(file_path, file_type)
        
        # Update database record
        resume = db_session.query(ParsedResume).filter(ParsedResume.id == resume_id).first()
        if resume:
            resume.raw_text = parsed_data["raw_text"]
            resume.skills = parsed_data["skills"]
            resume.achievements = parsed_data["achievements"]
            resume.work_history = parsed_data["work_history"]
            resume.education = parsed_data["education"]
            resume.companies = parsed_data["companies"]
            resume.keywords = parsed_data["keywords"]
            resume.parsing_confidence = parsed_data["parsing_confidence"]
            resume.parsed_at = parsed_data["parsed_at"]
            resume.parser_version = parsed_data["parser_version"]
            
            db_session.commit()
            logger.info(f"Resume {resume_id} parsed successfully (confidence: {parsed_data['parsing_confidence']:.2f})")
        
    except Exception as e:
        logger.error(f"Error parsing resume {resume_id}: {e}")
        # Update status to failed
        resume = db_session.query(ParsedResume).filter(ParsedResume.id == resume_id).first()
        if resume:
            resume.parsing_confidence = 0.0
            db_session.commit()


@router.post("/resumes/upload")
async def upload_resume(
    background_tasks: BackgroundTasks,
    file: UploadFile = File(...),
    user: UserContext = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> Dict[str, Any]:
    """
    Upload resume file for parsing.
    
    Accepts PDF, DOCX, DOC, or TXT files up to 10MB.
    Returns resume_id for tracking parsing status.
    """
    # Validate file
    if not file.filename:
        raise HTTPException(status_code=400, detail="No file uploaded")
    
    if not allowed_file(file.filename):
        raise HTTPException(
            status_code=400,
            detail=f"File type not allowed. Supported: {', '.join(ALLOWED_EXTENSIONS)}",
        )
    
    # Check file size
    file.file.seek(0, 2)  # Seek to end
    file_size = file.file.tell()
    file.file.seek(0)  # Reset to beginning
    
    if file_size > settings.max_upload_size:
        raise HTTPException(
            status_code=400,
            detail=f"File too large. Maximum size: {settings.max_upload_size / 1024 / 1024:.1f}MB",
        )
    
    # Generate unique filename
    file_ext = file.filename.rsplit(".", 1)[1].lower()
    unique_filename = f"{uuid.uuid4()}.{file_ext}"
    file_path = os.path.join(settings.upload_dir, unique_filename)
    
    # Save file
    try:
        with open(file_path, "wb") as f:
            content = await file.read()
            f.write(content)
    except Exception as e:
        logger.error(f"Error saving file: {e}")
        raise HTTPException(status_code=500, detail="Failed to save file")
    
    # Get or create user profile
    user_profile = db.query(UserProfile).filter(UserProfile.user_id == user.user_id).first()
    if not user_profile:
        user_profile = UserProfile(
            user_id=user.user_id,
            email=user.email,
        )
        db.add(user_profile)
        db.commit()
        db.refresh(user_profile)
    
    # Create ParsedResume record
    parsed_resume = ParsedResume(
        user_id=user.user_id,
        raw_text="",  # Will be filled by background task
        parsing_confidence=0.0,  # Initial value
    )
    db.add(parsed_resume)
    db.commit()
    db.refresh(parsed_resume)
    
    # Update user profile
    user_profile.resume_file_path = file_path
    user_profile.resume_file_name = file.filename
    user_profile.resume_file_size = file_size
    user_profile.parsed_resume_id = parsed_resume.id
    db.commit()
    
    # Schedule background parsing
    background_tasks.add_task(
        parse_resume_background,
        file_path,
        file_ext,
        parsed_resume.id,
        db,
    )
    
    return {
        "message": "Resume uploaded successfully",
        "resume_id": parsed_resume.id,
        "status": "parsing",
        "filename": file.filename,
    }


@router.get("/resumes/{resume_id}/status")
async def get_resume_status(
    resume_id: str,
    user: UserContext = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> Dict[str, Any]:
    """Get parsing status of uploaded resume."""
    resume = db.query(ParsedResume).filter(
        ParsedResume.id == resume_id,
        ParsedResume.user_id == user.user_id,
    ).first()
    
    if not resume:
        raise HTTPException(status_code=404, detail="Resume not found")
    
    # Determine status
    if resume.parsing_confidence == 0.0 and not resume.raw_text:
        status = "parsing"
        progress = 50
    elif resume.parsing_confidence > 0.0:
        status = "parsed_success"
        progress = 100
    else:
        status = "parsing_failed"
        progress = 0
    
    return {
        "resume_id": resume.id,
        "status": status,
        "progress": progress,
        "parsing_confidence": resume.parsing_confidence,
    }


@router.get("/resumes/{resume_id}")
async def get_resume(
    resume_id: str,
    user: UserContext = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> Dict[str, Any]:
    """
    Get parsed resume data.
    
    Returns structured resume information including:
    - skills: List of extracted skills
    - achievements: Quantifiable accomplishments with metrics
    - work_history: Array of job entries (company, title, dates, description)
    - education: Degree and institution information
    - companies: Company names for network mapping
    - keywords: Extracted keywords for ally matching
    - parsing_confidence: Confidence score (0.0-1.0)
    """
    resume = db.query(ParsedResume).filter(
        ParsedResume.id == resume_id,
        ParsedResume.user_profile_id == user.user_id,
    ).first()
    
    if not resume:
        raise HTTPException(status_code=404, detail="Resume not found")
    
    return {
        "id": resume.id,
        "user_profile_id": resume.user_profile_id,
        "skills": resume.skills or [],
        "achievements": resume.achievements or [],
        "work_history": resume.work_history or [],
        "education": resume.education or [],
        "companies": resume.companies or [],
        "keywords": resume.keywords or [],
        "parsing_confidence": resume.parsing_confidence,
        "parsed_at": resume.parsed_at.isoformat() if resume.parsed_at else None,
        "parser_version": resume.parser_version,
    }
