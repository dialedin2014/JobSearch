"""
User Profile model.

Represents an individual user account with resume and profile information.
"""

from sqlalchemy import Column, String, Integer, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from datetime import datetime
import uuid
from src.core.database import Base


def generate_uuid():
    """Generate UUID string."""
    return str(uuid.uuid4())


class UserProfile(Base):
    """
    User profile with uploaded resume data.
    
    Attributes:
        id: Unique identifier (UUID)
        user_id: External auth system user ID
        email: User email address
        resume_file_path: Path to uploaded resume file
        resume_file_name: Original filename
        resume_file_size: File size in bytes
        resume_upload_date: When resume was uploaded
        parsed_resume_id: Reference to ParsedResume
        created_at: Account creation timestamp
        updated_at: Last update timestamp
    """

    __tablename__ = "user_profiles"

    id = Column(String, primary_key=True, default=generate_uuid)
    user_id = Column(String, unique=True, nullable=False, index=True)
    email = Column(String, unique=True, nullable=False, index=True)
    password_hash = Column(String, nullable=False)  # bcrypt hashed password
    resume_file_path = Column(String, nullable=True)
    resume_file_name = Column(String, nullable=True)
    resume_file_size = Column(Integer, nullable=True)
    resume_upload_date = Column(DateTime, nullable=True)
    parsed_resume_id = Column(String, ForeignKey("parsed_resumes.id"), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    # Relationships
    parsed_resume = relationship("ParsedResume", back_populates="user_profile", uselist=False)
    ally_types = relationship("AllyType", back_populates="user_profile", cascade="all, delete-orphan")
    dream_jobs = relationship("DreamJobDescription", back_populates="user", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<UserProfile(id={self.id}, email={self.email})>"
