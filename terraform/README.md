# RetirementAdvisorPro AWS Infrastructure

This Terraform configuration deploys a complete, production-ready AWS infrastructure for the RetirementAdvisorPro application. The architecture is cost-optimized and follows AWS best practices for security, scalability, and reliability.

## Architecture Overview

### 🏗️ High-Level Architecture

```
Internet → CloudFront CDN → ALB → ECS Fargate Services
                                     ├── Frontend (Vue.js)
                                     ├── Backend (Django)
                                     ├── Celery Worker
                                     ├── Celery Beat
                                     └── Celery Flower
                                            │
                                            ├── RDS PostgreSQL
                                            ├── ElastiCache Redis
                                            └── S3 Buckets
```

### 💰 Cost-Optimized Design

- **Fargate Spot**: 50-70% savings on compute costs
- **Single NAT Gateway**: $32/month vs $64/month for dual AZ
- **t3.micro instances**: Cost-effective for RDS and Redis
- **Intelligent storage tiering**: Automatic S3 cost optimization
- **Short log retention**: 14 days default to minimize storage costs

### 📊 Estimated Monthly Costs

| Component | Configuration | Estimated Cost |
|-----------|---------------|----------------|
| ECS Fargate (3 services) | 0.25-1 vCPU, 0.5-2GB RAM | $40-80 |
| RDS PostgreSQL | db.t3.micro | $13-15 |
| ElastiCache Redis | cache.t3.micro | $13-15 |
| Application Load Balancer | Standard ALB | $16-20 |
| NAT Gateway | Single gateway | $32-35 |
| S3 Storage | Various buckets | $5-15 |
| CloudFront CDN | Global distribution | $5-20 |
| Data Transfer | Varies by usage | $10-30 |
| **Total Estimated** | | **$150-300/month** |

*Costs vary based on usage patterns and AWS region*

## 🚀 Quick Start

### Prerequisites

1. **AWS CLI** configured with appropriate permissions
2. **Terraform** v1.0+ installed
3. **GitHub personal access token** with repo permissions
4. **Domain name** (optional but recommended)
5. **SSL certificate** in AWS Certificate Manager (optional)

### 1. Clone and Configure

```bash
# Navigate to terraform directory
cd terraform

# Copy and customize variables
cp terraform.tfvars.example terraform.tfvars
```

### 2. Set Required Variables

Edit `terraform.tfvars`:

```hcl
# Required: GitHub configuration
github_owner = "your-github-username"
github_repo  = "retirementadvisorpro"

# Optional: Custom domain
domain_name = "app.yourdomain.com"

# Optional: SSL certificate ARN
certificate_arn = "arn:aws:acm:us-east-1:123456789012:certificate/abcdef..."

# Required: Auth0 configuration
auth0_domain    = "your-tenant.us.auth0.com"
auth0_client_id = "your-auth0-client-id"
auth0_audience  = "https://api.retirementadvisorpro.com"

# Required: Stripe public key
stripe_public_key = "pk_live_or_test_..."
```

### 3. Deploy Infrastructure

```bash
# Initialize Terraform
terraform init

# Review planned changes
terraform plan

# Deploy infrastructure
terraform apply
```

### 4. Configure Secrets

After deployment, set the required secrets in AWS Parameter Store:

```bash
# Auth0 client secret
aws ssm put-parameter \
  --name "/retirementadvisorpro-prod/auth0/client-secret" \
  --value "your-auth0-client-secret" \
  --type "SecureString" \
  --overwrite

# Stripe secret key
aws ssm put-parameter \
  --name "/retirementadvisorpro-prod/stripe/secret-key" \
  --value "your-stripe-secret-key" \
  --type "SecureString" \
  --overwrite

# Stripe price IDs
aws ssm put-parameter \
  --name "/retirementadvisorpro-prod/stripe/monthly-price-id" \
  --value "price_monthly_subscription_id" \
  --type "String" \
  --overwrite

aws ssm put-parameter \
  --name "/retirementadvisorpro-prod/stripe/annual-price-id" \
  --value "price_annual_subscription_id" \
  --type "String" \
  --overwrite
```

### 5. Configure GitHub Token

Create a secret in AWS Secrets Manager for the GitHub token:

```bash
aws secretsmanager create-secret \
  --name "github-token" \
  --description "GitHub personal access token for CodePipeline" \
  --secret-string "your-github-personal-access-token"
```

### 6. DNS Configuration (if using custom domain)

Update your DNS records to point to the load balancer:

```
Type: CNAME
Name: app (or your subdomain)
Value: <load_balancer_dns_name> (from terraform output)
```

## 📁 Infrastructure Components

### Networking (`vpc.tf`)
- **VPC**: Custom VPC with public, private, and database subnets
- **NAT Gateway**: Single gateway for cost optimization
- **VPC Endpoints**: Reduce NAT Gateway usage for AWS services

### Compute (`ecs.tf`, `ecs_services.tf`)
- **ECS Fargate**: Serverless container platform
- **Auto Scaling**: Automatic scaling based on CPU and request metrics
- **Health Checks**: Application-level health monitoring

### Database (`rds.tf`)
- **PostgreSQL 14**: Managed database service
- **Automated Backups**: 7-day retention by default
- **Performance Insights**: Free monitoring included

### Caching (`elasticache.tf`)
- **Redis 7**: In-memory data structure store
- **Persistence**: AOF and RDB snapshot configuration
- **Security**: VPC-isolated with security groups

### Storage (`s3.tf`)
- **Static Assets**: Frontend build artifacts
- **Media Files**: User-uploaded content
- **Backups**: Long-term data archival
- **CI/CD Artifacts**: Pipeline build artifacts

### CDN (`cloudfront.tf`)
- **Global Distribution**: Edge locations worldwide
- **Caching**: Optimized cache behaviors
- **Security Headers**: HTTPS redirect and security policies

### Security (`security_groups.tf`, `waf.tf`)
- **Security Groups**: Principle of least privilege
- **WAF**: Web Application Firewall (optional)
- **SSL/TLS**: Certificate Manager integration

### CI/CD (`codepipeline.tf`, `ecr.tf`)
- **CodePipeline**: Automated deployment pipeline
- **CodeBuild**: Build and test automation
- **ECR**: Container image registry

### Monitoring (`monitoring.tf`)
- **CloudWatch**: Comprehensive monitoring and alerting
- **Custom Dashboards**: Application-specific metrics
- **SNS Alerts**: Email notifications for issues

### Secrets (`parameter_store.tf`)
- **Parameter Store**: Secure configuration management
- **Secrets Manager**: Sensitive data encryption
- **IAM Roles**: Least privilege access

## 🔧 Operational Tasks

### Deployment Commands

```bash
# Force new deployment (without code changes)
aws ecs update-service \
  --cluster retirementadvisorpro-prod-cluster \
  --service retirementadvisorpro-prod-backend \
  --force-new-deployment

# Run database migrations
aws ecs run-task \
  --cluster retirementadvisorpro-prod-cluster \
  --task-definition retirementadvisorpro-prod-backend \
  --overrides '{"containerOverrides":[{"name":"backend","command":["python","manage.py","migrate"]}]}' \
  --network-configuration 'awsvpcConfiguration={subnets=["subnet-xxx"],securityGroups=["sg-xxx"]}' \
  --launch-type FARGATE

# View application logs
aws logs tail /ecs/retirementadvisorpro-prod-backend --follow
```

### Scaling Operations

```bash
# Scale backend service
aws ecs update-service \
  --cluster retirementadvisorpro-prod-cluster \
  --service retirementadvisorpro-prod-backend \
  --desired-count 3

# Scale Celery workers
aws ecs update-service \
  --cluster retirementadvisorpro-prod-cluster \
  --service retirementadvisorpro-prod-celery-worker \
  --desired-count 2
```

### Cache Management

```bash
# Invalidate CloudFront cache
aws cloudfront create-invalidation \
  --distribution-id E1234567890123 \
  --paths "/*"

# Flush Redis cache
aws elasticache reboot-cache-cluster \
  --cache-cluster-id retirementadvisorpro-prod-redis-001
```

## 🔐 Security Considerations

### Access Control
- **IAM Roles**: Service-specific roles with minimal permissions
- **Security Groups**: Network-level access control
- **Parameter Store**: Encrypted secrets management

### Data Protection
- **Encryption**: At rest and in transit encryption
- **Backups**: Automated RDS backups with retention
- **VPC**: Isolated network environment

### Monitoring
- **CloudTrail**: API activity logging
- **GuardDuty**: Threat detection (optional)
- **Config**: Configuration compliance monitoring

## 📈 Performance Optimization

### Caching Strategy
- **CloudFront**: Global edge caching
- **Redis**: Application-level caching
- **S3**: Static asset optimization

### Auto Scaling
- **Target Tracking**: CPU and memory-based scaling
- **Request-based**: Scale based on ALB request count
- **Predictive**: Scheduled scaling for known patterns

### Database Optimization
- **Performance Insights**: Query performance monitoring
- **Connection Pooling**: Efficient database connections
- **Read Replicas**: Scale read operations (optional)

## 🎯 Cost Optimization

### Compute Costs
- **Fargate Spot**: Up to 70% savings on compute
- **Right-sizing**: Monitor and adjust resource allocation
- **Auto Scaling**: Scale down during low usage

### Storage Costs
- **S3 Lifecycle**: Automatic tier transitions
- **Log Retention**: Short-term retention for cost control
- **EBS Optimization**: GP2 to GP3 migration

### Network Costs
- **VPC Endpoints**: Reduce NAT Gateway usage
- **CloudFront**: Reduce origin requests
- **Regional Resources**: Keep resources in same region

## 🚨 Troubleshooting

### Common Issues

**ECS Service Won't Start**
```bash
# Check service events
aws ecs describe-services \
  --cluster retirementadvisorpro-prod-cluster \
  --services retirementadvisorpro-prod-backend

# Check task definition
aws ecs describe-task-definition \
  --task-definition retirementadvisorpro-prod-backend
```

**Database Connection Issues**
```bash
# Check security group rules
aws ec2 describe-security-groups \
  --group-ids sg-xxxxx

# Test connectivity from ECS task
aws ecs run-task \
  --cluster retirementadvisorpro-prod-cluster \
  --task-definition retirementadvisorpro-prod-backend \
  --overrides '{"containerOverrides":[{"name":"backend","command":["nc","-zv","database-endpoint","5432"]}]}'
```

**High Costs**
```bash
# Check resource utilization
aws cloudwatch get-metric-statistics \
  --namespace AWS/ECS \
  --metric-name CPUUtilization \
  --dimensions Name=ServiceName,Value=retirementadvisorpro-prod-backend \
  --start-time 2023-01-01T00:00:00Z \
  --end-time 2023-01-02T00:00:00Z \
  --period 3600 \
  --statistics Average
```

### Monitoring and Alerting

The infrastructure includes comprehensive monitoring:

- **Application Metrics**: Response time, error rate, throughput
- **Infrastructure Metrics**: CPU, memory, disk, network
- **Cost Monitoring**: Billing alerts and cost optimization
- **Security Monitoring**: Failed login attempts, unusual access patterns

## 🔄 Backup and Disaster Recovery

### Automated Backups
- **RDS**: Daily automated backups with 7-day retention
- **S3**: Cross-region replication (optional)
- **Parameter Store**: Infrastructure as Code backup

### Recovery Procedures
1. **Database**: Point-in-time recovery from RDS backup
2. **Application**: Redeploy from Git repository
3. **Infrastructure**: Terraform state recovery

## 📝 Maintenance

### Regular Tasks
- **Security Updates**: Patch ECS agent and container images
- **Cost Review**: Monthly cost analysis and optimization
- **Performance Review**: Quarterly performance and scaling review
- **Backup Testing**: Quarterly disaster recovery testing

### Upgrade Procedures
1. **Database**: Plan maintenance windows for version upgrades
2. **Container Images**: Regular base image updates
3. **Infrastructure**: Terraform version upgrades
4. **Dependencies**: Application dependency updates

## 📞 Support and Resources

### AWS Documentation
- [ECS Best Practices](https://docs.aws.amazon.com/AmazonECS/latest/bestpracticesguide/)
- [RDS Best Practices](https://docs.aws.amazon.com/AmazonRDS/latest/UserGuide/CHAP_BestPractices.html)
- [Cost Optimization](https://aws.amazon.com/pricing/cost-optimization/)

### Terraform Resources
- [Terraform AWS Provider](https://registry.terraform.io/providers/hashicorp/aws/latest/docs)
- [Terraform Best Practices](https://www.terraform.io/docs/language/settings/backends/s3.html)

### Monitoring Tools
- [AWS CloudWatch Dashboard](https://console.aws.amazon.com/cloudwatch/home#dashboards:)
- [AWS Cost Explorer](https://console.aws.amazon.com/billing/home#/costexplorer)
- [AWS Trusted Advisor](https://console.aws.amazon.com/support/home#/trustedadvisor)