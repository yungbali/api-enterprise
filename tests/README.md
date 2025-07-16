# QA Testing Suite

This directory contains the comprehensive QA testing suite for the music distribution API. The testing infrastructure is designed to validate all aspects of the system including functional, integration, performance, and security testing.

## Directory Structure

```
tests/
├── README.md                   # This file
├── conftest.py                 # Shared pytest fixtures and configuration
├── test_infrastructure.py      # Infrastructure validation tests
├── factories/                  # Test data factories
├── fixtures/                   # Test data fixtures and mock services
│   └── wiremock/              # WireMock configurations for external services
├── unit/                       # Unit tests for individual components
├── integration/                # Integration tests for component interactions
├── e2e/                        # End-to-end workflow tests
├── performance/                # Performance and load tests
├── security/                   # Security and vulnerability tests
├── utils/                      # Test utilities and helper functions
└── reports/                    # Generated test reports
    ├── coverage/              # Code coverage reports
    ├── html/                  # HTML test reports
    └── performance/           # Performance test reports
```

## Test Categories

### Unit Tests (`tests/unit/`)
- Test individual components in isolation
- Mock external dependencies
- Fast execution (< 1 second per test)
- High code coverage focus

### Integration Tests (`tests/integration/`)
- Test component interactions
- Use real database and Redis instances
- Test API endpoints with full request/response cycle
- Validate data persistence and retrieval

### End-to-End Tests (`tests/e2e/`)
- Test complete business workflows
- Simulate real user scenarios
- Test from API request to final result
- Include error handling and recovery

### Performance Tests (`tests/performance/`)
- Load testing with Locust
- Response time validation
- Resource usage monitoring
- Scalability testing

### Security Tests (`tests/security/`)
- Authentication and authorization testing
- Input validation and sanitization
- Vulnerability assessment
- Rate limiting and abuse prevention

## Running Tests

### Prerequisites

1. **Docker and Docker Compose** - Required for containerized testing
2. **Python 3.11+** - For local test execution
3. **PostgreSQL and Redis** - For integration tests

### Using Docker (Recommended)

#### Start Test Environment
```bash
make test-env-up
```

#### Run All Tests
```bash
make test
```

#### Run Specific Test Categories
```bash
make test-unit          # Unit tests only
make test-integration   # Integration tests only
make test-e2e          # End-to-end tests only
make test-performance  # Performance tests only
make test-security     # Security tests only
```

#### Run Tests with Coverage
```bash
make test-coverage
```

#### Test Infrastructure Setup
```bash
make test-infrastructure
```

#### Standalone Test Execution
```bash
make test-standalone    # Runs tests in isolated environment
```

#### Stop Test Environment
```bash
make test-env-down
```

### Local Testing

#### Setup Local Test Environment
```bash
# Start test services
make test-env-up

# Run tests locally
make test-local
```

#### Direct pytest Execution
```bash
# Set environment variables
export ENVIRONMENT=testing
export DATABASE_URL=postgresql://enterprise_test_user:enterprise_test_pass@localhost:5433/enterprise_test_db
export REDIS_URL=redis://localhost:6380/0

# Run tests
pytest tests/ -v
pytest tests/ -v -m unit                    # Unit tests only
pytest tests/ -v -m "not slow"             # Exclude slow tests
pytest tests/ -v --cov=app                 # With coverage
```

## Test Configuration

### Environment Variables

The test suite uses the following environment variables (defined in `.env.test`):

```bash
ENVIRONMENT=testing
DATABASE_URL=postgresql://enterprise_test_user:enterprise_test_pass@localhost:5433/enterprise_test_db
REDIS_URL=redis://localhost:6380/0
SECRET_KEY=test-secret-key-for-testing-only-32-chars-minimum
# ... additional test-specific configurations
```

### pytest Configuration

Test behavior is configured in `pytest.ini`:

- **Test Discovery**: Automatically finds `test_*.py` files
- **Markers**: Categorize tests (unit, integration, e2e, etc.)
- **Coverage**: Automatic code coverage reporting
- **Output**: HTML reports and terminal output
- **Async Support**: Automatic async test handling

### Test Markers

Use pytest markers to categorize and filter tests:

```python
@pytest.mark.unit           # Unit test
@pytest.mark.integration    # Integration test
@pytest.mark.e2e           # End-to-end test
@pytest.mark.performance   # Performance test
@pytest.mark.security      # Security test
@pytest.mark.slow          # Slow running test
@pytest.mark.external_deps # Requires external dependencies
@pytest.mark.database      # Requires database
@pytest.mark.redis         # Requires Redis
@pytest.mark.celery        # Requires Celery
```

## Writing Tests

### Basic Test Structure

```python
import pytest
from tests.utils.test_helpers import APITestHelper, DatabaseTestHelper

@pytest.mark.unit
def test_example_unit():
    """Test individual component."""
    # Test logic here
    assert True

@pytest.mark.integration
@pytest.mark.database
def test_example_integration(db_session, api_helper):
    """Test component integration."""
    # Use database and API helpers
    db_helper = DatabaseTestHelper(db_session)
    
    # Test logic here
    assert True

@pytest.mark.e2e
async def test_example_e2e(async_test_client):
    """Test complete workflow."""
    # End-to-end test logic
    response = await async_test_client.get("/api/v1/health")
    assert response.status_code == 200
```

### Using Test Helpers

The test suite provides several helper classes:

```python
# Database operations
db_helper = DatabaseTestHelper(db_session)
user = db_helper.create_record(User, email="test@example.com")

# API testing
api_helper = APITestHelper(test_client)
response = api_helper.post_json("/api/v1/users", {"email": "test@example.com"})
api_helper.assert_status_code(response, 201)

# Performance testing
with TestTimer("api_call") as timer:
    response = test_client.get("/api/v1/users")
timer.assert_duration_under(0.5)  # 500ms threshold

# File operations
file_helper = FileTestHelper()
audio_file = file_helper.create_temp_audio_file(duration_seconds=30)
```

### Mock External Services

```python
@pytest.mark.integration
def test_with_mocked_services(mock_aws_s3, mock_musicbrainz):
    """Test with mocked external services."""
    # Configure mock responses
    mock_aws_s3.upload_fileobj.return_value = None
    
    # Test logic using mocked services
    # ...
```

## Test Data Management

### Factories

Use factories to generate consistent test data:

```python
# Will be implemented in task 2
from tests.factories import UserFactory, ReleaseFactory

user = UserFactory.create(email="test@example.com")
release = ReleaseFactory.create(title="Test Album", artist="Test Artist")
```

### Fixtures

Use fixtures for sample data:

```python
def test_with_sample_data(sample_release_data, sample_partner_data):
    """Test using predefined sample data."""
    assert sample_release_data["title"] == "Test Album"
    assert sample_partner_data["name"] == "Test Partner"
```

## Test Reports

### Coverage Reports

Coverage reports are generated automatically:

- **Terminal**: Summary displayed after test run
- **HTML**: Detailed report at `tests/reports/coverage/index.html`
- **XML**: Machine-readable report at `tests/reports/coverage.xml`

### HTML Test Reports

Detailed test reports are generated at `tests/reports/html/report.html` including:

- Test results and status
- Execution times
- Error details and stack traces
- Test categorization

### Performance Reports

Performance test results are saved to `tests/reports/performance/` including:

- Response time metrics
- Load test results
- Resource usage statistics
- Performance trend analysis

## Continuous Integration

The test suite is designed to integrate with CI/CD pipelines:

### GitHub Actions Example

```yaml
name: Test Suite
on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - name: Run Test Suite
        run: |
          make test-standalone
      - name: Upload Coverage
        uses: codecov/codecov-action@v1
        with:
          file: tests/reports/coverage.xml
```

## Troubleshooting

### Common Issues

1. **Database Connection Errors**
   ```bash
   # Check if test database is running
   docker-compose -f docker-compose.test.yml ps postgres-test
   
   # Check database logs
   make test-env-logs
   ```

2. **Redis Connection Errors**
   ```bash
   # Check if test Redis is running
   docker-compose -f docker-compose.test.yml ps redis-test
   
   # Test Redis connectivity
   redis-cli -h localhost -p 6380 ping
   ```

3. **Port Conflicts**
   ```bash
   # Check for port conflicts
   netstat -tulpn | grep -E ':(5433|6380|8001)'
   
   # Stop conflicting services
   make test-env-down
   ```

4. **Slow Test Execution**
   ```bash
   # Run only fast tests
   pytest tests/ -v -m "not slow"
   
   # Run tests in parallel
   pytest tests/ -v -n auto
   ```

### Debug Mode

Enable debug mode for detailed test output:

```bash
# Set debug environment
export DEBUG=true
export LOG_LEVEL=DEBUG

# Run tests with verbose output
pytest tests/ -v -s --tb=long
```

### Test Isolation Issues

If tests are interfering with each other:

```bash
# Run tests with database rollback (default)
pytest tests/ -v

# Run each test in separate database transaction
pytest tests/ -v --forked
```

## Best Practices

1. **Test Isolation**: Each test should be independent and not rely on other tests
2. **Fast Feedback**: Unit tests should execute quickly (< 1 second)
3. **Clear Naming**: Test names should clearly describe what is being tested
4. **Comprehensive Coverage**: Aim for high code coverage but focus on critical paths
5. **Mock External Services**: Use mocks for external dependencies in unit tests
6. **Real Services for Integration**: Use real services for integration tests
7. **Performance Baselines**: Establish and maintain performance benchmarks
8. **Security Testing**: Include security tests for all user inputs and authentication

## Contributing

When adding new tests:

1. Choose the appropriate test category (unit, integration, e2e, etc.)
2. Use existing fixtures and helpers when possible
3. Add appropriate pytest markers
4. Include docstrings explaining the test purpose
5. Follow the existing naming conventions
6. Update this README if adding new test utilities or patterns

For questions or issues with the testing infrastructure, please refer to the project documentation or create an issue in the project repository.