# AWS Systems Manager Parameter Store for secrets management
# Secure storage for sensitive configuration values

# Random Django Secret Key
resource "random_password" "django_secret_key" {
  length  = 50
  special = true
}

# Database Password (from RDS random password)
resource "aws_ssm_parameter" "db_password" {
  name  = "/${local.name_prefix}/database/password"
  type  = "SecureString"
  value = random_password.db_password.result

  description = "Database password for PostgreSQL"

  tags = merge(local.common_tags, {
    Name = "${local.name_prefix}-db-password"
  })
}

# Django Secret Key
resource "aws_ssm_parameter" "django_secret_key" {
  name  = "/${local.name_prefix}/django/secret-key"
  type  = "SecureString"
  value = random_password.django_secret_key.result

  description = "Django secret key for RetirementAdvisorPro"

  tags = merge(local.common_tags, {
    Name = "${local.name_prefix}-django-secret-key"
  })
}

# Auth0 Client Secret
resource "aws_ssm_parameter" "auth0_client_secret" {
  name  = "/${local.name_prefix}/auth0/client-secret"
  type  = "SecureString"
  value = "PLACEHOLDER_SET_MANUALLY"  # Must be set manually after creation

  description = "Auth0 client secret for authentication"

  tags = merge(local.common_tags, {
    Name = "${local.name_prefix}-auth0-client-secret"
  })

  lifecycle {
    ignore_changes = [value]
  }
}

# Stripe Secret Key
resource "aws_ssm_parameter" "stripe_secret_key" {
  name  = "/${local.name_prefix}/stripe/secret-key"
  type  = "SecureString"
  value = "PLACEHOLDER_SET_MANUALLY"  # Must be set manually after creation

  description = "Stripe secret key for payment processing"

  tags = merge(local.common_tags, {
    Name = "${local.name_prefix}-stripe-secret-key"
  })

  lifecycle {
    ignore_changes = [value]
  }
}

# Stripe Webhook Secret
resource "aws_ssm_parameter" "stripe_webhook_secret" {
  name  = "/${local.name_prefix}/stripe/webhook-secret"
  type  = "SecureString"
  value = "PLACEHOLDER_SET_MANUALLY"  # Must be set manually after creation

  description = "Stripe webhook secret for event validation"

  tags = merge(local.common_tags, {
    Name = "${local.name_prefix}-stripe-webhook-secret"
  })

  lifecycle {
    ignore_changes = [value]
  }
}

# OpenAI API Key
resource "aws_ssm_parameter" "openai_api_key" {
  name  = "/${local.name_prefix}/ai/openai-api-key"
  type  = "SecureString"
  value = "PLACEHOLDER_SET_MANUALLY"  # Must be set manually after creation

  description = "OpenAI API key for AI features"

  tags = merge(local.common_tags, {
    Name = "${local.name_prefix}-openai-api-key"
  })

  lifecycle {
    ignore_changes = [value]
  }
}

# Anthropic API Key
resource "aws_ssm_parameter" "anthropic_api_key" {
  name  = "/${local.name_prefix}/ai/anthropic-api-key"
  type  = "SecureString"
  value = "PLACEHOLDER_SET_MANUALLY"  # Must be set manually after creation

  description = "Anthropic API key for AI features"

  tags = merge(local.common_tags, {
    Name = "${local.name_prefix}-anthropic-api-key"
  })

  lifecycle {
    ignore_changes = [value]
  }
}

# Stripe Monthly Price ID
resource "aws_ssm_parameter" "stripe_monthly_price_id" {
  name  = "/${local.name_prefix}/stripe/monthly-price-id"
  type  = "String"
  value = "PLACEHOLDER_SET_MANUALLY"  # Must be set manually after creation

  description = "Stripe monthly subscription price ID"

  tags = merge(local.common_tags, {
    Name = "${local.name_prefix}-stripe-monthly-price-id"
  })

  lifecycle {
    ignore_changes = [value]
  }
}

# Stripe Annual Price ID
resource "aws_ssm_parameter" "stripe_annual_price_id" {
  name  = "/${local.name_prefix}/stripe/annual-price-id"
  type  = "String"
  value = "PLACEHOLDER_SET_MANUALLY"  # Must be set manually after creation

  description = "Stripe annual subscription price ID"

  tags = merge(local.common_tags, {
    Name = "${local.name_prefix}-stripe-annual-price-id"
  })

  lifecycle {
    ignore_changes = [value]
  }
}

# Auth0 Domain (non-sensitive, for reference)
resource "aws_ssm_parameter" "auth0_domain" {
  name  = "/${local.name_prefix}/auth0/domain"
  type  = "String"
  value = var.auth0_domain

  description = "Auth0 domain for authentication"

  tags = merge(local.common_tags, {
    Name = "${local.name_prefix}-auth0-domain"
  })
}

# Auth0 Client ID (non-sensitive, for reference)
resource "aws_ssm_parameter" "auth0_client_id" {
  name  = "/${local.name_prefix}/auth0/client-id"
  type  = "String"
  value = var.auth0_client_id

  description = "Auth0 client ID for authentication"

  tags = merge(local.common_tags, {
    Name = "${local.name_prefix}-auth0-client-id"
  })
}

# Auth0 Audience (non-sensitive, for reference)
resource "aws_ssm_parameter" "auth0_audience" {
  name  = "/${local.name_prefix}/auth0/audience"
  type  = "String"
  value = var.auth0_audience

  description = "Auth0 audience for API authentication"

  tags = merge(local.common_tags, {
    Name = "${local.name_prefix}-auth0-audience"
  })
}

# Database connection parameters (for reference and monitoring tools)
resource "aws_ssm_parameter" "database_host" {
  name  = "/${local.name_prefix}/database/host"
  type  = "String"
  value = aws_db_instance.main.endpoint

  description = "RDS PostgreSQL database host"

  tags = merge(local.common_tags, {
    Name = "${local.name_prefix}-database-host"
  })
}

resource "aws_ssm_parameter" "database_port" {
  name  = "/${local.name_prefix}/database/port"
  type  = "String"
  value = tostring(aws_db_instance.main.port)

  description = "RDS PostgreSQL database port"

  tags = merge(local.common_tags, {
    Name = "${local.name_prefix}-database-port"
  })
}

resource "aws_ssm_parameter" "database_name" {
  name  = "/${local.name_prefix}/database/name"
  type  = "String"
  value = aws_db_instance.main.db_name

  description = "RDS PostgreSQL database name"

  tags = merge(local.common_tags, {
    Name = "${local.name_prefix}-database-name"
  })
}

# Redis connection parameters
resource "aws_ssm_parameter" "redis_host" {
  name  = "/${local.name_prefix}/redis/host"
  type  = "String"
  value = aws_elasticache_replication_group.main.primary_endpoint_address

  description = "ElastiCache Redis host"

  tags = merge(local.common_tags, {
    Name = "${local.name_prefix}-redis-host"
  })
}

resource "aws_ssm_parameter" "redis_port" {
  name  = "/${local.name_prefix}/redis/port"
  type  = "String"
  value = "6379"

  description = "ElastiCache Redis port"

  tags = merge(local.common_tags, {
    Name = "${local.name_prefix}-redis-port"
  })
}

# S3 bucket names for reference
resource "aws_ssm_parameter" "s3_static_bucket" {
  name  = "/${local.name_prefix}/s3/static-bucket"
  type  = "String"
  value = aws_s3_bucket.static_assets.id

  description = "S3 bucket for static assets"

  tags = merge(local.common_tags, {
    Name = "${local.name_prefix}-s3-static-bucket"
  })
}

resource "aws_ssm_parameter" "s3_media_bucket" {
  name  = "/${local.name_prefix}/s3/media-bucket"
  type  = "String"
  value = aws_s3_bucket.media_files.id

  description = "S3 bucket for media files"

  tags = merge(local.common_tags, {
    Name = "${local.name_prefix}-s3-media-bucket"
  })
}

# Application URLs
resource "aws_ssm_parameter" "frontend_url" {
  name  = "/${local.name_prefix}/urls/frontend"
  type  = "String"
  value = var.domain_name != "" ? "https://${var.domain_name}" : "http://${aws_lb.main.dns_name}"

  description = "Frontend application URL"

  tags = merge(local.common_tags, {
    Name = "${local.name_prefix}-frontend-url"
  })
}

resource "aws_ssm_parameter" "backend_url" {
  name  = "/${local.name_prefix}/urls/backend"
  type  = "String"
  value = var.domain_name != "" ? "https://${var.domain_name}/api" : "http://${aws_lb.main.dns_name}/api"

  description = "Backend API URL"

  tags = merge(local.common_tags, {
    Name = "${local.name_prefix}-backend-url"
  })
}

# CloudFront distribution URL (if enabled)
resource "aws_ssm_parameter" "cloudfront_url" {
  count = var.enable_cloudfront ? 1 : 0

  name  = "/${local.name_prefix}/urls/cloudfront"
  type  = "String"
  value = "https://${aws_cloudfront_distribution.frontend[0].domain_name}"

  description = "CloudFront distribution URL"

  tags = merge(local.common_tags, {
    Name = "${local.name_prefix}-cloudfront-url"
  })
}

# IAM policy to allow ECS tasks to read parameters
resource "aws_iam_policy" "parameter_store_read" {
  name        = "${local.name_prefix}-parameter-store-read"
  description = "Allow reading RetirementAdvisorPro parameters from Parameter Store"

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Effect = "Allow"
        Action = [
          "ssm:GetParameter",
          "ssm:GetParameters",
          "ssm:GetParametersByPath"
        ]
        Resource = [
          "arn:aws:ssm:${var.aws_region}:${data.aws_caller_identity.current.account_id}:parameter/${local.name_prefix}/*"
        ]
      },
      {
        Effect = "Allow"
        Action = [
          "kms:Decrypt"
        ]
        Resource = [
          "arn:aws:kms:${var.aws_region}:${data.aws_caller_identity.current.account_id}:key/*"
        ]
        Condition = {
          StringEquals = {
            "kms:ViaService" = "ssm.${var.aws_region}.amazonaws.com"
          }
        }
      }
    ]
  })

  tags = merge(local.common_tags, {
    Name = "${local.name_prefix}-parameter-store-read"
  })
}

# Attach parameter store policy to ECS task execution role
resource "aws_iam_role_policy_attachment" "ecs_task_execution_parameter_store" {
  role       = aws_iam_role.ecs_task_execution_role.name
  policy_arn = aws_iam_policy.parameter_store_read.arn
}

# Output instructions for manual parameter updates
locals {
  manual_parameters = [
    {
      name        = aws_ssm_parameter.auth0_client_secret.name
      description = "Auth0 client secret from your Auth0 application settings"
    },
    {
      name        = aws_ssm_parameter.stripe_secret_key.name
      description = "Stripe secret key from your Stripe dashboard"
    },
    {
      name        = aws_ssm_parameter.stripe_monthly_price_id.name
      description = "Stripe monthly subscription price ID"
    },
    {
      name        = aws_ssm_parameter.stripe_annual_price_id.name
      description = "Stripe annual subscription price ID"
    }
  ]
}