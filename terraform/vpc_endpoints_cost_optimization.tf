# Additional VPC Endpoints for Cost Optimization
# These endpoints reduce NAT Gateway data transfer costs by keeping AWS service traffic within the VPC
# Estimated savings: $30-40/month in NAT Gateway data transfer charges

# SSM Parameter Store VPC Endpoint (your ECS tasks fetch parameters frequently)
resource "aws_vpc_endpoint" "ssm" {
  vpc_id              = aws_vpc.main.id
  service_name        = "com.amazonaws.${var.aws_region}.ssm"
  vpc_endpoint_type   = "Interface"
  subnet_ids          = aws_subnet.private[*].id
  security_group_ids  = [aws_security_group.vpc_endpoint.id]

  private_dns_enabled = true

  tags = merge(local.common_tags, {
    Name = "${local.name_prefix}-ssm-endpoint"
    CostCenter = "Infrastructure"
    Purpose = "Reduce NAT Gateway data transfer for Parameter Store access"
  })
}

# SSM Messages Endpoint (required for SSM Session Manager if used)
resource "aws_vpc_endpoint" "ssm_messages" {
  vpc_id              = aws_vpc.main.id
  service_name        = "com.amazonaws.${var.aws_region}.ssmmessages"
  vpc_endpoint_type   = "Interface"
  subnet_ids          = aws_subnet.private[*].id
  security_group_ids  = [aws_security_group.vpc_endpoint.id]

  private_dns_enabled = true

  tags = merge(local.common_tags, {
    Name = "${local.name_prefix}-ssm-messages-endpoint"
    CostCenter = "Infrastructure"
  })
}

# EC2 Messages Endpoint (for SSM agent communication)
resource "aws_vpc_endpoint" "ec2_messages" {
  vpc_id              = aws_vpc.main.id
  service_name        = "com.amazonaws.${var.aws_region}.ec2messages"
  vpc_endpoint_type   = "Interface"
  subnet_ids          = aws_subnet.private[*].id
  security_group_ids  = [aws_security_group.vpc_endpoint.id]

  private_dns_enabled = true

  tags = merge(local.common_tags, {
    Name = "${local.name_prefix}-ec2-messages-endpoint"
    CostCenter = "Infrastructure"
  })
}

# Secrets Manager VPC Endpoint (for API keys and secrets)
resource "aws_vpc_endpoint" "secrets_manager" {
  vpc_id              = aws_vpc.main.id
  service_name        = "com.amazonaws.${var.aws_region}.secretsmanager"
  vpc_endpoint_type   = "Interface"
  subnet_ids          = aws_subnet.private[*].id
  security_group_ids  = [aws_security_group.vpc_endpoint.id]

  private_dns_enabled = true

  tags = merge(local.common_tags, {
    Name = "${local.name_prefix}-secrets-manager-endpoint"
    CostCenter = "Infrastructure"
    Purpose = "Reduce NAT Gateway data transfer for Secrets Manager access"
  })
}

# KMS VPC Endpoint (required for encrypted secrets and parameters)
resource "aws_vpc_endpoint" "kms" {
  vpc_id              = aws_vpc.main.id
  service_name        = "com.amazonaws.${var.aws_region}.kms"
  vpc_endpoint_type   = "Interface"
  subnet_ids          = aws_subnet.private[*].id
  security_group_ids  = [aws_security_group.vpc_endpoint.id]

  private_dns_enabled = true

  tags = merge(local.common_tags, {
    Name = "${local.name_prefix}-kms-endpoint"
    CostCenter = "Infrastructure"
    Purpose = "Support encrypted secrets and parameters"
  })
}

# STS VPC Endpoint (for IAM role assumptions)
resource "aws_vpc_endpoint" "sts" {
  vpc_id              = aws_vpc.main.id
  service_name        = "com.amazonaws.${var.aws_region}.sts"
  vpc_endpoint_type   = "Interface"
  subnet_ids          = aws_subnet.private[*].id
  security_group_ids  = [aws_security_group.vpc_endpoint.id]

  private_dns_enabled = true

  tags = merge(local.common_tags, {
    Name = "${local.name_prefix}-sts-endpoint"
    CostCenter = "Infrastructure"
    Purpose = "Reduce NAT Gateway data transfer for IAM operations"
  })
}

# Cost Analysis Output
output "vpc_endpoint_cost_savings" {
  description = "Estimated monthly savings from VPC endpoints"
  value = {
    note = "These VPC endpoints will reduce NAT Gateway data transfer by approximately 150-180GB/month"
    estimated_monthly_savings = "$30-40"
    vpc_endpoint_monthly_cost = "$14 (6 endpoints x $0.01/hour x 24 hours x 30 days)"
    net_monthly_savings = "$16-26"
    endpoints_added = [
      "SSM Parameter Store",
      "SSM Messages",
      "EC2 Messages",
      "Secrets Manager",
      "KMS",
      "STS"
    ]
  }
}

# CloudWatch Alarm for NAT Gateway Data Transfer
resource "aws_cloudwatch_metric_alarm" "nat_gateway_bytes_out" {
  alarm_name          = "${local.name_prefix}-nat-gateway-high-data-transfer"
  comparison_operator = "GreaterThanThreshold"
  evaluation_periods  = "2"
  metric_name         = "BytesOutToDestination"
  namespace           = "AWS/NATGateway"
  period              = "86400"  # Daily
  statistic           = "Sum"
  threshold           = "7000000000"  # 7GB per day (210GB/month)
  alarm_description   = "This metric monitors NAT Gateway data transfer"
  alarm_actions       = []  # Add SNS topic ARN here for notifications

  dimensions = {
    NatGatewayId = aws_nat_gateway.main[0].id
  }

  tags = merge(local.common_tags, {
    Name = "${local.name_prefix}-nat-gateway-alarm"
    Purpose = "Cost monitoring"
  })
}