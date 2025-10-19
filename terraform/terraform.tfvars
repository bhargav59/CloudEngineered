# Terraform Variables for CloudEngineered
# Configured for AWS deployment

# AWS Configuration
aws_region = "us-east-1"
environment = "prod"

# Network Configuration
vpc_cidr = "10.0.0.0/16"
allowed_ssh_cidr_blocks = ["20.192.21.54/32"]  # Your current IP for security

# Database Configuration
db_instance_class = "db.t3.micro"
db_allocated_storage = 20
db_name = "cloudengineered"
db_username = "cloudengineered"
db_password = "FCqcsZzDi3RU6g5xNEyBfg"

# Redis Configuration
redis_node_type = "cache.t3.micro"

# S3 Configuration
static_bucket_name = "cloudengineered-static-594331568872"  # Globally unique with account ID

# EC2 Configuration
ec2_ami_id = "ami-0341d95f75f311023"  # Amazon Linux 2023 in us-east-1
ec2_instance_type = "t3.medium"
key_pair_name = "cloudengineered-key"

# Domain Configuration (optional - leave empty to skip SSL/Route53)
domain_name = ""  # e.g., "yourdomain.com"

# Django Configuration
django_secret_key = "Vwwd64Wd0cnYsuRqDveTltja8TuSe4dmN_ydnqns9ow"

# API Keys (optional)
openai_api_key = ""
anthropic_api_key = ""
github_token = ""

# Email Configuration (optional)
ses_smtp_user = ""
ses_smtp_password = ""