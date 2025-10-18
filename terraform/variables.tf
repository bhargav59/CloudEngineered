# Terraform Variables for CloudEngineered AWS Deployment

variable "aws_region" {
  description = "AWS region to deploy resources"
  type        = string
  default     = "us-east-1"
}

variable "environment" {
  description = "Environment name (dev, staging, prod)"
  type        = string
  default     = "prod"
}

variable "vpc_cidr" {
  description = "CIDR block for VPC"
  type        = string
  default     = "10.0.0.0/16"
}

variable "allowed_ssh_cidr_blocks" {
  description = "CIDR blocks allowed to SSH into EC2 instances"
  type        = list(string)
  default     = ["0.0.0.0/0"] # Change this to your IP for security
}

# Database Configuration
variable "db_instance_class" {
  description = "RDS instance class"
  type        = string
  default     = "db.t3.micro"
}

variable "db_allocated_storage" {
  description = "Allocated storage for RDS (GB)"
  type        = number
  default     = 20
}

variable "db_name" {
  description = "Database name"
  type        = string
  default     = "cloudengineered"
}

variable "db_username" {
  description = "Database username"
  type        = string
  default     = "cloudengineered"
}

variable "db_password" {
  description = "Database password"
  type        = string
  sensitive   = true
}

# Redis Configuration
variable "redis_node_type" {
  description = "ElastiCache Redis node type"
  type        = string
  default     = "cache.t3.micro"
}

# S3 Configuration
variable "static_bucket_name" {
  description = "S3 bucket name for static files"
  type        = string
  default     = "cloudengineered-static"
}

# EC2 Configuration
variable "ec2_ami_id" {
  description = "AMI ID for EC2 instance (Amazon Linux 2)"
  type        = string
  default     = "ami-0c7217cdde317cfec" # Amazon Linux 2 in us-east-1
}

variable "ec2_instance_type" {
  description = "EC2 instance type"
  type        = string
  default     = "t3.medium"
}

variable "key_pair_name" {
  description = "Name of the EC2 key pair"
  type        = string
}

# Domain Configuration (optional)
variable "domain_name" {
  description = "Domain name for SSL certificate and Route 53 (leave empty to skip)"
  type        = string
  default     = ""
}

# Django Configuration
variable "django_secret_key" {
  description = "Django SECRET_KEY"
  type        = string
  sensitive   = true
}

# API Keys (optional - can be set via environment variables)
variable "openai_api_key" {
  description = "OpenAI API key"
  type        = string
  sensitive   = true
  default     = ""
}

variable "anthropic_api_key" {
  description = "Anthropic API key"
  type        = string
  sensitive   = true
  default     = ""
}

variable "github_token" {
  description = "GitHub token"
  type        = string
  sensitive   = true
  default     = ""
}

# Email Configuration (optional)
variable "ses_smtp_user" {
  description = "SES SMTP username"
  type        = string
  default     = ""
}

variable "ses_smtp_password" {
  description = "SES SMTP password"
  type        = string
  sensitive   = true
  default     = ""
}