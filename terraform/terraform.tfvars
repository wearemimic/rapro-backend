# RetirementAdvisorPro Terraform Configuration
# Production deployment settings

# Basic Configuration
aws_region     = "us-east-1"
environment    = "prod"
project_name   = "rapro"
domain_name    = "app.retirementadvisorpro.com"  # Set your custom domain when ready

# GitHub Configuration for CI/CD
github_owner  = "wearemimic"  # Update with your GitHub username
github_repo   = "retirementadvisorpro"
github_branch = "main"
github_token_secret_name = "github-token"

# Network Configuration
vpc_cidr = "10.0.0.0/16"

# ECS Configuration - Cost Optimized for Initial Deployment
frontend_cpu    = 512   # 0.5 vCPU
frontend_memory = 1024  # 1 GB
backend_cpu     = 1024  # 1 vCPU
backend_memory  = 2048  # 2 GB

celery_worker_cpu    = 512   # 0.5 vCPU
celery_worker_memory = 1024  # 1 GB
celery_beat_cpu      = 256   # 0.25 vCPU
celery_beat_memory   = 512   # 512 MB

# Auto Scaling Configuration
frontend_min_capacity = 1
frontend_max_capacity = 5
backend_min_capacity  = 2  # Min 2 for better availability
backend_max_capacity  = 10

celery_worker_min_capacity = 1
celery_worker_max_capacity = 5

# Database Configuration - Production Ready but Cost Optimized
db_instance_class        = "db.t3.small"  # Suitable for production start
db_allocated_storage     = 30
db_max_allocated_storage = 200
db_backup_retention_period = 7
db_multi_az             = false  # Enable for production high availability

# Redis Configuration - Using ElastiCache
redis_node_type        = "cache.t3.small"  # Better performance than micro
redis_num_cache_nodes  = 1
redis_parameter_group_name = "default.redis7"

# Cost Optimization Settings
enable_fargate_spot = true   # Save 50-70% on compute costs
enable_nat_gateway  = true   # Required for private subnet internet access
single_nat_gateway  = true   # Single NAT Gateway to save costs

# CDN and Security
enable_cloudfront = false  # Disabled until SSL certificate is configured
enable_waf        = false  # Enable later for enhanced security
certificate_arn   = ""     # Add SSL certificate ARN from ACM when ready

# Monitoring and Logging
log_retention_in_days     = 30    # 30 days for compliance
enable_detailed_monitoring = false  # Enable for production monitoring
notification_email        = "mannese@wearemimic.com"    # Email for pipeline approvals and CloudWatch alerts

# Auth0 Configuration (from your .env files)
auth0_domain    = "genai-030069804226358743.us.auth0.com"
auth0_client_id = "MS2O3usgLl8btDkPNwO6i0ZzC4LxR0Jw"
auth0_audience  = "https://api.retirementadvisorpro.com"

# Stripe Configuration (Public key only, secret goes in Parameter Store)
stripe_public_key = "pk_live_51MKmFTDXYH4nUgjBhJ8lIWxB9iNkkZIXV3tHKUxOKiNWk5Zlgkx4lOBtiYpAsW55OvI1U7E9Ty82nSErHQHxW7BS00YEJ4LkEq"  # Add your Stripe publishable key here

# Tags for resource management
tags = {
  Environment = "production"
  Project     = "RetirementAdvisorPro"
  ManagedBy   = "Terraform"
  Owner       = "DevTeam"
}

# Uncomment for higher performance production settings:
# 
# # Production Resource Sizing
# frontend_cpu    = 1024
# frontend_memory = 2048
# backend_cpu     = 2048
# backend_memory  = 4096
# 
# # Production Database
# db_instance_class = "db.r5.large"
# db_multi_az      = true
# 
# # Production Redis
# redis_node_type = "cache.r6g.large"
# redis_num_cache_nodes = 2
# 
# # Production Security
# enable_waf = true
# enable_detailed_monitoring = true