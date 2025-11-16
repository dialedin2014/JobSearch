# Running Live GitHub GraphQL API Integration Tests

## Overview

The test file `test_github_live_api.py` contains integration tests that make **actual API calls** to the **GitHub GraphQL API (v4)**. These tests are marked with `@pytest.mark.live_api` and are skipped by default unless you explicitly run them.

## Why GraphQL?

GitHub's GraphQL API v4 provides several advantages over the REST API:

- **Fetch exactly what you need** - no over-fetching or under-fetching
- **Single request for complex data** - get user, repos, orgs, contributions in one call
- **Built-in rate limit info** - every response includes remaining quota and cost
- **Strongly typed schema** - better validation and error handling
- **Future-proof** - GitHub's recommended API for new integrations

## Prerequisites

1. **GitHub Personal Access Token**: You need a valid GitHub API token

   - Create one at: https://github.com/settings/tokens
   - Minimum scopes required: `read:user`, `user:email`, `read:org`

2. **Set Environment Variable**:

   ```bash
   export GITHUB_API_TOKEN="your_github_token_here"
   ```

   Or add to your `.env` file:

   ```
   GITHUB_API_TOKEN=your_github_token_here
   ```

## Running the Tests

### Run ONLY live API tests:

```bash
cd backend
pytest -m live_api
```

### Run live API tests with verbose output:

```bash
cd backend
pytest -m live_api -v
```

### Run specific live API test:

```bash
cd backend
pytest tests/integration/test_github_live_api.py::test_github_graphql_search_real_api -v
```

### Skip live API tests (default behavior):

```bash
cd backend
pytest -m "not live_api"
```

### Run ALL tests including live API:

```bash
cd backend
pytest -m ""  # Runs all markers
```

## What the Tests Validate

1. **test_github_graphql_search_real_api**:

   - GraphQL API responds successfully (200 status)
   - Response structure: `data.search.edges[].node` contains user data
   - User fields: `login`, `id`, `avatarUrl`, `url`, `bio`, `company`, `location`
   - Rate limit info: `remaining`, `resetAt`, `cost` included in response
   - Data quality: results match search term

2. **test_github_graphql_user_profile**:

   - Tests get_user_profile_graphql endpoint
   - Validates detailed profile structure with nested objects
   - Confirms follower/following/repository counts
   - Validates organizations and contribution data

3. **test_github_graphql_search_multiple_results**:

   - Validates multiple results returned
   - Ensures consistent structure across results
   - Verifies unique IDs
   - Tests pagination info (`hasNextPage`, `endCursor`)

4. **test_github_graphql_rate_limit_details**:

   - Verifies rate limit information in every response
   - Validates `remaining`, `resetAt`, `cost` fields
   - Confirms query cost calculation

5. **test_github_graphql_rich_user_data**:
   - Tests GraphQL-specific rich data (organizations, contributions)
   - Validates nested GraphQL objects
   - Confirms data not available in REST API

## GraphQL Query Examples

### User Search Query

```graphql
query ($query: String!, $first: Int!) {
  search(query: $query, type: USER, first: $first) {
    edges {
      node {
        ... on User {
          login
          id
          avatarUrl
          url
          bio
          company
          location
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
```

### User Profile Query

```graphql
query ($login: String!) {
  user(login: $login) {
    login
    name
    bio
    followers {
      totalCount
    }
    repositories {
      totalCount
    }
    organizations(first: 10) {
      nodes {
        login
        name
      }
    }
  }
  rateLimit {
    remaining
    resetAt
  }
}
```

## Expected Behavior

- **Without token**: Tests are automatically skipped with message:

  ```
  SKIPPED [5] GITHUB_API_TOKEN not configured - skipping live API test
  ```

- **With token**: Tests run and validate against live GitHub GraphQL API

## Rate Limiting

GitHub GraphQL API limits:

- **Rate limit**: 5,000 points/hour
- **Query cost**: Each query costs points based on complexity
- **Built-in info**: Every response includes `rateLimit { remaining, resetAt, cost }`

These tests use minimal API calls (~5 total) with low query costs.

## Troubleshooting

### Tests are skipped

- **Cause**: `GITHUB_API_TOKEN` not set
- **Fix**: Export the environment variable or add to `.env`

### HTTP 401 Unauthorized

- **Cause**: Invalid or expired token
- **Fix**: Generate a new token from GitHub settings

### HTTP 403 Rate Limit Exceeded

- **Cause**: Too many API requests
- **Fix**: Wait for rate limit reset (check `X-RateLimit-Reset` header)

### Connection Errors

- **Cause**: Network issues or GitHub API down
- **Fix**: Check internet connection and GitHub status page

## CI/CD Integration

For CI/CD pipelines, you can:

1. **Skip live tests** (default):

   ```yaml
   pytest -m "not live_api"
   ```

2. **Run live tests with secrets**:
   ```yaml
   env:
     GITHUB_API_TOKEN: ${{ secrets.GITHUB_API_TOKEN }}
   run: pytest -m live_api
   ```

## Test Task ID

This test file implements **T044i** from the Phase 2 task list:

- Write live GitHub API integration test
- Validate response structure
- Verify rate limit headers
- Confirm data quality
- Optional execution with token requirement
