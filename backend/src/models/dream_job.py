"""
Dream Job Description model.

Represents user's career aspirations with versioning support.
"""

from sqlalchemy import Column, String, Text, Integer, Boolean, DateTime, JSON, ForeignKey
from sqlalchemy.orm import relationship
from datetime import datetime
from src.core.database import Base
from src.models.user_profile import generate_uuid


class DreamJobDescription(Base):
    """
    User's dream job description with version tracking.
    
    Attributes:
        id: Unique identifier (UUID)
        user_id: Reference to UserProfile
        description: Full dream job description text
        version: Version number (increments on updates)
        desired_role: Target job title
        desired_industry: Target industry
        desired_company_type: Type of company (startup, enterprise, etc.)
        required_skills: JSON array of required skills
        responsibilities: JSON array of desired responsibilities
        created_at: Creation timestamp
        is_active: Whether this is the current active version
        previous_version_id: Link to previous version
    """

    __tablename__ = "dream_job_descriptions"

    id = Column(String, primary_key=True, default=generate_uuid)
    user_id = Column(String, ForeignKey("user_profiles.user_id"), nullable=False, index=True)
    description = Column(Text, nullable=False)
    version = Column(Integer, nullable=False, default=1)
    desired_role = Column(String, nullable=True)
    desired_industry = Column(String, nullable=True)
    desired_company_type = Column(String, nullable=True)
    required_skills = Column(JSON, nullable=True, default=list)
    responsibilities = Column(JSON, nullable=True, default=list)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    is_active = Column(Boolean, default=True, nullable=False)
    previous_version_id = Column(String, ForeignKey("dream_job_descriptions.id"), nullable=True)

    # Relationships
    user = relationship("UserProfile", back_populates="dream_jobs")
    ally_types = relationship("DeducedAllyType", back_populates="dream_job", cascade="all, delete-orphan")
    previous_version = relationship("DreamJobDescription", remote_side=[id], backref="next_version")

    def __repr__(self):
        return f"<DreamJobDescription(id={self.id}, user_id={self.user_id}, version={self.version})>"
