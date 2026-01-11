#!/usr/bin/env python3
"""
CNB.cool API Verification Script
Validates the CNB API response formats match expectations for Rust integration
"""

import json
import sys
import requests
from typing import Optional, Dict, Any

# Configuration
API_BASE_URL = "https://api.cnb.cool"
API_TOKEN = "db5HVM2xIiR0Zo11dcsuL4WeHGE"
TEST_REPO = "astral-sh/uv"
TEST_TAG = "v0.9.18"
TIMEOUT = 30
RETRY_COUNT = 3

class Colors:
    """ANSI color codes"""
    GREEN = '\033[92m'
    RED = '\033[91m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    END = '\033[0m'

def print_header(text: str):
    """Print section header"""
    print(f"{Colors.YELLOW}{'='*70}")
    print(f"  {text}")
    print(f"{'='*70}{Colors.END}")

def print_success(text: str):
    """Print success message"""
    print(f"{Colors.GREEN}✅ {text}{Colors.END}")

def print_error(text: str):
    """Print error message"""
    print(f"{Colors.RED}❌ {text}{Colors.END}")

def print_info(text: str):
    """Print info message"""
    print(f"{Colors.BLUE}ℹ️  {text}{Colors.END}")

def validate_release_structure(release: Dict[str, Any]) -> bool:
    """Validate that release has expected structure"""
    required_fields = ['id', 'name', 'assets', 'created_at']
    
    for field in required_fields:
        if field not in release:
            print_error(f"Missing required field: {field}")
            return False
    
    # Validate assets structure
    if not isinstance(release['assets'], list):
        print_error("assets field should be a list")
        return False
    
    for asset in release['assets']:
        if not isinstance(asset, dict):
            print_error("Each asset should be a dict")
            return False
    
    print_success("Release structure valid")
    return True

def test_api_endpoint(
    method: str,
    endpoint: str,
    expected_status: int = 200
) -> Optional[Dict[str, Any]]:
    """Test a single API endpoint"""
    url = f"{API_BASE_URL}{endpoint}"
    headers = {
        "Authorization": f"Bearer {API_TOKEN}",
        "Accept": "application/vnd.cnb.api+json"
    }
    
    print_info(f"Testing: {method} {endpoint}")
    
    try:
        if method == "GET":
            response = requests.get(url, headers=headers, timeout=TIMEOUT)
        else:
            print_error(f"Unsupported method: {method}")
            return None
        
        if response.status_code == expected_status:
            print_success(f"HTTP {response.status_code}")
            
            # Try to parse JSON
            try:
                data = response.json()
                return data
            except json.JSONDecodeError:
                print_error("Response is not valid JSON")
                return None
        else:
            print_error(f"Expected HTTP {expected_status}, got {response.status_code}")
            print_info(f"Response: {response.text[:200]}")
            return None
    
    except requests.exceptions.Timeout:
        print_error("Request timeout")
        return None
    except requests.exceptions.RequestException as e:
        print_error(f"Request failed: {str(e)}")
        return None

def main():
    """Run all tests"""
    print(f"\n{Colors.BLUE}{'='*70}")
    print(f"  CNB.cool API Verification Suite")
    print(f"{'='*70}{Colors.END}")
    
    print(f"Base URL: {API_BASE_URL}")
    print(f"Test Repository: {TEST_REPO}")
    print(f"Test Tag: {TEST_TAG}")
    print(f"Token: {API_TOKEN[:10]}...")
    print()
    
    results = {
        "passed": 0,
        "failed": 0,
        "endpoints_tested": []
    }
    
    # Test 1: Get Latest Release
    print_header("Test 1: Get Latest Release")
    endpoint = f"/{TEST_REPO}/-/releases/latest"
    if data := test_api_endpoint("GET", endpoint):
        if validate_release_structure(data):
            print_info(f"Release tag: {data.get('tag_name', 'N/A')}")
            print_info(f"Release name: {data.get('name', 'N/A')}")
            print_info(f"Assets count: {len(data.get('assets', []))}")
            results["passed"] += 1
        else:
            results["failed"] += 1
    else:
        results["failed"] += 1
    results["endpoints_tested"].append(endpoint)
    print()
    
    # Test 2: Get Release by Tag
    print_header("Test 2: Get Release by Tag")
    endpoint = f"/{TEST_REPO}/-/releases/tags/{TEST_TAG}"
    if data := test_api_endpoint("GET", endpoint):
        if validate_release_structure(data):
            print_info(f"Release ID: {data.get('id', 'N/A')}")
            print_info(f"Is latest: {data.get('is_latest', False)}")
            results["passed"] += 1
        else:
            results["failed"] += 1
    else:
        results["failed"] += 1
    results["endpoints_tested"].append(endpoint)
    print()
    
    # Test 3: List Releases
    print_header("Test 3: List Releases (Pagination)")
    endpoint = f"/{TEST_REPO}/-/releases?page=1&page_size=10"
    if data := test_api_endpoint("GET", endpoint):
        if isinstance(data, list):
            print_success(f"Received list of {len(data)} releases")
            if len(data) > 0:
                print_info(f"First release: {data[0].get('name', 'N/A')}")
                if validate_release_structure(data[0]):
                    results["passed"] += 1
                else:
                    results["failed"] += 1
            else:
                results["passed"] += 1
        else:
            print_error("Expected list response")
            results["failed"] += 1
    else:
        results["failed"] += 1
    results["endpoints_tested"].append(endpoint)
    print()
    
    # Test 4: Authentication
    print_header("Test 4: Authentication")
    url = f"{API_BASE_URL}/{TEST_REPO}/-/releases/latest"
    headers = {"Authorization": "Bearer invalid_token"}
    
    print_info("Testing with invalid token...")
    try:
        response = requests.get(url, headers=headers, timeout=TIMEOUT)
        if response.status_code in [401, 403]:
            print_success(f"Authentication properly enforced (HTTP {response.status_code})")
            results["passed"] += 1
        else:
            print_error(f"Expected 401/403, got {response.status_code}")
            results["failed"] += 1
    except requests.exceptions.RequestException as e:
        print_error(f"Request failed: {str(e)}")
        results["failed"] += 1
    print()
    
    # Summary
    print_header("Test Summary")
    print_info(f"Passed: {results['passed']}")
    print_info(f"Failed: {results['failed']}")
    print_info(f"Total endpoints tested: {len(results['endpoints_tested'])}")
    print()
    
    if results["failed"] == 0:
        print_success("All tests passed! ✨")
        
        # Print summary data
        print()
        print_header("Data Model Summary")
        print(json.dumps({
            "api_base_url": API_BASE_URL,
            "release_endpoints": [
                "GET /{repo}/-/releases/latest",
                "GET /{repo}/-/releases/tags/{tag}",
                "GET /{repo}/-/releases?page={page}&page_size={page_size}",
                "GET /{repo}/-/releases/{release_id}",
                "GET /{repo}/-/releases/download/{tag}/{filename}"
            ],
            "release_fields": [
                "id", "tag_name", "name", "body", "draft", "is_latest",
                "prerelease", "author", "assets", "created_at",
                "updated_at", "published_at"
            ],
            "asset_fields": [
                "id", "name", "size", "download_url",
                "browser_download_url", "content_type", "created_at"
            ],
            "error_response_fields": [
                "errcode", "errmsg", "errparam"
            ]
        }, indent=2))
        
        return 0
    else:
        print_error("Some tests failed!")
        return 1

if __name__ == "__main__":
    sys.exit(main())
