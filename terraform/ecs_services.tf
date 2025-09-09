# ECS Services for RetirementAdvisorPro
# Auto-scaling services with cost optimization using Fargate Spot

# Frontend Service
resource "aws_ecs_service" "frontend" {
  name            = "${local.name_prefix}-frontend"
  cluster         = aws_ecs_cluster.main.id
  task_definition = aws_ecs_task_definition.frontend.arn
  desired_count   = var.frontend_min_capacity

  # Cost optimization with Fargate Spot
  capacity_provider_strategy {
    capacity_provider = var.enable_fargate_spot ? "FARGATE_SPOT" : "FARGATE"
    weight           = 1
    base             = var.frontend_min_capacity
  }

  network_configuration {
    subnets          = aws_subnet.private[*].id
    security_groups  = [aws_security_group.ecs_tasks.id]
    assign_public_ip = false
  }

  load_balancer {
    target_group_arn = aws_lb_target_group.frontend.arn
    container_name   = "frontend"
    container_port   = 3000
  }

  # Deployment configuration
  deployment_maximum_percent         = 200
  deployment_minimum_healthy_percent = 100
  
  deployment_circuit_breaker {
    enable   = true
    rollback = true
  }

  # Health check grace period
  health_check_grace_period_seconds = 60

  # Enable service discovery (optional)
  # service_registries {
  #   registry_arn = aws_service_discovery_service.frontend.arn
  # }

  depends_on = [aws_lb_listener.http, aws_lb_listener.https]

  tags = merge(local.common_tags, {
    Name = "${local.name_prefix}-frontend-service"
  })

  lifecycle {
    ignore_changes = [desired_count]
  }
}

# Backend Service
resource "aws_ecs_service" "backend" {
  name            = "${local.name_prefix}-backend"
  cluster         = aws_ecs_cluster.main.id
  task_definition = aws_ecs_task_definition.backend.arn
  desired_count   = var.backend_min_capacity

  # Cost optimization with Fargate Spot
  capacity_provider_strategy {
    capacity_provider = var.enable_fargate_spot ? "FARGATE_SPOT" : "FARGATE"
    weight           = 1
    base             = var.backend_min_capacity
  }

  network_configuration {
    subnets          = aws_subnet.private[*].id
    security_groups  = [aws_security_group.ecs_tasks.id]
    assign_public_ip = false
  }

  load_balancer {
    target_group_arn = aws_lb_target_group.backend.arn
    container_name   = "backend"
    container_port   = 8000
  }

  # Give Django time to start before health checks begin
  health_check_grace_period_seconds = 180

  # Deployment configuration
  deployment_maximum_percent         = 200
  deployment_minimum_healthy_percent = 50  # Allow lower for API services
  
  deployment_circuit_breaker {
    enable   = true
    rollback = true
  }

  # Longer health check grace period for Django startup
  health_check_grace_period_seconds = 120

  depends_on = [
    aws_lb_listener.http,
    aws_lb_listener.https,
    aws_db_instance.main,
    aws_elasticache_replication_group.main
  ]

  tags = merge(local.common_tags, {
    Name = "${local.name_prefix}-backend-service"
  })

  lifecycle {
    ignore_changes = [desired_count]
  }
}

# Celery Worker Service
resource "aws_ecs_service" "celery_worker" {
  name            = "${local.name_prefix}-celery-worker"
  cluster         = aws_ecs_cluster.main.id
  task_definition = aws_ecs_task_definition.celery_worker.arn
  desired_count   = var.celery_worker_min_capacity

  # Cost optimization with Fargate Spot (good for batch processing)
  capacity_provider_strategy {
    capacity_provider = var.enable_fargate_spot ? "FARGATE_SPOT" : "FARGATE"
    weight           = 1
    base             = var.celery_worker_min_capacity
  }

  network_configuration {
    subnets          = aws_subnet.private[*].id
    security_groups  = [aws_security_group.ecs_tasks.id]
    assign_public_ip = false
  }

  # Deployment configuration
  deployment_maximum_percent         = 200
  deployment_minimum_healthy_percent = 0  # Allow zero for background workers during deployments
  
  deployment_circuit_breaker {
    enable   = true
    rollback = true
  }

  depends_on = [
    aws_db_instance.main,
    aws_elasticache_replication_group.main
  ]

  tags = merge(local.common_tags, {
    Name = "${local.name_prefix}-celery-worker-service"
  })

  lifecycle {
    ignore_changes = [desired_count]
  }
}

# Celery Beat Service (scheduler - only need 1 instance)
resource "aws_ecs_service" "celery_beat" {
  name            = "${local.name_prefix}-celery-beat"
  cluster         = aws_ecs_cluster.main.id
  task_definition = aws_ecs_task_definition.celery_beat.arn
  desired_count   = 1  # Always 1 for scheduler

  # Regular Fargate for scheduler (needs reliability)
  capacity_provider_strategy {
    capacity_provider = "FARGATE"  # Don't use Spot for critical scheduler
    weight           = 1
    base             = 1
  }

  network_configuration {
    subnets          = aws_subnet.private[*].id
    security_groups  = [aws_security_group.ecs_tasks.id]
    assign_public_ip = false
  }

  # Deployment configuration
  deployment_maximum_percent         = 100  # Don't run multiple schedulers
  deployment_minimum_healthy_percent = 0
  
  deployment_circuit_breaker {
    enable   = true
    rollback = true
  }

  depends_on = [
    aws_db_instance.main,
    aws_elasticache_replication_group.main
  ]

  tags = merge(local.common_tags, {
    Name = "${local.name_prefix}-celery-beat-service"
  })
}

# Celery Flower Service (optional monitoring)
resource "aws_ecs_service" "celery_flower" {
  count = length(aws_ecs_task_definition.celery_flower)

  name            = "${local.name_prefix}-celery-flower"
  cluster         = aws_ecs_cluster.main.id
  task_definition = aws_ecs_task_definition.celery_flower[0].arn
  desired_count   = 1

  # Fargate Spot is fine for monitoring
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
    target_group_arn = aws_lb_target_group.celery_flower[0].arn
    container_name   = "celery-flower"
    container_port   = 5555
  }

  # Deployment configuration
  deployment_maximum_percent         = 200
  deployment_minimum_healthy_percent = 0  # Non-critical service
  
  deployment_circuit_breaker {
    enable   = true
    rollback = true
  }

  health_check_grace_period_seconds = 60

  depends_on = [
    aws_lb_listener.https,
    aws_elasticache_replication_group.main
  ]

  tags = merge(local.common_tags, {
    Name = "${local.name_prefix}-celery-flower-service"
  })
}

# Auto Scaling Targets and Policies

# Frontend Auto Scaling Target
resource "aws_appautoscaling_target" "frontend" {
  max_capacity       = var.frontend_max_capacity
  min_capacity       = var.frontend_min_capacity
  resource_id        = "service/${aws_ecs_cluster.main.name}/${aws_ecs_service.frontend.name}"
  scalable_dimension = "ecs:service:DesiredCount"
  service_namespace  = "ecs"

  tags = merge(local.common_tags, {
    Name = "${local.name_prefix}-frontend-autoscaling-target"
  })
}

# Frontend Auto Scaling Policy - CPU
resource "aws_appautoscaling_policy" "frontend_cpu" {
  name               = "${local.name_prefix}-frontend-cpu-scaling"
  policy_type        = "TargetTrackingScaling"
  resource_id        = aws_appautoscaling_target.frontend.resource_id
  scalable_dimension = aws_appautoscaling_target.frontend.scalable_dimension
  service_namespace  = aws_appautoscaling_target.frontend.service_namespace

  target_tracking_scaling_policy_configuration {
    predefined_metric_specification {
      predefined_metric_type = "ECSServiceAverageCPUUtilization"
    }
    target_value       = 70.0
    scale_in_cooldown  = 300
    scale_out_cooldown = 300
  }
}

# Frontend Auto Scaling Policy - Memory
resource "aws_appautoscaling_policy" "frontend_memory" {
  name               = "${local.name_prefix}-frontend-memory-scaling"
  policy_type        = "TargetTrackingScaling"
  resource_id        = aws_appautoscaling_target.frontend.resource_id
  scalable_dimension = aws_appautoscaling_target.frontend.scalable_dimension
  service_namespace  = aws_appautoscaling_target.frontend.service_namespace

  target_tracking_scaling_policy_configuration {
    predefined_metric_specification {
      predefined_metric_type = "ECSServiceAverageMemoryUtilization"
    }
    target_value       = 80.0
    scale_in_cooldown  = 300
    scale_out_cooldown = 300
  }
}

# Backend Auto Scaling Target
resource "aws_appautoscaling_target" "backend" {
  max_capacity       = var.backend_max_capacity
  min_capacity       = var.backend_min_capacity
  resource_id        = "service/${aws_ecs_cluster.main.name}/${aws_ecs_service.backend.name}"
  scalable_dimension = "ecs:service:DesiredCount"
  service_namespace  = "ecs"

  tags = merge(local.common_tags, {
    Name = "${local.name_prefix}-backend-autoscaling-target"
  })
}

# Backend Auto Scaling Policy - CPU
resource "aws_appautoscaling_policy" "backend_cpu" {
  name               = "${local.name_prefix}-backend-cpu-scaling"
  policy_type        = "TargetTrackingScaling"
  resource_id        = aws_appautoscaling_target.backend.resource_id
  scalable_dimension = aws_appautoscaling_target.backend.scalable_dimension
  service_namespace  = aws_appautoscaling_target.backend.service_namespace

  target_tracking_scaling_policy_configuration {
    predefined_metric_specification {
      predefined_metric_type = "ECSServiceAverageCPUUtilization"
    }
    target_value       = 70.0
    scale_in_cooldown  = 300
    scale_out_cooldown = 180  # Scale out faster for API services
  }
}

# Backend Auto Scaling Policy - Request Count per Target
resource "aws_appautoscaling_policy" "backend_request_count" {
  name               = "${local.name_prefix}-backend-request-scaling"
  policy_type        = "TargetTrackingScaling"
  resource_id        = aws_appautoscaling_target.backend.resource_id
  scalable_dimension = aws_appautoscaling_target.backend.scalable_dimension
  service_namespace  = aws_appautoscaling_target.backend.service_namespace

  target_tracking_scaling_policy_configuration {
    predefined_metric_specification {
      predefined_metric_type = "ALBRequestCountPerTarget"
      resource_label         = "${aws_lb.main.arn_suffix}/${aws_lb_target_group.backend.arn_suffix}"
    }
    target_value       = 1000.0  # Requests per minute per target
    scale_in_cooldown  = 300
    scale_out_cooldown = 180
  }
}

# Celery Worker Auto Scaling Target
resource "aws_appautoscaling_target" "celery_worker" {
  max_capacity       = var.celery_worker_max_capacity
  min_capacity       = var.celery_worker_min_capacity
  resource_id        = "service/${aws_ecs_cluster.main.name}/${aws_ecs_service.celery_worker.name}"
  scalable_dimension = "ecs:service:DesiredCount"
  service_namespace  = "ecs"

  tags = merge(local.common_tags, {
    Name = "${local.name_prefix}-celery-worker-autoscaling-target"
  })
}

# Celery Worker Auto Scaling Policy - CPU
resource "aws_appautoscaling_policy" "celery_worker_cpu" {
  name               = "${local.name_prefix}-celery-worker-cpu-scaling"
  policy_type        = "TargetTrackingScaling"
  resource_id        = aws_appautoscaling_target.celery_worker.resource_id
  scalable_dimension = aws_appautoscaling_target.celery_worker.scalable_dimension
  service_namespace  = aws_appautoscaling_target.celery_worker.service_namespace

  target_tracking_scaling_policy_configuration {
    predefined_metric_specification {
      predefined_metric_type = "ECSServiceAverageCPUUtilization"
    }
    target_value       = 80.0  # Higher threshold for batch processing
    scale_in_cooldown  = 600   # Longer cooldown for workers
    scale_out_cooldown = 300
  }
}

# Custom CloudWatch metric for Celery queue length (requires custom implementation)
# This would require a custom CloudWatch metric from your Celery monitoring
# resource "aws_appautoscaling_policy" "celery_worker_queue_length" {
#   name               = "${local.name_prefix}-celery-worker-queue-scaling"
#   policy_type        = "TargetTrackingScaling"
#   resource_id        = aws_appautoscaling_target.celery_worker.resource_id
#   scalable_dimension = aws_appautoscaling_target.celery_worker.scalable_dimension
#   service_namespace  = aws_appautoscaling_target.celery_worker.service_namespace

#   target_tracking_scaling_policy_configuration {
#     customized_metric_specification {
#       metric_name = "CeleryQueueLength"
#       namespace   = "RetirementAdvisorPro/Celery"
#       statistic   = "Average"
#     }
#     target_value       = 10.0  # Scale when queue has more than 10 tasks
#     scale_in_cooldown  = 600
#     scale_out_cooldown = 300
#   }
# }