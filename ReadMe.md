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
terraform apply --target=aws_ecr_repository.api_repo --auto-approve

# Log in to the ECR registry
aws ecr get-login-password --region us-east-1 | docker login --username AWS --password-stdin 051055614445.dkr.ecr.us-east-1.amazonaws.com

# Build the Docker image
docker build -t quick-api-repo .

docker buildx build --platform linux/amd64 --provenance=false -t quick-api-repo:latest .



# Tag the image for ECR
docker tag quick-api-repo:latest 051055614445.dkr.ecr.us-east-1.amazonaws.com/quick-api-repo:latest

# Push the image to ECR
docker push 051055614445.dkr.ecr.us-east-1.amazonaws.com/quick-api-repo:latest

# Make it so
terraform apply --auto-approve
```


### Authentication

1. Add requirements - pip install "fastapi[all]" python-jose[cryptography] fastapi-sso

1. Get Credentials from your IdP:
    - Client ID
    - Client Secret
    - Redirect URI (also called Callback URL). For local development 
    this is often http://localhost:8000/auth/callback.
    
1. Implement SSO Logic

``` Python
import os
from fastapi import FastAPI, Depends, HTTPException, Request
from fastapi.responses import HTMLResponse
from fastapi_sso.sso.google import GoogleSSO
from jose import jwt, JWTError
from starlette.status import HTTP_403_FORBIDDEN

# Load credentials from environment variables
GOOGLE_CLIENT_ID = os.environ.get('GOOGLE_CLIENT_ID')
GOOGLE_CLIENT_SECRET = os.environ.get('GOOGLE_CLIENT_SECRET')
SECRET_KEY = os.environ.get('SECRET_KEY', 'a_very_secret_key') # For signing JWTs

app = FastAPI()

# Initialize Google SSO
google_sso = GoogleSSO(
    client_id=GOOGLE_CLIENT_ID,
    client_secret=GOOGLE_CLIENT_SECRET,
    redirect_uri="http://localhost:8000/auth/callback",
    allow_insecure_http=True # Use False in production with HTTPS
)

# Dependency to verify JWT
async def get_current_user(request: Request):
    token = request.cookies.get("access_token")
    if not token:
        raise HTTPException(status_code=HTTP_403_FORBIDDEN, detail="Not authenticated")
    try:
        # The token from the cookie is the session JWT, not the IdP token
        payload = jwt.decode(token, SECRET_KEY, algorithms=["HS256"])
        return payload
    except JWTError:
        raise HTTPException(status_code=HTTP_403_FORBIDDEN, detail="Invalid token")

# SSO Login and Callback Routes
@app.get("/auth/login")
async def auth_init():
    """Generate login url and redirect."""
    return await google_sso.get_login_redirect()

@app.get("/auth/callback")
async def auth_callback(request: Request):
    """
    Process login response from Google and create a session token.
    This sets a cookie in the user's browser.
    """
    user = await google_sso.verify_and_process(request)
    if user is None:
        raise HTTPException(status_code=401, detail="Authentication failed")

    # Create a session JWT for our app
    session_token = jwt.encode(user.model_dump(), SECRET_KEY, algorithm="HS256")

    response = HTMLResponse(content="<p>Successfully authenticated! You can now access protected routes. <a href='/'>Home</a></p>")
    response.set_cookie(
        key="access_token",
        value=f"Bearer {session_token}",
        httponly=True # Prevents client-side script access
    )
    return response

# Protected API Endpoint
@app.get("/api/me")
async def read_users_me(current_user: dict = Depends(get_current_user)):
    """A protected endpoint that requires authentication."""
    return {"email": current_user.get("email"), "provider": current_user.get("provider")}

# Root endpoint with a login link
@app.get("/")
def read_root():
    return HTMLResponse('<h1>Hello, World</h1><a href="/auth/login">Login with Google</a>')
```

1. Store secrets
```
aws secretsmanager create-secret --name my-app/sso-secrets \
    --secret-string '{"GOOGLE_CLIENT_ID":"your_id","GOOGLE_CLIENT_SECRET":"your_secret","SECRET_KEY":"your_jwt_secret"}'
```

1. TF

```
terraform {
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 5.0"
    }
  }
}

provider "aws" {
  region = "us-east-1"
}

# Fetch secrets from AWS Secrets Manager
data "aws_secretsmanager_secret" "sso_secrets" {
  name = "my-app/sso-secrets"
}

data "aws_secretsmanager_secret_version" "sso_secrets_version" {
  secret_id = data.aws_secretsmanager_secret.sso_secrets.id
}

locals {
  sso_secrets = jsondecode(data.aws_secretsmanager_secret_version.sso_secrets_version.secret_string)
}

# Networking (VPC, Subnets) - simplified for brevity
resource "aws_vpc" "main" {
  cidr_block = "10.0.0.0/16"
}

resource "aws_subnet" "public" {
  count             = 2
  vpc_id            = aws_vpc.main.id
  cidr_block        = cidrsubnet(aws_vpc.main.cidr_block, 8, count.index)
  availability_zone = ["us-east-1a", "us-east-1b"][count.index]
}

# ECS Cluster
resource "aws_ecs_cluster" "main" {
  name = "my-app-cluster"
}

# IAM Role for ECS Task Execution
resource "aws_iam_role" "ecs_task_execution_role" {
  name = "ecs-task-execution-role"
  assume_role_policy = jsonencode({
    Version   = "2012-10-17",
    Statement = [{
      Action    = "sts:AssumeRole",
      Effect    = "Allow",
      Principal = { Service = "ecs-tasks.amazonaws.com" }
    }]
  })
}

# Policy to allow access to Secrets Manager
resource "aws_iam_role_policy_attachment" "ecs_secrets_manager_access" {
  role       = aws_iam_role.ecs_task_execution_role.name
  policy_arn = "arn:aws:iam::aws:policy/SecretsManagerReadWrite" # Or a more restrictive custom policy
}

resource "aws_iam_role_policy_attachment" "ecs_task_execution_role_policy" {
    role       = aws_iam_role.ecs_task_execution_role.name
    policy_arn = "arn:aws:iam::aws:policy/service-role/AmazonECSTaskExecutionRolePolicy"
}

# ECS Task Definition
resource "aws_ecs_task_definition" "app_task" {
  family                   = "my-app-task"
  cpu                      = 256
  memory                   = 512
  network_mode             = "awsvpc"
  requires_compatibilities = ["FARGATE"]
  execution_role_arn       = aws_iam_role.ecs_task_execution_role.arn

  container_definitions = jsonencode([{
    name      = "my-app-container"
    image     = "YOUR_AWS_ECR_REPO_URL:latest" # e.g., 123456789012.dkr.ecr.us-east-1.amazonaws.com/my-app:latest
    portMappings = [{
      containerPort = 8000
      hostPort      = 8000
    }]
    # Inject secrets as environment variables
    secrets = [
      {
        name      = "GOOGLE_CLIENT_ID"
        valueFrom = "${data.aws_secretsmanager_secret.sso_secrets.arn}:GOOGLE_CLIENT_ID::"
      },
      {
        name      = "GOOGLE_CLIENT_SECRET"
        valueFrom = "${data.aws_secretsmanager_secret.sso_secrets.arn}:GOOGLE_CLIENT_SECRET::"
      },
      {
        name      = "SECRET_KEY"
        valueFrom = "${data.aws_secretsmanager_secret.sso_secrets.arn}:SECRET_KEY::"
      }
    ]
  }])
}

# ECS Service
resource "aws_ecs_service" "main" {
  name            = "my-app-service"
  cluster         = aws_ecs_cluster.main.id
  task_definition = aws_ecs_task_definition.app_task.arn
  desired_count   = 1
  launch_type     = "FARGATE"

  network_configuration {
    subnets         = aws_subnet.public[*].id
    assign_public_ip = true # For simplicity; use a load balancer in production
  }
}
```

docker run -p 8888:8000 -e GOOGLE_CLIENT_ID="YOUR_GOOGLE_CLIENT_ID" -e GOOGLE_CLIENT_SECRET="YOUR_GOOGLE_CLIENT_SECRET" -e SECRET_KEY="a_super_secret_key_for_jwt" quick-api-repo


    .\venv\Scripts\Activate.ps1

uvicorn main:app --reload --port 8989
