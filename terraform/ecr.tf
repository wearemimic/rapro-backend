# ECR repositories for RetirementAdvisorPro container images
# Separate repositories for frontend, backend, and Celery

# ECR Repository for Frontend (Vue.js)
resource "aws_ecr_repository" "frontend" {
  name                 = "${local.name_prefix}-frontend"
  image_tag_mutability = "MUTABLE"

  image_scanning_configuration {
    scan_on_push = true
  }

  encryption_configuration {
    encryption_type = "AES256"
  }

  tags = merge(local.common_tags, {
    Name = "${local.name_prefix}-frontend"
  })
}

# ECR Repository for Backend (Django)
resource "aws_ecr_repository" "backend" {
  name                 = "${local.name_prefix}-backend"
  image_tag_mutability = "MUTABLE"

  image_scanning_configuration {
    scan_on_push = true
  }

  encryption_configuration {
    encryption_type = "AES256"
  }

  tags = merge(local.common_tags, {
    Name = "${local.name_prefix}-backend"
  })
}

# ECR Lifecycle Policies to manage image retention and costs

# Frontend lifecycle policy - keep last 10 images
resource "aws_ecr_lifecycle_policy" "frontend" {
  repository = aws_ecr_repository.frontend.name

  policy = jsonencode({
    rules = [
      {
        rulePriority = 1
        description  = "Keep last 10 production images"
        selection = {
          tagStatus     = "tagged"
          tagPrefixList = ["prod", "latest", "v"]
          countType     = "imageCountMoreThan"
          countNumber   = 10
        }
        action = {
          type = "expire"
        }
      },
      {
        rulePriority = 2
        description  = "Keep last 5 development images"
        selection = {
          tagStatus     = "tagged"
          tagPrefixList = ["dev", "staging", "feature"]
          countType     = "imageCountMoreThan"
          countNumber   = 5
        }
        action = {
          type = "expire"
        }
      },
      {
        rulePriority = 3
        description  = "Delete untagged images older than 1 day"
        selection = {
          tagStatus   = "untagged"
          countType   = "sinceImagePushed"
          countUnit   = "days"
          countNumber = 1
        }
        action = {
          type = "expire"
        }
      }
    ]
  })
}

# Backend lifecycle policy - keep last 10 images
resource "aws_ecr_lifecycle_policy" "backend" {
  repository = aws_ecr_repository.backend.name

  policy = jsonencode({
    rules = [
      {
        rulePriority = 1
        description  = "Keep last 10 production images"
        selection = {
          tagStatus     = "tagged"
          tagPrefixList = ["prod", "latest", "v"]
          countType     = "imageCountMoreThan"
          countNumber   = 10
        }
        action = {
          type = "expire"
        }
      },
      {
        rulePriority = 2
        description  = "Keep last 5 development images"
        selection = {
          tagStatus     = "tagged"
          tagPrefixList = ["dev", "staging", "feature"]
          countType     = "imageCountMoreThan"
          countNumber   = 5
        }
        action = {
          type = "expire"
        }
      },
      {
        rulePriority = 3
        description  = "Delete untagged images older than 1 day"
        selection = {
          tagStatus   = "untagged"
          countType   = "sinceImagePushed"
          countUnit   = "days"
          countNumber = 1
        }
        action = {
          type = "expire"
        }
      }
    ]
  })
}

# IAM policy for ECR access
data "aws_iam_policy_document" "ecr_policy" {
  statement {
    effect = "Allow"
    principals {
      type        = "AWS"
      identifiers = ["arn:aws:iam::${data.aws_caller_identity.current.account_id}:root"]
    }
    actions = [
      "ecr:GetDownloadUrlForLayer",
      "ecr:BatchGetImage",
      "ecr:BatchCheckLayerAvailability",
      "ecr:PutImage",
      "ecr:InitiateLayerUpload",
      "ecr:UploadLayerPart",
      "ecr:CompleteLayerUpload",
      "ecr:DescribeRepositories",
      "ecr:GetRepositoryPolicy",
      "ecr:ListImages",
      "ecr:DescribeImages",
      "ecr:BatchDeleteImage",
      "ecr:GetLifecyclePolicy",
      "ecr:PutLifecyclePolicy",
      "ecr:DeleteLifecyclePolicy",
      "ecr:GetLifecyclePolicyPreview",
      "ecr:StartLifecyclePolicyPreview"
    ]
  }
}

# Apply policy to repositories
resource "aws_ecr_repository_policy" "frontend" {
  repository = aws_ecr_repository.frontend.name
  policy     = data.aws_iam_policy_document.ecr_policy.json
}

resource "aws_ecr_repository_policy" "backend" {
  repository = aws_ecr_repository.backend.name
  policy     = data.aws_iam_policy_document.ecr_policy.json
}

# CloudWatch alarms for ECR repository metrics
resource "aws_cloudwatch_metric_alarm" "ecr_frontend_repository_size" {
  count = var.notification_email != "" ? 1 : 0

  alarm_name          = "${local.name_prefix}-ecr-frontend-size"
  comparison_operator = "GreaterThanThreshold"
  evaluation_periods  = "1"
  metric_name         = "RepositorySizeInBytes"
  namespace           = "AWS/ECR"
  period              = "86400"  # Daily
  statistic           = "Maximum"
  threshold           = "2147483648"  # 2GB in bytes
  alarm_description   = "Frontend ECR repository size exceeds 2GB"

  dimensions = {
    RepositoryName = aws_ecr_repository.frontend.name
  }

  alarm_actions = [aws_sns_topic.alerts[0].arn]

  tags = merge(local.common_tags, {
    Name = "${local.name_prefix}-ecr-frontend-size"
  })
}

resource "aws_cloudwatch_metric_alarm" "ecr_backend_repository_size" {
  count = var.notification_email != "" ? 1 : 0

  alarm_name          = "${local.name_prefix}-ecr-backend-size"
  comparison_operator = "GreaterThanThreshold"
  evaluation_periods  = "1"
  metric_name         = "RepositorySizeInBytes"
  namespace           = "AWS/ECR"
  period              = "86400"  # Daily
  statistic           = "Maximum"
  threshold           = "2147483648"  # 2GB in bytes
  alarm_description   = "Backend ECR repository size exceeds 2GB"

  dimensions = {
    RepositoryName = aws_ecr_repository.backend.name
  }

  alarm_actions = [aws_sns_topic.alerts[0].arn]

  tags = merge(local.common_tags, {
    Name = "${local.name_prefix}-ecr-backend-size"
  })
}