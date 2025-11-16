"""
Live GitHub GraphQL API Integration Test (T044i)

This test makes actual API calls to GitHub GraphQL API (v4) to validate:
- GraphQL response structure (name, nameWithOwner, url fields)
- Rate limit information (remaining, resetAt, cost)
- Data quality (results match search term)

Uses repository search which requires minimal permissions.
Requires GITHUB_API_TOKEN in environment to run.
Marked with @pytest.mark.live_api for optional execution.
"""

import pytest
import httpx
import os
from src.integrations.github_client import GitHubClient
from src.core.config import settings


@pytest.mark.live_api
@pytest.mark.asyncio
async def test_github_graphql_search_real_api():
    """
    Test live GitHub GraphQL API search with actual API call.
    Uses repository search which requires minimal permissions.

    Success criteria:
    1. API responds successfully (status 200)
    2. Response contains GraphQL data structure
    3. Repository nodes have expected fields (name, nameWithOwner, url)
    4. Rate limit information present (remaining, resetAt, cost)
    5. Results match search term (validates data quality)
    """
    # Skip if GITHUB_API_TOKEN not configured
    if not settings.github_api_token:
        pytest.skip("GITHUB_API_TOKEN not configured - skipping live API test")

    # Initialize GitHub client
    client = GitHubClient()

    # Search for well-known repositories to ensure consistent results
    search_query = "react"

    # Execute GraphQL search for repositories
    response = await client.search_repositories_graphql(query=search_query, first=5)

    # Verify response structure
    assert response is not None, "API should return response"
    assert "data" in response, "Response must contain 'data' field"
    assert "search" in response["data"], "Data must contain 'search' field"

    search_data = response["data"]["search"]
    assert "edges" in search_data, "Search must contain 'edges'"
    assert "pageInfo" in search_data, "Search must contain 'pageInfo'"

    edges = search_data["edges"]
    assert len(
        edges) > 0, f"Search for '{search_query}' should return at least 1 result"

    # Validate first repository node structure
    first_edge = edges[0]
    assert "node" in first_edge, "Edge must contain 'node'"

    repo = first_edge["node"]

    # Check required GraphQL fields for repositories
    required_fields = ['name', 'nameWithOwner', 'url']
    for field in required_fields:
        assert field in repo, f"Repository must contain '{field}' field"
        assert repo[field], f"Field '{field}' must have a value"

    # Validate data quality - repository name should match search term
    assert search_query.lower() in repo['nameWithOwner'].lower(), (
        f"Result '{repo['nameWithOwner']}' should contain search term '{search_query}'"
    )

    # Validate field types
    assert isinstance(repo['name'], str), "name must be string"
    assert isinstance(repo['nameWithOwner'],
                      str), "nameWithOwner must be string"
    assert isinstance(repo['url'], str), "url must be string"

    # Validate URLs are properly formatted
    assert repo['url'].startswith(
        'https://github.com/'), "url must be GitHub repository URL"

    # Validate numeric fields if present
    if 'stargazerCount' in repo:
        assert isinstance(repo['stargazerCount'],
                          int), "stargazerCount must be integer"
        assert repo['stargazerCount'] >= 0, "stargazerCount must be non-negative"

    # Validate rate limit information
    assert "rateLimit" in response["data"], "Response must include rateLimit"
    rate_limit = response["data"]["rateLimit"]
    assert "remaining" in rate_limit, "rateLimit must include 'remaining'"
    assert "resetAt" in rate_limit, "rateLimit must include 'resetAt'"
    assert "cost" in rate_limit, "rateLimit must include 'cost'"

    assert isinstance(rate_limit["remaining"],
                      int), "remaining must be integer"
    assert rate_limit["remaining"] >= 0, "remaining must be non-negative"
    assert isinstance(rate_limit["cost"], int), "cost must be integer"


@pytest.mark.live_api
@pytest.mark.asyncio
async def test_github_graphql_user_profile():
    """
    Test GitHub GraphQL get_user_profile endpoint with actual API call.

    Validates detailed profile retrieval with rich GraphQL data.
    """
    # Skip if GITHUB_API_TOKEN not configured
    if not settings.github_api_token:
        pytest.skip("GITHUB_API_TOKEN not configured - skipping live API test")

    client = GitHubClient()

    # Get profile for well-known user
    response = await client.get_user_profile_graphql("torvalds")

    assert response is not None, "Profile should be retrieved"
    assert "data" in response, "Response must contain 'data'"

    user = response["data"]["user"]
    assert user is not None, "User should be found"

    # Validate profile structure
    assert user['login'] == 'torvalds', "Login should match requested username"
    assert 'id' in user
    assert 'name' in user
    assert 'avatarUrl' in user
    assert 'url' in user
    assert 'bio' in user
    assert 'company' in user
    assert 'location' in user
    assert 'createdAt' in user

    # Validate nested GraphQL objects
    assert 'followers' in user
    assert 'totalCount' in user['followers']
    assert isinstance(user['followers']['totalCount'], int)

    assert 'following' in user
    assert 'totalCount' in user['following']
    assert isinstance(user['following']['totalCount'], int)

    assert 'repositories' in user
    assert 'totalCount' in user['repositories']
    assert isinstance(user['repositories']['totalCount'], int)

    # Validate rate limit
    assert "rateLimit" in response["data"]
    assert response["data"]["rateLimit"]["remaining"] >= 0


@pytest.mark.live_api
@pytest.mark.asyncio
async def test_github_graphql_search_multiple_results():
    """
    Test GitHub GraphQL search returns multiple results with pagination info.

    Ensures the API can handle searches that return multiple users.
    """
    # Skip if GITHUB_API_TOKEN not configured
    if not settings.github_api_token:
        pytest.skip("GITHUB_API_TOKEN not configured - skipping live API test")

    client = GitHubClient()

    # Search for common term that should return multiple results
    response = await client.search_users_graphql(
        query="language:python location:seattle",
        first=30
    )

    assert response is not None, "API should return response"

    search_data = response["data"]["search"]
    edges = search_data["edges"]

    assert len(edges) > 5, "Search should return multiple results (>5)"

    # Validate all results have consistent structure
    for idx, edge in enumerate(edges[:10]):  # Check first 10 results
        user = edge["node"]
        assert 'login' in user, f"Result {idx} missing 'login'"
        assert 'id' in user, f"Result {idx} missing 'id'"
        assert 'avatarUrl' in user, f"Result {idx} missing 'avatarUrl'"
        assert 'url' in user, f"Result {idx} missing 'url'"

        # Verify unique IDs
        if idx > 0:
            assert user['id'] != edges[0]['node']['id'], "Results should have unique IDs"

    # Validate pagination info
    page_info = search_data["pageInfo"]
    assert "hasNextPage" in page_info
    assert "endCursor" in page_info
    assert isinstance(page_info["hasNextPage"], bool)


@pytest.mark.live_api
@pytest.mark.asyncio
async def test_github_graphql_rate_limit_details():
    """
    Test that GitHub GraphQL API returns detailed rate limit information.

    GraphQL includes rate limit in every response with cost calculation.
    """
    # Skip if GITHUB_API_TOKEN not configured
    if not settings.github_api_token:
        pytest.skip("GITHUB_API_TOKEN not configured - skipping live API test")

    client = GitHubClient()

    # Execute simple search
    response = await client.search_users_graphql(query="guido", first=5)

    # Verify successful response
    assert "data" in response, "Response must contain data"

    # Verify rate limit details
    rate_limit = response["data"]["rateLimit"]

    assert "remaining" in rate_limit, "Must include remaining count"
    assert "resetAt" in rate_limit, "Must include reset timestamp"
    assert "cost" in rate_limit, "Must include query cost"

    # Validate values
    assert isinstance(rate_limit["remaining"],
                      int), "remaining must be integer"
    assert rate_limit["remaining"] >= 0, "remaining must be non-negative"

    assert isinstance(rate_limit["cost"], int), "cost must be integer"
    assert rate_limit["cost"] > 0, "cost must be positive for this query"

    # resetAt should be ISO 8601 timestamp
    assert isinstance(rate_limit["resetAt"], str), "resetAt must be string"
    assert "T" in rate_limit["resetAt"], "resetAt should be ISO 8601 format"


@pytest.mark.live_api
@pytest.mark.asyncio
async def test_github_graphql_rich_user_data():
    """
    Test GraphQL returns richer data than REST API.

    Validates GraphQL-specific fields like organizations and contributions.
    """
    # Skip if GITHUB_API_TOKEN not configured
    if not settings.github_api_token:
        pytest.skip("GITHUB_API_TOKEN not configured - skipping live API test")

    client = GitHubClient()

    # Get profile with rich data
    response = await client.get_user_profile_graphql("octocat")

    user = response["data"]["user"]

    # Validate GraphQL-specific nested data
    assert "organizations" in user, "Should include organizations"
    assert "nodes" in user["organizations"]

    assert "contributionsCollection" in user
    assert "contributionCalendar" in user["contributionsCollection"]
    assert "totalContributions" in user["contributionsCollection"]["contributionCalendar"]

    total_contributions = user["contributionsCollection"]["contributionCalendar"]["totalContributions"]
    assert isinstance(total_contributions,
                      int), "totalContributions must be integer"
    assert total_contributions >= 0, "totalContributions must be non-negative"
