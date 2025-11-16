"""
GitHub API client with rate limiting and circuit breaker pattern.

This module provides async HTTP client for GitHub API with resilience features.
"""

import httpx
from circuitbreaker import circuit
from tenacity import retry, stop_after_attempt, wait_exponential
from typing import Dict, Any, List, Optional
import logging
from src.core.config import settings
from src.core.rate_limiter import rate_limiter_manager

logger = logging.getLogger(__name__)


class GitHubClient:
    """
    GitHub API client with rate limiting and circuit breaker.

    Attributes:
        base_url: GitHub API base URL
        headers: Default headers including auth token
        rate_limiter: Token bucket rate limiter (5000 req/hour = 1.39 req/sec)
    """

    def __init__(self):
        """Initialize GitHub client."""
        self.base_url = "https://api.github.com"
        self.graphql_url = "https://api.github.com/graphql"
        self.headers = {
            "Accept": "application/vnd.github.v3+json",
            "User-Agent": "Dream-Job-Ally-Deduction",
        }

        if settings.github_api_token:
            self.headers["Authorization"] = f"Bearer {settings.github_api_token}"

        # Rate limiter: 5000 req/hour = 1.39 req/sec
        self.rate_limiter = rate_limiter_manager.get_or_create(
            "github", capacity=100, refill_rate=1.39
        )

    @circuit(failure_threshold=5, recovery_timeout=60)
    @retry(stop=stop_after_attempt(3), wait=wait_exponential(min=1, max=10))
    async def search_users(
        self, query: str, per_page: int = 30, page: int = 1
    ) -> List[Dict[str, Any]]:
        """
        Search for users on GitHub.

        Args:
            query: Search query (e.g., "location:Seattle language:Python")
            per_page: Results per page (max 100)
            page: Page number

        Returns:
            List of user dictionaries with profile information
        """
        if not self.rate_limiter.wait_and_acquire(tokens=1, timeout=60.0):
            logger.warning("GitHub rate limit exceeded")
            return []

        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(
                    f"{self.base_url}/search/users",
                    headers=self.headers,
                    params={"q": query, "per_page": per_page, "page": page},
                    timeout=30.0,
                )
                response.raise_for_status()
                data = response.json()
                return data.get("items", [])
        except httpx.HTTPStatusError as e:
            logger.error(f"GitHub API error: {e.response.status_code}")
            raise
        except Exception as e:
            logger.error(f"GitHub search users failed: {e}")
            raise

    @circuit(failure_threshold=5, recovery_timeout=60)
    @retry(stop=stop_after_attempt(3), wait=wait_exponential(min=1, max=10))
    async def get_user_profile(self, username: str) -> Optional[Dict[str, Any]]:
        """
        Get detailed user profile.

        Args:
            username: GitHub username

        Returns:
            User profile dictionary or None if not found
        """
        if not self.rate_limiter.wait_and_acquire(tokens=1, timeout=60.0):
            logger.warning("GitHub rate limit exceeded")
            return None

        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(
                    f"{self.base_url}/users/{username}",
                    headers=self.headers,
                    timeout=30.0,
                )
                response.raise_for_status()
                return response.json()
        except httpx.HTTPStatusError as e:
            if e.response.status_code == 404:
                logger.info(f"GitHub user not found: {username}")
                return None
            logger.error(f"GitHub API error: {e.response.status_code}")
            raise
        except Exception as e:
            logger.error(f"GitHub get user profile failed: {e}")
            raise

    @circuit(failure_threshold=5, recovery_timeout=60)
    @retry(stop=stop_after_attempt(3), wait=wait_exponential(min=1, max=10))
    async def search_repositories_graphql(
        self, query: str, first: int = 10, after: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Search for repositories on GitHub using GraphQL API.
        This is a simple query that requires minimal permissions.

        Args:
            query: Search query (e.g., "react" or "language:python stars:>1000")
            first: Number of results to return (max 100)
            after: Cursor for pagination

        Returns:
            GraphQL response with repositories and pageInfo
        """
        if not self.rate_limiter.wait_and_acquire(tokens=1, timeout=60.0):
            logger.warning("GitHub rate limit exceeded")
            return {"data": {"search": {"edges": [], "pageInfo": {}}}}

        graphql_query = """
        query($query: String!, $first: Int!, $after: String) {
          search(query: $query, type: REPOSITORY, first: $first, after: $after) {
            repositoryCount
            edges {
              node {
                ... on Repository {
                  name
                  nameWithOwner
                  description
                  url
                  stargazerCount
                  forkCount
                  primaryLanguage {
                    name
                  }
                  createdAt
                  updatedAt
                }
              }
            }
            pageInfo {
              hasNextPage
              endCursor
            }
          }
          rateLimit {
            remaining
            resetAt
            cost
          }
        }
        """

        variables = {
            "query": query,
            "first": first,
            "after": after
        }

        try:
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    self.graphql_url,
                    headers=self.headers,
                    json={"query": graphql_query, "variables": variables},
                    timeout=30.0,
                )
                response.raise_for_status()
                return response.json()
        except httpx.HTTPStatusError as e:
            logger.error(f"GitHub GraphQL API error: {e.response.status_code}")
            raise
        except Exception as e:
            logger.error(f"GitHub GraphQL search repositories failed: {e}")
            raise

    @circuit(failure_threshold=5, recovery_timeout=60)
    @retry(stop=stop_after_attempt(3), wait=wait_exponential(min=1, max=10))
    async def search_users_graphql(
        self, query: str, first: int = 30, after: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Search for users on GitHub using GraphQL API.

        Args:
            query: Search query (e.g., "location:Seattle language:Python")
            first: Number of results to return (max 100)
            after: Cursor for pagination

        Returns:
            GraphQL response with users and pageInfo
        """
        if not self.rate_limiter.wait_and_acquire(tokens=1, timeout=60.0):
            logger.warning("GitHub rate limit exceeded")
            return {"data": {"search": {"edges": [], "pageInfo": {}}}}

        graphql_query = """
        query($query: String!, $first: Int!, $after: String) {
          search(query: $query, type: USER, first: $first, after: $after) {
            userCount
            edges {
              node {
                ... on User {
                  login
                  id
                  name
                  avatarUrl
                  url
                  bio
                  company
                  location
                  email
                  websiteUrl
                  followers {
                    totalCount
                  }
                  following {
                    totalCount
                  }
                  repositories {
                    totalCount
                  }
                  createdAt
                }
              }
            }
            pageInfo {
              hasNextPage
              endCursor
            }
          }
          rateLimit {
            remaining
            resetAt
            cost
          }
        }
        """

        variables = {
            "query": query,
            "first": first,
            "after": after
        }

        try:
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    self.graphql_url,
                    headers=self.headers,
                    json={"query": graphql_query, "variables": variables},
                    timeout=30.0,
                )
                response.raise_for_status()
                return response.json()
        except httpx.HTTPStatusError as e:
            logger.error(f"GitHub GraphQL API error: {e.response.status_code}")
            raise
        except Exception as e:
            logger.error(f"GitHub GraphQL search users failed: {e}")
            raise

    @circuit(failure_threshold=5, recovery_timeout=60)
    @retry(stop=stop_after_attempt(3), wait=wait_exponential(min=1, max=10))
    async def get_user_profile_graphql(self, username: str) -> Optional[Dict[str, Any]]:
        """
        Get detailed user profile using GraphQL API.

        Args:
            username: GitHub username

        Returns:
            GraphQL response with user profile or None if not found
        """
        if not self.rate_limiter.wait_and_acquire(tokens=1, timeout=60.0):
            logger.warning("GitHub rate limit exceeded")
            return None

        graphql_query = """
        query($login: String!) {
          user(login: $login) {
            login
            id
            name
            avatarUrl
            url
            bio
            company
            location
            email
            websiteUrl
            twitterUsername
            followers {
              totalCount
            }
            following {
              totalCount
            }
            repositories {
              totalCount
            }
            gists {
              totalCount
            }
            organizations(first: 10) {
              nodes {
                login
                name
                url
              }
            }
            contributionsCollection {
              contributionCalendar {
                totalContributions
              }
            }
            createdAt
            updatedAt
          }
          rateLimit {
            remaining
            resetAt
            cost
          }
        }
        """

        variables = {"login": username}

        try:
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    self.graphql_url,
                    headers=self.headers,
                    json={"query": graphql_query, "variables": variables},
                    timeout=30.0,
                )
                response.raise_for_status()
                data = response.json()

                # Check if user was found
                if data.get("data", {}).get("user") is None:
                    logger.info(f"GitHub user not found: {username}")
                    return None

                return data
        except httpx.HTTPStatusError as e:
            logger.error(f"GitHub GraphQL API error: {e.response.status_code}")
            raise
        except Exception as e:
            logger.error(f"GitHub GraphQL get user profile failed: {e}")
            raise


# Global client instance
github_client = GitHubClient()
