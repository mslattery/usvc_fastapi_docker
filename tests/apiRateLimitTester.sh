#!/bin/bash

# Define colors for better readability
GREEN='\033[0;32m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Test Parameters
API_URL="http://localhost:8989/api/v1/health"
REQUESTS=10
DELAY=0.001

message="# Testing rate limits on $API_URL ($REQUESTS requests, ${DELAY}s delay) #"
length=${#message}
for (( i=1; i<=length; i++ )); do
  echo -n "#"
done
echo
echo $message
for (( i=1; i<=length; i++ )); do
  echo -n "#"
done
echo

# Test
for ((i=1; i<=REQUESTS; i++)); do
    # Get response body and HTTP status code in one call
    response=$(curl -s -w "\n%{http_code}" "$API_URL")

    # Efficiently separate body and status code using parameter expansion
    body="${response%$'\n'*}"
    status_code="${response##*$'\n'}"

    if [[ "$status_code" -eq 429 ]]; then
        echo -e "Status: ${RED}$status_code (Rate Limit Exceeded)${NC}"
    else
        # Look for the "status" key in the JSON response
        if [[ $body =~ \"status\"\s*:\s*\"([^\"]*)\" ]]; then
            message="${BASH_REMATCH[1]}"
        else
            message="<parsing failed>"
        fi
        echo -e "Status: ${GREEN}$status_code${NC} Message: $message"
    fi

    # Sleep between requests, but not after the last one
    (( i < REQUESTS )) && sleep "$DELAY"
done

echo -e "----------------------------------------\nTest completed!"