# CodePipeline for CI/CD of RetirementAdvisorPro
# Automatically builds and deploys from GitHub main branch

# CodeBuild Service Role
resource "aws_iam_role" "codebuild_role" {
  name = "${local.name_prefix}-codebuild-role"

  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Action = "sts:AssumeRole"
        Effect = "Allow"
        Principal = {
          Service = "codebuild.amazonaws.com"
        }
      }
    ]
  })

  tags = merge(local.common_tags, {
    Name = "${local.name_prefix}-codebuild-role"
  })
}

# CodeBuild Policy
resource "aws_iam_role_policy" "codebuild_policy" {
  role = aws_iam_role.codebuild_role.name

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Effect = "Allow"
        Action = [
          "logs:CreateLogGroup",
          "logs:CreateLogStream",
          "logs:PutLogEvents"
        ]
        Resource = [
          "arn:aws:logs:*:*:*",
          "arn:aws:logs:${var.aws_region}:${data.aws_caller_identity.current.account_id}:log-group:/aws/codebuild/${local.name_prefix}-*",
          "arn:aws:logs:${var.aws_region}:${data.aws_caller_identity.current.account_id}:log-group:/aws/codebuild/${local.name_prefix}-*:*"
        ]
      },
      {
        Effect = "Allow"
        Action = [
          "ecr:BatchCheckLayerAvailability",
          "ecr:GetDownloadUrlForLayer",
          "ecr:BatchGetImage",
          "ecr:GetAuthorizationToken"
        ]
        Resource = "*"
      },
      {
        Effect = "Allow"
        Action = [
          "ecr:InitiateLayerUpload",
          "ecr:UploadLayerPart",
          "ecr:CompleteLayerUpload",
          "ecr:PutImage"
        ]
        Resource = [
          aws_ecr_repository.frontend.arn,
          aws_ecr_repository.backend.arn
        ]
      },
      {
        Effect = "Allow"
        Action = [
          "s3:GetBucketAcl",
          "s3:GetBucketLocation",
          "s3:GetObject",
          "s3:GetObjectVersion",
          "s3:PutObject",
          "s3:DeleteObject"
        ]
        Resource = [
          aws_s3_bucket.codepipeline_artifacts.arn,
          "${aws_s3_bucket.codepipeline_artifacts.arn}/*",
          aws_s3_bucket.static_assets.arn,
          "${aws_s3_bucket.static_assets.arn}/*"
        ]
      },
      {
        Effect = "Allow"
        Action = [
          "ecs:DescribeTaskDefinition",
          "ecs:RegisterTaskDefinition"
        ]
        Resource = "*"
      },
      {
        Effect = "Allow"
        Action = [
          "ecs:UpdateService",
          "ecs:DescribeServices"
        ]
        Resource = [
          aws_ecs_service.frontend.id,
          aws_ecs_service.backend.id,
          aws_ecs_service.celery_worker.id,
          aws_ecs_service.celery_beat.id
        ]
      },
      {
        Effect = "Allow"
        Action = [
          "iam:PassRole"
        ]
        Resource = [
          aws_iam_role.ecs_task_execution_role.arn,
          aws_iam_role.ecs_task_role.arn
        ]
      },
      {
        Effect = "Allow"
        Action = [
          "ssm:GetParameter",
          "ssm:GetParameters"
        ]
        Resource = "arn:aws:ssm:${var.aws_region}:${data.aws_caller_identity.current.account_id}:parameter/${local.name_prefix}/*"
      }
    ]
  })
}

# CodeBuild VPC Configuration Policy
resource "aws_iam_role_policy" "codebuild_vpc_policy" {
  role = aws_iam_role.codebuild_role.name

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Effect = "Allow"
        Action = [
          "ec2:CreateNetworkInterface",
          "ec2:DescribeDhcpOptions",
          "ec2:DescribeNetworkInterfaces",
          "ec2:DeleteNetworkInterface",
          "ec2:DescribeSubnets",
          "ec2:DescribeSecurityGroups",
          "ec2:DescribeVpcs"
        ]
        Resource = "*"
      },
      {
        Effect = "Allow"
        Action = [
          "ec2:CreateNetworkInterfacePermission"
        ]
        Resource = "arn:aws:ec2:${var.aws_region}:${data.aws_caller_identity.current.account_id}:network-interface/*"
        Condition = {
          StringEquals = {
            "ec2:Subnet" = [for subnet in aws_subnet.private : subnet.arn]
            "ec2:AuthorizedService" = "codebuild.amazonaws.com"
          }
        }
      }
    ]
  })
}

# CloudFront invalidation policy (if CloudFront is enabled)
resource "aws_iam_role_policy" "codebuild_cloudfront_policy" {
  count = var.enable_cloudfront ? 1 : 0
  role  = aws_iam_role.codebuild_role.name

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Effect = "Allow"
        Action = [
          "cloudfront:CreateInvalidation"
        ]
        Resource = aws_cloudfront_distribution.frontend[0].arn
      }
    ]
  })
}

# CodeBuild Projects

# Frontend Build Project
resource "aws_codebuild_project" "frontend" {
  name          = "${local.name_prefix}-frontend-build"
  description   = "Build project for RetirementAdvisorPro frontend"
  service_role  = aws_iam_role.codebuild_role.arn

  artifacts {
    type = "CODEPIPELINE"
  }

  environment {
    compute_type                = "BUILD_GENERAL1_SMALL"  # Cost optimization
    image                      = "aws/codebuild/amazonlinux2-x86_64-standard:5.0"
    type                       = "LINUX_CONTAINER"
    image_pull_credentials_type = "CODEBUILD"
    privileged_mode            = true  # Required for Docker builds

    environment_variable {
      name  = "AWS_DEFAULT_REGION"
      value = var.aws_region
    }

    environment_variable {
      name  = "AWS_ACCOUNT_ID"
      value = data.aws_caller_identity.current.account_id
    }

    environment_variable {
      name  = "IMAGE_REPO_NAME"
      value = aws_ecr_repository.frontend.name
    }

    environment_variable {
      name  = "IMAGE_TAG"
      value = "latest"
    }

    environment_variable {
      name  = "STATIC_BUCKET"
      value = aws_s3_bucket.static_assets.id
    }

    # Vite Environment Variables for Build Time
    environment_variable {
      name  = "VITE_AUTH0_DOMAIN"
      value = var.auth0_domain
    }

    environment_variable {
      name  = "VITE_AUTH0_CLIENT_ID"
      value = var.auth0_client_id
    }

    environment_variable {
      name  = "VITE_AUTH0_AUDIENCE"
      value = var.auth0_audience
    }

    environment_variable {
      name  = "VITE_STRIPE_PUBLIC_KEY"
      value = var.stripe_public_key
    }
    
    # For production builds, use production URLs
    environment_variable {
      name  = "VITE_API_BASE_URL"
      value = "http://app.retirementadvisorpro.com"
    }
    
    environment_variable {
      name  = "VITE_API_URL"
      value = "http://app.retirementadvisorpro.com/api"
    }
    
    environment_variable {
      name  = "VITE_FRONTEND_URL"
      value = "http://app.retirementadvisorpro.com"
    }

    dynamic "environment_variable" {
      for_each = var.enable_cloudfront ? [1] : []
      content {
        name  = "CLOUDFRONT_DISTRIBUTION_ID"
        value = aws_cloudfront_distribution.frontend[0].id
      }
    }
  }

  source {
    type = "CODEPIPELINE"
    buildspec = yamlencode({
      version = "0.2"
      phases = {
        pre_build = {
          commands = [
            "echo Logging in to Amazon ECR...",
            "aws ecr get-login-password --region $AWS_DEFAULT_REGION | docker login --username AWS --password-stdin $AWS_ACCOUNT_ID.dkr.ecr.$AWS_DEFAULT_REGION.amazonaws.com",
            "echo Pre-build started on `date`",
            "echo Installing dependencies...",
            "cd frontend",
            "npm install"
          ]
        }
        build = {
          commands = [
            "echo Build started on `date`",
            "echo Building the Vue.js application...",
            "echo Current directory: $(pwd)",
            "echo Node version: $(node --version)",
            "echo NPM version: $(npm --version)",
            "echo Running npm run build...",
            "npm run build",
            "echo Building Docker image for frontend...",
            "cd $CODEBUILD_SRC_DIR",
            "echo Current directory after cd to CODEBUILD_SRC_DIR: $(pwd)",
            "ls -la",
            "echo Checking docker directory...",
            "ls -la docker/",
            "docker build -f docker/Dockerfile.frontend.prod -t $IMAGE_REPO_NAME:$IMAGE_TAG --build-arg VITE_API_BASE_URL=$VITE_API_BASE_URL --build-arg VITE_API_URL=$VITE_API_URL --build-arg VITE_FRONTEND_URL=$VITE_FRONTEND_URL .",
            "docker tag $IMAGE_REPO_NAME:$IMAGE_TAG $AWS_ACCOUNT_ID.dkr.ecr.$AWS_DEFAULT_REGION.amazonaws.com/$IMAGE_REPO_NAME:$IMAGE_TAG"
          ]
        }
        post_build = {
          commands = [
            "echo Build completed on `date`",
            "echo Pushing Docker image to ECR...",
            "docker push $AWS_ACCOUNT_ID.dkr.ecr.$AWS_DEFAULT_REGION.amazonaws.com/$IMAGE_REPO_NAME:$IMAGE_TAG",
            "printf '[{\"name\":\"frontend\",\"imageUri\":\"%s\"}]' $AWS_ACCOUNT_ID.dkr.ecr.$AWS_DEFAULT_REGION.amazonaws.com/$IMAGE_REPO_NAME:$IMAGE_TAG > imagedefinitions.json",
            "cat imagedefinitions.json"
          ]
        }
      }
      artifacts = {
        files = ["imagedefinitions.json"]
        name = "frontend-build-$(date +%Y-%m-%d)"
      }
    })
  }

  vpc_config {
    vpc_id = aws_vpc.main.id

    subnets = aws_subnet.private[*].id

    security_group_ids = [aws_security_group.codebuild.id]
  }

  tags = merge(local.common_tags, {
    Name = "${local.name_prefix}-frontend-build"
  })
}

# Backend Build Project
resource "aws_codebuild_project" "backend" {
  name          = "${local.name_prefix}-backend-build"
  description   = "Build project for RetirementAdvisorPro backend"
  service_role  = aws_iam_role.codebuild_role.arn

  artifacts {
    type = "CODEPIPELINE"
  }

  environment {
    compute_type                = "BUILD_GENERAL1_SMALL"  # Cost optimization
    image                      = "aws/codebuild/amazonlinux2-x86_64-standard:5.0"
    type                       = "LINUX_CONTAINER"
    image_pull_credentials_type = "CODEBUILD"
    privileged_mode            = true  # Required for Docker builds

    environment_variable {
      name  = "AWS_DEFAULT_REGION"
      value = var.aws_region
    }

    environment_variable {
      name  = "AWS_ACCOUNT_ID"
      value = data.aws_caller_identity.current.account_id
    }

    environment_variable {
      name  = "IMAGE_REPO_NAME"
      value = aws_ecr_repository.backend.name
    }

    environment_variable {
      name  = "IMAGE_TAG"
      value = "latest"
    }

    environment_variable {
      name  = "CLUSTER_NAME"
      value = aws_ecs_cluster.main.name
    }

    environment_variable {
      name  = "FRONTEND_SERVICE_NAME"
      value = aws_ecs_service.frontend.name
    }

    environment_variable {
      name  = "BACKEND_SERVICE_NAME"
      value = aws_ecs_service.backend.name
    }

    environment_variable {
      name  = "CELERY_WORKER_SERVICE_NAME"
      value = aws_ecs_service.celery_worker.name
    }

    environment_variable {
      name  = "CELERY_BEAT_SERVICE_NAME"
      value = aws_ecs_service.celery_beat.name
    }
  }

  source {
    type = "CODEPIPELINE"
    buildspec = yamlencode({
      version = "0.2"
      phases = {
        pre_build = {
          commands = [
            "echo Logging in to Amazon ECR...",
            "aws ecr get-login-password --region $AWS_DEFAULT_REGION | docker login --username AWS --password-stdin $AWS_ACCOUNT_ID.dkr.ecr.$AWS_DEFAULT_REGION.amazonaws.com",
            "echo Pre-build started on `date`"
          ]
        }
        build = {
          commands = [
            "echo Build started on `date`",
            "echo Building Django Docker image...",
            "docker build -f docker/Dockerfile.backend -t $IMAGE_REPO_NAME:$IMAGE_TAG .",
            "docker tag $IMAGE_REPO_NAME:$IMAGE_TAG $AWS_ACCOUNT_ID.dkr.ecr.$AWS_DEFAULT_REGION.amazonaws.com/$IMAGE_REPO_NAME:$IMAGE_TAG"
          ]
        }
        post_build = {
          commands = [
            "echo Build completed on `date`",
            "echo Pushing Docker image to ECR...",
            "docker push $AWS_ACCOUNT_ID.dkr.ecr.$AWS_DEFAULT_REGION.amazonaws.com/$IMAGE_REPO_NAME:$IMAGE_TAG",
            "printf '[{\"name\":\"backend\",\"imageUri\":\"%s\"}]' $AWS_ACCOUNT_ID.dkr.ecr.$AWS_DEFAULT_REGION.amazonaws.com/$IMAGE_REPO_NAME:$IMAGE_TAG > imagedefinitions.json",
            "printf '[{\"name\":\"celery-worker\",\"imageUri\":\"%s\"}]' $AWS_ACCOUNT_ID.dkr.ecr.$AWS_DEFAULT_REGION.amazonaws.com/$IMAGE_REPO_NAME:$IMAGE_TAG > imagedefinitions_celery.json",
            "cat imagedefinitions.json",
            "cat imagedefinitions_celery.json"
          ]
        }
      }
      artifacts = {
        files = ["imagedefinitions.json", "imagedefinitions_celery.json"]
        name = "backend-build-$(date +%Y-%m-%d)"
      }
    })
  }

  vpc_config {
    vpc_id = aws_vpc.main.id

    subnets = aws_subnet.private[*].id

    security_group_ids = [aws_security_group.codebuild.id]
  }

  tags = merge(local.common_tags, {
    Name = "${local.name_prefix}-backend-build"
  })
}

# CodePipeline Service Role
resource "aws_iam_role" "codepipeline_role" {
  name = "${local.name_prefix}-codepipeline-role"

  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Action = "sts:AssumeRole"
        Effect = "Allow"
        Principal = {
          Service = "codepipeline.amazonaws.com"
        }
      }
    ]
  })

  tags = merge(local.common_tags, {
    Name = "${local.name_prefix}-codepipeline-role"
  })
}

# CodePipeline Policy
resource "aws_iam_role_policy" "codepipeline_policy" {
  role = aws_iam_role.codepipeline_role.name

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Effect = "Allow"
        Action = [
          "s3:GetBucketAcl",
          "s3:GetBucketLocation",
          "s3:GetObject",
          "s3:GetObjectVersion",
          "s3:PutObject"
        ]
        Resource = [
          aws_s3_bucket.codepipeline_artifacts.arn,
          "${aws_s3_bucket.codepipeline_artifacts.arn}/*"
        ]
      },
      {
        Effect = "Allow"
        Action = [
          "codebuild:BatchGetBuilds",
          "codebuild:StartBuild"
        ]
        Resource = [
          aws_codebuild_project.frontend.arn,
          aws_codebuild_project.backend.arn,
          aws_codebuild_project.integration_tests.arn,
          aws_codebuild_project.smoke_tests.arn
        ]
      },
      {
        Effect = "Allow"
        Action = [
          "ecs:*"
        ]
        Resource = "*"
      },
      {
        Effect = "Allow"
        Action = [
          "ecr:GetAuthorizationToken",
          "ecr:BatchCheckLayerAvailability",
          "ecr:GetDownloadUrlForLayer",
          "ecr:BatchGetImage"
        ]
        Resource = "*"
      },
      {
        Effect = "Allow"
        Action = [
          "iam:PassRole"
        ]
        Resource = [
          aws_iam_role.ecs_task_execution_role.arn,
          aws_iam_role.ecs_task_role.arn
        ]
      },
      {
        Effect = "Allow"
        Action = [
          "sns:Publish"
        ]
        Resource = aws_sns_topic.pipeline_approval.arn
      }
    ]
  })
}

# GitHub connection (requires manual setup in AWS Console)
# resource "aws_codestar_connection" "github" {
#   name          = "${local.name_prefix}-github-connection"
#   provider_type = "GitHub"

#   tags = merge(local.common_tags, {
#     Name = "${local.name_prefix}-github-connection"
#   })
# }

# CodePipeline
resource "aws_codepipeline" "main" {
  name     = "${local.name_prefix}-pipeline"
  role_arn = aws_iam_role.codepipeline_role.arn

  artifact_store {
    location = aws_s3_bucket.codepipeline_artifacts.bucket
    type     = "S3"

    encryption_key {
      id   = "arn:aws:kms:${var.aws_region}:${data.aws_caller_identity.current.account_id}:alias/aws/s3"
      type = "KMS"
    }
  }

  stage {
    name = "Source"

    action {
      name             = "Source"
      category         = "Source"
      owner            = "ThirdParty"
      provider         = "GitHub"
      version          = "1"
      output_artifacts = ["source_output"]

      configuration = {
        Owner      = var.github_owner
        Repo       = var.github_repo
        Branch     = var.github_branch
        OAuthToken = data.aws_secretsmanager_secret_version.github_token.secret_string
      }
    }
  }

  stage {
    name = "Build"

    action {
      name             = "BuildFrontend"
      category         = "Build"
      owner            = "AWS"
      provider         = "CodeBuild"
      input_artifacts  = ["source_output"]
      output_artifacts = ["frontend_build_output"]
      version          = "1"
      run_order        = 1

      configuration = {
        ProjectName = aws_codebuild_project.frontend.name
      }
    }

    action {
      name             = "BuildBackend"
      category         = "Build"
      owner            = "AWS"
      provider         = "CodeBuild"
      input_artifacts  = ["source_output"]
      output_artifacts = ["backend_build_output"]
      version          = "1"
      run_order        = 2

      configuration = {
        ProjectName = aws_codebuild_project.backend.name
      }
    }
  }

  tags = merge(local.common_tags, {
    Name = "${local.name_prefix}-pipeline"
  })
}

# GitHub Token Secret (must be created manually)
data "aws_secretsmanager_secret" "github_token" {
  name = var.github_token_secret_name
}

data "aws_secretsmanager_secret_version" "github_token" {
  secret_id = data.aws_secretsmanager_secret.github_token.id
}

# CloudWatch alarms for pipeline
resource "aws_cloudwatch_metric_alarm" "pipeline_failed" {
  count = var.notification_email != "" ? 1 : 0

  alarm_name          = "${local.name_prefix}-pipeline-failed"
  comparison_operator = "GreaterThanOrEqualToThreshold"
  evaluation_periods  = "1"
  metric_name         = "PipelineExecutionFailure"
  namespace           = "AWS/CodePipeline"
  period              = "300"
  statistic           = "Sum"
  threshold           = "1"
  alarm_description   = "Pipeline execution failed"

  dimensions = {
    PipelineName = aws_codepipeline.main.name
  }

  alarm_actions = [aws_sns_topic.alerts[0].arn]

  tags = merge(local.common_tags, {
    Name = "${local.name_prefix}-pipeline-failed"
  })
}

# CloudWatch Event Rule for automatic triggering
resource "aws_cloudwatch_event_rule" "pipeline_trigger" {
  name        = "${local.name_prefix}-pipeline-trigger"
  description = "Trigger pipeline on push to main branch"

  event_pattern = jsonencode({
    source      = ["aws.s3"]
    detail_type = ["Object Created"]
    detail = {
      bucket = {
        name = [aws_s3_bucket.codepipeline_artifacts.id]
      }
    }
  })

  tags = merge(local.common_tags, {
    Name = "${local.name_prefix}-pipeline-trigger"
  })
}

resource "aws_cloudwatch_event_target" "pipeline" {
  rule      = aws_cloudwatch_event_rule.pipeline_trigger.name
  target_id = "TriggerPipeline"
  arn       = aws_codepipeline.main.arn
  role_arn  = aws_iam_role.codepipeline_event_role.arn
}

resource "aws_iam_role" "codepipeline_event_role" {
  name = "${local.name_prefix}-codepipeline-event-role"

  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Action = "sts:AssumeRole"
        Effect = "Allow"
        Principal = {
          Service = "events.amazonaws.com"
        }
      }
    ]
  })

  tags = merge(local.common_tags, {
    Name = "${local.name_prefix}-codepipeline-event-role"
  })
}

resource "aws_iam_role_policy" "codepipeline_event_policy" {
  role = aws_iam_role.codepipeline_event_role.name

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Effect = "Allow"
        Action = [
          "codepipeline:StartPipelineExecution"
        ]
        Resource = aws_codepipeline.main.arn
      }
    ]
  })
}