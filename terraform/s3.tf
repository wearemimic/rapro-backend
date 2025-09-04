# S3 buckets for RetirementAdvisorPro
# Includes static assets, media files, and CI/CD artifacts

# S3 bucket for static assets (frontend build artifacts)
resource "aws_s3_bucket" "static_assets" {
  bucket = "${local.name_prefix}-static-assets"

  tags = merge(local.common_tags, {
    Name = "${local.name_prefix}-static-assets"
  })
}

resource "aws_s3_bucket_public_access_block" "static_assets" {
  bucket = aws_s3_bucket.static_assets.id

  block_public_acls       = false
  block_public_policy     = false
  ignore_public_acls      = false
  restrict_public_buckets = false
}

resource "aws_s3_bucket_cors_configuration" "static_assets" {
  bucket = aws_s3_bucket.static_assets.id

  cors_rule {
    allowed_headers = ["*"]
    allowed_methods = ["GET", "HEAD"]
    allowed_origins = ["*"]
    expose_headers  = ["ETag"]
    max_age_seconds = 3000
  }
}

resource "aws_s3_bucket_versioning" "static_assets" {
  bucket = aws_s3_bucket.static_assets.id
  
  versioning_configuration {
    status = "Enabled"
  }
}

# Lifecycle configuration for cost optimization
resource "aws_s3_bucket_lifecycle_configuration" "static_assets" {
  bucket = aws_s3_bucket.static_assets.id

  rule {
    id     = "static_assets_lifecycle"
    status = "Enabled"

    # Apply to all objects
    filter {}

    # Delete old versions after 30 days
    noncurrent_version_expiration {
      noncurrent_days = 30
    }

    # Move to Intelligent Tiering after 30 days
    transition {
      days          = 30
      storage_class = "INTELLIGENT_TIERING"
    }
  }
}

# S3 bucket for media files (user uploads)
resource "aws_s3_bucket" "media_files" {
  bucket = "${local.name_prefix}-media-files"

  tags = merge(local.common_tags, {
    Name = "${local.name_prefix}-media-files"
  })
}

resource "aws_s3_bucket_public_access_block" "media_files" {
  bucket = aws_s3_bucket.media_files.id

  block_public_acls       = true
  block_public_policy     = true
  ignore_public_acls      = true
  restrict_public_buckets = true
}

resource "aws_s3_bucket_server_side_encryption_configuration" "media_files" {
  bucket = aws_s3_bucket.media_files.id

  rule {
    apply_server_side_encryption_by_default {
      sse_algorithm = "AES256"
    }
  }
}

resource "aws_s3_bucket_versioning" "media_files" {
  bucket = aws_s3_bucket.media_files.id
  
  versioning_configuration {
    status = "Enabled"
  }
}

resource "aws_s3_bucket_cors_configuration" "media_files" {
  bucket = aws_s3_bucket.media_files.id

  cors_rule {
    allowed_headers = ["*"]
    allowed_methods = ["GET", "PUT", "POST", "DELETE"]
    allowed_origins = var.domain_name != "" ? ["https://${var.domain_name}", "https://www.${var.domain_name}"] : ["*"]
    expose_headers  = ["ETag"]
    max_age_seconds = 3000
  }
}

# Lifecycle configuration for media files
resource "aws_s3_bucket_lifecycle_configuration" "media_files" {
  bucket = aws_s3_bucket.media_files.id

  rule {
    id     = "media_files_lifecycle"
    status = "Enabled"

    # Apply to all objects
    filter {}

    # Move to Standard-IA after 30 days
    transition {
      days          = 30
      storage_class = "STANDARD_IA"
    }

    # Move to Glacier after 90 days
    transition {
      days          = 90
      storage_class = "GLACIER"
    }

    # Delete old versions after 90 days
    noncurrent_version_expiration {
      noncurrent_days = 90
    }

    # Delete incomplete multipart uploads after 7 days
    abort_incomplete_multipart_upload {
      days_after_initiation = 7
    }
  }
}

# S3 bucket for CodePipeline artifacts
resource "aws_s3_bucket" "codepipeline_artifacts" {
  bucket = "${local.name_prefix}-codepipeline-artifacts"

  tags = merge(local.common_tags, {
    Name = "${local.name_prefix}-codepipeline-artifacts"
  })
}

resource "aws_s3_bucket_public_access_block" "codepipeline_artifacts" {
  bucket = aws_s3_bucket.codepipeline_artifacts.id

  block_public_acls       = true
  block_public_policy     = true
  ignore_public_acls      = true
  restrict_public_buckets = true
}

resource "aws_s3_bucket_server_side_encryption_configuration" "codepipeline_artifacts" {
  bucket = aws_s3_bucket.codepipeline_artifacts.id

  rule {
    apply_server_side_encryption_by_default {
      sse_algorithm = "AES256"
    }
  }
}

resource "aws_s3_bucket_versioning" "codepipeline_artifacts" {
  bucket = aws_s3_bucket.codepipeline_artifacts.id
  
  versioning_configuration {
    status = "Enabled"
  }
}

# Lifecycle configuration for CI/CD artifacts
resource "aws_s3_bucket_lifecycle_configuration" "codepipeline_artifacts" {
  bucket = aws_s3_bucket.codepipeline_artifacts.id

  rule {
    id     = "codepipeline_artifacts_lifecycle"
    status = "Enabled"

    # Apply to all objects
    filter {}

    # Delete artifacts after 30 days (they're rebuilds anyway)
    expiration {
      days = 30
    }

    # Delete old versions after 7 days
    noncurrent_version_expiration {
      noncurrent_days = 7
    }

    # Delete incomplete multipart uploads after 1 day
    abort_incomplete_multipart_upload {
      days_after_initiation = 1
    }
  }
}

# S3 bucket for backups (database exports, logs, etc.)
resource "aws_s3_bucket" "backups" {
  bucket = "${local.name_prefix}-backups"

  tags = merge(local.common_tags, {
    Name = "${local.name_prefix}-backups"
  })
}

resource "aws_s3_bucket_public_access_block" "backups" {
  bucket = aws_s3_bucket.backups.id

  block_public_acls       = true
  block_public_policy     = true
  ignore_public_acls      = true
  restrict_public_buckets = true
}

resource "aws_s3_bucket_server_side_encryption_configuration" "backups" {
  bucket = aws_s3_bucket.backups.id

  rule {
    apply_server_side_encryption_by_default {
      sse_algorithm = "AES256"
    }
  }
}

resource "aws_s3_bucket_versioning" "backups" {
  bucket = aws_s3_bucket.backups.id
  
  versioning_configuration {
    status = "Enabled"
  }
}

# Lifecycle configuration for backups with long-term archival
resource "aws_s3_bucket_lifecycle_configuration" "backups" {
  bucket = aws_s3_bucket.backups.id

  rule {
    id     = "backups_lifecycle"
    status = "Enabled"

    # Apply to all objects
    filter {}

    # Move to Standard-IA after 30 days
    transition {
      days          = 30
      storage_class = "STANDARD_IA"
    }

    # Move to Glacier after 90 days
    transition {
      days          = 90
      storage_class = "GLACIER"
    }

    # Move to Deep Archive after 365 days for long-term retention
    transition {
      days          = 365
      storage_class = "DEEP_ARCHIVE"
    }

    # Keep backups for 7 years (compliance requirement)
    expiration {
      days = 2555  # ~7 years
    }

    # Delete old versions after 30 days
    noncurrent_version_expiration {
      noncurrent_days = 30
    }
  }
}

# IAM policy for ECS tasks to access S3 buckets
data "aws_iam_policy_document" "s3_access" {
  # Static assets - read/write for deployment
  statement {
    effect = "Allow"
    actions = [
      "s3:GetObject",
      "s3:PutObject",
      "s3:DeleteObject",
      "s3:ListBucket"
    ]
    resources = [
      aws_s3_bucket.static_assets.arn,
      "${aws_s3_bucket.static_assets.arn}/*"
    ]
  }

  # Media files - full access for Django
  statement {
    effect = "Allow"
    actions = [
      "s3:GetObject",
      "s3:PutObject",
      "s3:DeleteObject",
      "s3:ListBucket",
      "s3:GetObjectVersion"
    ]
    resources = [
      aws_s3_bucket.media_files.arn,
      "${aws_s3_bucket.media_files.arn}/*"
    ]
  }

  # Backups - write access for application backups
  statement {
    effect = "Allow"
    actions = [
      "s3:PutObject",
      "s3:ListBucket"
    ]
    resources = [
      aws_s3_bucket.backups.arn,
      "${aws_s3_bucket.backups.arn}/*"
    ]
  }
}

# CloudWatch metrics for S3 bucket monitoring
resource "aws_cloudwatch_metric_alarm" "s3_media_files_size" {
  count = var.notification_email != "" ? 1 : 0

  alarm_name          = "${local.name_prefix}-s3-media-files-size"
  comparison_operator = "GreaterThanThreshold"
  evaluation_periods  = "1"
  metric_name         = "BucketSizeBytes"
  namespace           = "AWS/S3"
  period              = "86400"  # Daily
  statistic           = "Average"
  threshold           = "5368709120"  # 5GB in bytes
  alarm_description   = "Media files bucket size exceeds 5GB"

  dimensions = {
    BucketName  = aws_s3_bucket.media_files.id
    StorageType = "StandardStorage"
  }

  alarm_actions = [aws_sns_topic.alerts[0].arn]

  tags = merge(local.common_tags, {
    Name = "${local.name_prefix}-s3-media-files-size"
  })
}