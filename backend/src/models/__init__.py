"""Models package."""

# Import all models to ensure they're registered with SQLAlchemy
from src.models.user_profile import UserProfile
from src.models.resume import ParsedResume
from src.models.ally_type import AllyType, DeducedAllyType
from src.models.dream_job import DreamJobDescription
from src.models.contact import Contact
from src.models.content import Content
from src.models.search_query import SearchQuery, SearchResult

__all__ = [
    "UserProfile",
    "ParsedResume",
    "AllyType",
    "DeducedAllyType",
    "DreamJobDescription",
    "Contact",
    "Content",
    "SearchQuery",
    "SearchResult",
]
