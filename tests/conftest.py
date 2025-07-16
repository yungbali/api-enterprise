"""
Shared pytest fixtures and configuration for the test suite.
"""
import asyncio
import os
import pytest
import tempfile
from typing import Generator, AsyncGenerator
from unittest.mock import Mock, patch

from fastapi.testclient import TestClient
from sqlalchemy import create_engine, event
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.pool import StaticPool
import redis.asyncio as redis

from app.main import app
from app.core.database import get_db, Base
from app.core.redis import RedisClient
from app.core.config import Settings


# Test configuration
class TestSettings(Settings):
    """Test-specific settings."""
    ENVIRONMENT: str = "testing"
    DEBUG: bool = True
    DATABASE_URL: str = "sqlite:///./test_db.sqlite"
    DATABASE_TEST_URL: str = "sqlite:///./test_db.sqlite"
    REDIS_URL: str = "redis://localhost:6379/15"  # Use database 15 for tests
    REDIS_TEST_URL: str = "redis://localhost:6379/15"
    SECRET_KEY: str = "test-secret-key-for-testing-only"
    JWT_SECRET_KEY: str = "test-jwt-secret-key-for-testing-only"
    
    # AWS Test Configuration
    AWS_ACCESS_KEY_ID: str = "test-access-key"
    AWS_SECRET_ACCESS_KEY: str = "test-secret-key"
    AWS_REGION: str = "us-east-1"
    S3_BUCKET_NAME: str = "test-bucket"
    
    # External Services Test URLs
    MUSICBRAINZ_BASE_URL: str = "http://localhost:8080/mock-musicbrainz"
    
    # Celery Test Configuration
    CELERY_BROKER_URL: str = "redis://localhost:6379/14"
    CELERY_RESULT_BACKEND: str = "redis://localhost:6379/14"
    
    # Webhook Test Configuration
    WEBHOOK_SECRET: str = "test-webhook-secret"
    WEBHOOK_TIMEOUT: int = 5


@pytest.fixture(scope="session")
def test_settings() -> TestSettings:
    """Provide test settings."""
    # Override environment to ensure test settings are used
    import os
    os.environ["ENVIRONMENT"] = "testing"
    os.environ["SECRET_KEY"] = "test-secret-key-for-testing-only"
    os.environ["JWT_SECRET_KEY"] = "test-jwt-secret-key-for-testing-only"
    return TestSettings()


@pytest.fixture(scope="session")
def event_loop():
    """Create an instance of the default event loop for the test session."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


# Database fixtures
@pytest.fixture(scope="session")
def test_db_engine():
    """Create a test database engine."""
    # Use in-memory SQLite for fast tests
    engine = create_engine(
        "sqlite:///:memory:",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
        echo=False
    )
    
    # Create all tables
    Base.metadata.create_all(bind=engine)
    
    yield engine
    
    # Cleanup
    Base.metadata.drop_all(bind=engine)
    engine.dispose()


@pytest.fixture(scope="session")
def test_db_session_factory(test_db_engine):
    """Create a test database session factory."""
    return sessionmaker(autocommit=False, autoflush=False, bind=test_db_engine)


@pytest.fixture
def db_session(test_db_session_factory) -> Generator[Session, None, None]:
    """Create a test database session with automatic rollback."""
    session = test_db_session_factory()
    
    # Begin a transaction
    transaction = session.begin()
    
    try:
        yield session
    finally:
        # Always rollback to ensure test isolation
        transaction.rollback()
        session.close()


@pytest.fixture
def db_session_commit(test_db_session_factory) -> Generator[Session, None, None]:
    """Create a test database session that commits changes (for integration tests)."""
    session = test_db_session_factory()
    
    try:
        yield session
        session.commit()
    except Exception:
        session.rollback()
        raise
    finally:
        session.close()


# Redis fixtures
@pytest.fixture(scope="session")
async def test_redis_client(test_settings) -> AsyncGenerator[RedisClient, None]:
    """Create a test Redis client."""
    client = RedisClient(test_settings.REDIS_TEST_URL)
    await client.connect()
    
    # Clear test database
    redis_conn = await client.connect()
    await redis_conn.flushdb()
    
    yield client
    
    # Cleanup
    await redis_conn.flushdb()
    await client.close()


@pytest.fixture
async def redis_client(test_redis_client) -> AsyncGenerator[RedisClient, None]:
    """Provide a clean Redis client for each test."""
    # Clear any existing data
    redis_conn = await test_redis_client.connect()
    await redis_conn.flushdb()
    
    yield test_redis_client
    
    # Cleanup after test
    await redis_conn.flushdb()


# FastAPI client fixtures
@pytest.fixture
def override_get_db(db_session):
    """Override the get_db dependency."""
    def _override_get_db():
        yield db_session
    return _override_get_db


@pytest.fixture
def override_get_redis(redis_client):
    """Override Redis client dependency."""
    async def _override_get_redis():
        return redis_client
    return _override_get_redis


@pytest.fixture
def test_client(override_get_db, test_settings) -> Generator[TestClient, None, None]:
    """Create a test client with overridden dependencies."""
    # Override settings
    with patch('app.core.config.get_settings', return_value=test_settings):
        # Override database dependency
        app.dependency_overrides[get_db] = override_get_db
        
        with TestClient(app) as client:
            yield client
        
        # Clean up overrides
        app.dependency_overrides.clear()


@pytest.fixture
async def async_test_client(override_get_db, redis_client, test_settings):
    """Create an async test client for async endpoint testing."""
    from httpx import AsyncClient
    
    # Override settings
    with patch('app.core.config.get_settings', return_value=test_settings):
        # Override dependencies
        app.dependency_overrides[get_db] = override_get_db
        
        async with AsyncClient(app=app, base_url="http://test") as client:
            yield client
        
        # Clean up overrides
        app.dependency_overrides.clear()


# Authentication fixtures
@pytest.fixture
def test_user_data():
    """Provide test user data."""
    return {
        "email": "test@example.com",
        "password": "testpassword123",
        "full_name": "Test User",
        "is_active": True,
        "is_verified": True
    }


@pytest.fixture
def test_admin_data():
    """Provide test admin user data."""
    return {
        "email": "admin@example.com",
        "password": "adminpassword123",
        "full_name": "Admin User",
        "is_active": True,
        "is_verified": True,
        "is_superuser": True
    }


@pytest.fixture
def auth_headers(test_client, test_user_data):
    """Provide authentication headers for API requests."""
    # This will be implemented when we have user creation and auth endpoints
    # For now, return empty headers
    return {}


@pytest.fixture
def admin_auth_headers(test_client, test_admin_data):
    """Provide admin authentication headers for API requests."""
    # This will be implemented when we have user creation and auth endpoints
    # For now, return empty headers
    return {}


# Mock service fixtures
@pytest.fixture
def mock_aws_s3():
    """Mock AWS S3 client."""
    with patch('boto3.client') as mock_client:
        mock_s3 = Mock()
        mock_client.return_value = mock_s3
        
        # Configure common S3 operations
        mock_s3.upload_fileobj.return_value = None
        mock_s3.download_fileobj.return_value = None
        mock_s3.delete_object.return_value = {'DeleteMarker': True}
        mock_s3.head_object.return_value = {
            'ContentLength': 1024,
            'LastModified': '2023-01-01T00:00:00Z'
        }
        
        yield mock_s3


@pytest.fixture
def mock_musicbrainz():
    """Mock MusicBrainz API responses."""
    with patch('httpx.AsyncClient') as mock_client:
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "recordings": [{
                "id": "test-recording-id",
                "title": "Test Song",
                "artist-credit": [{"artist": {"name": "Test Artist"}}],
                "length": 180000
            }]
        }
        
        mock_client.return_value.__aenter__.return_value.get.return_value = mock_response
        yield mock_client


@pytest.fixture
def mock_celery():
    """Mock Celery task execution."""
    with patch('celery.Celery') as mock_celery:
        mock_task = Mock()
        mock_task.delay.return_value.id = "test-task-id"
        mock_task.delay.return_value.status = "SUCCESS"
        mock_task.delay.return_value.result = {"status": "completed"}
        
        mock_celery.return_value.task = lambda func: mock_task
        yield mock_celery


# Test data fixtures
@pytest.fixture
def sample_audio_file():
    """Provide a sample audio file for testing."""
    # Create a temporary file that simulates an audio file
    with tempfile.NamedTemporaryFile(suffix=".mp3", delete=False) as tmp_file:
        # Write some dummy data
        tmp_file.write(b"fake mp3 data for testing")
        tmp_file.flush()
        yield tmp_file.name
    
    # Cleanup
    try:
        os.unlink(tmp_file.name)
    except FileNotFoundError:
        pass


@pytest.fixture
def sample_release_data():
    """Provide sample release data for testing."""
    return {
        "title": "Test Album",
        "artist": "Test Artist",
        "release_date": "2023-12-01",
        "genre": "Electronic",
        "label": "Test Label",
        "catalog_number": "TEST001",
        "upc": "123456789012",
        "tracks": [
            {
                "title": "Track 1",
                "duration": 180,
                "track_number": 1,
                "isrc": "USRC17607839"
            },
            {
                "title": "Track 2", 
                "duration": 200,
                "track_number": 2,
                "isrc": "USRC17607840"
            }
        ]
    }


@pytest.fixture
def sample_partner_data():
    """Provide sample partner data for testing."""
    return {
        "name": "Test Partner",
        "api_endpoint": "https://api.testpartner.com",
        "api_key": "test-api-key",
        "supported_formats": ["mp3", "wav", "flac"],
        "delivery_method": "api",
        "is_active": True
    }


# Utility fixtures
@pytest.fixture
def temp_directory():
    """Provide a temporary directory for test files."""
    with tempfile.TemporaryDirectory() as tmp_dir:
        yield tmp_dir


@pytest.fixture(autouse=True)
def reset_environment():
    """Reset environment variables after each test."""
    original_env = os.environ.copy()
    yield
    
    # Restore original environment
    os.environ.clear()
    os.environ.update(original_env)


# Performance testing fixtures
@pytest.fixture
def performance_threshold():
    """Define performance thresholds for testing."""
    return {
        "api_response_time": 0.5,  # 500ms
        "database_query_time": 1.0,  # 1 second
        "file_upload_time": 5.0,  # 5 seconds
        "memory_usage_mb": 100  # 100MB
    }


# Pytest configuration
def pytest_configure(config):
    """Configure pytest with custom markers and settings."""
    config.addinivalue_line(
        "markers", "unit: mark test as a unit test"
    )
    config.addinivalue_line(
        "markers", "integration: mark test as an integration test"
    )
    config.addinivalue_line(
        "markers", "e2e: mark test as an end-to-end test"
    )
    config.addinivalue_line(
        "markers", "performance: mark test as a performance test"
    )
    config.addinivalue_line(
        "markers", "security: mark test as a security test"
    )
    config.addinivalue_line(
        "markers", "slow: mark test as slow running"
    )
    config.addinivalue_line(
        "markers", "external_deps: mark test as requiring external dependencies"
    )


def pytest_collection_modifyitems(config, items):
    """Modify test collection to add markers based on file location."""
    for item in items:
        # Add markers based on test file location
        if "unit" in str(item.fspath):
            item.add_marker(pytest.mark.unit)
        elif "integration" in str(item.fspath):
            item.add_marker(pytest.mark.integration)
        elif "e2e" in str(item.fspath):
            item.add_marker(pytest.mark.e2e)
        elif "performance" in str(item.fspath):
            item.add_marker(pytest.mark.performance)
        elif "security" in str(item.fspath):
            item.add_marker(pytest.mark.security)
        
        # Mark slow tests
        if "slow" in item.name or "load" in item.name:
            item.add_marker(pytest.mark.slow)
        
        # Mark tests requiring external dependencies
        if any(keyword in str(item.fspath) for keyword in ["external", "integration", "e2e"]):
            item.add_marker(pytest.mark.external_deps)