# Enterprise Suite API - MVP 1.0

## Overview
API-first backend for automating music distribution workflows, dynamically managing DSPs, and ingesting clean data for African music enterprises.

## Features
- 🎵 Headless Ingestion API (DDEX-compliant)
- 🔗 Dynamic Partner Management API
- 📊 Stateful Delivery Tracking
- 📈 Normalized Data & Analytics API
- 🤖 Agentic Workflow Control (HITL)
- 📡 Custom Webhooks

## Tech Stack
- **Backend**: Python (FastAPI)
- **Database**: PostgreSQL + Redis
- **Storage**: Amazon S3
- **Auth**: OAuth2 + API Key
- **Monitoring**: Sentry, Prometheus
- **Testing**: Pytest
- **Documentation**: Swagger/OpenAPI

## Quick Start

### Prerequisites
- Python 3.9+
- PostgreSQL 12+
- Redis 6+
- AWS S3 credentials

### Installation
```bash
# Clone the repository
git clone <repository-url>
cd api-enterprise

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Setup environment
cp .env.example .env
# Edit .env with your configuration

# Run migrations
alembic upgrade head

# Start the server
uvicorn app.main:app --reload
```

### API Documentation
Once running, visit:
- API Docs: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

## Project Structure
```
api-enterprise/
├── app/
│   ├── __init__.py
│   ├── main.py              # FastAPI app entry point
│   ├── core/                # Core configuration and security
│   ├── api/                 # API endpoints
│   ├── models/              # Database models
│   ├── schemas/             # Pydantic schemas
│   ├── crud/                # Database operations
│   ├── services/            # Business logic
│   └── utils/               # Utilities
├── tests/                   # Test files
├── alembic/                 # Database migrations
├── docs/                    # Documentation
├── requirements.txt         # Dependencies
└── .env.example            # Environment template
```

## Development
```bash
# Run tests
pytest

# Run with auto-reload
uvicorn app.main:app --reload

# Generate migration
alembic revision --autogenerate -m "description"

# Apply migrations
alembic upgrade head
```

## KPIs & Targets
- API Uptime: 99.5%
- Ingestion API Calls: 1000+ in 30 days
- DSPs Added Programmatically: 10+
- Webhook Response Time: < 2 seconds
- Customer Support Tickets: 50% reduction
- Enterprise MRR: $10K+

## License
Copyright © 2025 Afromuse Digital. All rights reserved.
