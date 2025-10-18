#!/bin/bash
# CloudEngineered Terraform Deployment Script
# This script automates the entire deployment process

set -e

echo "🚀 CloudEngineered AWS Deployment with Terraform"
echo "================================================"

# Check prerequisites
command -v terraform >/dev/null 2>&1 || { echo "❌ Terraform is not installed. Please install Terraform first."; exit 1; }
command -v aws >/dev/null 2>&1 || { echo "❌ AWS CLI is not configured. Please configure AWS CLI first."; exit 1; }

# Check AWS credentials
echo "🔍 Checking AWS credentials..."
aws sts get-caller-identity >/dev/null 2>&1 || { echo "❌ AWS credentials not configured. Please run 'aws configure'."; exit 1; }

# Navigate to terraform directory
cd terraform

# Check if terraform.tfvars exists
if [ ! -f "terraform.tfvars" ]; then
    echo "❌ terraform.tfvars not found!"
    echo "📝 Please copy terraform.tfvars.example to terraform.tfvars and configure your values:"
    echo "   cp terraform.tfvars.example terraform.tfvars"
    echo "   nano terraform.tfvars  # Edit with your values"
    exit 1
fi

echo "✅ Prerequisites check passed"

# Initialize Terraform
echo ""
echo "🔧 Initializing Terraform..."
terraform init

# Validate configuration
echo ""
echo "🔍 Validating Terraform configuration..."
terraform validate

# Plan deployment
echo ""
echo "📋 Planning deployment..."
terraform plan -out=tfplan

# Ask for confirmation
echo ""
echo "⚠️  This will create AWS resources that may incur costs."
read -p "🤔 Do you want to proceed with deployment? (y/N): " -n 1 -r
echo
if [[ ! $REPLY =~ ^[Yy]$ ]]; then
    echo "❌ Deployment cancelled"
    exit 1
fi

# Apply deployment
echo ""
echo "🚀 Deploying CloudEngineered to AWS..."
terraform apply tfplan

echo ""
echo "🎉 Deployment completed successfully!"
echo ""
echo "📋 Next steps:"
echo "1. Wait 5-10 minutes for EC2 bootstrap to complete"
echo "2. Access your application using the URL provided above"
echo "3. SSH into EC2 instance to check logs if needed"
echo "4. Create a superuser account for admin access"
echo ""
echo "📖 For detailed instructions, see terraform/README.md"
echo "🆘 For troubleshooting, check terraform/README.md#troubleshooting"