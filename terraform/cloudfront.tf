# CloudFront CDN for RetirementAdvisorPro frontend
# Provides global content delivery and caching for better performance

# Origin Access Identity for S3
resource "aws_cloudfront_origin_access_identity" "frontend" {
  count = var.enable_cloudfront ? 1 : 0

  comment = "OAI for ${local.name_prefix} static assets"
}

# S3 bucket policy to allow CloudFront access
resource "aws_s3_bucket_policy" "static_assets_cloudfront" {
  count = var.enable_cloudfront ? 1 : 0

  bucket = aws_s3_bucket.static_assets.id

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Sid    = "AllowCloudFrontAccess"
        Effect = "Allow"
        Principal = {
          AWS = aws_cloudfront_origin_access_identity.frontend[0].iam_arn
        }
        Action   = "s3:GetObject"
        Resource = "${aws_s3_bucket.static_assets.arn}/*"
      },
      {
        Sid    = "AllowCloudFrontListBucket"
        Effect = "Allow"
        Principal = {
          AWS = aws_cloudfront_origin_access_identity.frontend[0].iam_arn
        }
        Action   = "s3:ListBucket"
        Resource = aws_s3_bucket.static_assets.arn
      }
    ]
  })
}

# CloudFront Distribution
resource "aws_cloudfront_distribution" "frontend" {
  count = var.enable_cloudfront ? 1 : 0

  # S3 Origin for static assets
  origin {
    domain_name = aws_s3_bucket.static_assets.bucket_regional_domain_name
    origin_id   = "S3-${aws_s3_bucket.static_assets.id}"

    s3_origin_config {
      origin_access_identity = aws_cloudfront_origin_access_identity.frontend[0].cloudfront_access_identity_path
    }
  }

  # ALB Origin for API requests
  origin {
    domain_name = aws_lb.main.dns_name
    origin_id   = "ALB-${aws_lb.main.name}"

    custom_origin_config {
      http_port              = 80
      https_port             = 443
      origin_protocol_policy = var.certificate_arn != "" ? "https-only" : "http-only"
      origin_ssl_protocols   = ["TLSv1.2"]
    }
  }

  enabled             = true
  is_ipv6_enabled     = true
  comment             = "CloudFront distribution for ${local.name_prefix}"
  default_root_object = "index.html"

  # Aliases (custom domains)
  aliases = var.domain_name != "" ? [var.domain_name, "www.${var.domain_name}"] : []

  # Default cache behavior for frontend assets
  default_cache_behavior {
    allowed_methods  = ["DELETE", "GET", "HEAD", "OPTIONS", "PATCH", "POST", "PUT"]
    cached_methods   = ["GET", "HEAD"]
    target_origin_id = "S3-${aws_s3_bucket.static_assets.id}"
    compress         = true

    forwarded_values {
      query_string = false
      headers      = ["Origin", "Access-Control-Request-Headers", "Access-Control-Request-Method"]

      cookies {
        forward = "none"
      }
    }

    viewer_protocol_policy = var.certificate_arn != "" ? "redirect-to-https" : "allow-all"
    min_ttl                = 0
    default_ttl            = 3600    # 1 hour
    max_ttl                = 86400   # 24 hours

    # Enable response headers policy for security
    response_headers_policy_id = aws_cloudfront_response_headers_policy.security[0].id
  }

  # Cache behavior for API requests (no caching)
  ordered_cache_behavior {
    path_pattern     = "/api/*"
    allowed_methods  = ["DELETE", "GET", "HEAD", "OPTIONS", "PATCH", "POST", "PUT"]
    cached_methods   = ["GET", "HEAD", "OPTIONS"]
    target_origin_id = "ALB-${aws_lb.main.name}"
    compress         = true

    forwarded_values {
      query_string = true
      headers      = ["*"]

      cookies {
        forward = "all"
      }
    }

    viewer_protocol_policy = var.certificate_arn != "" ? "redirect-to-https" : "allow-all"
    min_ttl                = 0
    default_ttl            = 0
    max_ttl                = 0
  }

  # Cache behavior for admin panel (no caching)
  ordered_cache_behavior {
    path_pattern     = "/admin/*"
    allowed_methods  = ["DELETE", "GET", "HEAD", "OPTIONS", "PATCH", "POST", "PUT"]
    cached_methods   = ["GET", "HEAD", "OPTIONS"]
    target_origin_id = "ALB-${aws_lb.main.name}"
    compress         = true

    forwarded_values {
      query_string = true
      headers      = ["*"]

      cookies {
        forward = "all"
      }
    }

    viewer_protocol_policy = var.certificate_arn != "" ? "redirect-to-https" : "allow-all"
    min_ttl                = 0
    default_ttl            = 0
    max_ttl                = 0
  }

  # Cache behavior for auth endpoints (no caching)
  ordered_cache_behavior {
    path_pattern     = "/auth/*"
    allowed_methods  = ["DELETE", "GET", "HEAD", "OPTIONS", "PATCH", "POST", "PUT"]
    cached_methods   = ["GET", "HEAD", "OPTIONS"]
    target_origin_id = "ALB-${aws_lb.main.name}"
    compress         = true

    forwarded_values {
      query_string = true
      headers      = ["*"]

      cookies {
        forward = "all"
      }
    }

    viewer_protocol_policy = var.certificate_arn != "" ? "redirect-to-https" : "allow-all"
    min_ttl                = 0
    default_ttl            = 0
    max_ttl                = 0
  }

  # Cache behavior for media files (longer caching)
  ordered_cache_behavior {
    path_pattern     = "/media/*"
    allowed_methods  = ["GET", "HEAD", "OPTIONS"]
    cached_methods   = ["GET", "HEAD"]
    target_origin_id = "ALB-${aws_lb.main.name}"
    compress         = true

    forwarded_values {
      query_string = false
      headers      = ["Origin", "Access-Control-Request-Headers", "Access-Control-Request-Method"]

      cookies {
        forward = "none"
      }
    }

    viewer_protocol_policy = var.certificate_arn != "" ? "redirect-to-https" : "allow-all"
    min_ttl                = 0
    default_ttl            = 86400   # 24 hours
    max_ttl                = 31536000 # 365 days
  }

  # Cache behavior for static files (longest caching)
  ordered_cache_behavior {
    path_pattern     = "/static/*"
    allowed_methods  = ["GET", "HEAD", "OPTIONS"]
    cached_methods   = ["GET", "HEAD"]
    target_origin_id = "ALB-${aws_lb.main.name}"
    compress         = true

    forwarded_values {
      query_string = false
      headers      = ["Origin", "Access-Control-Request-Headers", "Access-Control-Request-Method"]

      cookies {
        forward = "none"
      }
    }

    viewer_protocol_policy = var.certificate_arn != "" ? "redirect-to-https" : "allow-all"
    min_ttl                = 0
    default_ttl            = 86400   # 24 hours
    max_ttl                = 31536000 # 365 days
  }

  # Price class for cost optimization
  price_class = "PriceClass_100"  # US, Canada, Europe (cheapest option)

  # Geographic restrictions
  restrictions {
    geo_restriction {
      restriction_type = "none"
    }
  }

  # SSL Certificate
  viewer_certificate {
    cloudfront_default_certificate = var.certificate_arn == ""
    acm_certificate_arn           = var.certificate_arn != "" ? var.certificate_arn : null
    ssl_support_method            = var.certificate_arn != "" ? "sni-only" : null
    minimum_protocol_version      = var.certificate_arn != "" ? "TLSv1.2_2021" : null
  }

  # Custom error pages for SPA routing
  custom_error_response {
    error_code            = 403
    error_caching_min_ttl = 10
    response_code         = 200
    response_page_path    = "/index.html"
  }

  custom_error_response {
    error_code            = 404
    error_caching_min_ttl = 10
    response_code         = 200
    response_page_path    = "/index.html"
  }

  # WAF Web ACL
  web_acl_id = var.enable_waf && length(aws_wafv2_web_acl.main) > 0 ? aws_wafv2_web_acl.main[0].arn : null

  tags = merge(local.common_tags, {
    Name = "${local.name_prefix}-cloudfront"
  })
}

# Response Headers Policy for security
resource "aws_cloudfront_response_headers_policy" "security" {
  count = var.enable_cloudfront ? 1 : 0

  name = "${local.name_prefix}-security-headers"

  security_headers_config {
    strict_transport_security {
      access_control_max_age_sec = 31536000
      include_subdomains         = true
      override                   = false
    }

    content_type_options {
      override = false
    }

    frame_options {
      frame_option = "DENY"
      override     = false
    }

    referrer_policy {
      referrer_policy = "strict-origin-when-cross-origin"
      override        = false
    }
  }

  cors_config {
    access_control_allow_credentials = false

    access_control_allow_headers {
      items = ["*"]
    }

    access_control_allow_methods {
      items = ["ALL"]
    }

    access_control_allow_origins {
      items = ["*"]
    }

    origin_override = false
  }
}

# CloudWatch alarms for CloudFront
resource "aws_cloudwatch_metric_alarm" "cloudfront_error_rate" {
  count = var.enable_cloudfront && var.notification_email != "" ? 1 : 0

  alarm_name          = "${local.name_prefix}-cloudfront-error-rate"
  comparison_operator = "GreaterThanThreshold"
  evaluation_periods  = "2"
  metric_name         = "4xxErrorRate"
  namespace           = "AWS/CloudFront"
  period              = "300"
  statistic           = "Average"
  threshold           = "5"
  alarm_description   = "CloudFront 4xx error rate is too high"

  dimensions = {
    DistributionId = aws_cloudfront_distribution.frontend[0].id
  }

  alarm_actions = [aws_sns_topic.alerts[0].arn]

  tags = merge(local.common_tags, {
    Name = "${local.name_prefix}-cloudfront-error-rate"
  })
}

resource "aws_cloudfront_monitoring_subscription" "frontend" {
  count = var.enable_cloudfront && var.enable_detailed_monitoring ? 1 : 0

  distribution_id = aws_cloudfront_distribution.frontend[0].id

  monitoring_subscription {
    realtime_metrics_subscription_config {
      realtime_metrics_subscription_status = "Enabled"
    }
  }
}

# Invalidation for cache busting during deployments
# This would be triggered by the CI/CD pipeline
resource "aws_cloudfront_cache_policy" "frontend_optimized" {
  count = var.enable_cloudfront ? 1 : 0

  name        = "${local.name_prefix}-frontend-cache-policy"
  comment     = "Optimized caching policy for frontend assets"
  default_ttl = 3600
  max_ttl     = 31536000
  min_ttl     = 0

  parameters_in_cache_key_and_forwarded_to_origin {
    enable_accept_encoding_gzip   = true
    enable_accept_encoding_brotli = true

    query_strings_config {
      query_string_behavior = "none"
    }

    headers_config {
      header_behavior = "whitelist"
      headers {
        items = ["Origin", "Access-Control-Request-Headers", "Access-Control-Request-Method"]
      }
    }

    cookies_config {
      cookie_behavior = "none"
    }
  }
}