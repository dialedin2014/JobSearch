#!/bin/bash
#
# Phase 1 Validation Test Suite
# Automated testing script for 001-civic-ally-hunter Phase 1
#

set -e

BASE_URL="http://localhost:8000"
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo "🧪 Phase 1 Validation Test Suite"
echo "=================================="
echo ""

# Test counter
declare -i TESTS_PASSED=0
declare -i TESTS_FAILED=0

# Helper function
test_endpoint() {
    local name="$1"
    local method="$2"
    local endpoint="$3"
    local headers="$4"
    local data="$5"
    local expected_code="$6"
    
    if [ -n "$data" ]; then
        response=$(curl -s -w "\n%{http_code}" -X "$method" "$BASE_URL$endpoint" $headers -H "Content-Type: application/json" -d "$data")
    else
        response=$(curl -s -w "\n%{http_code}" -X "$method" "$BASE_URL$endpoint" $headers)
    fi
    
    http_code=$(echo "$response" | tail -n1)
    body=$(echo "$response" | sed '$d')
    
    if [ "$http_code" -eq "$expected_code" ]; then
        echo -e "${GREEN}✓${NC} $name (HTTP $http_code)"
        ((TESTS_PASSED++))
        return 0
    else
        echo -e "${RED}✗${NC} $name (Expected $expected_code, got $http_code)"
        echo "   Response: $body"
        ((TESTS_FAILED++))
        return 1
    fi
}

# Check if server is running
echo "📡 Checking server status..."
if ! curl -s "$BASE_URL/api/v1/health" > /dev/null 2>&1; then
    echo -e "${RED}✗ Server not running at $BASE_URL${NC}"
    echo "  Start server with: cd backend && uvicorn src.main:app --reload"
    exit 1
fi
echo -e "${GREEN}✓ Server is running${NC}"
echo ""

# Test 1: Health Check
echo "🏥 Testing Health Endpoint..."
test_endpoint "Health Check" "GET" "/api/v1/health" "" "" 200
echo ""

# Test 2: User Registration
echo "👤 Testing Authentication..."
REGISTER_RESPONSE=$(curl -s -X POST "$BASE_URL/api/v1/auth/register" \
    -H "Content-Type: application/json" \
    -d "{\"email\": \"testuser_$(date +%s)@example.com\", \"password\": \"testpass123\"}")

ACCESS_TOKEN=$(echo "$REGISTER_RESPONSE" | jq -r '.access_token')

if [ -n "$ACCESS_TOKEN" ] && [ "$ACCESS_TOKEN" != "null" ]; then
    echo -e "${GREEN}✓${NC} User Registration"
    ((TESTS_PASSED++))
else
    echo -e "${RED}✗${NC} User Registration failed"
    echo "   Response: $REGISTER_RESPONSE"
    ((TESTS_FAILED++))
    exit 1
fi

# Test 3: Get Current User
test_endpoint "Get Current User" "GET" "/api/v1/auth/me" "-H \"Authorization: Bearer $ACCESS_TOKEN\"" "" 200

# Test 4: Unauthorized Access
test_endpoint "Unauthorized Access" "GET" "/api/v1/auth/me" "" "" 401
echo ""

# Test 5: Resume Upload
echo "📄 Testing Resume Upload..."
echo "Test Resume Content" > /tmp/test_resume_validation.txt
UPLOAD_RESPONSE=$(curl -s -X POST "$BASE_URL/api/v1/resumes/upload" \
    -H "Authorization: Bearer $ACCESS_TOKEN" \
    -F "file=@/tmp/test_resume_validation.txt")

RESUME_ID=$(echo "$UPLOAD_RESPONSE" | jq -r '.resume_id')

if [ -n "$RESUME_ID" ] && [ "$RESUME_ID" != "null" ]; then
    echo -e "${GREEN}✓${NC} Resume Upload"
    ((TESTS_PASSED++))
else
    echo -e "${RED}✗${NC} Resume Upload failed"
    echo "   Response: $UPLOAD_RESPONSE"
    ((TESTS_FAILED++))
fi

# Wait for parsing
echo "  ⏳ Waiting for parsing..."
sleep 2

# Test 6: Resume Status
test_endpoint "Resume Status Check" "GET" "/api/v1/resumes/$RESUME_ID/status" "-H \"Authorization: Bearer $ACCESS_TOKEN\"" "" 200

# Test 7: Resume Retrieval
test_endpoint "Resume Retrieval" "GET" "/api/v1/resumes/$RESUME_ID" "-H \"Authorization: Bearer $ACCESS_TOKEN\"" "" 200
echo ""

# Test 8: Ally Type CRUD
echo "🎯 Testing Ally Type CRUD..."

# Create
CREATE_RESPONSE=$(curl -s -X POST "$BASE_URL/api/v1/ally-types" \
    -H "Authorization: Bearer $ACCESS_TOKEN" \
    -H "Content-Type: application/json" \
    -d '{"name": "Test Ally Type", "keywords": ["test"], "criteria": "Test criteria"}')

ALLY_TYPE_ID=$(echo "$CREATE_RESPONSE" | jq -r '.id')

if [ -n "$ALLY_TYPE_ID" ] && [ "$ALLY_TYPE_ID" != "null" ]; then
    echo -e "${GREEN}✓${NC} Create Ally Type"
    ((TESTS_PASSED++))
else
    echo -e "${RED}✗${NC} Create Ally Type failed"
    ((TESTS_FAILED++))
fi

# List
test_endpoint "List Ally Types" "GET" "/api/v1/ally-types" "-H \"Authorization: Bearer $ACCESS_TOKEN\"" "" 200

# Get
test_endpoint "Get Ally Type" "GET" "/api/v1/ally-types/$ALLY_TYPE_ID" "-H \"Authorization: Bearer $ACCESS_TOKEN\"" "" 200

# Update
test_endpoint "Update Ally Type" "PUT" "/api/v1/ally-types/$ALLY_TYPE_ID" "-H \"Authorization: Bearer $ACCESS_TOKEN\"" "{\"name\": \"Updated Test Ally Type\"}" 200

# Export
test_endpoint "Export Ally Types" "GET" "/api/v1/ally-types/export" "-H \"Authorization: Bearer $ACCESS_TOKEN\"" "" 200

# Import
test_endpoint "Import Ally Types" "POST" "/api/v1/ally-types/import" "-H \"Authorization: Bearer $ACCESS_TOKEN\"" "{\"version\": \"1.0\", \"ally_types\": [{\"name\": \"Imported Ally\", \"keywords\": [\"test\"]}]}" 200

# Delete
DELETE_RESPONSE=$(curl -s -w "\n%{http_code}" -X DELETE "$BASE_URL/api/v1/ally-types/$ALLY_TYPE_ID" \
    -H "Authorization: Bearer $ACCESS_TOKEN")

DELETE_CODE=$(echo "$DELETE_RESPONSE" | tail -n1)

if [ "$DELETE_CODE" -eq 204 ]; then
    echo -e "${GREEN}✓${NC} Delete Ally Type (HTTP 204)"
    ((TESTS_PASSED++))
else
    echo -e "${RED}✗${NC} Delete Ally Type (Expected 204, got $DELETE_CODE)"
    ((TESTS_FAILED++))
fi

echo ""

# Summary
echo "=================================="
echo "📊 Test Summary"
echo "=================================="
echo -e "Passed: ${GREEN}$TESTS_PASSED${NC}"
echo -e "Failed: ${RED}$TESTS_FAILED${NC}"
echo ""

if [ $TESTS_FAILED -eq 0 ]; then
    echo -e "${GREEN}✅ All tests passed!${NC}"
    exit 0
else
    echo -e "${RED}❌ Some tests failed${NC}"
    exit 1
fi
