"""
Parsed Resume model.

Represents structured data extracted from uploaded resume.
"""

from sqlalchemy import Column, String, Text, Float, DateTime, JSON, ForeignKey
from sqlalchemy.orm import relationship
from datetime import datetime
from src.core.database import Base
from src.models.user_profile import generate_uuid


class ParsedResume(Base):
    """
    Structured resume data extracted from uploaded file.

    Attributes:
        id: Unique identifier (UUID)
        user_profile_id: Reference to UserProfile
        raw_text: Full extracted text from resume
        skills: JSON array of identified skills
        achievements: JSON array of notable accomplishments
        work_history: JSON array of work experience with company, title, dates, description
        education: JSON array of degrees and institutions
        companies: JSON array of company names for network mapping
        keywords: JSON array of extracted keywords for matching
        parsing_confidence: Quality score (0.0-1.0)
        parsed_at: When parsing occurred
        parser_version: Parsing algorithm version
    """

    __tablename__ = "parsed_resumes"

    id = Column(String, primary_key=True, default=generate_uuid)
    user_profile_id = Column(String, ForeignKey(
        "user_profiles.id"), nullable=False, index=True)
    raw_text = Column(Text, nullable=False)
    skills = Column(JSON, nullable=False, default=list)
    achievements = Column(JSON, nullable=True, default=list)
    work_history = Column(JSON, nullable=False, default=list)
    education = Column(JSON, nullable=True, default=list)
    companies = Column(JSON, nullable=False, default=list)
    keywords = Column(JSON, nullable=False, default=list)
    parsing_confidence = Column(Float, nullable=False, default=0.0)
    parsed_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    parser_version = Column(String, nullable=False, default="1.0")

    # Relationships
    # Many-to-one: Many resumes can belong to one user
    user_profile = relationship("UserProfile", back_populates="parsed_resumes")

    def __repr__(self):
        return f"<ParsedResume(id={self.id}, user_id={self.user_profile_id}, confidence={self.parsing_confidence})>"
