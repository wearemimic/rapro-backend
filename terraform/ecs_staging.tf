# ECS Staging Environment Configuration
# Smaller instances and lower scaling for staging

# Staging ECS Cluster
resource "aws_ecs_cluster" "staging" {
  name = "${local.name_prefix}-staging"

  setting {
    name  = "containerInsights"
    value = "enabled"
  }

  tags = merge(local.common_tags, {
    Name        = "${local.name_prefix}-staging"
    Environment = "staging"
  })
}

# Staging ECS Cluster Capacity Providers
resource "aws_ecs_cluster_capacity_providers" "staging" {
  cluster_name = aws_ecs_cluster.staging.name

  capacity_providers = ["FARGATE", "FARGATE_SPOT"]

  default_capacity_provider_strategy {
    capacity_provider = var.enable_fargate_spot ? "FARGATE_SPOT" : "FARGATE"
    weight            = 100
    base              = 0
  }
}

# Staging uses shared production database with schema separation
# This saves ~$10/month by eliminating the staging RDS instance
# Staging will use production database with staging schema prefix

# Staging ALB
resource "aws_lb" "staging" {
  name               = "${local.name_prefix}-staging"
  internal           = false
  load_balancer_type = "application"
  security_groups    = [aws_security_group.alb.id]
  subnets           = aws_subnet.public[*].id

  enable_deletion_protection = false
  enable_http2              = true
  enable_cross_zone_load_balancing = true

  tags = merge(local.common_tags, {
    Name        = "${local.name_prefix}-staging"
    Environment = "staging"
  })
}

# Staging Target Groups
resource "aws_lb_target_group" "frontend_staging" {
  name        = "${local.name_prefix}-frontend-staging"
  port        = 3000
  protocol    = "HTTP"
  vpc_id      = aws_vpc.main.id
  target_type = "ip"

  health_check {
    enabled             = true
    healthy_threshold   = 2
    unhealthy_threshold = 2
    timeout             = 5
    interval            = 30
    path                = "/"
    matcher             = "200"
  }

  deregistration_delay = 30

  tags = merge(local.common_tags, {
    Name        = "${local.name_prefix}-frontend-staging"
    Environment = "staging"
  })
}

resource "aws_lb_target_group" "backend_staging" {
  name        = "${local.name_prefix}-backend-staging"
  port        = 8000
  protocol    = "HTTP"
  vpc_id      = aws_vpc.main.id
  target_type = "ip"

  health_check {
    enabled             = true
    healthy_threshold   = 2
    unhealthy_threshold = 2
    timeout             = 5
    interval            = 30
    path                = "/api/health/"
    matcher             = "200"
  }

  deregistration_delay = 30

  tags = merge(local.common_tags, {
    Name        = "${local.name_prefix}-backend-staging"
    Environment = "staging"
  })
}

# Staging ALB Listeners
resource "aws_lb_listener" "staging_http" {
  load_balancer_arn = aws_lb.staging.arn
  port              = "80"
  protocol          = "HTTP"

  default_action {
    type             = "forward"
    target_group_arn = aws_lb_target_group.frontend_staging.arn
  }
}

resource "aws_lb_listener" "staging_https" {
  count = var.certificate_arn != "" ? 1 : 0
  
  load_balancer_arn = aws_lb.staging.arn
  port              = "443"
  protocol          = "HTTPS"
  ssl_policy        = "ELBSecurityPolicy-TLS-1-2-2017-01"
  certificate_arn   = var.certificate_arn

  default_action {
    type             = "forward"
    target_group_arn = aws_lb_target_group.frontend_staging.arn
  }
}

# Staging ALB Rules for Backend API
resource "aws_lb_listener_rule" "backend_api_staging" {
  listener_arn = var.certificate_arn != "" ? aws_lb_listener.staging_https[0].arn : aws_lb_listener.staging_http.arn
  priority     = 100

  action {
    type             = "forward"
    target_group_arn = aws_lb_target_group.backend_staging.arn
  }

  condition {
    path_pattern {
      values = ["/api/*", "/admin/*", "/static/*", "/media/*"]
    }
  }
}

# Staging ECS Services with reduced resources
resource "aws_ecs_service" "frontend_staging" {
  name            = "${local.name_prefix}-frontend-staging"
  cluster         = aws_ecs_cluster.staging.id
  task_definition = aws_ecs_task_definition.frontend_staging.arn
  desired_count   = 1  # Single instance for staging

  # Cost optimization with Fargate Spot
  capacity_provider_strategy {
    capacity_provider = var.enable_fargate_spot ? "FARGATE_SPOT" : "FARGATE"
    weight           = 1
    base             = 1
  }

  network_configuration {
    subnets          = aws_subnet.private[*].id
    security_groups  = [aws_security_group.ecs_tasks.id]
    assign_public_ip = false
  }

  load_balancer {
    target_group_arn = aws_lb_target_group.frontend_staging.arn
    container_name   = "frontend"
    container_port   = 3000
  }

  deployment_maximum_percent         = 200
  deployment_minimum_healthy_percent = 50
  
  deployment_circuit_breaker {
    enable   = true
    rollback = true
  }

  tags = merge(local.common_tags, {
    Name        = "${local.name_prefix}-frontend-staging"
    Environment = "staging"
  })

  depends_on = [aws_lb_listener.staging_http]
}

resource "aws_ecs_service" "backend_staging" {
  name            = "${local.name_prefix}-backend-staging"
  cluster         = aws_ecs_cluster.staging.id
  task_definition = aws_ecs_task_definition.backend_staging.arn
  desired_count   = 1  # Single instance for staging

  # Cost optimization with Fargate Spot
  capacity_provider_strategy {
    capacity_provider = var.enable_fargate_spot ? "FARGATE_SPOT" : "FARGATE"
    weight           = 1
    base             = 1
  }

  network_configuration {
    subnets          = aws_subnet.private[*].id
    security_groups  = [aws_security_group.ecs_tasks.id]
    assign_public_ip = false
  }

  load_balancer {
    target_group_arn = aws_lb_target_group.backend_staging.arn
    container_name   = "backend"
    container_port   = 8000
  }

  deployment_maximum_percent         = 200
  deployment_minimum_healthy_percent = 50
  
  deployment_circuit_breaker {
    enable   = true
    rollback = true
  }

  tags = merge(local.common_tags, {
    Name        = "${local.name_prefix}-backend-staging"
    Environment = "staging"
  })

  depends_on = [aws_lb_listener.staging_http]
}

resource "aws_ecs_service" "celery_worker_staging" {
  name            = "${local.name_prefix}-celery-worker-staging"
  cluster         = aws_ecs_cluster.staging.id
  task_definition = aws_ecs_task_definition.celery_worker_staging.arn
  desired_count   = 1  # Single worker for staging

  # Cost optimization with Fargate Spot
  capacity_provider_strategy {
    capacity_provider = var.enable_fargate_spot ? "FARGATE_SPOT" : "FARGATE"
    weight           = 1
    base             = 1
  }

  network_configuration {
    subnets          = aws_subnet.private[*].id
    security_groups  = [aws_security_group.ecs_tasks.id]
    assign_public_ip = false
  }

  deployment_maximum_percent         = 200
  deployment_minimum_healthy_percent = 0
  
  deployment_circuit_breaker {
    enable   = true
    rollback = true
  }

  tags = merge(local.common_tags, {
    Name        = "${local.name_prefix}-celery-worker-staging"
    Environment = "staging"
  })
}

# Staging Task Definitions with reduced resources
resource "aws_ecs_task_definition" "frontend_staging" {
  family                   = "${local.name_prefix}-frontend-staging"
  network_mode            = "awsvpc"
  requires_compatibilities = ["FARGATE"]
  cpu                     = "256"  # Minimum CPU for staging
  memory                  = "512"  # Minimum memory for staging
  execution_role_arn      = aws_iam_role.ecs_task_execution_role.arn
  task_role_arn           = aws_iam_role.ecs_task_role.arn

  container_definitions = jsonencode([
    {
      name  = "frontend"
      image = "${aws_ecr_repository.frontend.repository_url}:latest"
      
      environment = [
        {
          name  = "NODE_ENV"
          value = "staging"
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
          value = "http://staging.retirementadvisorpro.com/api"
        },
        {
          name  = "VITE_API_BASE_URL"
          value = "http://staging.retirementadvisorpro.com"
        },
        {
          name  = "VITE_FRONTEND_URL"
          value = "http://staging.retirementadvisorpro.com"
        }
      ]
      
      portMappings = [
        {
          containerPort = 3000
          protocol      = "tcp"
        }
      ]
      
      logConfiguration = {
        logDriver = "awslogs"
        options = {
          "awslogs-group"         = aws_cloudwatch_log_group.frontend.name
          "awslogs-region"        = var.aws_region
          "awslogs-stream-prefix" = "frontend-staging"
        }
      }
      
      essential = true
    }
  ])

  tags = merge(local.common_tags, {
    Name        = "${local.name_prefix}-frontend-staging"
    Environment = "staging"
  })
}

resource "aws_ecs_task_definition" "backend_staging" {
  family                   = "${local.name_prefix}-backend-staging"
  network_mode            = "awsvpc"
  requires_compatibilities = ["FARGATE"]
  cpu                     = "256"  # Minimum CPU for staging
  memory                  = "512"  # Minimum memory for staging
  execution_role_arn      = aws_iam_role.ecs_task_execution_role.arn
  task_role_arn           = aws_iam_role.ecs_task_role.arn

  container_definitions = jsonencode([
    {
      name  = "backend"
      image = "${aws_ecr_repository.backend.repository_url}:latest"
      
      environment = [
        # Django Configuration
        {
          name  = "DJANGO_SETTINGS_MODULE"
          value = "retirementadvisorpro.settings"
        },
        {
          name  = "DEBUG"
          value = "True"  # Enable debug for staging
        },
        {
          name  = "ENVIRONMENT"
          value = "staging"
        },
        
        # Database Configuration - Uses shared production database
        {
          name  = "DATABASE_URL"
          value = "postgres://postgres:${random_password.db_password.result}@${aws_db_instance.main.address}:${aws_db_instance.main.port}/${aws_db_instance.main.db_name}?options=-c%20search_path=staging,public"
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
          name  = "DB_SCHEMA_PREFIX"
          value = "staging"
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
          value = "http://staging.retirementadvisorpro.com"
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
          value = "anthropic"
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
          name  = "ENABLE_CLIENT_PORTAL"
          value = "True"
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
          name  = "USE_S3"
          value = "True"
        },
        
        {
          name  = "ALLOWED_HOSTS"
          value = "staging.retirementadvisorpro.com,${aws_lb.staging.dns_name},localhost"
        }
      ]
      
      secrets = [
        # Database Secrets - Uses shared production database
        {
          name      = "DATABASE_PASSWORD"
          valueFrom = aws_ssm_parameter.db_password.arn
        },
        {
          name      = "POSTGRES_PASSWORD"
          valueFrom = aws_ssm_parameter.db_password.arn
        },
        {
          name      = "DJANGO_SECRET_KEY"
          valueFrom = aws_ssm_parameter.django_secret_key.arn
        },
        
        # Auth0 Secrets
        {
          name      = "AUTH0_CLIENT_SECRET"
          valueFrom = aws_ssm_parameter.auth0_client_secret.arn
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
      
      portMappings = [
        {
          containerPort = 8000
          protocol      = "tcp"
        }
      ]
      
      logConfiguration = {
        logDriver = "awslogs"
        options = {
          "awslogs-group"         = aws_cloudwatch_log_group.backend.name
          "awslogs-region"        = var.aws_region
          "awslogs-stream-prefix" = "backend-staging"
        }
      }
      
      essential = true
    }
  ])

  tags = merge(local.common_tags, {
    Name        = "${local.name_prefix}-backend-staging"
    Environment = "staging"
  })
}

resource "aws_ecs_task_definition" "celery_worker_staging" {
  family                   = "${local.name_prefix}-celery-worker-staging"
  network_mode            = "awsvpc"
  requires_compatibilities = ["FARGATE"]
  cpu                     = "256"
  memory                  = "512"
  execution_role_arn      = aws_iam_role.ecs_task_execution_role.arn
  task_role_arn           = aws_iam_role.ecs_task_role.arn

  container_definitions = jsonencode([
    {
      name  = "celery-worker"
      image = "${aws_ecr_repository.backend.repository_url}:latest"
      
      command = ["celery", "-A", "retirementadvisorpro", "worker", "--loglevel=info", "--concurrency=2"]
      
      environment = [
        # Django Configuration
        {
          name  = "DJANGO_SETTINGS_MODULE"
          value = "retirementadvisorpro.settings"
        },
        {
          name  = "DEBUG"
          value = "True"
        },
        {
          name  = "ENVIRONMENT"
          value = "staging"
        },
        
        # Database Configuration - Uses shared production database
        {
          name  = "DATABASE_URL"
          value = "postgres://postgres:${random_password.db_password.result}@${aws_db_instance.main.address}:${aws_db_instance.main.port}/${aws_db_instance.main.db_name}?options=-c%20search_path=staging,public"
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
          name  = "DB_SCHEMA_PREFIX"
          value = "staging"
        },
        
        # Redis Configuration - Critical for Celery
        {
          name  = "REDIS_URL"
          value = "redis://${aws_elasticache_replication_group.main.primary_endpoint_address}:6379/0"
        },
        {
          name  = "CELERY_BROKER_URL"
          value = "redis://${aws_elasticache_replication_group.main.primary_endpoint_address}:6379/0"
        },
        {
          name  = "CELERY_RESULT_BACKEND"
          value = "redis://${aws_elasticache_replication_group.main.primary_endpoint_address}:6379/0"
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
          name  = "USE_S3"
          value = "True"
        }
      ]
      
      secrets = [
        # Database Secrets - Uses shared production database
        {
          name      = "DATABASE_PASSWORD"
          valueFrom = aws_ssm_parameter.db_password.arn
        },
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
        }
      ]
      
      logConfiguration = {
        logDriver = "awslogs"
        options = {
          "awslogs-group"         = aws_cloudwatch_log_group.celery_worker.name
          "awslogs-region"        = var.aws_region
          "awslogs-stream-prefix" = "celery-worker-staging"
        }
      }
      
      essential = true
    }
  ])

  tags = merge(local.common_tags, {
    Name        = "${local.name_prefix}-celery-worker-staging"
    Environment = "staging"
  })
}