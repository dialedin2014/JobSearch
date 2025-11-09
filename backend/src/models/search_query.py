"""
SearchQuery model for tracking search executions and results.

This module defines the SearchQuery SQLAlchemy model for storing
search parameters, execution metadata, and result statistics.
"""

from sqlalchemy import Column, String, DateTime, Integer, ForeignKey, Float, JSON
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from datetime import datetime
import uuid

from src.core.database import Base


class SearchQuery(Base):
    """
    SearchQuery model for tracking searches.

    Stores search queries, filters, execution metadata, and counter-queries
    (shadow sequences) for result analysis.

    Attributes:
        id: Unique search query identifier
        user_profile_id: Foreign key to UserProfile
        original_query: Original search keywords
        ally_type_filters: JSON list of ally type IDs to filter by
        counter_queries: JSON list of generated counter-queries
        results_count: Number of results found
        status: Query status (processing, completed, failed)
        metadata: JSON with additional search parameters
        executed_at: Timestamp when search was executed
        completed_at: Timestamp when search completed
    """

    __tablename__ = "search_queries"

    # Primary key
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)

    # Foreign keys
    user_profile_id = Column(
        UUID(as_uuid=True),
        ForeignKey("user_profiles.id", ondelete="CASCADE"),
        nullable=False,
        index=True
    )

    # Search parameters
    original_query = Column(String(500), nullable=False)
    ally_type_filters = Column(
        JSON,
        default=list,
        comment="List of ally type UUIDs to filter search"
    )

    # Counter-queries (shadow sequences)
    counter_queries = Column(
        JSON,
        default=list,
        comment="Generated counter-queries for diverse perspectives"
    )

    # Results
    results_count = Column(Integer, default=0)
    status = Column(
        String(50),
        default="processing",
        index=True,
        comment="Status: processing, completed, failed"
    )

    # Metadata
    query_metadata = Column(
        JSON,
        default=dict,
        comment="Search parameters, platform filters, alternative_strategies, etc."
    )

    # Timestamps
    executed_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    completed_at = Column(DateTime, nullable=True)

    # Relationships
    user_profile = relationship("UserProfile", back_populates="search_queries")
    search_results = relationship(
        "SearchResult",
        back_populates="search_query",
        cascade="all, delete-orphan"
    )

    def __repr__(self) -> str:
        """String representation of SearchQuery."""
        return (
            f"<SearchQuery(id={self.id}, query='{self.original_query}', "
            f"status={self.status}, results={self.results_count})>"
        )

    def to_dict(self) -> dict:
        """
        Convert search query to dictionary for API responses.

        Returns:
            Dictionary representation of search query
        """
        return {
            "id": str(self.id),
            "user_profile_id": str(self.user_profile_id),
            "original_query": self.original_query,
            "ally_type_filters": self.ally_type_filters,
            "counter_queries": self.counter_queries,
            "results_count": self.results_count,
            "status": self.status,
            "query_metadata": self.query_metadata,
            "executed_at": self.executed_at.isoformat() if self.executed_at else None,
            "completed_at": self.completed_at.isoformat() if self.completed_at else None,
        }


class SearchResult(Base):
    """
    Individual search result linking to a Contact.

    Many-to-many relationship between SearchQuery and Contact,
    with additional metadata about the match.

    Attributes:
        id: Unique identifier
        search_query_id: Foreign key to SearchQuery
        contact_id: Foreign key to Contact
        match_score: Relevance score for this specific query
        matched_via: How contact was found (query, counter_query, etc.)
        created_at: When result was added
    """

    __tablename__ = "search_results"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)

    search_query_id = Column(
        UUID(as_uuid=True),
        ForeignKey("search_queries.id", ondelete="CASCADE"),
        nullable=False,
        index=True
    )

    contact_id = Column(
        UUID(as_uuid=True),
        ForeignKey("contacts.id", ondelete="CASCADE"),
        nullable=False,
        index=True
    )

    match_score = Column(Float, default=0.0)
    matched_via = Column(
        String(100),
        default="original_query",
        comment="original_query, counter_query, or specific counter_query text"
    )

    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    # Relationships
    search_query = relationship("SearchQuery", back_populates="search_results")
    contact = relationship("Contact")

    def __repr__(self) -> str:
        """String representation of SearchResult."""
        return (
            f"<SearchResult(search_query_id={self.search_query_id}, "
            f"contact_id={self.contact_id}, score={self.match_score:.2f})>"
        )
