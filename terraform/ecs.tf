# ECS Cluster and Services for RetirementAdvisorPro
# Cost-optimized with Fargate and Fargate Spot capacity providers

# ECS Cluster
resource "aws_ecs_cluster" "main" {
  name = "${local.name_prefix}-cluster"

  setting {
    name  = "containerInsights"
    value = var.enable_detailed_monitoring ? "enabled" : "disabled"
  }

  tags = merge(local.common_tags, {
    Name = "${local.name_prefix}-cluster"
  })
}

# ECS Cluster Capacity Providers
resource "aws_ecs_cluster_capacity_providers" "main" {
  cluster_name = aws_ecs_cluster.main.name

  capacity_providers = var.ecs_cluster_capacity_providers

  default_capacity_provider_strategy {
    capacity_provider = var.enable_fargate_spot ? "FARGATE_SPOT" : "FARGATE"
    weight           = var.enable_fargate_spot ? 1 : 1
    base             = 1
  }
}

# ECS Task Execution Role
resource "aws_iam_role" "ecs_task_execution_role" {
  name = "${local.name_prefix}-ecs-task-execution-role"

  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Action = "sts:AssumeRole"
        Effect = "Allow"
        Principal = {
          Service = "ecs-tasks.amazonaws.com"
        }
      }
    ]
  })

  tags = merge(local.common_tags, {
    Name = "${local.name_prefix}-ecs-task-execution-role"
  })
}

resource "aws_iam_role_policy_attachment" "ecs_task_execution_role_policy" {
  role       = aws_iam_role.ecs_task_execution_role.name
  policy_arn = "arn:aws:iam::aws:policy/service-role/AmazonECSTaskExecutionRolePolicy"
}

# ECS Task Role for application permissions
resource "aws_iam_role" "ecs_task_role" {
  name = "${local.name_prefix}-ecs-task-role"

  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Action = "sts:AssumeRole"
        Effect = "Allow"
        Principal = {
          Service = "ecs-tasks.amazonaws.com"
        }
      }
    ]
  })

  tags = merge(local.common_tags, {
    Name = "${local.name_prefix}-ecs-task-role"
  })
}

# Attach S3 access policy to task role
resource "aws_iam_role_policy" "ecs_task_s3_policy" {
  name = "${local.name_prefix}-ecs-task-s3-policy"
  role = aws_iam_role.ecs_task_role.id

  policy = data.aws_iam_policy_document.s3_access.json
}

# CloudWatch Logs Groups
resource "aws_cloudwatch_log_group" "frontend" {
  name              = "/ecs/${local.name_prefix}-frontend"
  retention_in_days = var.log_retention_in_days

  tags = merge(local.common_tags, {
    Name = "${local.name_prefix}-frontend-logs"
  })
}

resource "aws_cloudwatch_log_group" "backend" {
  name              = "/ecs/${local.name_prefix}-backend"
  retention_in_days = var.log_retention_in_days

  tags = merge(local.common_tags, {
    Name = "${local.name_prefix}-backend-logs"
  })
}

resource "aws_cloudwatch_log_group" "celery_worker" {
  name              = "/ecs/${local.name_prefix}-celery-worker"
  retention_in_days = var.log_retention_in_days

  tags = merge(local.common_tags, {
    Name = "${local.name_prefix}-celery-worker-logs"
  })
}

resource "aws_cloudwatch_log_group" "celery_beat" {
  name              = "/ecs/${local.name_prefix}-celery-beat"
  retention_in_days = var.log_retention_in_days

  tags = merge(local.common_tags, {
    Name = "${local.name_prefix}-celery-beat-logs"
  })
}

resource "aws_cloudwatch_log_group" "celery_flower" {
  name              = "/ecs/${local.name_prefix}-celery-flower"
  retention_in_days = var.log_retention_in_days

  tags = merge(local.common_tags, {
    Name = "${local.name_prefix}-celery-flower-logs"
  })
}

# Task Definitions

# Frontend Task Definition
resource "aws_ecs_task_definition" "frontend" {
  family                   = "${local.name_prefix}-frontend"
  requires_compatibilities = ["FARGATE"]
  network_mode             = "awsvpc"
  cpu                      = var.frontend_cpu
  memory                   = var.frontend_memory
  execution_role_arn       = aws_iam_role.ecs_task_execution_role.arn
  task_role_arn           = aws_iam_role.ecs_task_role.arn

  container_definitions = jsonencode([
    {
      name  = "frontend"
      image = "${aws_ecr_repository.frontend.repository_url}:latest"
      
      portMappings = [
        {
          containerPort = 3000
          hostPort      = 3000
        }
      ]

      environment = [
        {
          name  = "NODE_ENV"
          value = "production"
        },
        {
          name  = "PORT"
          value = "3000"
        },
        {
          name  = "VITE_AUTH0_DOMAIN"
          value = var.auth0_domain
        },
        {
          name  = "VITE_AUTH0_CLIENT_ID"
          value = var.auth0_client_id
        },
        {
          name  = "VITE_AUTH0_AUDIENCE"
          value = var.auth0_audience
        },
        {
          name  = "VITE_STRIPE_PUBLIC_KEY"
          value = var.stripe_public_key
        },
        {
          name  = "VITE_API_URL"
          value = "http://app.retirementadvisorpro.com/api"
        },
        {
          name  = "VITE_API_BASE_URL"
          value = "http://app.retirementadvisorpro.com"
        },
        {
          name  = "VITE_FRONTEND_URL"
          value = "http://app.retirementadvisorpro.com"
        }
      ]

      logConfiguration = {
        logDriver = "awslogs"
        options = {
          "awslogs-group"         = aws_cloudwatch_log_group.frontend.name
          "awslogs-region"        = var.aws_region
          "awslogs-stream-prefix" = "ecs"
        }
      }

      healthCheck = {
        command     = ["CMD-SHELL", "curl -f http://localhost:3000/ || exit 1"]
        interval    = 30
        timeout     = 5
        retries     = 3
        startPeriod = 60
      }

      essential = true
    }
  ])

  tags = merge(local.common_tags, {
    Name = "${local.name_prefix}-frontend-task"
  })
}

# Backend Task Definition
resource "aws_ecs_task_definition" "backend" {
  family                   = "${local.name_prefix}-backend"
  requires_compatibilities = ["FARGATE"]
  network_mode             = "awsvpc"
  cpu                      = var.backend_cpu
  memory                   = var.backend_memory
  execution_role_arn       = aws_iam_role.ecs_task_execution_role.arn
  task_role_arn           = aws_iam_role.ecs_task_role.arn

  container_definitions = jsonencode([
    {
      name  = "backend"
      image = "${aws_ecr_repository.backend.repository_url}:latest"
      
      portMappings = [
        {
          containerPort = 8000
          hostPort      = 8000
        }
      ]

      environment = [
        # Django Configuration
        {
          name  = "DJANGO_SETTINGS_MODULE"
          value = "retirementadvisorpro.settings"
        },
        {
          name  = "DEBUG"
          value = var.environment == "prod" ? "False" : "True"
        },
        {
          name  = "ENVIRONMENT"
          value = var.environment
        },
        
        # Database Configuration
        {
          name  = "DATABASE_URL"
          value = "postgres://postgres:${random_password.db_password.result}@${aws_db_instance.main.address}:${aws_db_instance.main.port}/${aws_db_instance.main.db_name}"
        },
        {
          name  = "POSTGRES_DB"
          value = aws_db_instance.main.db_name
        },
        {
          name  = "POSTGRES_USER"
          value = aws_db_instance.main.username
        },
        {
          name  = "DATABASE_HOST"
          value = aws_db_instance.main.address
        },
        {
          name  = "DATABASE_NAME"
          value = aws_db_instance.main.db_name
        },
        {
          name  = "DATABASE_USER"
          value = aws_db_instance.main.username
        },
        {
          name  = "DATABASE_PASSWORD"
          value = random_password.db_password.result
        },
        
        # Redis Configuration
        {
          name  = "REDIS_URL"
          value = "redis://${aws_elasticache_replication_group.main.primary_endpoint_address}:6379/0"
        },
        {
          name  = "REDIS_HOST"
          value = aws_elasticache_replication_group.main.primary_endpoint_address
        },
        {
          name  = "REDIS_PORT"
          value = "6379"
        },
        {
          name  = "CELERY_BROKER_URL"
          value = "redis://${aws_elasticache_replication_group.main.primary_endpoint_address}:6379/0"
        },
        {
          name  = "CELERY_RESULT_BACKEND"
          value = "redis://${aws_elasticache_replication_group.main.primary_endpoint_address}:6379/0"
        },
        
        # Frontend URL for redirects
        {
          name  = "FRONTEND_URL"
          value = "http://app.retirementadvisorpro.com"
        },
        
        # Auth0 Configuration
        {
          name  = "AUTH0_DOMAIN"
          value = var.auth0_domain
        },
        {
          name  = "AUTH0_CLIENT_ID"
          value = var.auth0_client_id
        },
        {
          name  = "AUTH0_AUDIENCE"
          value = var.auth0_audience
        },
        {
          name  = "AUTH0_ALGORITHM"
          value = "RS256"
        },
        
        # Stripe Configuration (Public values)
        {
          name  = "STRIPE_PUBLISHABLE_KEY"
          value = var.stripe_public_key
        },
        
        # AI Configuration
        {
          name  = "SS_AI_PROVIDER"
          value = "anthropic"  # Default to Anthropic as in .env
        },
        {
          name  = "OPENAI_MODEL_VERSION"
          value = "gpt-4-turbo-preview"
        },
        
        # Report Center Settings
        {
          name  = "AI_COST_LIMIT_PER_USER_MONTHLY"
          value = "100.00"
        },
        {
          name  = "REPORT_GENERATION_TIMEOUT"
          value = "300"
        },
        {
          name  = "BULK_EXPORT_BATCH_SIZE"
          value = "50"
        },
        {
          name  = "TEMPLATE_CACHE_TIMEOUT"
          value = "3600"
        },
        {
          name  = "REPORT_FILE_RETENTION_DAYS"
          value = "90"
        },
        
        # File Upload Configuration
        {
          name  = "MAX_UPLOAD_SIZE"
          value = "52428800"  # 50MB
        },
        
        # Feature Flags
        {
          name  = "ENABLE_AI_FEATURES"
          value = "True"
        },
        {
          name  = "ENABLE_BULK_EXPORTS"
          value = "True"
        },
        {
          name  = "ENABLE_REPORT_SCHEDULING"
          value = "True"
        },
        {
          name  = "ENABLE_CLIENT_PORTAL"
          value = "True"
        },
        
        # Analytics Configuration
        {
          name  = "ANALYTICS_RETENTION_MONTHS"
          value = "12"
        },
        
        # AWS S3 Configuration
        {
          name  = "AWS_STORAGE_BUCKET_NAME"
          value = aws_s3_bucket.media_files.id
        },
        {
          name  = "AWS_S3_REGION_NAME"
          value = var.aws_region
        },
        {
          name  = "AWS_DEFAULT_ACL"
          value = "private"
        },
        {
          name  = "USE_S3"
          value = "True"
        },
        {
          name  = "AWS_S3_CUSTOM_DOMAIN"
          value = var.enable_cloudfront ? aws_cloudfront_distribution.frontend[0].domain_name : aws_s3_bucket.static_assets.bucket_domain_name
        },
        {
          name  = "ALLOWED_HOSTS"
          value = "app.retirementadvisorpro.com,${aws_lb.main.dns_name},localhost"
        }
      ]

      secrets = [
        # Authentication Secrets
        {
          name      = "AUTH0_CLIENT_SECRET"
          valueFrom = aws_ssm_parameter.auth0_client_secret.arn
        },
        {
          name      = "DJANGO_SECRET_KEY"
          valueFrom = aws_ssm_parameter.django_secret_key.arn
        },
        
        # Database Secrets
        {
          name      = "POSTGRES_PASSWORD"
          valueFrom = aws_ssm_parameter.db_password.arn
        },
        
        # Stripe Secrets
        {
          name      = "STRIPE_SECRET_KEY"
          valueFrom = aws_ssm_parameter.stripe_secret_key.arn
        },
        {
          name      = "STRIPE_WEBHOOK_SECRET"
          valueFrom = aws_ssm_parameter.stripe_webhook_secret.arn
        },
        {
          name      = "STRIPE_MONTHLY_PRICE_ID"
          valueFrom = aws_ssm_parameter.stripe_monthly_price_id.arn
        },
        {
          name      = "STRIPE_ANNUAL_PRICE_ID"
          valueFrom = aws_ssm_parameter.stripe_annual_price_id.arn
        },
        
        # AI API Keys
        {
          name      = "OPENAI_API_KEY"
          valueFrom = aws_ssm_parameter.openai_api_key.arn
        },
        {
          name      = "ANTHROPIC_API_KEY"
          valueFrom = aws_ssm_parameter.anthropic_api_key.arn
        }
      ]

      logConfiguration = {
        logDriver = "awslogs"
        options = {
          "awslogs-group"         = aws_cloudwatch_log_group.backend.name
          "awslogs-region"        = var.aws_region
          "awslogs-stream-prefix" = "ecs"
        }
      }

      healthCheck = {
        command     = ["CMD-SHELL", "curl -f http://localhost:8000/health/ || exit 1"]
        interval    = 30
        timeout     = 5
        retries     = 3
        startPeriod = 90
      }

      essential = true
    }
  ])

  tags = merge(local.common_tags, {
    Name = "${local.name_prefix}-backend-task"
  })
}

# Celery Worker Task Definition
resource "aws_ecs_task_definition" "celery_worker" {
  family                   = "${local.name_prefix}-celery-worker"
  requires_compatibilities = ["FARGATE"]
  network_mode             = "awsvpc"
  cpu                      = var.celery_worker_cpu
  memory                   = var.celery_worker_memory
  execution_role_arn       = aws_iam_role.ecs_task_execution_role.arn
  task_role_arn           = aws_iam_role.ecs_task_role.arn

  container_definitions = jsonencode([
    {
      name  = "celery-worker"
      image = "${aws_ecr_repository.backend.repository_url}:latest"
      
      # Copy the same environment variables as backend since Celery uses Django
      environment = [
        # Django Configuration
        {
          name  = "DJANGO_SETTINGS_MODULE"
          value = "retirementadvisorpro.settings"
        },
        {
          name  = "DEBUG"
          value = var.environment == "prod" ? "False" : "True"
        },
        {
          name  = "ENVIRONMENT"
          value = var.environment
        },
        
        # Database Configuration
        {
          name  = "DATABASE_URL"
          value = "postgres://postgres:${random_password.db_password.result}@${aws_db_instance.main.address}:${aws_db_instance.main.port}/${aws_db_instance.main.db_name}"
        },
        {
          name  = "POSTGRES_DB"
          value = aws_db_instance.main.db_name
        },
        {
          name  = "POSTGRES_USER"
          value = aws_db_instance.main.username
        },
        {
          name  = "DATABASE_HOST"
          value = aws_db_instance.main.address
        },
        {
          name  = "DATABASE_NAME"
          value = aws_db_instance.main.db_name
        },
        {
          name  = "DATABASE_USER"
          value = aws_db_instance.main.username
        },
        {
          name  = "DATABASE_PASSWORD"
          value = random_password.db_password.result
        },
        
        # Redis Configuration - Critical for Celery
        {
          name  = "REDIS_URL"
          value = "redis://${aws_elasticache_replication_group.main.primary_endpoint_address}:6379/0"
        },
        {
          name  = "REDIS_HOST"
          value = aws_elasticache_replication_group.main.primary_endpoint_address
        },
        {
          name  = "REDIS_PORT"
          value = "6379"
        },
        {
          name  = "CELERY_BROKER_URL"
          value = "redis://${aws_elasticache_replication_group.main.primary_endpoint_address}:6379/0"
        },
        {
          name  = "CELERY_RESULT_BACKEND"
          value = "redis://${aws_elasticache_replication_group.main.primary_endpoint_address}:6379/0"
        },
        
        # Frontend URL for redirects
        {
          name  = "FRONTEND_URL"
          value = "http://app.retirementadvisorpro.com"
        },
        
        # Auth0 Configuration
        {
          name  = "AUTH0_DOMAIN"
          value = var.auth0_domain
        },
        {
          name  = "AUTH0_CLIENT_ID"
          value = var.auth0_client_id
        },
        {
          name  = "AUTH0_AUDIENCE"
          value = var.auth0_audience
        },
        {
          name  = "AUTH0_ALGORITHM"
          value = "RS256"
        },
        
        # AI Configuration - Needed for background tasks
        {
          name  = "SS_AI_PROVIDER"
          value = "anthropic"
        },
        {
          name  = "OPENAI_MODEL_VERSION"
          value = "gpt-4-turbo-preview"
        },
        
        # Report Center Settings - Needed for background tasks
        {
          name  = "AI_COST_LIMIT_PER_USER_MONTHLY"
          value = "100.00"
        },
        {
          name  = "REPORT_GENERATION_TIMEOUT"
          value = "300"
        },
        {
          name  = "BULK_EXPORT_BATCH_SIZE"
          value = "50"
        },
        
        # AWS S3 Configuration
        {
          name  = "AWS_STORAGE_BUCKET_NAME"
          value = aws_s3_bucket.media_files.id
        },
        {
          name  = "AWS_S3_REGION_NAME"
          value = var.aws_region
        },
        {
          name  = "AWS_DEFAULT_ACL"
          value = "private"
        },
        {
          name  = "USE_S3"
          value = "True"
        }
      ]

      secrets = [
        # Database Secrets
        {
          name      = "POSTGRES_PASSWORD"
          valueFrom = aws_ssm_parameter.db_password.arn
        },
        {
          name      = "DJANGO_SECRET_KEY"
          valueFrom = aws_ssm_parameter.django_secret_key.arn
        },
        
        # AI API Keys - Critical for background processing
        {
          name      = "OPENAI_API_KEY"
          valueFrom = aws_ssm_parameter.openai_api_key.arn
        },
        {
          name      = "ANTHROPIC_API_KEY"
          valueFrom = aws_ssm_parameter.anthropic_api_key.arn
        },
        {
          name      = "STRIPE_SECRET_KEY"
          valueFrom = "${aws_ssm_parameter.stripe_secret_key.arn}"
        }
      ]

      command = [
        "sh", "-c",
        "celery -A retirementadvisorpro worker --loglevel=info --concurrency=4 --max-tasks-per-child=100"
      ]

      logConfiguration = {
        logDriver = "awslogs"
        options = {
          "awslogs-group"         = aws_cloudwatch_log_group.celery_worker.name
          "awslogs-region"        = var.aws_region
          "awslogs-stream-prefix" = "ecs"
        }
      }

      essential = true
    }
  ])

  tags = merge(local.common_tags, {
    Name = "${local.name_prefix}-celery-worker-task"
  })
}

# Celery Beat Task Definition
resource "aws_ecs_task_definition" "celery_beat" {
  family                   = "${local.name_prefix}-celery-beat"
  requires_compatibilities = ["FARGATE"]
  network_mode             = "awsvpc"
  cpu                      = var.celery_beat_cpu
  memory                   = var.celery_beat_memory
  execution_role_arn       = aws_iam_role.ecs_task_execution_role.arn
  task_role_arn           = aws_iam_role.ecs_task_role.arn

  container_definitions = jsonencode([
    {
      name  = "celery-beat"
      image = "${aws_ecr_repository.backend.repository_url}:latest"
      
      environment = [
        {
          name  = "DJANGO_SETTINGS_MODULE"
          value = "retirementadvisorpro.settings"
        },
        {
          name  = "DATABASE_URL"
          value = "postgres://postgres:${random_password.db_password.result}@${aws_db_instance.main.endpoint}:${aws_db_instance.main.port}/${aws_db_instance.main.db_name}"
        },
        {
          name  = "CELERY_BROKER_URL"
          value = "redis://${aws_elasticache_replication_group.main.primary_endpoint_address}:6379/0"
        },
        {
          name  = "CELERY_RESULT_BACKEND"
          value = "redis://${aws_elasticache_replication_group.main.primary_endpoint_address}:6379/0"
        }
      ]

      secrets = []

      command = [
        "sh", "-c",
        "celery -A retirementadvisorpro beat --loglevel=info --scheduler django_celery_beat.schedulers:DatabaseScheduler"
      ]

      logConfiguration = {
        logDriver = "awslogs"
        options = {
          "awslogs-group"         = aws_cloudwatch_log_group.celery_beat.name
          "awslogs-region"        = var.aws_region
          "awslogs-stream-prefix" = "ecs"
        }
      }

      essential = true
    }
  ])

  tags = merge(local.common_tags, {
    Name = "${local.name_prefix}-celery-beat-task"
  })
}

# Celery Flower Task Definition (optional monitoring)
resource "aws_ecs_task_definition" "celery_flower" {
  count = 1  # Set to 0 to disable

  family                   = "${local.name_prefix}-celery-flower"
  requires_compatibilities = ["FARGATE"]
  network_mode             = "awsvpc"
  cpu                      = var.celery_flower_cpu
  memory                   = var.celery_flower_memory
  execution_role_arn       = aws_iam_role.ecs_task_execution_role.arn
  task_role_arn           = aws_iam_role.ecs_task_role.arn

  container_definitions = jsonencode([
    {
      name  = "celery-flower"
      image = "${aws_ecr_repository.backend.repository_url}:latest"
      
      portMappings = [
        {
          containerPort = 5555
          hostPort      = 5555
        }
      ]

      environment = [
        {
          name  = "CELERY_BROKER_URL"
          value = "redis://${aws_elasticache_replication_group.main.primary_endpoint_address}:6379/0"
        },
        {
          name  = "CELERY_RESULT_BACKEND"
          value = "redis://${aws_elasticache_replication_group.main.primary_endpoint_address}:6379/0"
        }
      ]

      command = [
        "sh", "-c",
        "celery -A retirementadvisorpro flower --port=5555 --address=0.0.0.0"
      ]

      logConfiguration = {
        logDriver = "awslogs"
        options = {
          "awslogs-group"         = aws_cloudwatch_log_group.celery_flower.name
          "awslogs-region"        = var.aws_region
          "awslogs-stream-prefix" = "ecs"
        }
      }

      healthCheck = {
        command     = ["CMD-SHELL", "curl -f http://localhost:5555/ || exit 1"]
        interval    = 30
        timeout     = 5
        retries     = 3
        startPeriod = 60
      }

      essential = true
    }
  ])

  tags = merge(local.common_tags, {
    Name = "${local.name_prefix}-celery-flower-task"
  })
}