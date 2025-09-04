# Output values for RetirementAdvisorPro infrastructure
# Provides important information after deployment

# Network Information
output "vpc_id" {
  description = "ID of the VPC"
  value       = aws_vpc.main.id
}

output "vpc_cidr_block" {
  description = "CIDR block of the VPC"
  value       = aws_vpc.main.cidr_block
}

output "public_subnet_ids" {
  description = "IDs of the public subnets"
  value       = aws_subnet.public[*].id
}

output "private_subnet_ids" {
  description = "IDs of the private subnets"
  value       = aws_subnet.private[*].id
}

output "database_subnet_ids" {
  description = "IDs of the database subnets"
  value       = aws_subnet.database[*].id
}

# Load Balancer Information - Production
output "load_balancer_dns_name" {
  description = "DNS name of the production load balancer"
  value       = aws_lb.main.dns_name
}

output "load_balancer_zone_id" {
  description = "Zone ID of the production load balancer"
  value       = aws_lb.main.zone_id
}

output "load_balancer_arn" {
  description = "ARN of the production load balancer"
  value       = aws_lb.main.arn
}

# Load Balancer Information - Staging
output "staging_load_balancer_dns_name" {
  description = "DNS name of the staging load balancer"
  value       = aws_lb.staging.dns_name
}

output "staging_load_balancer_zone_id" {
  description = "Zone ID of the staging load balancer"
  value       = aws_lb.staging.zone_id
}

output "staging_load_balancer_arn" {
  description = "ARN of the staging load balancer"
  value       = aws_lb.staging.arn
}

# Application URLs - Production
output "frontend_url" {
  description = "URL to access the frontend application"
  value       = var.domain_name != "" ? "https://${var.domain_name}" : "http://${aws_lb.main.dns_name}"
}

# Application URLs - Staging
output "staging_url" {
  description = "URL to access the staging application"
  value       = "http://${aws_lb.staging.dns_name}"
}

output "backend_api_url" {
  description = "URL to access the backend API"
  value       = var.domain_name != "" ? "https://${var.domain_name}/api" : "http://${aws_lb.main.dns_name}/api"
}

output "admin_url" {
  description = "URL to access Django admin"
  value       = var.domain_name != "" ? "https://${var.domain_name}/admin" : "http://${aws_lb.main.dns_name}/admin"
}

output "celery_flower_url" {
  description = "URL to access Celery Flower monitoring (if enabled)"
  value       = length(aws_ecs_service.celery_flower) > 0 ? (var.domain_name != "" ? "https://${var.domain_name}/flower" : "http://${aws_lb.main.dns_name}/flower") : null
}

# CloudFront Information
output "cloudfront_distribution_id" {
  description = "CloudFront distribution ID"
  value       = var.enable_cloudfront ? aws_cloudfront_distribution.frontend[0].id : null
}

output "cloudfront_domain_name" {
  description = "CloudFront distribution domain name"
  value       = var.enable_cloudfront ? aws_cloudfront_distribution.frontend[0].domain_name : null
}

output "cloudfront_url" {
  description = "CloudFront distribution URL"
  value       = var.enable_cloudfront ? "https://${aws_cloudfront_distribution.frontend[0].domain_name}" : null
}

# Database Information
output "database_endpoint" {
  description = "RDS PostgreSQL endpoint"
  value       = aws_db_instance.main.endpoint
  sensitive   = true
}

output "database_port" {
  description = "RDS PostgreSQL port"
  value       = aws_db_instance.main.port
}

output "database_name" {
  description = "RDS PostgreSQL database name"
  value       = aws_db_instance.main.db_name
}

output "database_username" {
  description = "RDS PostgreSQL username"
  value       = aws_db_instance.main.username
  sensitive   = true
}

# Redis Information
output "redis_endpoint" {
  description = "ElastiCache Redis endpoint"
  value       = aws_elasticache_replication_group.main.primary_endpoint_address
  sensitive   = true
}

output "redis_port" {
  description = "ElastiCache Redis port"
  value       = aws_elasticache_replication_group.main.port
}

# S3 Bucket Information
output "static_assets_bucket" {
  description = "S3 bucket for static assets"
  value       = aws_s3_bucket.static_assets.id
}

output "static_assets_bucket_domain" {
  description = "S3 bucket domain for static assets"
  value       = aws_s3_bucket.static_assets.bucket_domain_name
}

output "media_files_bucket" {
  description = "S3 bucket for media files"
  value       = aws_s3_bucket.media_files.id
}

output "codepipeline_artifacts_bucket" {
  description = "S3 bucket for CodePipeline artifacts"
  value       = aws_s3_bucket.codepipeline_artifacts.id
}

output "backups_bucket" {
  description = "S3 bucket for backups"
  value       = aws_s3_bucket.backups.id
}

# ECR Repository Information
output "frontend_ecr_repository_url" {
  description = "ECR repository URL for frontend"
  value       = aws_ecr_repository.frontend.repository_url
}

output "backend_ecr_repository_url" {
  description = "ECR repository URL for backend"
  value       = aws_ecr_repository.backend.repository_url
}

# ECS Information
output "ecs_cluster_id" {
  description = "ECS cluster ID"
  value       = aws_ecs_cluster.main.id
}

output "ecs_cluster_arn" {
  description = "ECS cluster ARN"
  value       = aws_ecs_cluster.main.arn
}

output "frontend_service_name" {
  description = "ECS frontend service name"
  value       = aws_ecs_service.frontend.name
}

output "backend_service_name" {
  description = "ECS backend service name"
  value       = aws_ecs_service.backend.name
}

output "celery_worker_service_name" {
  description = "ECS Celery worker service name"
  value       = aws_ecs_service.celery_worker.name
}

output "celery_beat_service_name" {
  description = "ECS Celery beat service name"
  value       = aws_ecs_service.celery_beat.name
}

# CI/CD Information
output "codepipeline_name" {
  description = "CodePipeline name"
  value       = aws_codepipeline.main.name
}

output "codepipeline_url" {
  description = "CodePipeline URL in AWS Console"
  value       = "https://${var.aws_region}.console.aws.amazon.com/codesuite/codepipeline/pipelines/${aws_codepipeline.main.name}/view"
}

output "frontend_codebuild_project_name" {
  description = "CodeBuild project name for frontend"
  value       = aws_codebuild_project.frontend.name
}

output "backend_codebuild_project_name" {
  description = "CodeBuild project name for backend"
  value       = aws_codebuild_project.backend.name
}

# Monitoring Information
output "cloudwatch_dashboard_url" {
  description = "CloudWatch dashboard URL"
  value       = "https://${var.aws_region}.console.aws.amazon.com/cloudwatch/home?region=${var.aws_region}#dashboards:name=${aws_cloudwatch_dashboard.main.dashboard_name}"
}

output "sns_topic_arn" {
  description = "SNS topic ARN for alerts"
  value       = var.notification_email != "" ? aws_sns_topic.alerts[0].arn : null
}

# Security Information
output "waf_web_acl_id" {
  description = "WAF Web ACL ID"
  value       = var.enable_waf ? aws_wafv2_web_acl.main[0].id : null
}

# Parameter Store Information
output "parameter_store_prefix" {
  description = "Parameter Store prefix for application secrets"
  value       = "/${local.name_prefix}/"
}

# Manual Configuration Required
output "manual_configuration_required" {
  description = "Manual configuration steps required after deployment"
  value = {
    secrets_to_update = [
      {
        parameter_name = aws_ssm_parameter.auth0_client_secret.name
        description    = "Set Auth0 client secret from your Auth0 application"
        aws_cli_command = "aws ssm put-parameter --name '${aws_ssm_parameter.auth0_client_secret.name}' --value 'YOUR_AUTH0_CLIENT_SECRET' --type 'SecureString' --overwrite"
      },
      {
        parameter_name = aws_ssm_parameter.stripe_secret_key.name
        description    = "Set Stripe secret key from your Stripe dashboard"
        aws_cli_command = "aws ssm put-parameter --name '${aws_ssm_parameter.stripe_secret_key.name}' --value 'YOUR_STRIPE_SECRET_KEY' --type 'SecureString' --overwrite"
      },
      {
        parameter_name = aws_ssm_parameter.stripe_monthly_price_id.name
        description    = "Set Stripe monthly subscription price ID"
        aws_cli_command = "aws ssm put-parameter --name '${aws_ssm_parameter.stripe_monthly_price_id.name}' --value 'YOUR_MONTHLY_PRICE_ID' --type 'String' --overwrite"
      },
      {
        parameter_name = aws_ssm_parameter.stripe_annual_price_id.name
        description    = "Set Stripe annual subscription price ID"
        aws_cli_command = "aws ssm put-parameter --name '${aws_ssm_parameter.stripe_annual_price_id.name}' --value 'YOUR_ANNUAL_PRICE_ID' --type 'String' --overwrite"
      }
    ]
    github_token_secret = "Create a secret named '${var.github_token_secret_name}' in AWS Secrets Manager with your GitHub personal access token"
    dns_configuration   = var.domain_name != "" ? "Update your DNS to point ${var.domain_name} to ${aws_lb.main.dns_name}" : "No custom domain configured"
    ssl_certificate     = var.certificate_arn == "" ? "Request an SSL certificate in AWS Certificate Manager and update the certificate_arn variable" : "SSL certificate configured"
  }
}

# Cost Estimation Information
output "estimated_monthly_costs" {
  description = "Estimated monthly costs for the infrastructure"
  value = {
    fargate_frontend  = "$${var.frontend_min_capacity * 0.25 * 24 * 30}"  # Estimated cost per task per month
    fargate_backend   = "$${var.backend_min_capacity * 0.25 * 24 * 30}"
    fargate_celery    = "$${var.celery_worker_min_capacity * 0.25 * 24 * 30}"
    rds_instance      = var.db_instance_class == "db.t3.micro" ? "$13-15" : "$30-50"
    elasticache_redis = var.redis_node_type == "cache.t3.micro" ? "$13-15" : "$25-40"
    alb               = "$16-20"
    nat_gateway       = var.enable_nat_gateway ? (var.single_nat_gateway ? "$32-35" : "$64-70") : "$0"
    cloudfront        = var.enable_cloudfront ? "$5-20" : "$0"
    s3_storage        = "$5-15"
    data_transfer     = "$10-30"
    total_estimated   = "$150-300 per month"
    note              = "Costs vary based on usage, region, and specific configurations. Use AWS Cost Calculator for precise estimates."
  }
}

# Useful AWS CLI Commands
output "useful_aws_cli_commands" {
  description = "Useful AWS CLI commands for managing the deployment"
  value = {
    update_ecs_service = {
      frontend = "aws ecs update-service --cluster ${aws_ecs_cluster.main.name} --service ${aws_ecs_service.frontend.name} --force-new-deployment"
      backend  = "aws ecs update-service --cluster ${aws_ecs_cluster.main.name} --service ${aws_ecs_service.backend.name} --force-new-deployment"
    }
    view_logs = {
      frontend = "aws logs tail /ecs/${local.name_prefix}-frontend --follow"
      backend  = "aws logs tail /ecs/${local.name_prefix}-backend --follow"
    }
    run_migrations = "aws ecs run-task --cluster ${aws_ecs_cluster.main.name} --task-definition ${aws_ecs_task_definition.backend.arn} --overrides '{\"containerOverrides\":[{\"name\":\"backend\",\"command\":[\"python\",\"manage.py\",\"migrate\"]}]}' --network-configuration 'awsvpcConfiguration={subnets=[${join(",", aws_subnet.private[*].id)}],securityGroups=[${aws_security_group.ecs_tasks.id}]}' --launch-type FARGATE"
    invalidate_cloudfront = var.enable_cloudfront ? "aws cloudfront create-invalidation --distribution-id ${aws_cloudfront_distribution.frontend[0].id} --paths '/*'" : "CloudFront not enabled"
  }
}

# Health Check URLs
output "health_check_urls" {
  description = "URLs for health checking the services"
  value = {
    frontend_health = "${var.domain_name != "" ? "https://${var.domain_name}" : "http://${aws_lb.main.dns_name}"}/"
    backend_health  = "${var.domain_name != "" ? "https://${var.domain_name}" : "http://${aws_lb.main.dns_name}"}/health/"
    api_status      = "${var.domain_name != "" ? "https://${var.domain_name}" : "http://${aws_lb.main.dns_name}"}/api/"
  }
}