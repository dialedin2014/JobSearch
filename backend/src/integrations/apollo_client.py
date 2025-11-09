"""
Apollo API client for contact enrichment.

This module provides contact enrichment using Apollo.io API.
"""

import httpx
from circuitbreaker import circuit
from tenacity import retry, stop_after_attempt, wait_exponential
from typing import Dict, Any, Optional, List
import logging
from src.core.config import settings
from src.core.rate_limiter import rate_limiter_manager

logger = logging.getLogger(__name__)


class ApolloClient:
    """
    Apollo API client for contact enrichment.

    Apollo.io provides contact and company data enrichment.

    Free tier: 50 credits/month (1 credit = 1 contact enrichment)
    Basic tier ($49/mo): 1000 credits/month (~16 req/hour sustained)
    Professional tier ($99/mo): 3000 credits/month (~100 req/hour sustained)

    Attributes:
        base_url: Apollo API base URL
        headers: Default headers including API key
        rate_limiter: Token bucket rate limiter
        credits_used: Track credit usage
        credits_limit: Monthly credit limit
    """

    def __init__(self):
        """Initialize Apollo client."""
        self.base_url = "https://api.apollo.io/v1"
        self.headers = {
            "Content-Type": "application/json",
            "Cache-Control": "no-cache",
        }

        if settings.apollo_api_key:
            self.headers["Api-Key"] = settings.apollo_api_key

        # Rate limiter: Conservative for free tier (50 credits/month)
        # ~0.07 req/hour = 0.00002 req/sec for even distribution
        # But allow bursts with capacity=10
        self.rate_limiter = rate_limiter_manager.get_or_create(
            "apollo", capacity=10, refill_rate=0.01  # Conservative for free tier
        )

        self.credits_used = 0
        self.credits_limit = 50  # Free tier default

    @circuit(failure_threshold=5, recovery_timeout=60)
    @retry(stop=stop_after_attempt(3), wait=wait_exponential(min=1, max=10))
    async def enrich_contact(
        self, name: str, company: Optional[str] = None, email: Optional[str] = None
    ) -> Optional[Dict[str, Any]]:
        """
        Enrich contact information using Apollo API.

        Args:
            name: Contact's full name
            company: Company name (optional, improves accuracy)
            email: Email address (optional, for verification)

        Returns:
            Enriched contact data or None if not found/failed

        Response fields:
            - email: Verified email address
            - phone: Phone numbers
            - linkedin_url: LinkedIn profile URL
            - title: Current job title
            - organization: Company information
            - seniority: Job seniority level
            - departments: Departments/functions
        """
        if not settings.apollo_api_key:
            logger.warning("Apollo API key not configured")
            return None

        # Check credit limit
        if self.credits_used >= self.credits_limit:
            logger.warning(
                f"Apollo credit limit reached ({self.credits_used}/{self.credits_limit})"
            )
            return None

        # Rate limiting
        if not self.rate_limiter.wait_and_acquire(tokens=1, timeout=60.0):
            logger.warning("Apollo rate limit exceeded")
            return None

        try:
            async with httpx.AsyncClient() as client:
                # Apollo People Search API
                payload = {
                    "q_keywords": name,
                }

                if company:
                    payload["q_organization_domains"] = company

                if email:
                    payload["email"] = email

                response = await client.post(
                    f"{self.base_url}/people/search",
                    headers=self.headers,
                    json=payload,
                    timeout=30.0
                )

                response.raise_for_status()
                data = response.json()

                # Track credit usage
                self.credits_used += 1

                # Parse response
                if data.get("people") and len(data["people"]) > 0:
                    person = data["people"][0]  # Take first match

                    enriched = {
                        "email": person.get("email"),
                        "phone": person.get("phone_numbers", []),
                        "linkedin_url": person.get("linkedin_url"),
                        "title": person.get("title"),
                        "company": person.get("organization", {}).get("name"),
                        "company_domain": person.get("organization", {}).get("domain"),
                        "seniority": person.get("seniority"),
                        "departments": person.get("departments", []),
                        "city": person.get("city"),
                        "state": person.get("state"),
                        "country": person.get("country"),
                        "headline": person.get("headline"),
                        "source": "apollo",
                        "enriched_at": person.get("enriched_at"),
                    }

                    logger.info(f"Successfully enriched contact: {name}")
                    return enriched
                else:
                    logger.info(f"No Apollo data found for: {name}")
                    return None

        except httpx.HTTPStatusError as e:
            logger.error(
                f"Apollo API error: {e.response.status_code} - {e.response.text}")
            return None
        except Exception as e:
            logger.error(f"Apollo enrichment failed: {str(e)}")
            return None

    @circuit(failure_threshold=5, recovery_timeout=60)
    @retry(stop=stop_after_attempt(3), wait=wait_exponential(min=1, max=10))
    async def search_people(
        self,
        query: str,
        filters: Optional[Dict[str, Any]] = None,
        max_results: int = 10
    ) -> List[Dict[str, Any]]:
        """
        Search for people using Apollo API.

        Args:
            query: Search keywords
            filters: Optional filters (title, company, location, etc.)
            max_results: Maximum results to return

        Returns:
            List of person dictionaries
        """
        if not settings.apollo_api_key:
            logger.warning("Apollo API key not configured")
            return []

        # Check credit limit (each search uses 1 credit)
        if self.credits_used >= self.credits_limit:
            logger.warning(
                f"Apollo credit limit reached ({self.credits_used}/{self.credits_limit})"
            )
            return []

        # Rate limiting
        if not self.rate_limiter.wait_and_acquire(tokens=1, timeout=60.0):
            logger.warning("Apollo rate limit exceeded")
            return []

        try:
            async with httpx.AsyncClient() as client:
                payload = {
                    "q_keywords": query,
                    "per_page": min(max_results, 25),  # Apollo max is 25
                }

                # Add filters if provided
                if filters:
                    payload.update(filters)

                response = await client.post(
                    f"{self.base_url}/people/search",
                    headers=self.headers,
                    json=payload,
                    timeout=30.0
                )

                response.raise_for_status()
                data = response.json()

                # Track credit usage
                self.credits_used += 1

                people = data.get("people", [])
                logger.info(f"Apollo search returned {len(people)} results")

                return people

        except httpx.HTTPStatusError as e:
            logger.error(
                f"Apollo API error: {e.response.status_code} - {e.response.text}")
            return []
        except Exception as e:
            logger.error(f"Apollo search failed: {str(e)}")
            return []

    def get_credits_remaining(self) -> int:
        """
        Get remaining API credits.

        Returns:
            Number of credits remaining
        """
        return max(0, self.credits_limit - self.credits_used)

    def reset_credits(self, new_limit: Optional[int] = None) -> None:
        """
        Reset credit counter (for monthly reset).

        Args:
            new_limit: New credit limit (optional)
        """
        self.credits_used = 0
        if new_limit:
            self.credits_limit = new_limit
        logger.info(f"Apollo credits reset: {self.credits_limit} available")


# Global client instance
apollo_client = ApolloClient()
