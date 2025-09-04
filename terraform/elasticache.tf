# ElastiCache Redis cluster for RetirementAdvisorPro
# Used for caching and Celery message broker
# Cost-optimized with single node setup

# ElastiCache Subnet Group
resource "aws_elasticache_subnet_group" "main" {
  name       = "${local.name_prefix}-redis-subnet-group"
  subnet_ids = aws_subnet.private[*].id

  tags = merge(local.common_tags, {
    Name = "${local.name_prefix}-redis-subnet-group"
  })
}

# ElastiCache Parameter Group for Redis optimization
resource "aws_elasticache_parameter_group" "main" {
  family = "redis7"
  name   = "${local.name_prefix}-redis-params"

  # Memory management for small instances
  parameter {
    name  = "maxmemory-policy"
    value = "allkeys-lru"
  }



  # Connection settings
  parameter {
    name  = "timeout"
    value = "300"
  }

  parameter {
    name  = "tcp-keepalive"
    value = "60"
  }

  tags = merge(local.common_tags, {
    Name = "${local.name_prefix}-redis-params"
  })
}

# ElastiCache Redis Cluster
resource "aws_elasticache_replication_group" "main" {
  replication_group_id       = "${local.name_prefix}-redis"
  description                = "Redis cluster for RetirementAdvisorPro caching and Celery"

  # Node configuration
  node_type               = var.redis_node_type
  port                    = 6379
  parameter_group_name    = aws_elasticache_parameter_group.main.name

  # Cluster configuration
  num_cache_clusters      = var.redis_num_cache_nodes
  
  # Network configuration
  subnet_group_name       = aws_elasticache_subnet_group.main.name
  security_group_ids      = [aws_security_group.elasticache.id]

  # Backup and maintenance
  snapshot_retention_limit = 1  # Keep 1 backup for cost optimization
  snapshot_window         = "03:00-05:00"  # UTC
  maintenance_window      = "sun:05:00-sun:06:00"  # UTC
  
  # Auto failover for multi-node setups (disabled for single node)
  automatic_failover_enabled = var.redis_num_cache_nodes > 1
  
  # Multi-AZ for high availability (additional cost)
  multi_az_enabled = var.redis_num_cache_nodes > 1 && var.environment == "prod"

  # Encryption
  at_rest_encryption_enabled = true
  transit_encryption_enabled = false  # Disabled for simplicity, enable for production

  # Engine version
  engine_version = "7.0"
  
  # Auto minor version upgrade
  auto_minor_version_upgrade = true

  # Notification topic
  notification_topic_arn = var.notification_email != "" ? aws_sns_topic.alerts[0].arn : null

  tags = merge(local.common_tags, {
    Name = "${local.name_prefix}-redis"
  })

  lifecycle {
    ignore_changes = [num_cache_clusters]
  }
}

# CloudWatch alarms for Redis
resource "aws_cloudwatch_metric_alarm" "redis_cpu_high" {
  alarm_name          = "${local.name_prefix}-redis-cpu-high"
  comparison_operator = "GreaterThanThreshold"
  evaluation_periods  = "2"
  metric_name         = "CPUUtilization"
  namespace           = "AWS/ElastiCache"
  period              = "300"
  statistic           = "Average"
  threshold           = "75"
  alarm_description   = "This metric monitors ElastiCache CPU utilization"

  dimensions = {
    CacheClusterId = aws_elasticache_replication_group.main.id
  }

  alarm_actions = var.notification_email != "" ? [aws_sns_topic.alerts[0].arn] : []

  tags = merge(local.common_tags, {
    Name = "${local.name_prefix}-redis-cpu-high"
  })
}

resource "aws_cloudwatch_metric_alarm" "redis_memory_high" {
  alarm_name          = "${local.name_prefix}-redis-memory-high"
  comparison_operator = "GreaterThanThreshold"
  evaluation_periods  = "2"
  metric_name         = "DatabaseMemoryUsagePercentage"
  namespace           = "AWS/ElastiCache"
  period              = "300"
  statistic           = "Average"
  threshold           = "80"
  alarm_description   = "This metric monitors ElastiCache memory usage"

  dimensions = {
    CacheClusterId = aws_elasticache_replication_group.main.id
  }

  alarm_actions = var.notification_email != "" ? [aws_sns_topic.alerts[0].arn] : []

  tags = merge(local.common_tags, {
    Name = "${local.name_prefix}-redis-memory-high"
  })
}

resource "aws_cloudwatch_metric_alarm" "redis_connections_high" {
  alarm_name          = "${local.name_prefix}-redis-connections-high"
  comparison_operator = "GreaterThanThreshold"
  evaluation_periods  = "2"
  metric_name         = "CurrConnections"
  namespace           = "AWS/ElastiCache"
  period              = "300"
  statistic           = "Average"
  threshold           = "50"
  alarm_description   = "This metric monitors ElastiCache connection count"

  dimensions = {
    CacheClusterId = aws_elasticache_replication_group.main.id
  }

  alarm_actions = var.notification_email != "" ? [aws_sns_topic.alerts[0].arn] : []

  tags = merge(local.common_tags, {
    Name = "${local.name_prefix}-redis-connections-high"
  })
}

# Alternative: Redis container in ECS (cost comparison)
# If you prefer running Redis as a container instead of ElastiCache:
# 
# Pros of ElastiCache:
# - Managed service with automatic backups
# - Built-in monitoring and alerting
# - Automatic failover and Multi-AZ support
# - Security patches managed by AWS
# - Better performance and reliability
# 
# Pros of containerized Redis:
# - Lower cost (~$8/month vs ~$13/month for cache.t3.micro)
# - More control over configuration
# - Easier development environment parity
# - Can use ECS task CPU/memory
# 
# Current cost estimate:
# - ElastiCache t3.micro: ~$13/month
# - Container Redis on Fargate: ~$8/month (0.25 vCPU, 0.5GB memory)
# 
# Recommendation: Use ElastiCache for production for reliability,
# containerized Redis for development/staging for cost savings.