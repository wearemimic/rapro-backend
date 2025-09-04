# Variables for RetirementAdvisorPro Terraform deployment

variable "aws_region" {
  description = "AWS region for resources"
  type        = string
  default     = "us-east-1"
}

variable "environment" {
  description = "Environment name (dev, staging, prod)"
  type        = string
  default     = "prod"
}

variable "project_name" {
  description = "Name of the project"
  type        = string
  default     = "retirementadvisorpro"
}

variable "domain_name" {
  description = "Domain name for the application"
  type        = string
  default     = ""
}

variable "tags" {
  description = "Tags to apply to resources"
  type        = map(string)
  default     = {}
}

# VPC Configuration
variable "vpc_cidr" {
  description = "CIDR block for VPC"
  type        = string
  default     = "10.0.0.0/16"
}

# ECS Configuration
variable "ecs_cluster_capacity_providers" {
  description = "List of capacity providers for ECS cluster"
  type        = list(string)
  default     = ["FARGATE", "FARGATE_SPOT"]
}

variable "frontend_cpu" {
  description = "CPU units for frontend container (1024 = 1 vCPU)"
  type        = number
  default     = 512
}

variable "frontend_memory" {
  description = "Memory for frontend container in MB"
  type        = number
  default     = 1024
}

variable "backend_cpu" {
  description = "CPU units for backend container (1024 = 1 vCPU)"
  type        = number
  default     = 512
}

variable "backend_memory" {
  description = "Memory for backend container in MB"
  type        = number
  default     = 1024
}

variable "celery_worker_cpu" {
  description = "CPU units for Celery worker container"
  type        = number
  default     = 512
}

variable "celery_worker_memory" {
  description = "Memory for Celery worker container in MB"
  type        = number
  default     = 1024
}

variable "celery_beat_cpu" {
  description = "CPU units for Celery beat container"
  type        = number
  default     = 256
}

variable "celery_beat_memory" {
  description = "Memory for Celery beat container in MB"
  type        = number
  default     = 512
}

variable "celery_flower_cpu" {
  description = "CPU units for Celery flower container"
  type        = number
  default     = 256
}

variable "celery_flower_memory" {
  description = "Memory for Celery flower container in MB"
  type        = number
  default     = 512
}

# Auto Scaling Configuration
variable "frontend_min_capacity" {
  description = "Minimum number of frontend tasks"
  type        = number
  default     = 1
}

variable "frontend_max_capacity" {
  description = "Maximum number of frontend tasks"
  type        = number
  default     = 10
}

variable "backend_min_capacity" {
  description = "Minimum number of backend tasks"
  type        = number
  default     = 1
}

variable "backend_max_capacity" {
  description = "Maximum number of backend tasks"
  type        = number
  default     = 10
}

variable "celery_worker_min_capacity" {
  description = "Minimum number of Celery worker tasks"
  type        = number
  default     = 1
}

variable "celery_worker_max_capacity" {
  description = "Maximum number of Celery worker tasks"
  type        = number
  default     = 5
}

# RDS Configuration
variable "db_instance_class" {
  description = "RDS instance class"
  type        = string
  default     = "db.t3.micro"
}

variable "db_allocated_storage" {
  description = "Allocated storage for RDS instance in GB"
  type        = number
  default     = 20
}

variable "db_max_allocated_storage" {
  description = "Maximum allocated storage for RDS auto scaling"
  type        = number
  default     = 100
}

variable "db_backup_retention_period" {
  description = "Number of days to retain backups"
  type        = number
  default     = 7
}

variable "db_multi_az" {
  description = "Enable Multi-AZ deployment for RDS"
  type        = bool
  default     = false
}

# ElastiCache Configuration
variable "redis_node_type" {
  description = "ElastiCache Redis node type"
  type        = string
  default     = "cache.t3.micro"
}

variable "redis_num_cache_nodes" {
  description = "Number of cache nodes in Redis cluster"
  type        = number
  default     = 1
}

variable "redis_parameter_group_name" {
  description = "Parameter group for Redis"
  type        = string
  default     = "default.redis7"
}

# CodePipeline Configuration
variable "github_owner" {
  description = "GitHub repository owner"
  type        = string
  default     = ""
}

variable "github_repo" {
  description = "GitHub repository name"
  type        = string
  default     = "retirementadvisorpro"
}

variable "github_branch" {
  description = "GitHub branch to deploy from"
  type        = string
  default     = "main"
}

variable "github_token_secret_name" {
  description = "Name of the secret containing GitHub token in AWS Secrets Manager"
  type        = string
  default     = "github-token"
}

# CloudWatch Logs Configuration
variable "log_retention_in_days" {
  description = "CloudWatch log retention period"
  type        = number
  default     = 14
}

# Cost Optimization Settings
variable "enable_fargate_spot" {
  description = "Enable Fargate Spot for cost optimization"
  type        = bool
  default     = true
}

variable "enable_nat_gateway" {
  description = "Enable NAT Gateway (costs ~$45/month per gateway)"
  type        = bool
  default     = true
}

variable "single_nat_gateway" {
  description = "Use single NAT Gateway for cost optimization"
  type        = bool
  default     = true
}

variable "enable_cloudfront" {
  description = "Enable CloudFront CDN for frontend"
  type        = bool
  default     = true
}

variable "enable_waf" {
  description = "Enable AWS WAF for security"
  type        = bool
  default     = false
}

# SSL Certificate
variable "certificate_arn" {
  description = "ARN of SSL certificate for HTTPS"
  type        = string
  default     = ""
}

# Monitoring and Alerting
variable "enable_detailed_monitoring" {
  description = "Enable detailed CloudWatch monitoring"
  type        = bool
  default     = false
}

variable "notification_email" {
  description = "Email for CloudWatch alarms"
  type        = string
  default     = ""
}

# Environment Variables - Sensitive values should be set via AWS Parameter Store
variable "auth0_domain" {
  description = "Auth0 domain"
  type        = string
  default     = ""
}

variable "auth0_client_id" {
  description = "Auth0 client ID"
  type        = string
  default     = ""
}

variable "auth0_audience" {
  description = "Auth0 audience"
  type        = string
  default     = ""
}

variable "stripe_public_key" {
  description = "Stripe public key"
  type        = string
  default     = ""
}