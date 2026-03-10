#!/bin/bash
# Test script for MOJ Component Search API

API_URL="${API_URL:-http://localhost:5000}"

echo "🧪 Testing MOJ Component Search API"
echo "===================================="
echo ""

# Test 1: Health check
echo "Test 1: Health Check"
echo "-------------------"
curl -s "$API_URL/health" | jq '.' || echo "Failed"
echo ""
echo ""

# Test 2: Root endpoint
echo "Test 2: Root Endpoint"
echo "--------------------"
curl -s "$API_URL/" | jq '.' || echo "Failed"
echo ""
echo ""

# Test 3: Search for alert components
echo "Test 3: Search - Alert Components"
echo "---------------------------------"
curl -s -X POST "$API_URL/search" \
  -H "Content-Type: application/json" \
  -d '{"message": "How do I show error messages to users?", "limit": 3}' | jq '.'
echo ""
echo ""

# Test 4: Search for date picker
echo "Test 4: Search - Date Picker"
echo "----------------------------"
curl -s -X POST "$API_URL/search" \
  -H "Content-Type: application/json" \
  -d '{"message": "date picker component", "limit": 2}' | jq '.'
echo ""
echo ""

# Test 5: Search with research
echo "Test 5: Search - Components with Research"
echo "-----------------------------------------"
curl -s -X POST "$API_URL/search" \
  -H "Content-Type: application/json" \
  -d '{"message": "components that have user research", "limit": 5}' | jq '.'
echo ""
echo ""

# Test 6: Invalid request (missing message)
echo "Test 6: Invalid Request (Missing Message)"
echo "-----------------------------------------"
curl -s -X POST "$API_URL/search" \
  -H "Content-Type: application/json" \
  -d '{"query": "wrong field"}' | jq '.'
echo ""
echo ""

echo "✅ Tests complete!"
