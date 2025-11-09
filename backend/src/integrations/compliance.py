"""
API Terms of Service (ToS) compliance validation.

This module ensures all external API usage complies with platform ToS,
including rate limits, allowed endpoints, and forbidden patterns.
"""

from typing import Optional
import logging
from typing import Dict, Any, List
from datetime import datetime

logger = logging.getLogger(__name__)


class ComplianceError(Exception):
    """Raised when API usage violates ToS."""
    pass


class APIComplianceValidator:
    """
    Validates API usage against Terms of Service.

    Documents and enforces compliance rules for:
    - GitHub API
    - Twitter/X API  
    - LinkedIn (manual URL input only)
    - Apollo API
    """

    # GitHub API ToS Documentation
    GITHUB_RULES = {
        "rate_limits": {
            "authenticated": 5000,  # per hour
            "unauthenticated": 60,  # per hour
        },
        "allowed_endpoints": [
            "/users",
            "/search/users",
            "/users/{username}",
            "/users/{username}/repos",
            "/repos/{owner}/{repo}/issues",
        ],
        "forbidden_patterns": [
            "automated_following",
            "mass_starring",
            "spam_issues",
            "scraping_for_commercial_use",
        ],
        "tos_url": "https://docs.github.com/en/site-policy/github-terms/github-terms-of-service",
        "acceptable_use_url": "https://docs.github.com/en/site-policy/acceptable-use-policies/github-acceptable-use-policies",
    }

    # Twitter API ToS Documentation
    TWITTER_RULES = {
        "rate_limits": {
            "free_tier": {
                "user_lookup": 300,  # per 15 minutes
                "search": 180,  # per 15 minutes
            },
            "basic_tier": {
                "user_lookup": 300,  # per 15 minutes
                "search": 180,  # per 15 minutes
            },
        },
        "allowed_endpoints": [
            "/2/users",
            "/2/users/by",
            "/2/users/by/username/{username}",
            "/2/tweets/search/recent",
        ],
        "forbidden_patterns": [
            "automated_posting",
            "bulk_following",
            "scraping_tweets",
            "user_tracking_without_consent",
        ],
        "tos_url": "https://developer.twitter.com/en/developer-terms/agreement-and-policy",
        "rate_limit_docs": "https://developer.twitter.com/en/docs/twitter-api/rate-limits",
    }

    # LinkedIn ToS Documentation
    LINKEDIN_RULES = {
        "rate_limits": {
            "manual_url_input": None,  # No automated requests allowed
            "scraping": 0,  # Forbidden
        },
        "allowed_endpoints": [],  # No public API without partnership
        "allowed_methods": [
            "manual_url_input",  # Primary method: users paste profile URLs
        ],
        "forbidden_patterns": [
            "automated_scraping",
            "profile_harvesting",
            "data_collection_without_consent",
            "robots_txt_violations",
        ],
        "tos_url": "https://www.linkedin.com/legal/user-agreement",
        "robots_txt": "https://www.linkedin.com/robots.txt",
        "note": "LinkedIn restricts automated access. Manual URL input is the compliant method.",
    }

    # Apollo API ToS Documentation
    APOLLO_RULES = {
        "rate_limits": {
            "free_tier": 50,  # credits per month
            "basic_tier": 1000,  # credits per month
            "professional_tier": 3000,  # credits per month
        },
        "allowed_endpoints": [
            "/v1/people/search",
            "/v1/people/match",
            "/v1/organizations/search",
        ],
        "forbidden_patterns": [
            "reselling_data",
            "bulk_downloads",
            "competitive_intelligence_without_license",
        ],
        "tos_url": "https://www.apollo.io/terms",
        "privacy_url": "https://www.apollo.io/privacy",
    }

    @staticmethod
    def check_github_tos(
        request_count_per_hour: int,
        is_authenticated: bool,
        endpoint: str
    ) -> None:
        """
        Validate GitHub API usage compliance.

        Args:
            request_count_per_hour: Current hourly request count
            is_authenticated: Whether using authenticated requests
            endpoint: API endpoint being accessed

        Raises:
            ComplianceError: If usage violates ToS
        """
        rules = APIComplianceValidator.GITHUB_RULES

        # Check rate limits
        limit = rules["rate_limits"]["authenticated" if is_authenticated else "unauthenticated"]
        if request_count_per_hour > limit:
            raise ComplianceError(
                f"GitHub rate limit exceeded: {request_count_per_hour}/{limit} per hour. "
                f"See {rules['tos_url']}"
            )

        # Check endpoint is allowed
        endpoint_allowed = any(
            allowed in endpoint
            for allowed in rules["allowed_endpoints"]
        )
        if not endpoint_allowed:
            logger.warning(
                f"GitHub endpoint not in allowed list: {endpoint}. "
                f"Verify compliance: {rules['acceptable_use_url']}"
            )

    @staticmethod
    def check_twitter_tos(
        request_count_per_15min: int,
        tier: str = "free_tier",
        endpoint_type: str = "user_lookup"
    ) -> None:
        """
        Validate Twitter API usage compliance.

        Args:
            request_count_per_15min: Request count in current 15-min window
            tier: API tier ('free_tier', 'basic_tier')
            endpoint_type: Type of endpoint ('user_lookup', 'search')

        Raises:
            ComplianceError: If usage violates ToS
        """
        rules = APIComplianceValidator.TWITTER_RULES

        # Check rate limits
        tier_limits = rules["rate_limits"].get(
            tier, rules["rate_limits"]["free_tier"])
        limit = tier_limits.get(endpoint_type, 300)

        if request_count_per_15min > limit:
            raise ComplianceError(
                f"Twitter rate limit exceeded: {request_count_per_15min}/{limit} per 15 minutes. "
                f"See {rules['rate_limit_docs']}"
            )

    @staticmethod
    def check_linkedin_tos(method: str = "manual_url_input") -> None:
        """
        Validate LinkedIn usage compliance.

        Args:
            method: Method of accessing LinkedIn data

        Raises:
            ComplianceError: If method violates ToS
        """
        rules = APIComplianceValidator.LINKEDIN_RULES

        # Only manual URL input is allowed
        if method not in rules["allowed_methods"]:
            raise ComplianceError(
                f"LinkedIn method '{method}' violates ToS. "
                f"Only manual URL input is compliant. "
                f"See {rules['tos_url']} and {rules['robots_txt']}"
            )

        logger.info(
            "LinkedIn compliance: Using manual URL input (compliant method)")

    @staticmethod
    def check_apollo_tos(
        credits_used: int,
        tier: str = "free_tier",
        monthly_limit: Optional[int] = None
    ) -> None:
        """
        Validate Apollo API usage compliance.

        Args:
            credits_used: Number of credits used this month
            tier: API tier ('free_tier', 'basic_tier', 'professional_tier')
            monthly_limit: Optional custom monthly limit

        Raises:
            ComplianceError: If usage violates ToS
        """
        rules = APIComplianceValidator.APOLLO_RULES

        # Check credit limits
        limit = monthly_limit or rules["rate_limits"].get(tier, 50)

        if credits_used > limit:
            raise ComplianceError(
                f"Apollo credit limit exceeded: {credits_used}/{limit} credits per month. "
                f"Upgrade tier or wait for monthly reset. "
                f"See {rules['tos_url']}"
            )

    @staticmethod
    def get_compliance_report() -> Dict[str, Any]:
        """
        Generate compliance report for all APIs.

        Returns:
            Dictionary with compliance rules for each platform
        """
        return {
            "github": APIComplianceValidator.GITHUB_RULES,
            "twitter": APIComplianceValidator.TWITTER_RULES,
            "linkedin": APIComplianceValidator.LINKEDIN_RULES,
            "apollo": APIComplianceValidator.APOLLO_RULES,
            "generated_at": datetime.utcnow().isoformat(),
        }


# Optional type hint import
