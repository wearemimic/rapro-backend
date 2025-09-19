# CloudWatch monitoring and alerting for RetirementAdvisorPro
# Comprehensive monitoring for all infrastructure components

# SNS Topic for Alerts
resource "aws_sns_topic" "alerts" {
  count = var.notification_email != "" ? 1 : 0

  name         = "${local.name_prefix}-alerts"
  display_name = "RetirementAdvisorPro Alerts"

  tags = merge(local.common_tags, {
    Name = "${local.name_prefix}-alerts"
  })
}

resource "aws_sns_topic_subscription" "email_alerts" {
  count = var.notification_email != "" ? 1 : 0

  topic_arn = aws_sns_topic.alerts[0].arn
  protocol  = "email"
  endpoint  = var.notification_email
}

# CloudWatch Dashboard
resource "aws_cloudwatch_dashboard" "main" {
  dashboard_name = "${local.name_prefix}-dashboard"

  dashboard_body = jsonencode({
    widgets = [
      # Application Load Balancer Metrics
      {
        type   = "metric"
        x      = 0
        y      = 0
        width  = 12
        height = 6

        properties = {
          metrics = [
            ["AWS/ApplicationELB", "RequestCount", "LoadBalancer", aws_lb.main.arn_suffix],
            [".", "TargetResponseTime", ".", "."],
            [".", "HTTPCode_Target_2XX_Count", ".", "."],
            [".", "HTTPCode_Target_4XX_Count", ".", "."],
            [".", "HTTPCode_Target_5XX_Count", ".", "."]
          ]
          view    = "timeSeries"
          stacked = false
          region  = var.aws_region
          title   = "Application Load Balancer Metrics"
          period  = 300
        }
      },

      # ECS Service Metrics
      {
        type   = "metric"
        x      = 12
        y      = 0
        width  = 12
        height = 6

        properties = {
          metrics = [
            ["AWS/ECS", "CPUUtilization", "ServiceName", aws_ecs_service.frontend.name, "ClusterName", aws_ecs_cluster.main.name],
            [".", "MemoryUtilization", ".", ".", ".", "."],
            [".", "CPUUtilization", "ServiceName", aws_ecs_service.backend.name, "ClusterName", aws_ecs_cluster.main.name],
            [".", "MemoryUtilization", ".", ".", ".", "."]
          ]
          view    = "timeSeries"
          stacked = false
          region  = var.aws_region
          title   = "ECS Service Resource Utilization"
          period  = 300
        }
      },

      # RDS Metrics
      {
        type   = "metric"
        x      = 0
        y      = 6
        width  = 12
        height = 6

        properties = {
          metrics = [
            ["AWS/RDS", "CPUUtilization", "DBInstanceIdentifier", aws_db_instance.main.id],
            [".", "DatabaseConnections", ".", "."],
            [".", "FreeableMemory", ".", "."],
            [".", "ReadLatency", ".", "."],
            [".", "WriteLatency", ".", "."]
          ]
          view    = "timeSeries"
          stacked = false
          region  = var.aws_region
          title   = "RDS Database Metrics"
          period  = 300
        }
      },

      # ElastiCache Metrics
      {
        type   = "metric"
        x      = 12
        y      = 6
        width  = 12
        height = 6

        properties = {
          metrics = [
            ["AWS/ElastiCache", "CPUUtilization", "CacheClusterId", aws_elasticache_replication_group.main.id],
            [".", "DatabaseMemoryUsagePercentage", ".", "."],
            [".", "CurrConnections", ".", "."],
            [".", "CacheHits", ".", "."],
            [".", "CacheMisses", ".", "."]
          ]
          view    = "timeSeries"
          stacked = false
          region  = var.aws_region
          title   = "ElastiCache Redis Metrics"
          period  = 300
        }
      },


      # Application Errors Log Insights
      {
        type   = "log"
        x      = 12
        y      = 12
        width  = 12
        height = 6

        properties = {
          query = "SOURCE '/ecs/${local.name_prefix}-backend' | fields @timestamp, @message | filter @message like /ERROR/ | sort @timestamp desc | limit 20"
          region = var.aws_region
          title  = "Recent Application Errors"
        }
      }
    ]
  })
}

# Custom CloudWatch Metrics for Application Performance

# Custom metric for Celery queue length (example - requires implementation in app)
resource "aws_cloudwatch_log_metric_filter" "celery_queue_length" {
  name           = "${local.name_prefix}-celery-queue-length"
  log_group_name = aws_cloudwatch_log_group.celery_worker.name
  pattern        = "[timestamp, level=\"INFO\", message=\"Queue length:\", length]"

  metric_transformation {
    name      = "CeleryQueueLength"
    namespace = "RetirementAdvisorPro/Celery"
    value     = "$length"
  }
}

# Custom metric for Django response time (example - requires implementation)
resource "aws_cloudwatch_log_metric_filter" "django_response_time" {
  name           = "${local.name_prefix}-django-response-time"
  log_group_name = aws_cloudwatch_log_group.backend.name
  pattern        = "[timestamp, level, message=\"Response time:\", duration, ms]"

  metric_transformation {
    name      = "DjangoResponseTime"
    namespace = "RetirementAdvisorPro/Django"
    value     = "$duration"
    unit      = "Milliseconds"
  }
}

# Application-specific alarms

# High error rate alarm
resource "aws_cloudwatch_metric_alarm" "high_error_rate" {
  count = var.notification_email != "" ? 1 : 0

  alarm_name          = "${local.name_prefix}-high-error-rate"
  comparison_operator = "GreaterThanThreshold"
  evaluation_periods  = "2"
  metric_name         = "HTTPCode_Target_5XX_Count"
  namespace           = "AWS/ApplicationELB"
  period              = "300"
  statistic           = "Sum"
  threshold           = "10"
  alarm_description   = "High 5XX error rate detected"

  dimensions = {
    LoadBalancer = aws_lb.main.arn_suffix
  }

  alarm_actions = [aws_sns_topic.alerts[0].arn]

  tags = merge(local.common_tags, {
    Name = "${local.name_prefix}-high-error-rate"
  })
}

# Low request volume alarm (potential issue)
resource "aws_cloudwatch_metric_alarm" "low_request_volume" {
  count = var.notification_email != "" ? 1 : 0

  alarm_name          = "${local.name_prefix}-low-request-volume"
  comparison_operator = "LessThanThreshold"
  evaluation_periods  = "3"
  metric_name         = "RequestCount"
  namespace           = "AWS/ApplicationELB"
  period              = "300"
  statistic           = "Sum"
  threshold           = "1"
  alarm_description   = "Very low request volume - potential service issue"
  treat_missing_data  = "breaching"

  dimensions = {
    LoadBalancer = aws_lb.main.arn_suffix
  }

  alarm_actions = [aws_sns_topic.alerts[0].arn]

  tags = merge(local.common_tags, {
    Name = "${local.name_prefix}-low-request-volume"
  })
}

# ECS Service unhealthy alarm
resource "aws_cloudwatch_metric_alarm" "ecs_service_unhealthy" {
  count = var.notification_email != "" ? 1 : 0

  alarm_name          = "${local.name_prefix}-ecs-service-unhealthy"
  comparison_operator = "LessThanThreshold"
  evaluation_periods  = "2"
  metric_name         = "HealthyHostCount"
  namespace           = "AWS/ApplicationELB"
  period              = "60"
  statistic           = "Average"
  threshold           = "1"
  alarm_description   = "No healthy ECS service instances"

  dimensions = {
    TargetGroup  = aws_lb_target_group.backend.arn_suffix
    LoadBalancer = aws_lb.main.arn_suffix
  }

  alarm_actions = [aws_sns_topic.alerts[0].arn]

  tags = merge(local.common_tags, {
    Name = "${local.name_prefix}-ecs-service-unhealthy"
  })
}

# Cost monitoring alarm
resource "aws_cloudwatch_metric_alarm" "billing_alarm" {
  count = var.notification_email != "" ? 1 : 0

  alarm_name          = "${local.name_prefix}-billing-alarm"
  comparison_operator = "GreaterThanThreshold"
  evaluation_periods  = "1"
  metric_name         = "EstimatedCharges"
  namespace           = "AWS/Billing"
  period              = "86400"  # Daily
  statistic           = "Maximum"
  threshold           = "200"  # Adjust based on expected monthly spend
  alarm_description   = "AWS billing exceeded $200"

  dimensions = {
    Currency = "USD"
  }

  alarm_actions = [aws_sns_topic.alerts[0].arn]

  tags = merge(local.common_tags, {
    Name = "${local.name_prefix}-billing-alarm"
  })
}

# Log Groups retention settings (already defined in other files but worth monitoring)
resource "aws_cloudwatch_log_metric_filter" "error_count" {
  name           = "${local.name_prefix}-error-count"
  log_group_name = aws_cloudwatch_log_group.backend.name
  pattern        = "ERROR"

  metric_transformation {
    name      = "ErrorCount"
    namespace = "RetirementAdvisorPro/Application"
    value     = "1"
  }
}

resource "aws_cloudwatch_metric_alarm" "application_errors" {
  count = var.notification_email != "" ? 1 : 0

  alarm_name          = "${local.name_prefix}-application-errors"
  comparison_operator = "GreaterThanThreshold"
  evaluation_periods  = "2"
  metric_name         = "ErrorCount"
  namespace           = "RetirementAdvisorPro/Application"
  period              = "300"
  statistic           = "Sum"
  threshold           = "5"
  alarm_description   = "High application error rate"
  treat_missing_data  = "notBreaching"

  alarm_actions = [aws_sns_topic.alerts[0].arn]

  tags = merge(local.common_tags, {
    Name = "${local.name_prefix}-application-errors"
  })
}

# ECS Task stopped alarm - disabled until Container Insights is enabled
# resource "aws_cloudwatch_log_metric_filter" "ecs_task_stopped" {
#   name           = "${local.name_prefix}-ecs-task-stopped"
#   log_group_name = "/aws/ecs/containerinsights/${aws_ecs_cluster.main.name}/performance"
#   pattern        = "[version, account, time, region, cluster_name, task_arn, task_definition_arn, service_name=\"${aws_ecs_service.backend.name}\", last_status=\"STOPPED\", desired_status, ...]"
#
#   metric_transformation {
#     name      = "ECSTaskStopped"
#     namespace = "RetirementAdvisorPro/ECS"
#     value     = "1"
#   }
# }

# X-Ray Tracing (optional for detailed performance monitoring)
# resource "aws_xray_sampling_rule" "retirementadvisorpro" {
#   rule_name      = "${local.name_prefix}-sampling-rule"
#   priority       = 9000
#   version        = 1
#   reservoir_size = 1
#   fixed_rate     = 0.1
#   url_path       = "*"
#   host           = "*"
#   http_method    = "*"
#   service_type   = "*"
#   service_name   = "*"
#   resource_arn   = "*"
# }

# Performance monitoring for Celery workers
resource "aws_cloudwatch_log_metric_filter" "celery_task_duration" {
  name           = "${local.name_prefix}-celery-task-duration"
  log_group_name = aws_cloudwatch_log_group.celery_worker.name
  pattern        = "[timestamp, level=\"INFO\", message=\"Task completed in\", duration, seconds]"

  metric_transformation {
    name      = "CeleryTaskDuration"
    namespace = "RetirementAdvisorPro/Celery"
    value     = "$duration"
    unit      = "Seconds"
  }
}

resource "aws_cloudwatch_metric_alarm" "celery_task_duration_high" {
  count = var.notification_email != "" ? 1 : 0

  alarm_name          = "${local.name_prefix}-celery-task-duration-high"
  comparison_operator = "GreaterThanThreshold"
  evaluation_periods  = "2"
  metric_name         = "CeleryTaskDuration"
  namespace           = "RetirementAdvisorPro/Celery"
  period              = "300"
  statistic           = "Average"
  threshold           = "300"  # 5 minutes
  alarm_description   = "Celery tasks taking too long to complete"
  treat_missing_data  = "notBreaching"

  alarm_actions = [aws_sns_topic.alerts[0].arn]

  tags = merge(local.common_tags, {
    Name = "${local.name_prefix}-celery-task-duration-high"
  })
}