"""
User-defined Ally Type model for the Professional Ally-Hunting Platform.

Represents user-created ally type categories for targeted professional discovery.
"""

from sqlalchemy import Column, String, Text, Boolean, Float, Integer, DateTime, JSON, ForeignKey
from sqlalchemy.orm import relationship
from datetime import datetime
from src.core.database import Base
from src.models.user_profile import generate_uuid


class AllyType(Base):
    """
    User-defined professional ally type category.
    
    Attributes:
        id: Unique identifier (UUID)
        user_profile_id: Reference to UserProfile who created this ally type
        name: Display name (e.g., "AI Researchers", "Fintech Investors")
        keywords: JSON array of keywords for matching
        criteria: User-defined text criteria for this ally type
        search_parameters: JSON object with platform-specific search settings
        created_at: Creation timestamp
        is_active: Whether this ally type is currently active for searches
    """

    __tablename__ = "ally_types"

    id = Column(String, primary_key=True, default=generate_uuid)
    user_profile_id = Column(String, ForeignKey("user_profiles.id"), nullable=False, index=True)
    name = Column(String, nullable=False)
    keywords = Column(JSON, nullable=False, default=list)
    criteria = Column(Text, nullable=True)
    search_parameters = Column(JSON, nullable=False, default=dict)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    is_active = Column(Boolean, default=True, nullable=False)

    # Relationships
    user_profile = relationship("UserProfile", back_populates="ally_types")

    def __repr__(self):
        return f"<AllyType(id={self.id}, name={self.name}, user_profile_id={self.user_profile_id})>"


# Legacy model for backward compatibility with 002-dream-job-ally-deduction
class DeducedAllyType(Base):
    """
    AI-deduced professional ally type with confidence scoring.
    
    This is the legacy model from the dream-job-ally-deduction feature.
    New development should use the AllyType model above.
    """

    __tablename__ = "deduced_ally_types"

    id = Column(String, primary_key=True, default=generate_uuid)
    dream_job_id = Column(String, ForeignKey("dream_job_descriptions.id"), nullable=False, index=True)
    ally_type_name = Column(String, nullable=False)
    confidence_score = Column(Float, nullable=False)
    selection_rationale = Column(Text, nullable=False)
    search_queries = Column(JSON, nullable=False, default=dict)
    engagement_strategy = Column(Text, nullable=True)
    rank = Column(Integer, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    llm_model = Column(String, nullable=False, default="claude-3-sonnet-20240229")
    llm_prompt_version = Column(String, nullable=False, default="1.0")

    # Relationships
    dream_job = relationship("DreamJobDescription", back_populates="ally_types")

    def __repr__(self):
        return f"<DeducedAllyType(id={self.id}, name={self.ally_type_name}, confidence={self.confidence_score})>"
