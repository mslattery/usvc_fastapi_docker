# A Quick Framework for Python APIs with FastAPI, Docker, and Terraform

## Architecture: The Four Core Components

1. FastAPI (The Python Framework): A modern, fast (high-performance) web framework for building APIs with Python 3.7+ based on standard Python type hints.

1. Docker (The Containerization Tool): We will package our FastAPI application and all its dependencies into a standard, portable container image. This guarantees the application runs the same everywhere.

1. AWS Lambda + API Gateway (The Serverless Runtime): Instead of managing a virtual server, we'll deploy our Docker container as a serverless function (Lambda). AWS automatically handles scaling and execution. API Gateway provides a public HTTP endpoint that triggers the function.

1. Terraform (The Deployment Tool): We will define all the necessary AWS resources (the ECR container registry, the Lambda function, API Gateway, etc.) in a simple, declarative configuration file. This is Infrastructure as Code (IaC), which makes your deployment reliable and repeatable.

### Prerequisites
- Python 3.7+
- Docker
- Terraform
- AWS CLI (with your credentials configured)

## Build, Push, and Deploy

```
# Initilize Terraform
terraform init

# Create the ECR repo
terraform apply -target=aws_ecr_repository.api_repo --auto-approve

# Log in to the ECR registry
aws ecr get-login-password --region <YOUR_AWS_REGION> | docker login --username AWS --password-stdin <YOUR_AWS_ACCOUNT_ID>.dkr.ecr.<YOUR_AWS_REGION>.amazonaws.com

# Build the Docker image
docker build -t quick-api-repo .

# Tag the image for ECR
docker tag quick-api-repo:latest <YOUR_AWS_ACCOUNT_ID>.dkr.ecr.<YOUR_AWS_REGION>.amazonaws.com/quick-api-repo:latest

# Push the image to ECR
docker push <YOUR_AWS_ACCOUNT_ID>.dkr.ecr.<YOUR_AWS_REGION>.amazonaws.com/quick-api-repo:latest

# Make it so
terraform apply --auto-approve
```