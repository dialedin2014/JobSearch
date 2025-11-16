"""
GitHub GraphQL API Demo

This script demonstrates how to use the GitHubClient with GraphQL.
Run with: python examples/github_graphql_demo.py

Requires GITHUB_API_TOKEN environment variable.
"""

from src.core.config import settings
from src.integrations.github_client import GitHubClient
import asyncio
import os
import sys
from pathlib import Path

# Add backend to path
backend_dir = Path(__file__).parent.parent
sys.path.insert(0, str(backend_dir))


async def demo_search_users():
    """Demo GraphQL user search."""
    print("\n" + "="*60)
    print("GitHub GraphQL User Search Demo")
    print("="*60)

    if not settings.github_api_token:
        print("❌ GITHUB_API_TOKEN not set. Please set it in .env or environment.")
        return

    client = GitHubClient()

    # Search for Python developers in Seattle
    print("\n🔍 Searching for: 'language:python location:seattle'")
    response = await client.search_users_graphql(
        query="language:python location:seattle",
        first=5
    )

    # Display results
    search_data = response["data"]["search"]
    print(f"\n📊 Found {search_data.get('userCount', 0)} total users")
    print(f"📄 Showing first {len(search_data['edges'])} results:\n")

    for idx, edge in enumerate(search_data['edges'], 1):
        user = edge['node']
        print(f"{idx}. @{user['login']}")
        if user.get('name'):
            print(f"   Name: {user['name']}")
        if user.get('company'):
            print(f"   Company: {user['company']}")
        if user.get('location'):
            print(f"   Location: {user['location']}")
        if user.get('bio'):
            print(f"   Bio: {user['bio'][:100]}...")
        print(f"   Followers: {user['followers']['totalCount']}")
        print(f"   Repos: {user['repositories']['totalCount']}")
        print(f"   URL: {user['url']}\n")

    # Display rate limit info
    rate_limit = response["data"]["rateLimit"]
    print(f"\n⚡ Rate Limit Info:")
    print(f"   Remaining: {rate_limit['remaining']} points")
    print(f"   Query Cost: {rate_limit['cost']} points")
    print(f"   Reset At: {rate_limit['resetAt']}")

    # Display pagination info
    page_info = search_data["pageInfo"]
    if page_info["hasNextPage"]:
        print(
            f"\n📖 More results available. Next cursor: {page_info['endCursor'][:20]}...")


async def demo_user_profile():
    """Demo GraphQL user profile retrieval."""
    print("\n" + "="*60)
    print("GitHub GraphQL User Profile Demo")
    print("="*60)

    if not settings.github_api_token:
        print("❌ GITHUB_API_TOKEN not set. Please set it in .env or environment.")
        return

    client = GitHubClient()

    # Get profile for a well-known user
    username = "torvalds"
    print(f"\n🔍 Fetching profile for: @{username}")

    response = await client.get_user_profile_graphql(username)

    if response and response["data"]["user"]:
        user = response["data"]["user"]

        print(f"\n👤 Profile Information:")
        print(f"   Login: @{user['login']}")
        print(f"   Name: {user.get('name', 'N/A')}")
        print(f"   Bio: {user.get('bio', 'N/A')}")
        print(f"   Company: {user.get('company', 'N/A')}")
        print(f"   Location: {user.get('location', 'N/A')}")
        print(f"   Email: {user.get('email', 'N/A')}")
        print(f"   Website: {user.get('websiteUrl', 'N/A')}")
        print(f"   Twitter: @{user.get('twitterUsername', 'N/A')}")

        print(f"\n📊 Statistics:")
        print(f"   Followers: {user['followers']['totalCount']}")
        print(f"   Following: {user['following']['totalCount']}")
        print(f"   Public Repos: {user['repositories']['totalCount']}")
        print(f"   Gists: {user['gists']['totalCount']}")
        print(
            f"   Total Contributions: {user['contributionsCollection']['contributionCalendar']['totalContributions']}")

        if user.get('organizations', {}).get('nodes'):
            print(
                f"\n🏢 Organizations ({len(user['organizations']['nodes'])}):")
            for org in user['organizations']['nodes'][:5]:
                print(f"   - {org['name']} (@{org['login']})")
                print(f"     {org['url']}")

        print(f"\n📅 Account Created: {user['createdAt']}")
        print(f"   Last Updated: {user['updatedAt']}")
        print(f"   Profile URL: {user['url']}")

        # Display rate limit info
        rate_limit = response["data"]["rateLimit"]
        print(f"\n⚡ Rate Limit Info:")
        print(f"   Remaining: {rate_limit['remaining']} points")
        print(f"   Query Cost: {rate_limit['cost']} points")
        print(f"   Reset At: {rate_limit['resetAt']}")
    else:
        print(f"❌ User not found: @{username}")


async def demo_comparison():
    """Demo showing GraphQL advantages over REST."""
    print("\n" + "="*60)
    print("GraphQL vs REST API Comparison")
    print("="*60)

    print("\n🎯 Why GraphQL is Better:")
    print("\n1. Single Request for Complex Data")
    print("   REST: Need 3+ requests (user, repos, orgs)")
    print("   GraphQL: Get everything in 1 request")

    print("\n2. No Over-fetching")
    print("   REST: Returns all fields (many unused)")
    print("   GraphQL: Request only fields you need")

    print("\n3. Built-in Rate Limit Info")
    print("   REST: Separate header parsing")
    print("   GraphQL: Included in every response")

    print("\n4. Strongly Typed Schema")
    print("   REST: Documentation can be outdated")
    print("   GraphQL: Schema is the documentation")

    print("\n5. Nested Data in One Call")
    print("   REST: Followers count requires separate request")
    print("   GraphQL: Get followers.totalCount directly")

    print("\n📖 GraphQL Query Example:")
    print("""
    query {
      user(login: "torvalds") {
        login
        name
        followers { totalCount }
        repositories { totalCount }
        organizations { nodes { login } }
        contributionsCollection {
          contributionCalendar { totalContributions }
        }
      }
    }
    """)


async def main():
    """Run all demos."""
    try:
        await demo_comparison()
        await demo_search_users()
        await demo_user_profile()

        print("\n" + "="*60)
        print("✅ Demo Complete!")
        print("="*60)

    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    # Check if token is set
    if not os.getenv("GITHUB_API_TOKEN"):
        print("\n⚠️  Warning: GITHUB_API_TOKEN not set!")
        print("Set it with: export GITHUB_API_TOKEN='your_token_here'")
        print("\nRunning comparison demo only...\n")
        asyncio.run(demo_comparison())
    else:
        print("\n✅ GITHUB_API_TOKEN found. Running full demo...")
        asyncio.run(main())
