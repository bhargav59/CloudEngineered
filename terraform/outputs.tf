# Terraform Outputs for CloudEngineered

output "vpc_id" {
  description = "VPC ID"
  value       = aws_vpc.main.id
}

output "public_subnet_ids" {
  description = "Public subnet IDs"
  value       = aws_subnet.public[*].id
}

output "private_subnet_ids" {
  description = "Private subnet IDs"
  value       = aws_subnet.private[*].id
}

output "database_endpoint" {
  description = "RDS database endpoint"
  value       = aws_db_instance.main.address
  sensitive   = true
}

output "database_port" {
  description = "RDS database port"
  value       = aws_db_instance.main.port
}

output "redis_endpoint" {
  description = "Redis cluster endpoint"
  value       = aws_elasticache_cluster.main.cache_nodes[0].address
  sensitive   = true
}

output "redis_port" {
  description = "Redis port"
  value       = aws_elasticache_cluster.main.cache_nodes[0].port
}

output "s3_static_bucket" {
  description = "S3 bucket for static files"
  value       = aws_s3_bucket.static.bucket
}

output "cloudfront_distribution_id" {
  description = "CloudFront distribution ID"
  value       = aws_cloudfront_distribution.static.id
}

output "cloudfront_domain_name" {
  description = "CloudFront domain name"
  value       = aws_cloudfront_distribution.static.domain_name
}

output "ec2_instance_id" {
  description = "EC2 instance ID"
  value       = aws_instance.web.id
}

output "ec2_public_ip" {
  description = "EC2 instance public IP"
  value       = aws_instance.web.public_ip
}

output "ec2_public_dns" {
  description = "EC2 instance public DNS"
  value       = aws_instance.web.public_dns
}

output "load_balancer_dns_name" {
  description = "Application Load Balancer DNS name"
  value       = aws_lb.main.dns_name
}

output "load_balancer_zone_id" {
  description = "Application Load Balancer zone ID"
  value       = aws_lb.main.zone_id
}

output "ssl_certificate_arn" {
  description = "SSL certificate ARN (if domain provided)"
  value       = var.domain_name != "" ? aws_acm_certificate.main[0].arn : null
}

output "route53_zone_id" {
  description = "Route 53 hosted zone ID (if domain provided)"
  value       = var.domain_name != "" ? data.aws_route53_zone.main[0].zone_id : null
}

output "application_url" {
  description = "Application URL"
  value       = var.domain_name != "" ? "https://${var.domain_name}" : "http://${aws_lb.main.dns_name}"
}

output "ssh_command" {
  description = "SSH command to connect to EC2 instance"
  value       = "ssh -i <your-key-pair>.pem ec2-user@${aws_instance.web.public_ip}"
}

output "database_connection_string" {
  description = "Database connection string for application"
  value       = "postgresql://${var.db_username}:${var.db_password}@${aws_db_instance.main.address}:${aws_db_instance.main.port}/${var.db_name}"
  sensitive   = true
}

output "redis_connection_string" {
  description = "Redis connection string"
  value       = "redis://${aws_elasticache_cluster.main.cache_nodes[0].address}:${aws_elasticache_cluster.main.cache_nodes[0].port}"
  sensitive   = true
}

# Instructions output
output "next_steps" {
  description = "Next steps after Terraform deployment"
  value = <<EOT
🎉 Infrastructure deployed successfully!

Next steps:
1. SSH into EC2 instance: ${"ssh -i <your-key-pair>.pem ec2-user@${aws_instance.web.public_ip}"}
2. Check application logs: sudo docker-compose -f docker-compose.prod.yml logs web
3. Access application at: ${var.domain_name != "" ? "https://${var.domain_name}" : "http://${aws_lb.main.dns_name}"}
4. Create superuser: sudo docker-compose -f docker-compose.prod.yml exec web python manage.py createsuperuser
5. Run initial data setup: sudo docker-compose -f docker-compose.prod.yml exec web python manage.py setup_initial_data

For SSL certificate validation (if domain provided):
- Check AWS Certificate Manager for DNS validation records
- Add them to your DNS settings if not using Route 53

Monitoring:
- CloudWatch alarms are set up for high CPU usage
- Check logs in /opt/cloudengineered/logs/
EOT
}