"""
Content model for storing contact-generated content.

This module defines the Content SQLAlchemy model for storing posts, tweets,
issues, and other content created by contacts for semantic analysis.
"""

from sqlalchemy import Column, String, DateTime, Text, ForeignKey, LargeBinary, JSON
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from datetime import datetime
import uuid

from src.core.database import Base


class Content(Base):
    """
    Content model for contact-generated posts and articles.

    Stores content (posts, tweets, issues, articles) created by contacts
    for semantic analysis, keyword matching, and interest extraction.

    Attributes:
        id: Unique content identifier
        contact_id: Foreign key to Contact
        text: Full text content
        source_platform: Platform where content was posted
        url: URL to original content
        metadata: JSON containing additional metadata
        posted_at: Timestamp when content was posted
        embedding_vector: FAISS vector embedding (384-dim for all-MiniLM-L6-v2)
        ally_type_classification: JSON with ally type relevance scores
        created_at: Timestamp of record creation
    """

    __tablename__ = "content"

    # Primary key
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)

    # Foreign keys
    contact_id = Column(
        UUID(as_uuid=True),
        ForeignKey("contacts.id", ondelete="CASCADE"),
        nullable=False,
        index=True
    )

    # Content
    text = Column(Text, nullable=False)
    source_platform = Column(
        String(50),
        nullable=False,
        index=True,
        comment="Platform: github, twitter, linkedin, blog, etc."
    )
    url = Column(String(500), nullable=True)

    # Metadata
    content_metadata = Column(
        JSON,
        default=dict,
        comment="Additional metadata (likes, shares, comments, tags, etc.)"
    )
    posted_at = Column(DateTime, nullable=True, index=True)

    # Vector embedding for semantic search
    embedding_vector = Column(
        LargeBinary,
        nullable=True,
        comment="384-dim vector embedding from sentence-transformers"
    )

    # Ally type classification
    ally_type_classification = Column(
        JSON,
        default=dict,
        comment="Relevance scores for each ally type {ally_type_id: score}"
    )

    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    # Relationships
    contact = relationship("Contact", back_populates="content")

    def __repr__(self) -> str:
        """String representation of Content."""
        preview = self.text[:50] + "..." if len(self.text) > 50 else self.text
        return (
            f"<Content(id={self.id}, contact_id={self.contact_id}, "
            f"source={self.source_platform}, text='{preview}')>"
        )

    def to_dict(self) -> dict:
        """
        Convert content to dictionary for API responses.

        Returns:
            Dictionary representation of content
        """
        return {
            "id": str(self.id),
            "contact_id": str(self.contact_id),
            "text": self.text,
            "source_platform": self.source_platform,
            "url": self.url,
            "content_metadata": self.content_metadata,
            "posted_at": self.posted_at.isoformat() if self.posted_at else None,
            "has_embedding": self.embedding_vector is not None,
            "ally_type_classification": self.ally_type_classification,
            "created_at": self.created_at.isoformat() if self.created_at else None,
        }
