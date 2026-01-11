#!/bin/bash

# Test script for CNB.cool API integration
# This script validates the CNB API endpoints and response formats

set -e

# Configuration
API_BASE_URL="${API_BASE_URL:-https://api.cnb.cool}"
CNB_TOKEN="${CNB_TOKEN:-db5HVM2xIiR0Zo11dcsuL4WeHGE}"
TEST_REPO="${TEST_REPO:-astral-sh/uv}"
TEST_TAG="${TEST_TAG:-v0.9.18}"
RETRY_COUNT=3
TIMEOUT=30

# Color output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

# Helper functions
print_header() {
    echo -e "${YELLOW}=== $1 ===${NC}"
}

print_success() {
    echo -e "${GREEN}✅ $1${NC}"
}

print_error() {
    echo -e "${RED}❌ $1${NC}"
}

# Execute request with retry logic
execute_request() {
    local method=$1
    local endpoint=$2
    local max_attempts=$3
    
    local attempt=1
    while [ $attempt -le $max_attempts ]; do
        echo -e "${YELLOW}Request attempt $attempt: $method $endpoint${NC}"
        
        response=$(curl -s -w "\n%{http_code}" \
            --max-time $TIMEOUT \
            -H "Authorization: Bearer $CNB_TOKEN" \
            -H "Content-Type: application/json" \
            -X "$method" \
            "$API_BASE_URL$endpoint")
        
        http_code=$(echo "$response" | tail -n 1)
        body=$(echo "$response" | head -n -1)
        
        if [ "$http_code" = "200" ] || [ "$http_code" = "302" ]; then
            print_success "HTTP $http_code"
            echo "$body"
            return 0
        elif [ "$http_code" = "429" ]; then
            print_error "Rate limited (HTTP 429)"
            if [ $attempt -lt $max_attempts ]; then
                sleep $((2 ** (attempt - 1)))
                attempt=$((attempt + 1))
            else
                return 1
            fi
        else
            print_error "HTTP $http_code"
            echo "Response: $body"
            return 1
        fi
    done
}

# Test Cases
print_header "CNB.cool API Integration Test Suite"
echo "Base URL: $API_BASE_URL"
echo "Test Repository: $TEST_REPO"
echo "Test Tag: $TEST_TAG"
echo "Token: ${CNB_TOKEN:0:10}..."
echo ""

# Test 1: Get Latest Release
print_header "Test 1: Get Latest Release"
if response=$(execute_request "GET" "/${TEST_REPO}/-/releases/latest" $RETRY_COUNT); then
    if echo "$response" | grep -q "tag_name\|id"; then
        print_success "Latest release retrieved"
        echo "Response preview: $(echo "$response" | head -c 200)..."
    else
        print_error "Invalid response format"
    fi
else
    print_error "Failed to get latest release"
fi
echo ""

# Test 2: Get Release by Tag
print_header "Test 2: Get Release by Tag ($TEST_TAG)"
if response=$(execute_request "GET" "/${TEST_REPO}/-/releases/tags/${TEST_TAG}" $RETRY_COUNT); then
    if echo "$response" | grep -q "tag_name"; then
        print_success "Release by tag retrieved"
        echo "Response preview: $(echo "$response" | head -c 200)..."
    else
        print_error "Invalid response format"
    fi
else
    print_error "Failed to get release by tag"
fi
echo ""

# Test 3: List Releases with Pagination
print_header "Test 3: List Releases (pagination)"
if response=$(execute_request "GET" "/${TEST_REPO}/-/releases?page=1&page_size=10" $RETRY_COUNT); then
    if echo "$response" | grep -q "\["; then
        print_success "Releases list retrieved"
        count=$(echo "$response" | grep -o "id" | wc -l)
        echo "Number of releases in response: $count"
    else
        print_error "Invalid response format"
    fi
else
    print_error "Failed to list releases"
fi
echo ""

# Test 4: Test Authentication
print_header "Test 4: Authentication Test"
if response=$(curl -s -w "\n%{http_code}" \
    --max-time $TIMEOUT \
    -H "Authorization: Bearer invalid_token" \
    "$API_BASE_URL/${TEST_REPO}/-/releases/latest"); then
    http_code=$(echo "$response" | tail -n 1)
    if [ "$http_code" = "401" ] || [ "$http_code" = "403" ]; then
        print_success "Authentication properly required (HTTP $http_code)"
    else
        print_error "Expected 401/403, got HTTP $http_code"
    fi
else
    print_error "Request failed"
fi
echo ""

# Summary
print_header "Test Summary"
print_success "All tests completed!"
echo ""
echo "Next steps:"
echo "1. Review test results above"
echo "2. Validate error handling"
echo "3. Check rate limiting behavior"
echo "4. Run Rust unit tests: cargo test --features cnb_releases"
