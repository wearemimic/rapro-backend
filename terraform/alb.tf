# Application Load Balancer for RetirementAdvisorPro
# Routes traffic between frontend and backend services

# Application Load Balancer
resource "aws_lb" "main" {
  name               = "${local.name_prefix}-alb"
  internal           = false
  load_balancer_type = "application"
  security_groups    = [aws_security_group.alb.id]
  subnets            = aws_subnet.public[*].id

  enable_deletion_protection = var.environment == "prod" ? true : false

  # Access logs for debugging and compliance
  access_logs {
    bucket  = aws_s3_bucket.static_assets.id
    prefix  = "alb-access-logs"
    enabled = false  # Enable if needed, incurs additional costs
  }

  tags = merge(local.common_tags, {
    Name = "${local.name_prefix}-alb"
  })
}

# Target Groups

# Frontend Target Group
resource "aws_lb_target_group" "frontend" {
  name        = "${local.name_prefix}-frontend-tg"
  port        = 3000
  protocol    = "HTTP"
  target_type = "ip"
  vpc_id      = aws_vpc.main.id

  health_check {
    enabled             = true
    healthy_threshold   = 2
    unhealthy_threshold = 2
    timeout             = 5
    interval            = 30
    path                = "/"
    matcher             = "200"
    port                = "traffic-port"
    protocol            = "HTTP"
  }

  # Deregistration delay for graceful shutdowns
  deregistration_delay = 30

  tags = merge(local.common_tags, {
    Name = "${local.name_prefix}-frontend-tg"
  })

  lifecycle {
    create_before_destroy = true
  }
}

# Backend API Target Group
resource "aws_lb_target_group" "backend" {
  name        = "${local.name_prefix}-backend-tg"
  port        = 8000
  protocol    = "HTTP"
  target_type = "ip"
  vpc_id      = aws_vpc.main.id

  health_check {
    enabled             = true
    healthy_threshold   = 2
    unhealthy_threshold = 2
    timeout             = 5
    interval            = 30
    path                = "/health/"  # Django health check endpoint
    matcher             = "200"
    port                = "traffic-port"
    protocol            = "HTTP"
  }

  # Longer deregistration delay for API processing
  deregistration_delay = 60

  # Sticky sessions for Django sessions (if not using database sessions)
  stickiness {
    type            = "lb_cookie"
    cookie_duration = 86400  # 24 hours
    enabled         = false   # Set to true if needed
  }

  tags = merge(local.common_tags, {
    Name = "${local.name_prefix}-backend-tg"
  })

  lifecycle {
    create_before_destroy = true
  }
}

# Celery Flower Target Group (optional monitoring)
resource "aws_lb_target_group" "celery_flower" {
  count = 1  # Set to 0 to disable Flower

  name        = "${local.name_prefix}-flower-tg"
  port        = 5555
  protocol    = "HTTP"
  target_type = "ip"
  vpc_id      = aws_vpc.main.id

  health_check {
    enabled             = true
    healthy_threshold   = 2
    unhealthy_threshold = 2
    timeout             = 5
    interval            = 30
    path                = "/"
    matcher             = "200"
    port                = "traffic-port"
    protocol            = "HTTP"
  }

  deregistration_delay = 30

  tags = merge(local.common_tags, {
    Name = "${local.name_prefix}-flower-tg"
  })

  lifecycle {
    create_before_destroy = true
  }
}

# HTTP Listener (redirects to HTTPS if certificate provided)
resource "aws_lb_listener" "http" {
  load_balancer_arn = aws_lb.main.arn
  port              = "80"
  protocol          = "HTTP"

  # If certificate is provided, redirect to HTTPS
  dynamic "default_action" {
    for_each = var.certificate_arn != "" ? [1] : []
    content {
      type = "redirect"
      redirect {
        port        = "443"
        protocol    = "HTTPS"
        status_code = "HTTP_301"
      }
    }
  }

  # If no certificate, serve frontend directly
  dynamic "default_action" {
    for_each = var.certificate_arn == "" ? [1] : []
    content {
      type             = "forward"
      target_group_arn = aws_lb_target_group.frontend.arn
    }
  }

  tags = merge(local.common_tags, {
    Name = "${local.name_prefix}-http-listener"
  })
}

# HTTPS Listener (only if certificate is provided)
resource "aws_lb_listener" "https" {
  count = var.certificate_arn != "" ? 1 : 0

  load_balancer_arn = aws_lb.main.arn
  port              = "443"
  protocol          = "HTTPS"
  ssl_policy        = "ELBSecurityPolicy-TLS-1-2-2017-01"
  certificate_arn   = var.certificate_arn

  # Default action forwards to frontend
  default_action {
    type             = "forward"
    target_group_arn = aws_lb_target_group.frontend.arn
  }

  tags = merge(local.common_tags, {
    Name = "${local.name_prefix}-https-listener"
  })
}

# Listener Rules for routing

# API routes to backend (HTTP)
resource "aws_lb_listener_rule" "api_http" {
  count = var.certificate_arn == "" ? 1 : 0

  listener_arn = aws_lb_listener.http.arn
  priority     = 100

  action {
    type             = "forward"
    target_group_arn = aws_lb_target_group.backend.arn
  }

  condition {
    path_pattern {
      values = ["/api/*", "/admin/*", "/auth/*"]
    }
  }

  tags = merge(local.common_tags, {
    Name = "${local.name_prefix}-api-http-rule"
  })
}

# API routes to backend (HTTPS)
resource "aws_lb_listener_rule" "api_https" {
  count = var.certificate_arn != "" ? 1 : 0

  listener_arn = aws_lb_listener.https[0].arn
  priority     = 100

  action {
    type             = "forward"
    target_group_arn = aws_lb_target_group.backend.arn
  }

  condition {
    path_pattern {
      values = ["/api/*", "/admin/*", "/auth/*"]
    }
  }

  tags = merge(local.common_tags, {
    Name = "${local.name_prefix}-api-https-rule"
  })
}

# Celery Flower monitoring route (HTTPS only for security)
resource "aws_lb_listener_rule" "flower_https" {
  count = var.certificate_arn != "" && length(aws_lb_target_group.celery_flower) > 0 ? 1 : 0

  listener_arn = aws_lb_listener.https[0].arn
  priority     = 200

  action {
    type             = "forward"
    target_group_arn = aws_lb_target_group.celery_flower[0].arn
  }

  condition {
    path_pattern {
      values = ["/flower/*"]
    }
  }

  # Optional: Add basic auth or IP restriction for security
  # condition {
  #   source_ip {
  #     values = ["10.0.0.0/8"]  # Restrict to internal network
  #   }
  # }

  tags = merge(local.common_tags, {
    Name = "${local.name_prefix}-flower-https-rule"
  })
}

# Static files route (serve from S3 via CloudFront if enabled)
# This rule is lower priority than API routes
resource "aws_lb_listener_rule" "static_files" {
  count = var.enable_cloudfront ? 0 : 1  # Only if CloudFront is disabled

  listener_arn = var.certificate_arn != "" ? aws_lb_listener.https[0].arn : aws_lb_listener.http.arn
  priority     = 300

  action {
    type             = "forward"
    target_group_arn = aws_lb_target_group.backend.arn
  }

  condition {
    path_pattern {
      values = ["/static/*", "/media/*"]
    }
  }

  tags = merge(local.common_tags, {
    Name = "${local.name_prefix}-static-files-rule"
  })
}

# CloudWatch alarms for ALB
resource "aws_cloudwatch_metric_alarm" "alb_response_time" {
  alarm_name          = "${local.name_prefix}-alb-response-time"
  comparison_operator = "GreaterThanThreshold"
  evaluation_periods  = "2"
  metric_name         = "TargetResponseTime"
  namespace           = "AWS/ApplicationELB"
  period              = "300"
  statistic           = "Average"
  threshold           = "2"
  alarm_description   = "ALB response time is too high"

  dimensions = {
    LoadBalancer = aws_lb.main.arn_suffix
  }

  alarm_actions = var.notification_email != "" ? [aws_sns_topic.alerts[0].arn] : []

  tags = merge(local.common_tags, {
    Name = "${local.name_prefix}-alb-response-time"
  })
}

resource "aws_cloudwatch_metric_alarm" "alb_healthy_hosts" {
  alarm_name          = "${local.name_prefix}-alb-healthy-hosts"
  comparison_operator = "LessThanThreshold"
  evaluation_periods  = "2"
  metric_name         = "HealthyHostCount"
  namespace           = "AWS/ApplicationELB"
  period              = "300"
  statistic           = "Average"
  threshold           = "1"
  alarm_description   = "ALB has less than 1 healthy host"

  dimensions = {
    TargetGroup  = aws_lb_target_group.backend.arn_suffix
    LoadBalancer = aws_lb.main.arn_suffix
  }

  alarm_actions = var.notification_email != "" ? [aws_sns_topic.alerts[0].arn] : []

  tags = merge(local.common_tags, {
    Name = "${local.name_prefix}-alb-healthy-hosts"
  })
}

resource "aws_cloudwatch_metric_alarm" "alb_5xx_errors" {
  alarm_name          = "${local.name_prefix}-alb-5xx-errors"
  comparison_operator = "GreaterThanThreshold"
  evaluation_periods  = "2"
  metric_name         = "HTTPCode_ELB_5XX_Count"
  namespace           = "AWS/ApplicationELB"
  period              = "300"
  statistic           = "Sum"
  threshold           = "10"
  alarm_description   = "ALB 5XX error rate is too high"
  treat_missing_data  = "notBreaching"

  dimensions = {
    LoadBalancer = aws_lb.main.arn_suffix
  }

  alarm_actions = var.notification_email != "" ? [aws_sns_topic.alerts[0].arn] : []

  tags = merge(local.common_tags, {
    Name = "${local.name_prefix}-alb-5xx-errors"
  })
}