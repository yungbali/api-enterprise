# Docker Setup for Enterprise Suite API

This guide covers the complete Docker setup for the Enterprise Suite API, including development, staging, and production environments.

## 🚀 Quick Start

### Prerequisites
- Docker Desktop or Docker Engine
- Docker Compose v2.0+
- Make (optional, for convenience commands)

### 1. Clone and Setup
```bash
git clone <repository-url>
cd api-enterprise

# Copy environment template
cp .env.docker .env.docker.local

# Edit environment variables
nano .env.docker.local
```

### 2. Start Development Environment
```bash
# Option 1: Using Make (recommended)
make quickstart

# Option 2: Using Docker Compose directly
docker-compose --env-file .env.docker up -d --build
```

### 3. Access Services
Once started, you can access:
- **API**: http://localhost:8000
- **API Documentation**: http://localhost:8000/docs
- **Flower (Celery monitoring)**: http://localhost:5555
- **Grafana (Monitoring)**: http://localhost:3000 (admin:admin123)
- **Prometheus**: http://localhost:9090
- **MinIO (S3 alternative)**: http://localhost:9001 (minioadmin:minioadmin123)

## 📋 Available Services

### Core Services
- **api**: FastAPI application server
- **celery-worker**: Background task processing
- **celery-beat**: Scheduled task scheduler
- **postgres**: PostgreSQL database
- **redis**: Redis cache and message broker

### Development Services
- **flower**: Celery monitoring dashboard
- **minio**: S3-compatible object storage
- **nginx**: Reverse proxy and load balancer

### Monitoring Services
- **prometheus**: Metrics collection
- **grafana**: Visualization dashboards

## 🛠️ Development Commands

### Basic Operations
```bash
# Start all services
make up

# Stop all services
make down

# Restart services
make restart

# View logs
make logs

# View specific service logs
make logs-api
make logs-worker
make logs-db
```

### Database Operations
```bash
# Run migrations
make migrate

# Create new migration
make migrate-create

# Access database shell
make shell-db

# Seed database with sample data
make seed

# Backup database
make backup

# Restore database
make restore
```

### Development Tools
```bash
# Access API container shell
make shell

# Run tests
make test

# Run tests with coverage
make test-coverage

# Format code
make format

# Lint code
make lint

# Security check
make security-check
```

## 🏗️ Service Architecture

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│     Nginx       │    │   Grafana       │    │   Prometheus    │
│  (Port 80/443)  │    │   (Port 3000)   │    │   (Port 9090)   │
└─────────────────┘    └─────────────────┘    └─────────────────┘
         │                       │                       │
         │              ┌────────┴────────┐             │
         │              │                 │             │
         ▼              ▼                 ▼             ▼
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   FastAPI API   │    │     Flower      │    │      MinIO      │
│  (Port 8000)    │    │   (Port 5555)   │    │  (Port 9000)    │
└─────────────────┘    └─────────────────┘    └─────────────────┘
         │                       │
         │              ┌────────┴────────┐
         │              │                 │
         ▼              ▼                 ▼
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│ Celery Workers  │    │  Celery Beat    │    │   PostgreSQL    │
│  (Background)   │    │  (Scheduler)    │    │  (Port 5432)    │
└─────────────────┘    └─────────────────┘    └─────────────────┘
         │                       │                       │
         │              ┌────────┴────────┐             │
         │              │                 │             │
         ▼              ▼                 ▼             ▼
┌─────────────────────────────────────────────────────────────┐
│                      Redis                                  │
│               (Port 6379)                                   │
│     Cache (DB 0) | Celery Broker (DB 1) | Results (DB 2)   │
└─────────────────────────────────────────────────────────────┘
```

## 🔧 Environment Configuration

### Key Environment Variables
```bash
# Application
ENVIRONMENT=development
DEBUG=true
SECRET_KEY=your-secret-key-here

# Database
DATABASE_URL=postgresql://user:pass@postgres:5432/db
REDIS_URL=redis://redis:6379/0

# Celery
CELERY_BROKER_URL=redis://redis:6379/1
CELERY_RESULT_BACKEND=redis://redis:6379/2

# AWS (for S3 integration)
AWS_ACCESS_KEY_ID=your-access-key
AWS_SECRET_ACCESS_KEY=your-secret-key
S3_BUCKET_NAME=your-bucket-name
```

### Environment Files
- `.env.docker`: Template for development
- `.env.docker.local`: Your local development settings
- `.env.docker.prod`: Production environment settings

## 📊 Monitoring and Observability

### Prometheus Metrics
The API exposes metrics at `/metrics` endpoint:
- HTTP request duration and count
- Database connection pool metrics
- Celery task metrics
- Custom business metrics

### Grafana Dashboards
Pre-configured dashboards for:
- API performance metrics
- Database monitoring
- Celery task monitoring
- Infrastructure metrics

### Health Checks
- API health check: http://localhost:8000/health
- Database health: `make health`
- Redis health: `make health`

## 🚀 Production Deployment

### AWS ECS/Fargate Deployment
```bash
# 1. Configure production environment
cp .env.docker .env.docker.prod
# Edit production settings

# 2. Deploy to production
make prod

# 3. Monitor deployment
make logs
```

### Key Production Configurations
- **Resource Limits**: CPU and memory constraints
- **Auto-scaling**: Based on CPU/memory metrics
- **Load Balancing**: Application Load Balancer
- **Secrets Management**: AWS Secrets Manager
- **Database**: Managed RDS PostgreSQL
- **Cache**: Managed ElastiCache Redis

## 🔒 Security Considerations

### Development Security
- Non-root user in containers
- Network isolation
- Environment variable secrets
- Health checks for all services

### Production Security
- SSL/TLS termination
- Secret rotation
- Container image scanning
- Network security groups
- IAM roles and policies

## 🐛 Troubleshooting

### Common Issues

#### Services won't start
```bash
# Check logs
make logs

# Rebuild containers
make clean && make build

# Check system resources
docker system df
```

#### Database connection issues
```bash
# Check database health
make health

# Access database directly
make shell-db

# Reset database
make down && docker volume rm api-enterprise_postgres_data && make up
```

#### Performance issues
```bash
# Monitor resource usage
docker stats

# Check application logs
make logs-api

# Monitor with Grafana
# Visit http://localhost:3000
```

### Log Analysis
```bash
# Follow all logs
make logs

# Filter specific service
make logs-api

# Search logs
docker-compose logs api | grep ERROR
```

## 📈 Performance Optimization

### Development Performance
- Use volume mounts for code changes
- Optimize Docker layer caching
- Use multi-stage builds
- Enable BuildKit for faster builds

### Production Performance
- Resource limits and reservations
- Connection pooling
- Redis optimization
- Database indexing
- CDN for static assets

## 🔄 CI/CD Integration

### GitHub Actions Example
```yaml
name: Docker Build and Deploy
on:
  push:
    branches: [main]
jobs:
  build:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - name: Build and test
        run: |
          make build
          make test
      - name: Deploy to staging
        run: make prod
```

### Docker Registry
```bash
# Tag image for registry
docker tag api-enterprise:latest your-registry/api-enterprise:latest

# Push to registry
docker push your-registry/api-enterprise:latest
```

## 📚 Additional Resources

- [Docker Compose Documentation](https://docs.docker.com/compose/)
- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [Celery Documentation](https://docs.celeryq.dev/)
- [Prometheus Documentation](https://prometheus.io/docs/)
- [Grafana Documentation](https://grafana.com/docs/)

## 🆘 Support

For issues or questions:
1. Check the logs: `make logs`
2. Review the troubleshooting section
3. Check existing GitHub issues
4. Create a new issue with logs and system information

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make changes and test with Docker
4. Submit a pull request

```bash
# Test your changes
make test
make lint
make security-check
```
