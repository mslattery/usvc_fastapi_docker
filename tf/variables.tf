variable "aws_region" {
  description = "AWS region"
  type        = string
  default = "us-east-1"
}

variable "common_tags" {
  description = "A list of common tags to be applied to all resources"
  type        = map(string)
  default = {
    Environment = "dev"
    Team        = "cloud team"
  }
}
