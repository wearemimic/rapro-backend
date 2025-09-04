# Security Groups for RetirementAdvisorPro infrastructure
# Following principle of least privilege for security

# Application Load Balancer Security Group
resource "aws_security_group" "alb" {
  name_prefix = "${local.name_prefix}-alb"
  vpc_id      = aws_vpc.main.id
  description = "Security group for Application Load Balancer"

  # HTTP access from internet
  ingress {
    from_port   = 80
    to_port     = 80
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
    description = "HTTP access from internet"
  }

  # HTTPS access from internet
  ingress {
    from_port   = 443
    to_port     = 443
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
    description = "HTTPS access from internet"
  }

  # All outbound traffic
  egress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
    description = "All outbound traffic"
  }

  tags = merge(local.common_tags, {
    Name = "${local.name_prefix}-alb-sg"
  })

  lifecycle {
    create_before_destroy = true
  }
}

# ECS Tasks Security Group
resource "aws_security_group" "ecs_tasks" {
  name_prefix = "${local.name_prefix}-ecs-tasks"
  vpc_id      = aws_vpc.main.id
  description = "Security group for ECS tasks"

  # Frontend port access from ALB
  ingress {
    from_port       = 3000
    to_port         = 3000
    protocol        = "tcp"
    security_groups = [aws_security_group.alb.id]
    description     = "Frontend port access from ALB"
  }

  # Backend port access from ALB
  ingress {
    from_port       = 8000
    to_port         = 8000
    protocol        = "tcp"
    security_groups = [aws_security_group.alb.id]
    description     = "Backend port access from ALB"
  }

  # Celery Flower port access from ALB (for monitoring)
  ingress {
    from_port       = 5555
    to_port         = 5555
    protocol        = "tcp"
    security_groups = [aws_security_group.alb.id]
    description     = "Celery Flower monitoring access"
  }

  # Inter-container communication
  ingress {
    from_port = 0
    to_port   = 65535
    protocol  = "tcp"
    self      = true
    description = "Inter-container communication"
  }

  # All outbound traffic
  egress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
    description = "All outbound traffic"
  }

  tags = merge(local.common_tags, {
    Name = "${local.name_prefix}-ecs-tasks-sg"
  })

  lifecycle {
    create_before_destroy = true
  }
}

# RDS Security Group
resource "aws_security_group" "rds" {
  name_prefix = "${local.name_prefix}-rds"
  vpc_id      = aws_vpc.main.id
  description = "Security group for RDS PostgreSQL instance"

  # PostgreSQL port access from ECS tasks
  ingress {
    from_port       = 5432
    to_port         = 5432
    protocol        = "tcp"
    security_groups = [aws_security_group.ecs_tasks.id]
    description     = "PostgreSQL access from ECS tasks"
  }

  # Optional: Access from bastion host or specific IP for maintenance
  # ingress {
  #   from_port   = 5432
  #   to_port     = 5432
  #   protocol    = "tcp"
  #   cidr_blocks = ["10.0.0.0/8"]  # Adjust as needed
  #   description = "PostgreSQL access for maintenance"
  # }

  tags = merge(local.common_tags, {
    Name = "${local.name_prefix}-rds-sg"
  })

  lifecycle {
    create_before_destroy = true
  }
}

# ElastiCache Redis Security Group
resource "aws_security_group" "elasticache" {
  name_prefix = "${local.name_prefix}-elasticache"
  vpc_id      = aws_vpc.main.id
  description = "Security group for ElastiCache Redis cluster"

  # Redis port access from ECS tasks
  ingress {
    from_port       = 6379
    to_port         = 6379
    protocol        = "tcp"
    security_groups = [aws_security_group.ecs_tasks.id]
    description     = "Redis access from ECS tasks"
  }

  tags = merge(local.common_tags, {
    Name = "${local.name_prefix}-elasticache-sg"
  })

  lifecycle {
    create_before_destroy = true
  }
}

# CodeBuild Security Group
resource "aws_security_group" "codebuild" {
  name_prefix = "${local.name_prefix}-codebuild"
  vpc_id      = aws_vpc.main.id
  description = "Security group for CodeBuild projects"

  # All outbound traffic for downloading dependencies and pushing images
  egress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
    description = "All outbound traffic"
  }

  tags = merge(local.common_tags, {
    Name = "${local.name_prefix}-codebuild-sg"
  })

  lifecycle {
    create_before_destroy = true
  }
}

# Optional: Bastion Host Security Group (for debugging/maintenance)
resource "aws_security_group" "bastion" {
  count = 0  # Set to 1 if you want to enable bastion host

  name_prefix = "${local.name_prefix}-bastion"
  vpc_id      = aws_vpc.main.id
  description = "Security group for bastion host"

  # SSH access from specific IPs (configure as needed)
  ingress {
    from_port   = 22
    to_port     = 22
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]  # SECURITY: Restrict this to your IP
    description = "SSH access"
  }

  # All outbound traffic
  egress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
    description = "All outbound traffic"
  }

  tags = merge(local.common_tags, {
    Name = "${local.name_prefix}-bastion-sg"
  })

  lifecycle {
    create_before_destroy = true
  }
}