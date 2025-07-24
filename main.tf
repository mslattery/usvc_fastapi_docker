# main.tf

# Configure the AWS provider
provider "aws" {
  region = "us-east-1" # You can change this to your preferred region
}

# 1. Create an ECR repository to store our Docker image
resource "aws_ecr_repository" "api_repo" {
  name                 = "quick-api-repo"
  image_tag_mutability = "MUTABLE" # Allows us to overwrite tags like 'latest'
}

# 2. Create an IAM role for the Lambda function
# This gives our function permission to run and write logs.
resource "aws_iam_role" "lambda_exec_role" {
  name = "quick-api-lambda-exec-role"

  assume_role_policy = jsonencode({
    Version   = "2012-10-17",
    Statement = [
      {
        Action    = "sts:AssumeRole",
        Effect    = "Allow",
        Principal = {
          Service = "lambda.amazonaws.com"
        }
      }
    ]
  })
}

# Attach the basic Lambda execution policy to the role
resource "aws_iam_role_policy_attachment" "lambda_basic_execution" {
  role       = aws_iam_role.lambda_exec_role.name
  policy_arn = "arn:aws:iam::aws:policy/service-role/AWSLambdaBasicExecutionRole"
}

# 3. Create the Lambda function itself from a Docker image
resource "aws_lambda_function" "api_lambda" {
  function_name = "quick-api-function"
  role          = aws_iam_role.lambda_exec_role.arn
  package_type  = "Image" # Specify we are using a container image

  # Point to the image in our ECR repository
  image_uri = "${aws_ecr_repository.api_repo.repository_url}:latest"
}

# 4. Create the API Gateway to expose the Lambda to the internet
resource "aws_apigatewayv2_api" "http_api" {
  name          = "quick-http-api"
  protocol_type = "HTTP"
}

# 5. Create the integration between API Gateway and the Lambda function
resource "aws_apigatewayv2_integration" "lambda_integration" {
  api_id           = aws_apigatewayv2_api.http_api.id
  integration_type = "AWS_PROXY"
  integration_uri  = aws_lambda_function.api_lambda.invoke_arn
}

# 6. Define the routes. The '$default' route catches all requests.
resource "aws_apigatewayv2_route" "default_route" {
  api_id    = aws_apigatewayv2_api.http_api.id
  route_key = "$default"
  target    = "integrations/${aws_apigatewayv2_integration.lambda_integration.id}"
}

# 7. Create a stage for deployment
resource "aws_apigatewayv2_stage" "api_stage" {
  api_id      = aws_apigatewayv2_api.http_api.id
  name        = "$default"
  auto_deploy = true
}

# 8. Give API Gateway permission to invoke the Lambda function
resource "aws_lambda_permission" "api_gateway_permission" {
  statement_id  = "AllowAPIGatewayInvoke"
  action        = "lambda:InvokeFunction"
  function_name = aws_lambda_function.api_lambda.function_name
  principal     = "apigateway.amazonaws.com"

  source_arn = "${aws_apigatewayv2_api.http_api.execution_arn}/*/*"
}

# Output the repository URL and the final API endpoint
output "ecr_repository_url" {
  description = "The URL of the ECR repository"
  value       = aws_ecr_repository.api_repo.repository_url
}

output "api_endpoint" {
  description = "The URL endpoint for the API Gateway"
  value       = aws_apigatewayv2_stage.api_stage.invoke_url
}
