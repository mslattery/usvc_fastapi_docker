
output "lambda_function_name" {
  description = "The name of the Lambda function"
  value       = aws_lambda_function.api_lambda.function_name
}

output "ecr_repository_url" {
  description = "The URL of the ECR repository"
  value       = aws_ecr_repository.api_repo.repository_url
}

output "api_endpoint" {
  description = "The URL endpoint for the API Gateway"
  value       = aws_apigatewayv2_stage.api_stage.invoke_url
}
