# AWS Deployment Guide

## 📋 Prerequisites

1. **AWS Account** with appropriate permissions
2. **AWS CLI** installed and configured
3. **SAM CLI** installed (for serverless deployment)
4. **Docker** installed (for containerized deployment)
5. **Python 3.9+** installed

## 🚀 Deployment Options

### Option A: Serverless (Recommended for MVP)

#### 1. Install SAM CLI
```bash
# macOS
brew install aws-sam-cli

# Linux
pip install aws-sam-cli
```

#### 2. Configure AWS Credentials
```bash
aws configure
# Enter your AWS Access Key ID, Secret Access Key, and Region
```

#### 3. Create Secrets in AWS Secrets Manager
```bash
aws secretsmanager create-secret \
  --name "dev-enterprise-suite-secrets" \
  --secret-string '{
    "secret_key": "your-secret-key-here",
    "jwt_secret_key": "your-jwt-secret-key-here",
    "webhook_secret": "your-webhook-secret-here"
  }'
```

#### 4. Deploy with SAM
```bash
# Build the application
sam build

# Deploy to dev environment
sam deploy \
  --parameter-overrides \
    Environment=dev \
    DBPassword=your-db-password \
  --guided

# Deploy to production
sam deploy \
  --parameter-overrides \
    Environment=prod \
    DBPassword=your-prod-db-password \
  --stack-name enterprise-suite-api-prod
```

#### 5. Get API Gateway URL
```bash
aws cloudformation describe-stacks \
  --stack-name enterprise-suite-api-dev \
  --query 'Stacks[0].Outputs[?OutputKey==`EnterpriseAPIUrl`].OutputValue' \
  --output text
```

### Option B: Containerized (ECS)

#### 1. Create ECR Repository
```bash
aws ecr create-repository --repository-name enterprise-suite-api
```

#### 2. Build and Push Docker Image
```bash
# Get login token
aws ecr get-login-password --region us-east-1 | docker login --username AWS --password-stdin YOUR_ACCOUNT_ID.dkr.ecr.us-east-1.amazonaws.com

# Build image
docker build -t enterprise-suite-api .

# Tag image
docker tag enterprise-suite-api:latest YOUR_ACCOUNT_ID.dkr.ecr.us-east-1.amazonaws.com/enterprise-suite-api:latest

# Push image
docker push YOUR_ACCOUNT_ID.dkr.ecr.us-east-1.amazonaws.com/enterprise-suite-api:latest
```

#### 3. Create ECS Cluster and Service
```bash
# Create cluster
aws ecs create-cluster --cluster-name enterprise-suite-cluster

# Create task definition (see ecs-task-definition.json)
aws ecs register-task-definition --cli-input-json file://ecs-task-definition.json

# Create service
aws ecs create-service \
  --cluster enterprise-suite-cluster \
  --service-name enterprise-suite-api-service \
  --task-definition enterprise-suite-api:1 \
  --desired-count 2 \
  --launch-type FARGATE \
  --network-configuration "awsvpcConfiguration={subnets=[subnet-12345],securityGroups=[sg-12345],assignPublicIp=ENABLED}"
```

## 🔧 Configuration

### Environment Variables
Set these environment variables in your deployment:

```bash
# Application
APP_NAME=Enterprise Suite API
APP_VERSION=1.0.0
ENVIRONMENT=dev  # or prod
SECRET_KEY=your-secret-key
JWT_SECRET_KEY=your-jwt-secret-key
WEBHOOK_SECRET=your-webhook-secret

# Database
DATABASE_URL=postgresql://user:password@host:5432/database
REDIS_URL=redis://host:6379/0

# AWS
AWS_REGION=us-east-1
S3_BUCKET_NAME=your-bucket-name
```

### Database Setup
```bash
# Connect to RDS instance
psql -h your-rds-endpoint -U enterprise_user -d enterprise_suite_db

# Run migrations (if using Alembic)
alembic upgrade head
```

## 🔐 Security Best Practices

### 1. Use IAM Roles
- Create specific IAM roles for Lambda functions and ECS tasks
- Follow principle of least privilege
- Use AWS Secrets Manager for sensitive data

### 2. Enable Security Features
- Enable VPC for RDS and Redis
- Use Security Groups to restrict access
- Enable encryption at rest and in transit
- Enable CloudTrail for API auditing

### 3. Monitor and Alert
- Set up CloudWatch alarms for errors and performance
- Use AWS X-Ray for distributed tracing
- Enable VPC Flow Logs for network monitoring

## 📊 Monitoring Setup

### CloudWatch Dashboards
Create dashboards to monitor:
- API Gateway metrics (requests, latency, errors)
- Lambda function metrics (invocations, duration, errors)
- RDS metrics (CPU, connections, storage)
- Redis metrics (CPU, memory, connections)

### Alerts
Set up alerts for:
- High error rates (>5%)
- High latency (>2 seconds)
- Database connection issues
- Lambda function failures

## 🧪 Testing Deployment

### Health Check
```bash
curl -X GET https://your-api-url/health
```

### Create Test Release
```bash
curl -X POST https://your-api-url/api/v1/releases \
  -H "Content-Type: application/json" \
  -H "X-API-Key: your-api-key" \
  -d '{
    "title": "Test Release",
    "artist": "Test Artist",
    "release_type": "single",
    "tracks": [
      {
        "title": "Test Track",
        "artist": "Test Artist",
        "track_number": 1,
        "isrc": "TEST1234567"
      }
    ]
  }'
```

## 🚨 Troubleshooting

### Common Issues

#### 1. Lambda Cold Start
- Increase memory allocation
- Use provisioned concurrency for critical functions
- Implement connection pooling

#### 2. Database Connection Issues
- Check security group rules
- Verify subnet configuration
- Monitor connection pool usage

#### 3. API Gateway Timeout
- Increase timeout settings
- Implement async processing for long-running tasks
- Use EventBridge for background processing

### Debugging Commands
```bash
# View CloudWatch logs
aws logs tail /aws/lambda/enterprise-suite-api --follow

# Check stack events
aws cloudformation describe-stack-events --stack-name enterprise-suite-api-dev

# Test Lambda function
aws lambda invoke \
  --function-name enterprise-suite-api-dev \
  --payload '{"httpMethod": "GET", "path": "/health"}' \
  response.json
```

## 🔄 CI/CD Pipeline

The project includes GitHub Actions workflows for:
- **Testing**: Runs tests on every PR
- **Security Scanning**: Scans for vulnerabilities
- **Serverless Deployment**: Deploys to AWS using SAM
- **Container Deployment**: Builds and deploys Docker images

### Required GitHub Secrets
- `AWS_ACCESS_KEY_ID`
- `AWS_SECRET_ACCESS_KEY`
- `DB_PASSWORD`

## 📈 Scaling Considerations

### Auto Scaling
- Configure API Gateway throttling
- Set up Lambda concurrent execution limits
- Use ECS auto scaling for containerized deployments

### Database Scaling
- Enable RDS auto scaling
- Consider read replicas for read-heavy workloads
- Monitor connection pool usage

### Caching
- Implement Redis caching for frequently accessed data
- Use CloudFront for static content
- Enable API Gateway caching

## 💰 Cost Optimization

### Serverless
- Use appropriate memory allocation for Lambda
- Enable API Gateway caching
- Use S3 lifecycle policies

### Containerized
- Right-size ECS tasks
- Use Spot instances where appropriate
- Monitor resource utilization

## 🔒 Backup and Disaster Recovery

### Database Backups
- Enable automated RDS backups
- Set appropriate retention period
- Test backup restoration

### Application Backups
- Store deployment artifacts in S3
- Version control infrastructure code
- Document recovery procedures
