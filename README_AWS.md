# Enterprise Suite API - AWS Deployment

## 🏗️ AWS Architecture Overview

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                                 AWS Cloud                                    │
├─────────────────────────────────────────────────────────────────────────────┤
│  ┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐          │
│  │   API Gateway   │    │   EventBridge   │    │      SNS        │          │
│  │                 │    │                 │    │                 │          │
│  └─────────┬───────┘    └─────────┬───────┘    └─────────┬───────┘          │
│            │                      │                      │                  │
│  ┌─────────▼───────┐    ┌─────────▼───────┐    ┌─────────▼───────┐          │
│  │   Lambda API    │    │ Lambda Delivery │    │ Lambda Webhook  │          │
│  │                 │    │   Processor     │    │   Processor     │          │
│  └─────────┬───────┘    └─────────┬───────┘    └─────────┬───────┘          │
│            │                      │                      │                  │
│  ┌─────────▼───────┐    ┌─────────▼───────┐    ┌─────────▼───────┐          │
│  │   RDS Postgres  │    │   ElastiCache   │    │      S3         │          │
│  │                 │    │     Redis       │    │                 │          │
│  └─────────────────┘    └─────────────────┘    └─────────────────┘          │
│                                                                              │
│  ┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐          │
│  │   CloudWatch    │    │     X-Ray       │    │    Athena       │          │
│  │   Monitoring    │    │    Tracing      │    │   Analytics     │          │
│  └─────────────────┘    └─────────────────┘    └─────────────────┘          │
└─────────────────────────────────────────────────────────────────────────────┘
```

## 🚀 Quick Start

### 1. Prerequisites
- AWS Account with appropriate permissions
- AWS CLI configured
- SAM CLI installed
- Python 3.9+

### 2. Deploy to AWS
```bash
# Clone repository
git clone <repository-url>
cd api-enterprise

# Deploy with SAM
sam build
sam deploy --guided
```

### 3. Test API
```bash
# Get API URL from CloudFormation output
API_URL=$(aws cloudformation describe-stacks \
  --stack-name enterprise-suite-api-dev \
  --query 'Stacks[0].Outputs[?OutputKey==`EnterpriseAPIUrl`].OutputValue' \
  --output text)

# Test health endpoint
curl $API_URL/health
```

## 📋 Features Implemented

### ✅ Core APIs
- **Headless Ingestion API** (`POST /api/v1/releases`)
- **Dynamic Partner Management** (`POST /api/v1/delivery-partners`)
- **Delivery Status Tracking** (`GET /api/v1/delivery-status`)
- **Analytics API** (`GET /api/v1/analytics`)
- **Webhook Management** (`POST /api/v1/webhooks`)
- **Workflow Control** (`POST /api/v1/workflow/rules`)

### ✅ AWS Services Integration
- **API Gateway** for REST API endpoints
- **Lambda** for serverless compute
- **RDS PostgreSQL** for relational data
- **ElastiCache Redis** for caching and sessions
- **S3** for file storage
- **EventBridge** for event-driven processing
- **SNS** for notifications
- **CloudWatch** for monitoring
- **X-Ray** for distributed tracing

### ✅ Background Processing
- **Delivery Engine** for DSP delivery automation
- **Webhook Processor** for event notifications
- **Analytics Pipeline** for data normalization

## 🔧 Configuration

### Environment Variables
```bash
# Application
APP_NAME=Enterprise Suite API
ENVIRONMENT=dev
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

### AWS Secrets Manager
Store sensitive configuration in AWS Secrets Manager:
```json
{
  "secret_key": "your-application-secret-key",
  "jwt_secret_key": "your-jwt-secret-key",
  "webhook_secret": "your-webhook-secret-key"
}
```

## 🏭 Deployment Options

### Option 1: Serverless (Recommended for MVP)
- **API Gateway + Lambda** for REST endpoints
- **EventBridge + Lambda** for background processing
- **RDS + ElastiCache** for data storage
- **S3** for file storage

**Benefits:**
- Pay-per-use pricing
- Automatic scaling
- No server management
- Built-in monitoring

### Option 2: Containerized (ECS/Fargate)
- **ECS Fargate** for containerized deployment
- **Application Load Balancer** for load distribution
- **RDS + ElastiCache** for data storage
- **S3** for file storage

**Benefits:**
- Predictable performance
- Full control over environment
- Easier local development
- Support for long-running processes

## 🔄 CI/CD Pipeline

The project includes GitHub Actions workflows for:

### Testing
- Unit tests with pytest
- Integration tests with test database
- Security scanning with Bandit
- Code coverage reporting

### Deployment
- **Serverless**: SAM CLI deployment
- **Containerized**: Docker build and ECS deployment
- **Multi-environment**: Separate dev/staging/prod deployments

## 📊 Monitoring & Observability

### CloudWatch Integration
- **Metrics**: API latency, error rates, throughput
- **Logs**: Structured logging with correlation IDs
- **Alarms**: Automated alerts for critical issues

### X-Ray Tracing
- End-to-end request tracing
- Performance bottleneck identification
- Dependency mapping

### Custom Dashboards
- API performance metrics
- Business KPIs (releases, deliveries, revenue)
- System health indicators

## 🔐 Security Features

### Authentication & Authorization
- **JWT tokens** for user authentication
- **API keys** for service-to-service communication
- **IAM roles** for AWS service access

### Data Protection
- **Encryption at rest** for database and S3
- **Encryption in transit** for all communications
- **VPC isolation** for network security

### Access Control
- **Security groups** for network access
- **IAM policies** for resource permissions
- **API Gateway throttling** for rate limiting

## 📈 Scaling & Performance

### Auto Scaling
- **Lambda concurrency** scaling
- **RDS storage** auto-scaling
- **ElastiCache** cluster scaling

### Caching Strategy
- **Redis** for API response caching
- **API Gateway** caching for static responses
- **CloudFront** for static content delivery

### Performance Optimization
- **Connection pooling** for database connections
- **Async processing** for long-running tasks
- **Background jobs** for non-critical operations

## 💰 Cost Optimization

### Serverless Benefits
- **No idle costs** - pay only for actual usage
- **Automatic scaling** - no over-provisioning
- **Managed services** - reduced operational overhead

### Cost Monitoring
- **Cost allocation tags** for resource tracking
- **Budget alerts** for cost management
- **Usage optimization** recommendations

## 🚨 Troubleshooting

### Common Issues

1. **Lambda Cold Starts**
   - Increase memory allocation
   - Use provisioned concurrency
   - Implement connection pooling

2. **Database Connection Issues**
   - Check security group rules
   - Verify subnet configuration
   - Monitor connection pool usage

3. **API Gateway Timeouts**
   - Increase timeout settings
   - Implement async processing
   - Use EventBridge for background tasks

### Debugging Tools
```bash
# View logs
aws logs tail /aws/lambda/enterprise-suite-api --follow

# Check stack status
aws cloudformation describe-stack-events --stack-name enterprise-suite-api-dev

# Test Lambda function
aws lambda invoke \
  --function-name enterprise-suite-api-dev \
  --payload '{"httpMethod": "GET", "path": "/health"}' \
  response.json
```

## 📚 Documentation

- [AWS Deployment Guide](docs/AWS_DEPLOYMENT.md)
- [API Documentation](http://localhost:8000/docs) (when running locally)
- [Architecture Decision Records](docs/adr/)

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests
5. Submit a pull request

## 📄 License

Copyright © 2025 Afromuse Digital. All rights reserved.

---

**Built with ❤️ for African Music Distribution**

## API Endpoints

> All endpoints require authentication via Bearer JWT unless otherwise noted.

### Authentication
- `POST /api/v1/auth/login` — Obtain JWT access token (**implemented**)
- `POST /api/v1/auth/logout` — Logout (**placeholder**)
- `POST /api/v1/auth/refresh` — Refresh JWT token (**placeholder**)

### Releases
- `POST /api/v1/releases/` — Create a new release (**implemented**)
- `GET /api/v1/releases/` — List all releases (**implemented**)
- `GET /api/v1/releases/{release_id}` — Get a release by string release_id (**implemented**)
- `PUT /api/v1/releases/{id}` — Update a release by numeric id (**implemented**)
- `DELETE /api/v1/releases/{release_id}` — Delete a release by string release_id (**implemented**)

### Partners
- `POST /api/v1/partners/` — Create partner (**placeholder**)
- `GET /api/v1/partners/{partner_id}` — Get partner by ID (**partially implemented**)
- `PUT /api/v1/partners/{partner_id}` — Update partner (**placeholder**)
- `DELETE /api/v1/partners/{partner_id}` — Delete partner (**placeholder**)

### Delivery
- `GET /api/v1/delivery/status` — Get delivery status (**placeholder**)
- `POST /api/v1/delivery/retry` — Retry delivery (**placeholder**)

### Analytics
- `GET /api/v1/analytics/` — Get analytics data (**placeholder**)
- `GET /api/v1/analytics/reports` — Get revenue reports (**placeholder**)

### Webhooks
- `POST /api/v1/webhooks/` — Create webhook (**placeholder**)
- `GET /api/v1/webhooks/{webhook_id}` — Get webhook by ID (**placeholder**)
- `DELETE /api/v1/webhooks/{webhook_id}` — Delete webhook by ID (**placeholder**)

### Workflow
- `POST /api/v1/workflow/rules` — Create workflow rule (**placeholder**)
- `GET /api/v1/workflow/rules/{rule_id}` — Get workflow rule by ID (**placeholder**)
- `GET /api/v1/workflow/executions` — Get workflow executions (**placeholder**)

### MusicBrainz Integration
- Rich set of endpoints for searching and retrieving artist, release, and recording data from MusicBrainz (**implemented**)

---

## Authentication Example

Obtain a JWT token:
```sh
curl -X POST "http://<API_URL>/api/v1/auth/login" \
  -H "Content-Type: application/json" \
  -d '{"email": "testuser@example.com", "password": "testpassword"}'
```

Use the token in subsequent requests:
```sh
curl -X GET "http://<API_URL>/api/v1/releases/" \
  -H "Authorization: Bearer <YOUR_TOKEN>"
```

---
