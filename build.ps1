docker buildx build --platform linux/amd64 --provenance=false -t quick-api-repo:latest .
docker tag quick-api-repo:latest 051055614445.dkr.ecr.us-east-1.amazonaws.com/quick-api-repo:latest
