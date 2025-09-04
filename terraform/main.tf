# Main Terraform configuration for RetirementAdvisorPro AWS deployment
# Cost-optimized architecture for Django/Vue.js SaaS platform

terraform {
  required_version = ">= 1.0"
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 5.0"
    }
  }

  # Uncomment and configure for remote state management
  # backend "s3" {
  #   bucket = "your-terraform-state-bucket"
  #   key    = "retirementadvisorpro/terraform.tfstate"
  #   region = "us-east-1"
  # }
}

provider "aws" {
  region = var.aws_region

  default_tags {
    tags = {
      Project     = "RetirementAdvisorPro"
      Environment = var.environment
      ManagedBy   = "Terraform"
    }
  }
}

# Data sources for availability zones
data "aws_availability_zones" "available" {
  state = "available"
}

# Data source for current AWS account ID
data "aws_caller_identity" "current" {}

# Data source for ECR authorization token
data "aws_ecr_authorization_token" "token" {}

# Random password for RDS
resource "random_password" "db_password" {
  length  = 32
  special = true
}

# Local values for resource naming and configuration
locals {
  name_prefix = "${var.project_name}-${var.environment}"
  
  # AZ selection - use first 2 AZs for cost optimization
  availability_zones = slice(data.aws_availability_zones.available.names, 0, 2)
  
  # Common tags
  common_tags = {
    Project     = var.project_name
    Environment = var.environment
    ManagedBy   = "Terraform"
  }

  # Container configurations
  containers = {
    frontend = {
      name = "frontend"
      port = 3000
    }
    backend = {
      name = "backend"
      port = 8000
    }
    celery_worker = {
      name = "celery-worker"
      port = null
    }
    celery_beat = {
      name = "celery-beat"
      port = null
    }
    celery_flower = {
      name = "celery-flower"
      port = 5555
    }
  }
}