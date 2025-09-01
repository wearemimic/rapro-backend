# Report Center Environment Configuration Guide

## Required Environment Variables

### 🔴 **CRITICAL - Required for Core Functionality**

```bash
# OpenAI API Configuration (REQUIRED)
OPENAI_API_KEY=your-openai-api-key-here
OPENAI_MODEL_VERSION=gpt-4-turbo-preview

# Background Task Processing (REQUIRED)
CELERY_BROKER_URL=redis://localhost:6379/0
CELERY_RESULT_BACKEND=redis://localhost:6379/0
```

### 🟡 **RECOMMENDED - For Production Performance**

```bash
# File Storage Configuration
MEDIA_URL=/media/
STATIC_URL=/static/
CDN_URL=https://your-cdn-domain.com  # Optional CDN for file delivery

# Redis Configuration (if different from default)
REDIS_URL=redis://localhost:6379/0

# Email Configuration (for report sharing notifications)
EMAIL_BACKEND=django.core.mail.backends.smtp.EmailBackend
EMAIL_HOST=your-smtp-server.com
EMAIL_PORT=587
EMAIL_USE_TLS=True
EMAIL_HOST_USER=your-email@domain.com
EMAIL_HOST_PASSWORD=your-email-password

# File Upload Limits
MAX_UPLOAD_SIZE=50485760  # 48MB
REPORT_FILE_RETENTION_DAYS=90
```

### 🟢 **OPTIONAL - Advanced Features**

```bash
# Analytics & Monitoring
ANALYTICS_RETENTION_MONTHS=12
AI_COST_LIMIT_PER_USER_MONTHLY=100.00

# Performance Optimization
TEMPLATE_CACHE_TIMEOUT=3600
REPORT_GENERATION_TIMEOUT=300
BULK_EXPORT_BATCH_SIZE=50

# Feature Flags
ENABLE_AI_FEATURES=True
ENABLE_BULK_EXPORTS=True
ENABLE_REPORT_SCHEDULING=True
ENABLE_CLIENT_PORTAL=True
```

## Environment-Specific Configurations

### **Development Environment (.env.development)**
```bash
# Core Requirements
OPENAI_API_KEY=sk-your-dev-key
OPENAI_MODEL_VERSION=gpt-4o-mini  # Cheaper for development
CELERY_BROKER_URL=redis://localhost:6379/0
CELERY_RESULT_BACKEND=redis://localhost:6379/0

# Development Settings
DEBUG=True
AI_COST_LIMIT_PER_USER_MONTHLY=10.00  # Lower limit for dev
REPORT_GENERATION_TIMEOUT=60  # Faster timeout for testing
```

### **Staging Environment (.env.staging)**
```bash
# Core Requirements
OPENAI_API_KEY=sk-your-staging-key
OPENAI_MODEL_VERSION=gpt-4-turbo-preview
CELERY_BROKER_URL=redis://staging-redis:6379/0
CELERY_RESULT_BACKEND=redis://staging-redis:6379/0

# Staging Settings
DEBUG=False
CDN_URL=https://staging-cdn.retirementadvisorpro.com
AI_COST_LIMIT_PER_USER_MONTHLY=25.00
EMAIL_BACKEND=django.core.mail.backends.console.EmailBackend  # Console for staging
```

### **Production Environment (.env.production)**
```bash
# Core Requirements (REQUIRED)
OPENAI_API_KEY=sk-your-production-key
OPENAI_MODEL_VERSION=gpt-4-turbo-preview
CELERY_BROKER_URL=redis://prod-redis-cluster:6379/0
CELERY_RESULT_BACKEND=redis://prod-redis-cluster:6379/0

# Production Settings (CRITICAL)
DEBUG=False
CDN_URL=https://cdn.retirementadvisorpro.com
AI_COST_LIMIT_PER_USER_MONTHLY=100.00
REPORT_GENERATION_TIMEOUT=300
BULK_EXPORT_BATCH_SIZE=100

# Email Configuration (REQUIRED for notifications)
EMAIL_BACKEND=django.core.mail.backends.smtp.EmailBackend
EMAIL_HOST=smtp.sendgrid.net
EMAIL_PORT=587
EMAIL_USE_TLS=True
EMAIL_HOST_USER=apikey
EMAIL_HOST_PASSWORD=your-sendgrid-api-key

# Security & Performance
SECURE_SSL_REDIRECT=True
SECURE_PROXY_SSL_HEADER=('HTTP_X_FORWARDED_PROTO', 'https')
```

## Required System Dependencies

### **Backend Dependencies**
- **Redis Server**: Required for Celery background tasks
- **PostgreSQL**: Database (already configured)
- **OpenAI API Access**: Required for AI features
- **Python packages**: All listed in requirements.txt

### **Infrastructure Requirements**
- **File Storage**: Local filesystem or cloud storage (S3, etc.)
- **Background Workers**: Celery worker processes
- **Task Scheduler**: Celery beat for scheduled reports

## Deployment Checklist

### **Pre-Deployment Steps**
- [ ] Obtain OpenAI API key with sufficient credits
- [ ] Set up Redis server instance
- [ ] Configure email service (SendGrid, etc.)
- [ ] Set up CDN (optional but recommended)
- [ ] Configure file storage permissions

### **Post-Deployment Verification**
- [ ] Test AI content generation: `/api/report-center/ai/executive-summary/`
- [ ] Verify background tasks: Check Celery worker status
- [ ] Test report generation: Create and export a sample report
- [ ] Verify file uploads: Upload template assets
- [ ] Test client portal access: Share a report with a client

## Cost Considerations

### **OpenAI API Costs (Monthly Estimates)**
- **Light Usage** (5 reports/day): ~$15-25/month
- **Medium Usage** (20 reports/day): ~$50-75/month  
- **Heavy Usage** (50+ reports/day): ~$150-250/month

### **Infrastructure Costs**
- **Redis**: $10-20/month (managed service)
- **File Storage**: $5-15/month (depending on volume)
- **Email Service**: $0-20/month (depending on volume)

## Monitoring & Alerts

### **Key Metrics to Monitor**
- AI API usage and costs
- Report generation success rate  
- Background task queue length
- File storage usage
- Client portal access rates

### **Recommended Alerts**
- Daily AI costs exceeding $X
- Report generation failures
- Celery worker downtime
- High error rates on AI endpoints

## Security Considerations

### **API Key Security**
- Store OpenAI API key in secure environment variables
- Use different keys for dev/staging/production
- Implement API key rotation policies
- Monitor API key usage for anomalies

### **File Security**
- Implement proper file permissions
- Use secure file URLs with expiration
- Regular cleanup of temporary files
- Virus scanning for uploaded files (recommended)

## Support & Troubleshooting

### **Common Issues**
1. **AI Generation Fails**: Check OpenAI API key and credits
2. **Slow Report Generation**: Verify Celery workers are running
3. **File Upload Issues**: Check storage permissions and size limits
4. **Background Tasks Stuck**: Restart Celery workers

### **Log Locations**
- Django logs: Standard Django logging
- Celery logs: Celery worker output
- AI service logs: `/logs/ai_report_service.log`
- Report generation: `/logs/report_generation.log`

---

**Next Steps:**
1. Copy appropriate environment configuration to your `.env` file
2. Obtain OpenAI API key and add to configuration
3. Set up Redis server for background tasks
4. Test AI functionality with a sample report
5. Configure email service for production report sharing