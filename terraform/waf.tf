# AWS WAF for web application protection
# Optional security layer for CloudFront and ALB

# WAFv2 Web ACL
resource "aws_wafv2_web_acl" "main" {
  count = var.enable_waf ? 1 : 0

  name  = "${local.name_prefix}-web-acl"
  scope = "CLOUDFRONT"  # Use "REGIONAL" for ALB

  default_action {
    allow {}
  }

  # AWS Managed Rule Set - Core Rule Set
  rule {
    name     = "AWS-AWSManagedRulesCommonRuleSet"
    priority = 1

    override_action {
      none {}
    }

    statement {
      managed_rule_group_statement {
        name        = "AWSManagedRulesCommonRuleSet"
        vendor_name = "AWS"

        # Override rules that might interfere with legitimate API requests
        rule_action_override {
          name = "SizeRestrictions_BODY"
          action_to_use {
            allow {}
          }
        }
        rule_action_override {
          name = "GenericRFI_BODY"
          action_to_use {
            allow {}
          }
        }
      }
    }

    visibility_config {
      metric_name                = "CommonRuleSetMetric"
      sampled_requests_enabled   = true
      cloudwatch_metrics_enabled = true
    }
  }

  # AWS Managed Rule Set - Known Bad Inputs
  rule {
    name     = "AWS-AWSManagedRulesKnownBadInputsRuleSet"
    priority = 2

    override_action {
      none {}
    }

    statement {
      managed_rule_group_statement {
        name        = "AWSManagedRulesKnownBadInputsRuleSet"
        vendor_name = "AWS"
      }
    }

    visibility_config {
      metric_name                = "KnownBadInputsRuleSetMetric"
      sampled_requests_enabled   = true
      cloudwatch_metrics_enabled = true
    }
  }

  # AWS Managed Rule Set - SQL Injection
  rule {
    name     = "AWS-AWSManagedRulesSQLiRuleSet"
    priority = 3

    override_action {
      none {}
    }

    statement {
      managed_rule_group_statement {
        name        = "AWSManagedRulesSQLiRuleSet"
        vendor_name = "AWS"
      }
    }

    visibility_config {
      metric_name                = "SQLiRuleSetMetric"
      sampled_requests_enabled   = true
      cloudwatch_metrics_enabled = true
    }
  }

  # Rate limiting rule
  rule {
    name     = "RateLimitRule"
    priority = 4

    action {
      block {}
    }

    statement {
      rate_based_statement {
        limit              = 2000  # Requests per 5-minute window
        aggregate_key_type = "IP"

        # Optional: scope to specific paths
        scope_down_statement {
          byte_match_statement {
            search_string = "/api/"
            field_to_match {
              uri_path {}
            }
            text_transformation {
              priority = 0
              type     = "LOWERCASE"
            }
            positional_constraint = "STARTS_WITH"
          }
        }
      }
    }

    visibility_config {
      metric_name                = "RateLimitRuleMetric"
      sampled_requests_enabled   = true
      cloudwatch_metrics_enabled = true
    }
  }

  # Geo-restriction rule (if needed)
  # rule {
  #   name     = "GeoRestrictRule"
  #   priority = 5

  #   action {
  #     block {}
  #   }

  #   statement {
  #     geo_match_statement {
  #       country_codes = ["CN", "RU"]  # Block specific countries
  #     }
  #   }

  #   visibility_config {
  #     metric_name                = "GeoRestrictRuleMetric"
  #     sampled_requests_enabled   = true
  #     cloudwatch_metrics_enabled = true
  #   }
  # }

  # IP reputation rule
  rule {
    name     = "AWS-AWSManagedRulesAmazonIpReputationList"
    priority = 6

    override_action {
      none {}
    }

    statement {
      managed_rule_group_statement {
        name        = "AWSManagedRulesAmazonIpReputationList"
        vendor_name = "AWS"
      }
    }

    visibility_config {
      metric_name                = "IpReputationListMetric"
      sampled_requests_enabled   = true
      cloudwatch_metrics_enabled = true
    }
  }

  # Anonymous IP list
  rule {
    name     = "AWS-AWSManagedRulesAnonymousIpList"
    priority = 7

    override_action {
      none {}
    }

    statement {
      managed_rule_group_statement {
        name        = "AWSManagedRulesAnonymousIpList"
        vendor_name = "AWS"
      }
    }

    visibility_config {
      metric_name                = "AnonymousIpListMetric"
      sampled_requests_enabled   = true
      cloudwatch_metrics_enabled = true
    }
  }

  # Custom rule to protect admin paths
  rule {
    name     = "ProtectAdminPaths"
    priority = 8

    action {
      block {}
    }

    statement {
      and_statement {
        statement {
          byte_match_statement {
            search_string = "/admin"
            field_to_match {
              uri_path {}
            }
            text_transformation {
              priority = 0
              type     = "LOWERCASE"
            }
            positional_constraint = "STARTS_WITH"
          }
        }
        statement {
          not_statement {
            statement {
              ip_set_reference_statement {
                arn = aws_wafv2_ip_set.admin_whitelist[0].arn
              }
            }
          }
        }
      }
    }

    visibility_config {
      metric_name                = "ProtectAdminPathsMetric"
      sampled_requests_enabled   = true
      cloudwatch_metrics_enabled = true
    }
  }

  tags = merge(local.common_tags, {
    Name = "${local.name_prefix}-web-acl"
  })

  visibility_config {
    metric_name                = "RetirementAdvisorProWebACL"
    sampled_requests_enabled   = true
    cloudwatch_metrics_enabled = true
  }
}

# IP Set for admin path whitelist
resource "aws_wafv2_ip_set" "admin_whitelist" {
  count = var.enable_waf ? 1 : 0

  name               = "${local.name_prefix}-admin-whitelist"
  scope              = "CLOUDFRONT"
  ip_address_version = "IPV4"

  # Add your admin IP addresses here
  addresses = [
    "10.0.0.0/8",     # Internal networks
    "172.16.0.0/12",  # Private networks
    "192.168.0.0/16", # Private networks
    # "1.2.3.4/32",   # Add your specific admin IPs
  ]

  tags = merge(local.common_tags, {
    Name = "${local.name_prefix}-admin-whitelist"
  })
}

# CloudWatch alarms for WAF
resource "aws_cloudwatch_metric_alarm" "waf_blocked_requests" {
  count = var.enable_waf && var.notification_email != "" ? 1 : 0

  alarm_name          = "${local.name_prefix}-waf-blocked-requests"
  comparison_operator = "GreaterThanThreshold"
  evaluation_periods  = "2"
  metric_name         = "BlockedRequests"
  namespace           = "AWS/WAFV2"
  period              = "300"
  statistic           = "Sum"
  threshold           = "100"
  alarm_description   = "High number of blocked requests detected"

  dimensions = {
    WebACL = aws_wafv2_web_acl.main[0].name
    Rule   = "ALL"
  }

  alarm_actions = [aws_sns_topic.alerts[0].arn]

  tags = merge(local.common_tags, {
    Name = "${local.name_prefix}-waf-blocked-requests"
  })
}

resource "aws_cloudwatch_metric_alarm" "waf_rate_limit_triggered" {
  count = var.enable_waf && var.notification_email != "" ? 1 : 0

  alarm_name          = "${local.name_prefix}-waf-rate-limit"
  comparison_operator = "GreaterThanThreshold"
  evaluation_periods  = "1"
  metric_name         = "BlockedRequests"
  namespace           = "AWS/WAFV2"
  period              = "300"
  statistic           = "Sum"
  threshold           = "10"
  alarm_description   = "Rate limiting rule triggered"

  dimensions = {
    WebACL = aws_wafv2_web_acl.main[0].name
    Rule   = "RateLimitRule"
  }

  alarm_actions = [aws_sns_topic.alerts[0].arn]

  tags = merge(local.common_tags, {
    Name = "${local.name_prefix}-waf-rate-limit"
  })
}

# WAF Logging Configuration (additional cost)
# resource "aws_wafv2_web_acl_logging_configuration" "main" {
#   count = var.enable_waf && var.enable_detailed_monitoring ? 1 : 0

#   resource_arn            = aws_wafv2_web_acl.main[0].arn
#   log_destination_configs = [aws_cloudwatch_log_group.waf[0].arn]

#   redacted_fields {
#     single_header {
#       name = "authorization"
#     }
#   }

#   redacted_fields {
#     single_header {
#       name = "cookie"
#     }
#   }
# }

# resource "aws_cloudwatch_log_group" "waf" {
#   count = var.enable_waf && var.enable_detailed_monitoring ? 1 : 0

#   name              = "/aws/wafv2/${local.name_prefix}"
#   retention_in_days = var.log_retention_in_days

#   tags = merge(local.common_tags, {
#     Name = "${local.name_prefix}-waf-logs"
#   })
# }