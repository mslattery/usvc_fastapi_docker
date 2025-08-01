
# Create the ECR repo
terraform apply --target=aws_ecr_repository.api_repo --auto-approve

# Log in to the ECR registry
aws ecr get-login-password --region us-east-1 | docker login --username AWS --password-stdin 051055614445.dkr.ecr.us-east-1.amazonaws.com