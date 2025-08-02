#!/bin/bash

API_URL="http://localhost:8989/api/v1/hc"
REQUESTS=10
DELAY=0.001

echo "Testing rate limits on $API_URL ($REQUESTS requests, ${DELAY}s delay)"
echo "----------------------------------------"

for i in $(seq 1 $REQUESTS); do
    response=$(curl -i -s -w "\n%{http_code}" $API_URL)
    status_code=$(echo "$response" | tail -n1)

    printf "\nRequest %2d: Status %s%d\033[0m" $i \
        $([[ $status_code == 200 ]] && echo -e "\033[32m" || echo -e "\033[31m") $status_code

    echo "$response" | grep -E "X-RateLimit-Remaining|Retry-After"

    [[ $i -lt $REQUESTS ]] && sleep $DELAY
done

echo -e "\n----------------------------------------\nTest completed!"