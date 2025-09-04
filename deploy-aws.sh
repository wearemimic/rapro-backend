#!/bin/bash

# RetirementAdvisorPro AWS Deployment Script
# Automated deployment script for AWS infrastructure

set -e  # Exit on any error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration
TERRAFORM_DIR="terraform"
AWS_REGION="${AWS_REGION:-us-east-1}"
ENVIRONMENT="${ENVIRONMENT:-prod}"

# Functions
log_info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

log_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

log_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

check_prerequisites() {
    log_info "Checking prerequisites..."
    
    # Check if AWS CLI is installed and configured
    if ! command -v aws &> /dev/null; then
        log_error "AWS CLI is not installed. Please install it first."
        exit 1
    fi
    
    # Check if Terraform is installed
    if ! command -v terraform &> /dev/null; then
        log_error "Terraform is not installed. Please install it first."
        exit 1
    fi
    
    # Check AWS credentials
    if ! aws sts get-caller-identity &> /dev/null; then
        log_error "AWS credentials are not configured. Please run 'aws configure'."
        exit 1
    fi
    
    # Check if terraform directory exists
    if [[ ! -d "$TERRAFORM_DIR" ]]; then
        log_error "Terraform directory not found: $TERRAFORM_DIR"
        exit 1
    fi
    
    # Check if terraform.tfvars exists
    if [[ ! -f "$TERRAFORM_DIR/terraform.tfvars" ]]; then
        log_error "terraform.tfvars not found. Please copy from terraform.tfvars.example and configure."
        exit 1
    fi
    
    log_success "Prerequisites check passed"
}

validate_terraform() {
    log_info "Validating Terraform configuration..."
    
    cd "$TERRAFORM_DIR"
    
    terraform fmt -check
    if [[ $? -ne 0 ]]; then
        log_warning "Terraform formatting issues found. Running 'terraform fmt'..."
        terraform fmt
    fi
    
    terraform validate
    if [[ $? -ne 0 ]]; then
        log_error "Terraform validation failed"
        exit 1
    fi
    
    cd ..
    log_success "Terraform validation passed"
}

init_terraform() {
    log_info "Initializing Terraform..."
    
    cd "$TERRAFORM_DIR"
    terraform init
    cd ..
    
    log_success "Terraform initialized"
}

plan_terraform() {
    log_info "Planning Terraform changes..."
    
    cd "$TERRAFORM_DIR"
    terraform plan -out=tfplan
    cd ..
    
    log_success "Terraform plan generated"
}

apply_terraform() {
    log_info "Applying Terraform changes..."
    
    cd "$TERRAFORM_DIR"
    terraform apply tfplan
    cd ..
    
    log_success "Terraform applied successfully"
}

get_outputs() {
    log_info "Getting Terraform outputs..."
    
    cd "$TERRAFORM_DIR"
    
    # Get important outputs
    LOAD_BALANCER_DNS=$(terraform output -raw load_balancer_dns_name 2>/dev/null || echo "")
    STAGING_LOAD_BALANCER_DNS=$(terraform output -raw staging_load_balancer_dns_name 2>/dev/null || echo "")
    FRONTEND_URL=$(terraform output -raw frontend_url 2>/dev/null || echo "")
    BACKEND_URL=$(terraform output -raw backend_api_url 2>/dev/null || echo "")
    STAGING_URL=$(terraform output -raw staging_url 2>/dev/null || echo "")
    
    cd ..
}

configure_secrets() {
    log_info "Configuring secrets in Parameter Store..."
    
    # Get the parameter prefix from terraform
    cd "$TERRAFORM_DIR"
    PARAM_PREFIX=$(terraform output -raw parameter_store_prefix 2>/dev/null || echo "/retirementadvisorpro-${ENVIRONMENT}/")
    cd ..
    
    log_warning "Manual step required: Configure the following secrets in AWS Parameter Store:"
    echo ""
    echo "🔐 REQUIRED SECRETS (from your .env files):"
    echo ""
    echo "1. Auth0 Client Secret:"
    echo "   aws ssm put-parameter --name '${PARAM_PREFIX}auth0/client-secret' --value 'YOUR_AUTH0_CLIENT_SECRET' --type 'SecureString' --overwrite"
    echo ""
    echo "2. Stripe Configuration:"
    echo "   aws ssm put-parameter --name '${PARAM_PREFIX}stripe/secret-key' --value 'YOUR_STRIPE_SECRET_KEY' --type 'SecureString' --overwrite"
    echo "   aws ssm put-parameter --name '${PARAM_PREFIX}stripe/webhook-secret' --value 'YOUR_STRIPE_WEBHOOK_SECRET' --type 'SecureString' --overwrite"
    echo "   aws ssm put-parameter --name '${PARAM_PREFIX}stripe/monthly-price-id' --value 'YOUR_MONTHLY_PRICE_ID' --type 'String' --overwrite"
    echo "   aws ssm put-parameter --name '${PARAM_PREFIX}stripe/annual-price-id' --value 'YOUR_ANNUAL_PRICE_ID' --type 'String' --overwrite"
    echo ""
    echo "3. AI API Keys (for Report Center and background tasks):"
    echo "   aws ssm put-parameter --name '${PARAM_PREFIX}ai/openai-api-key' --value 'YOUR_OPENAI_API_KEY' --type 'SecureString' --overwrite"
    echo "   aws ssm put-parameter --name '${PARAM_PREFIX}ai/anthropic-api-key' --value 'YOUR_ANTHROPIC_API_KEY' --type 'SecureString' --overwrite"
    echo ""
    echo "📝 COPY FROM YOUR .ENV FILES:"
    echo "   - backend/.env: AUTH0_CLIENT_SECRET, STRIPE_SECRET_KEY, STRIPE_WEBHOOK_SECRET, OPENAI_API_KEY, ANTHROPIC_API_KEY"
    echo "   - backend/.env: STRIPE_MONTHLY_PRICE_ID, STRIPE_ANNUAL_PRICE_ID"
    echo ""
    echo "⚠️  Note: All environment variables from your .env files are now configured in the ECS task definitions!"
    echo ""
}

configure_github_token() {
    log_info "Configuring GitHub token in Secrets Manager..."
    
    log_warning "Manual step required: Create GitHub token secret:"
    echo ""
    echo "aws secretsmanager create-secret --name 'github-token' --description 'GitHub personal access token for CodePipeline' --secret-string 'YOUR_GITHUB_TOKEN'"
    echo ""
}

build_and_push_images() {
    log_info "Building and pushing Docker images..."
    
    cd "$TERRAFORM_DIR"
    FRONTEND_ECR_URL=$(terraform output -raw frontend_ecr_repository_url 2>/dev/null || echo "")
    BACKEND_ECR_URL=$(terraform output -raw backend_ecr_repository_url 2>/dev/null || echo "")
    cd ..
    
    if [[ -n "$FRONTEND_ECR_URL" && -n "$BACKEND_ECR_URL" ]]; then
        # Login to ECR
        aws ecr get-login-password --region $AWS_REGION | docker login --username AWS --password-stdin ${FRONTEND_ECR_URL%/*}
        
        # Build and push frontend
        log_info "Building frontend image..."
        docker build -f docker/Dockerfile.frontend.prod -t $FRONTEND_ECR_URL:latest .
        docker push $FRONTEND_ECR_URL:latest
        
        # Build and push backend (used for backend, celery worker, and celery beat)
        log_info "Building backend image (for Django, Celery worker, and Celery beat)..."
        docker build -f docker/Dockerfile.backend -t $BACKEND_ECR_URL:latest .
        docker push $BACKEND_ECR_URL:latest
        
        # Tag same backend image for celery services (using same image with different commands)
        docker tag $BACKEND_ECR_URL:latest $BACKEND_ECR_URL:celery-worker
        docker push $BACKEND_ECR_URL:celery-worker
        
        docker tag $BACKEND_ECR_URL:latest $BACKEND_ECR_URL:celery-beat
        docker push $BACKEND_ECR_URL:celery-beat
        
        log_success "Docker images built and pushed"
        log_info "Note: Using ElastiCache for Redis instead of container (better for production)"
    else
        log_warning "ECR URLs not found. Skipping image build."
    fi
}

run_initial_migration() {
    log_info "Running initial database migration..."
    
    cd "$TERRAFORM_DIR"
    CLUSTER_NAME=$(terraform output -raw ecs_cluster_id 2>/dev/null || echo "")
    BACKEND_TASK_DEF=$(terraform output -raw backend_service_name 2>/dev/null || echo "")
    PRIVATE_SUBNET=$(terraform output -json private_subnet_ids 2>/dev/null | jq -r '.[0]' || echo "")
    ECS_SECURITY_GROUP=$(terraform output -json vpc_id 2>/dev/null | xargs -I {} aws ec2 describe-security-groups --filters "Name=group-name,Values=*ecs-tasks*" "Name=vpc-id,Values={}" --query 'SecurityGroups[0].GroupId' --output text 2>/dev/null || echo "")
    cd ..
    
    if [[ -n "$CLUSTER_NAME" && -n "$BACKEND_TASK_DEF" && -n "$PRIVATE_SUBNET" && -n "$ECS_SECURITY_GROUP" ]]; then
        log_info "Running migration task..."
        
        TASK_ARN=$(aws ecs run-task \
            --cluster "$CLUSTER_NAME" \
            --task-definition "${CLUSTER_NAME}-backend" \
            --overrides '{"containerOverrides":[{"name":"backend","command":["python","manage.py","migrate"]}]}' \
            --network-configuration "awsvpcConfiguration={subnets=[\"$PRIVATE_SUBNET\"],securityGroups=[\"$ECS_SECURITY_GROUP\"],assignPublicIp=DISABLED}" \
            --launch-type FARGATE \
            --query 'tasks[0].taskArn' \
            --output text)
        
        if [[ -n "$TASK_ARN" ]]; then
            log_info "Waiting for migration to complete..."
            aws ecs wait tasks-stopped --cluster "$CLUSTER_NAME" --tasks "$TASK_ARN"
            
            # Check exit code
            EXIT_CODE=$(aws ecs describe-tasks --cluster "$CLUSTER_NAME" --tasks "$TASK_ARN" --query 'tasks[0].containers[0].exitCode' --output text)
            
            if [[ "$EXIT_CODE" == "0" ]]; then
                log_success "Database migration completed successfully"
            else
                log_error "Database migration failed with exit code: $EXIT_CODE"
                exit 1
            fi
        else
            log_error "Failed to start migration task"
            exit 1
        fi
    else
        log_warning "Could not determine ECS configuration for migration. Run manually after deployment."
    fi
}

display_architecture_info() {
    echo ""
    echo "=== Architecture Deployed ==="
    echo ""
    echo "🏗️  Infrastructure Components:"
    echo "  • VPC with public/private subnets across 2 AZs"
    echo "  • Application Load Balancers (Staging + Production)"
    echo "  • ECS Fargate clusters for containerized services"
    echo "  • RDS PostgreSQL database (Shared between environments)"
    echo "  • ElastiCache Redis for caching and Celery broker"
    echo "  • CloudFront CDN for static asset delivery"
    echo "  • S3 buckets for media files and static assets"
    echo ""
    echo "🐳 Container Services (Both Environments):"
    echo "  Production:"
    echo "    • Frontend (Vue.js) - Auto-scaling 1-5 instances"
    echo "    • Backend (Django) - Auto-scaling 2-10 instances"
    echo "    • Celery Worker - Auto-scaling 1-5 instances"
    echo "    • Celery Beat Scheduler - Single instance"
    echo "  Staging:"
    echo "    • Frontend - Single instance (minimal resources)"
    echo "    • Backend - Single instance (minimal resources)"
    echo "    • Celery Worker - Single instance"
    echo ""
    echo "💰 Cost Optimization Features:"
    echo "  • Fargate Spot instances (50-70% savings)"
    echo "  • Single NAT Gateway configuration"
    echo "  • Auto-scaling based on CPU/memory metrics"
    echo "  • Shared database between staging/production (-$10/month)"
    echo "  • Staging uses minimal container resources"
    echo "  • CloudWatch logs with 30-day retention"
    echo ""
    echo "🔄 CI/CD Pipeline with Staging/Production Flow:"
    echo "  1. Source: GitHub main branch"
    echo "  2. Build: Docker images for frontend/backend"
    echo "  3. Deploy: Automatic deployment to staging"
    echo "  4. Test: Integration tests on staging environment"
    echo "  5. Approve: Manual approval step for production"
    echo "  6. Deploy: Production deployment after approval"
    echo "  7. Validate: Smoke tests on production"
    echo ""
}

display_results() {
    log_success "Deployment completed successfully!"
    echo ""
    echo "=== Deployment Summary ==="
    echo ""
    echo "Production Environment:"
    if [[ -n "$FRONTEND_URL" ]]; then
        echo "  Frontend URL: $FRONTEND_URL"
    fi
    if [[ -n "$BACKEND_URL" ]]; then
        echo "  Backend API URL: $BACKEND_URL"
    fi
    if [[ -n "$LOAD_BALANCER_DNS" ]]; then
        echo "  Load Balancer DNS: $LOAD_BALANCER_DNS"
    fi
    echo ""
    echo "Staging Environment:"
    if [[ -n "$STAGING_URL" ]]; then
        echo "  Staging URL: $STAGING_URL"
    fi
    if [[ -n "$STAGING_LOAD_BALANCER_DNS" ]]; then
        echo "  Staging Load Balancer DNS: $STAGING_LOAD_BALANCER_DNS"
    fi
    echo ""
    
    display_architecture_info
    
    cd "$TERRAFORM_DIR"
    terraform output manual_configuration_required 2>/dev/null || true
    cd ..
    
    echo ""
    log_info "Next steps:"
    echo "1. Configure the secrets shown above in AWS Parameter Store"
    echo "2. Create the GitHub token secret in AWS Secrets Manager"
    echo "3. If using a custom domain, update your DNS records"
    echo "4. Wait for ECS services to become healthy (5-10 minutes)"
    echo "5. Run initial database seed: aws ecs run-task --cluster <cluster-name> --task-definition <task-def> --overrides '{\"containerOverrides\":[{\"name\":\"backend\",\"command\":[\"python\",\"manage.py\",\"seed_data\"]}]}'"
    echo "6. Test the application endpoints"
    echo ""
    log_info "Monitor deployment progress in AWS Console:"
    echo "- ECS Services: https://${AWS_REGION}.console.aws.amazon.com/ecs/home?region=${AWS_REGION}#/clusters"
    echo "- CodePipeline: https://${AWS_REGION}.console.aws.amazon.com/codesuite/codepipeline/pipelines"
    echo "- CloudWatch: https://${AWS_REGION}.console.aws.amazon.com/cloudwatch/home?region=${AWS_REGION}#dashboards:"
    echo "- RDS Database: https://${AWS_REGION}.console.aws.amazon.com/rds/home?region=${AWS_REGION}#databases:"
    echo "- ElastiCache: https://${AWS_REGION}.console.aws.amazon.com/elasticache/home?region=${AWS_REGION}#redis-clusters:"
}

show_help() {
    echo "RetirementAdvisorPro AWS Deployment Script"
    echo ""
    echo "Usage: $0 [options]"
    echo ""
    echo "Options:"
    echo "  --plan-only    Only run terraform plan (don't apply)"
    echo "  --skip-images  Skip building and pushing Docker images"
    echo "  --skip-migration  Skip initial database migration"
    echo "  --help         Show this help message"
    echo ""
    echo "Environment Variables:"
    echo "  AWS_REGION     AWS region (default: us-east-1)"
    echo "  ENVIRONMENT    Environment name (default: prod)"
    echo ""
}

# Main execution
main() {
    local plan_only=false
    local skip_images=false
    local skip_migration=false
    
    # Parse command line arguments
    while [[ $# -gt 0 ]]; do
        case $1 in
            --plan-only)
                plan_only=true
                shift
                ;;
            --skip-images)
                skip_images=true
                shift
                ;;
            --skip-migration)
                skip_migration=true
                shift
                ;;
            --help)
                show_help
                exit 0
                ;;
            *)
                log_error "Unknown option: $1"
                show_help
                exit 1
                ;;
        esac
    done
    
    log_info "Starting RetirementAdvisorPro AWS deployment..."
    log_info "Region: $AWS_REGION"
    log_info "Environment: $ENVIRONMENT"
    echo ""
    
    # Execute deployment steps
    check_prerequisites
    validate_terraform
    init_terraform
    plan_terraform
    
    if [[ "$plan_only" == true ]]; then
        log_info "Plan-only mode. Review the plan and run without --plan-only to apply."
        exit 0
    fi
    
    # Confirm before applying
    echo ""
    read -p "Do you want to apply the Terraform plan? (y/N): " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        log_info "Deployment cancelled by user."
        exit 0
    fi
    
    apply_terraform
    get_outputs
    
    if [[ "$skip_images" == false ]]; then
        build_and_push_images
    fi
    
    if [[ "$skip_migration" == false ]]; then
        run_initial_migration
    fi
    
    configure_secrets
    configure_github_token
    display_results
    
    log_success "Deployment script completed!"
}

# Run main function with all arguments
main "$@"