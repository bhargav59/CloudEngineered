# CloudEngineered Terraform Deployment

This directory contains Terraform configuration to deploy CloudEngineered to AWS with a production-ready infrastructure.

## 🚀 Quick Start

### Prerequisites

1. **AWS Account** with appropriate permissions
2. **Terraform** installed (v1.0+)
3. **AWS CLI** configured with your credentials
4. **SSH Key Pair** in AWS
5. **Domain Name** (optional but recommended)

### 1. Configure Variables

```bash
cd terraform
cp terraform.tfvars.example terraform.tfvars
# Edit terraform.tfvars with your values
```

**Required variables to set:**
- `db_password` - Secure database password
- `django_secret_key` - Random secret key (32+ chars)
- `key_pair_name` - Your AWS key pair name
- `allowed_ssh_cidr_blocks` - Your IP address for SSH access

### 2. Initialize Terraform

```bash
terraform init
```

### 3. Plan Deployment

```bash
terraform plan
```

Review the plan to ensure all resources will be created correctly.

### 4. Deploy Infrastructure

```bash
terraform apply
```

This will create:
- VPC with public/private subnets
- RDS PostgreSQL database
- ElastiCache Redis cluster
- S3 bucket with CloudFront CDN
- EC2 instance with application
- Application Load Balancer
- SSL certificate (if domain provided)
- Route 53 records (if domain provided)
- Security groups and IAM roles
- CloudWatch alarms

### 5. Access Application

After deployment, Terraform will output:
- Application URL
- SSH command for EC2 access
- Database connection details

## 📋 Architecture Overview

```
Internet → CloudFront (CDN) → S3 (Static Files)
       ↓
   Route 53 (DNS) → ALB (Load Balancer) → EC2 (Django App)
       ↓                    ↓
   Certificate Manager   Target Group
       ↓                    ↓
   SSL Certificate       Health Checks
                           ↓
                    Auto Scaling Group
                           ↓
                    EC2 Instance
                    ┌─────────────────┐
                    │  Docker Compose │
                    │ ┌─────────────┐ │
                    │ │  Nginx      │ │
                    │ │  (Reverse   │ │
                    │ │   Proxy)    │ │
                    │ └─────────────┘ │
                    │ ┌─────────────┐ │
                    │ │  Gunicorn   │ │
                    │ │  (WSGI)     │ │
                    │ └─────────────┘ │
                    │ ┌─────────────┐ │
                    │ │  Django     │ │
                    │ │  App        │ │
                    │ └─────────────┘ │
                    └─────────────────┘
                           ↓
                    ┌─────────────────┐
                    │  PostgreSQL    │ ← RDS
                    │  (Database)    │
                    └─────────────────┘
                           ↓
                    ┌─────────────────┐
                    │  Redis         │ ← ElastiCache
                    │  (Cache)       │
                    └─────────────────┘
```

## 🔧 Configuration Files

### Required Files

- `main.tf` - Main infrastructure configuration
- `variables.tf` - Input variable definitions
- `outputs.tf` - Output definitions
- `user_data.sh` - EC2 bootstrap script
- `terraform.tfvars` - Your variable values (create from example)

### Optional Files

- `terraform.tfvars.example` - Example variable values
- `backend.tf` - Remote state configuration (recommended for teams)

## 📊 Cost Estimate

| Service | Configuration | Monthly Cost |
|---------|---------------|--------------|
| EC2 (t3.medium) | 1 instance | $30-40 |
| RDS PostgreSQL | db.t3.micro | $15-25 |
| ElastiCache Redis | cache.t3.micro | $15-20 |
| S3 + CloudFront | Basic setup | $1-10 |
| Load Balancer | ALB | $15-20 |
| Route 53 | 1 hosted zone | $0.50 |
| **Total** | | **$76.50 - $115.50** |

*Costs may vary based on usage and region. Reserved instances can reduce costs by 30-50%.*

## 🔒 Security Features

- **Network Security**: Security groups restrict access to necessary ports only
- **SSH Access**: Limited to your IP address
- **Database Security**: RDS in private subnets, no public access
- **SSL/TLS**: HTTPS enforced with AWS Certificate Manager
- **IAM Roles**: Least-privilege access for EC2 instances
- **Secrets Management**: Sensitive data stored in SSM Parameter Store

## 📈 Scaling

### Horizontal Scaling

To add more EC2 instances:

```bash
# Update terraform.tfvars
desired_capacity = 3  # or more

# Apply changes
terraform apply
```

### Vertical Scaling

To change instance types:

```bash
# Update terraform.tfvars
ec2_instance_type = "t3.large"

# Apply changes
terraform apply
```

### Database Scaling

To upgrade RDS instance:

```bash
# Update terraform.tfvars
db_instance_class = "db.t3.small"

# Apply changes
terraform apply
```

## 🔧 Maintenance

### Update Application

```bash
# SSH into EC2 instance
ssh -i your-key.pem ec2-user@<ec2-public-ip>

# Pull latest changes
cd /opt/cloudengineered
git pull origin main

# Rebuild and restart
docker-compose -f docker-compose.prod.yml up -d --build
```

### Backup Database

```bash
# SSH into EC2 instance
ssh -i your-key.pem ec2-user@<ec2-public-ip>

# Run backup script
/opt/cloudengineered/backup.sh
```

### Monitor Application

```bash
# SSH into EC2 instance
ssh -i your-key.pem ec2-user@<ec2-public-ip>

# Check application health
/opt/cloudengineered/monitor.sh

# View logs
docker-compose -f docker-compose.prod.yml logs -f web
```

## 🆘 Troubleshooting

### Common Issues

1. **Terraform Apply Fails**
   ```bash
   # Check AWS credentials
   aws sts get-caller-identity

   # Check Terraform state
   terraform state list
   ```

2. **EC2 Instance Won't Start**
   ```bash
   # Check user data script logs
   aws ec2 get-console-output --instance-id <instance-id>
   ```

3. **Application Not Accessible**
   ```bash
   # Check load balancer health
   aws elbv2 describe-target-health --target-group-arn <target-group-arn>

   # Check security groups
   aws ec2 describe-security-groups --group-ids <security-group-id>
   ```

4. **SSL Certificate Pending**
   ```bash
   # Check certificate status
   aws acm describe-certificate --certificate-arn <certificate-arn>

   # Add DNS validation records to Route 53
   aws acm resend-validation-email --certificate-arn <certificate-arn> --domain <domain>
   ```

## 🧹 Cleanup

To destroy all resources:

```bash
# Be careful! This will delete everything
terraform destroy
```

**Note**: Some resources like S3 buckets with content may need manual deletion.

## 📚 Additional Resources

- [Terraform AWS Provider Documentation](https://registry.terraform.io/providers/hashicorp/aws/latest/docs)
- [AWS Well-Architected Framework](https://aws.amazon.com/architecture/well-architected/)
- [Django Deployment Checklist](https://docs.djangoproject.com/en/stable/howto/deployment/checklist/)

## 🤝 Contributing

1. Use feature branches for changes
2. Test with `terraform plan` before applying
3. Update documentation for infrastructure changes
4. Use meaningful commit messages

---

**Deployment Time**: 10-15 minutes (after configuration)
**Infrastructure Ready**: Immediately after Terraform apply
**Application Ready**: 5-10 minutes (EC2 bootstrap time)