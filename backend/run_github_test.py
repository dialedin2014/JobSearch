#!/usr/bin/env python3
"""
Standalone script to run GitHub integration test without pytest overhead.
"""
from src.core.config import settings
from src.integrations.github_client import GitHubClient
import sys
import os
import asyncio

# Add backend to path
sys.path.insert(0, '/workspace/backend')
os.chdir('/workspace/backend')


async def test_github_graphql_search_real_api():
    """
    Test live GitHub GraphQL API search with actual API call.
    Uses repository search which requires minimal permissions.
    """
    print("=" * 70)
    print("GitHub GraphQL API Integration Test")
    print("=" * 70)

    # Check if GITHUB_API_TOKEN is configured
    if not settings.github_api_token:
        print("❌ SKIP: GITHUB_API_TOKEN not configured")
        print("   Set GITHUB_API_TOKEN in .env file to run this test")
        return False

    print(
        f"✓ GitHub API Token configured: {settings.github_api_token[:10]}...")

    # Initialize GitHub client
    client = GitHubClient()
    print("✓ GitHub client initialized")

    # Search for well-known repositories to ensure consistent results
    search_query = "react"
    print(f"\nSearching for repositories matching '{search_query}'...")

    try:
        # Execute GraphQL search for repositories
        response = await client.search_repositories_graphql(query=search_query, first=5)

        # Check for errors first
        if "errors" in response:
            print(f"\n❌ GitHub API returned errors:")
            for error in response["errors"]:
                print(
                    f"   - {error.get('type', 'ERROR')}: {error.get('message', 'Unknown error')}")

            # Check if it's a scope issue
            if any('INSUFFICIENT_SCOPES' in str(e.get('type', '')) for e in response['errors']):
                print("\n💡 Solution: Your GitHub token needs additional scopes.")
                print("   Update your token at: https://github.com/settings/tokens")

            return False

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

        print(f"✓ Found {len(edges)} results")

        # Validate first repository node structure
        first_edge = edges[0]
        assert "node" in first_edge, "Edge must contain 'node'"

        repo = first_edge["node"]
        print(f"✓ First result: {repo.get('nameWithOwner', 'N/A')}")

        # Check required GraphQL fields for repository
        required_fields = ['name', 'nameWithOwner', 'url']
        for field in required_fields:
            assert field in repo, f"Repository must contain '{field}' field"
            assert repo[field], f"Field '{field}' must have a value"

        print(f"✓ Required fields present: {', '.join(required_fields)}")

        # Validate data quality - name should match search term
        assert search_query.lower() in repo['nameWithOwner'].lower(), (
            f"Result '{repo['nameWithOwner']}' should contain search term '{search_query}'"
        )
        print(f"✓ Data quality validated - repository name matches search term")

        # Validate field types
        assert isinstance(repo['name'], str), "name must be string"
        assert isinstance(repo['nameWithOwner'],
                          str), "nameWithOwner must be string"
        assert isinstance(repo['url'], str), "url must be string"
        print(f"✓ Field types validated")

        # Validate URLs are properly formatted
        assert repo['url'].startswith(
            'https://github.com/'), "url must be GitHub repository URL"
        print(f"✓ URLs properly formatted")

        # Validate numeric fields if present
        if 'stargazerCount' in repo:
            assert isinstance(repo['stargazerCount'],
                              int), "stargazerCount must be integer"
            assert repo['stargazerCount'] >= 0, "stargazerCount must be non-negative"
            print(f"✓ Repository has {repo['stargazerCount']} stars")

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

        print(
            f"✓ Rate limit info: {rate_limit['remaining']} requests remaining (cost: {rate_limit['cost']})")

        print("\n" + "=" * 70)
        print("✅ ALL TESTS PASSED - GitHub GraphQL API integration successful!")
        print("=" * 70)
        return True

    except AssertionError as e:
        print(f"\n❌ Test assertion failed: {e}")
        return False
    except Exception as e:
        print(f"\n❌ Unexpected error: {e}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    success = asyncio.run(test_github_graphql_search_real_api())
    sys.exit(0 if success else 1)
