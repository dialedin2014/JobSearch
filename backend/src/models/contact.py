"""
Contact model for storing discovered ally contacts.

This module defines the Contact SQLAlchemy model for storing information
about potential professional allies discovered through multi-platform search.
"""

from sqlalchemy import Column, String, Float, DateTime, Text, ForeignKey, Integer, JSON
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from datetime import datetime
import uuid

from src.core.database import Base


class Contact(Base):
    """
    Contact model for discovered allies.

    Stores information about potential professional contacts discovered
    through GitHub, Twitter, LinkedIn, or other platforms.

    Attributes:
        id: Unique contact identifier
        ally_type_id: Foreign key to AllyType (nullable for general contacts)
        name: Contact's full name
        title: Job title or role
        company: Current company/organization
        location: Geographic location
        email: Contact email address
        phone: Phone number
        github_url: GitHub profile URL
        twitter_url: Twitter/X profile URL
        linkedin_url: LinkedIn profile URL
        relevance_score: Calculated relevance (0.0-1.0)
        matched_keywords: JSON list of matched ally type keywords
        source_platform: Platform where contact was discovered
        profile_data: JSON containing full profile information
        enrichment_data: JSON containing Apollo or other enrichment data
        created_at: Timestamp of contact creation
        last_updated: Timestamp of last update
    """

    __tablename__ = "contacts"

    # Primary key
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)

    # Foreign keys
    ally_type_id = Column(
        UUID(as_uuid=True),
        ForeignKey("ally_types.id", ondelete="CASCADE"),
        nullable=True,
        index=True
    )

    # Basic information
    name = Column(String(255), nullable=False, index=True)
    title = Column(String(255), nullable=True)
    company = Column(String(255), nullable=True, index=True)
    location = Column(String(255), nullable=True)

    # Contact details
    email = Column(String(255), nullable=True, index=True)
    phone = Column(String(50), nullable=True)

    # Social profiles
    github_url = Column(String(500), nullable=True)
    twitter_url = Column(String(500), nullable=True)
    linkedin_url = Column(String(500), nullable=True)

    # Relevance metrics
    relevance_score = Column(Float, default=0.0, index=True)
    matched_keywords = Column(JSON, default=list)

    # Source tracking
    source_platform = Column(
        String(50),
        nullable=False,
        index=True,
        comment="Platform: github, twitter, linkedin, apollo, manual"
    )

    # Extended data (JSON)
    profile_data = Column(
        JSON,
        default=dict,
        comment="Full profile data from source platform"
    )
    enrichment_data = Column(
        JSON,
        default=dict,
        comment="Enrichment data from Apollo or other services"
    )

    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    last_updated = Column(
        DateTime,
        default=datetime.utcnow,
        onupdate=datetime.utcnow,
        nullable=False
    )

    # Relationships
    ally_type = relationship("AllyType", back_populates="contacts")
    content = relationship(
        "Content",
        back_populates="contact",
        cascade="all, delete-orphan"
    )
    bridge_pitches = relationship(
        "BridgePitch",
        back_populates="target_contact",
        cascade="all, delete-orphan",
        foreign_keys="BridgePitch.target_contact_id"
    )
    network_connections_as_source = relationship(
        "NetworkConnection",
        back_populates="source_contact",
        foreign_keys="NetworkConnection.source_contact_id",
        cascade="all, delete-orphan"
    )
    network_connections_as_target = relationship(
        "NetworkConnection",
        back_populates="target_contact",
        foreign_keys="NetworkConnection.target_contact_id",
        cascade="all, delete-orphan"
    )

    def __repr__(self) -> str:
        """String representation of Contact."""
        return (
            f"<Contact(id={self.id}, name='{self.name}', "
            f"title='{self.title}', company='{self.company}', "
            f"source={self.source_platform}, relevance={self.relevance_score:.2f})>"
        )

    def to_dict(self) -> dict:
        """
        Convert contact to dictionary for API responses.

        Returns:
            Dictionary representation of contact
        """
        return {
            "id": str(self.id),
            "ally_type_id": str(self.ally_type_id) if self.ally_type_id else None,
            "name": self.name,
            "title": self.title,
            "company": self.company,
            "location": self.location,
            "email": self.email,
            "phone": self.phone,
            "github_url": self.github_url,
            "twitter_url": self.twitter_url,
            "linkedin_url": self.linkedin_url,
            "relevance_score": self.relevance_score,
            "matched_keywords": self.matched_keywords,
            "source_platform": self.source_platform,
            "profile_data": self.profile_data,
            "enrichment_data": self.enrichment_data,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "last_updated": self.last_updated.isoformat() if self.last_updated else None,
        }
