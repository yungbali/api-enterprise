#!/bin/bash

# Test Infrastructure Validation Script
# This script validates that the testing infrastructure is properly set up

set -e

echo "🧪 Testing Infrastructure Validation"
echo "===================================="

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Function to print status
print_status() {
    if [ $1 -eq 0 ]; then
        echo -e "${GREEN}✅ $2${NC}"
    else
        echo -e "${RED}❌ $2${NC}"
        exit 1
    fi
}

print_info() {
    echo -e "${YELLOW}ℹ️  $1${NC}"
}

# Check if pytest is available
print_info "Checking pytest installation..."
python3 -m pytest --version > /dev/null 2>&1
print_status $? "pytest is installed"

# Check if required Python packages are available
print_info "Checking required Python packages..."
python3 -c "import fastapi, sqlalchemy, redis, faker, httpx" > /dev/null 2>&1
print_status $? "Required Python packages are available"

# Check pytest configuration
print_info "Validating pytest configuration..."
python3 -m pytest --collect-only tests/ > /dev/null 2>&1
print_status $? "pytest configuration is valid"

# Run basic infrastructure tests
print_info "Running basic infrastructure tests..."
python3 -m pytest tests/test_infrastructure.py -v -k "not redis and not database and not api" --tb=short -q
print_status $? "Basic infrastructure tests passed"

# Check if Docker and Docker Compose are available
print_info "Checking Docker availability..."
docker --version > /dev/null 2>&1
DOCKER_AVAILABLE=$?

docker-compose --version > /dev/null 2>&1 || docker compose version > /dev/null 2>&1
COMPOSE_AVAILABLE=$?

if [ $DOCKER_AVAILABLE -eq 0 ] && [ $COMPOSE_AVAILABLE -eq 0 ]; then
    print_status 0 "Docker and Docker Compose are available"
    
    # Validate Docker Compose test configuration
    print_info "Validating Docker Compose test configuration..."
    docker-compose -f docker-compose.test.yml config > /dev/null 2>&1
    print_status $? "Docker Compose test configuration is valid"
else
    echo -e "${YELLOW}⚠️  Docker/Docker Compose not available - skipping container tests${NC}"
fi

# Check test directory structure
print_info "Validating test directory structure..."
REQUIRED_DIRS=(
    "tests"
    "tests/unit"
    "tests/integration"
    "tests/e2e"
    "tests/performance"
    "tests/security"
    "tests/utils"
    "tests/factories"
    "tests/fixtures"
    "tests/reports"
)

for dir in "${REQUIRED_DIRS[@]}"; do
    if [ -d "$dir" ]; then
        echo -e "${GREEN}  ✅ $dir${NC}"
    else
        echo -e "${RED}  ❌ $dir${NC}"
        exit 1
    fi
done

# Check required configuration files
print_info "Validating configuration files..."
REQUIRED_FILES=(
    "pytest.ini"
    "tests/conftest.py"
    "tests/README.md"
    ".env.test"
    "docker-compose.test.yml"
)

for file in "${REQUIRED_FILES[@]}"; do
    if [ -f "$file" ]; then
        echo -e "${GREEN}  ✅ $file${NC}"
    else
        echo -e "${RED}  ❌ $file${NC}"
        exit 1
    fi
done

# Check WireMock fixtures
print_info "Validating WireMock fixtures..."
if [ -d "tests/fixtures/wiremock/mappings" ] && [ -d "tests/fixtures/wiremock/__files" ]; then
    print_status 0 "WireMock fixtures directory structure is correct"
else
    print_status 1 "WireMock fixtures directory structure is missing"
fi

# Test pytest markers
print_info "Testing pytest markers..."
python3 -m pytest --markers > /tmp/pytest_markers.txt 2>&1
if grep -q "unit:" /tmp/pytest_markers.txt; then
    print_status 0 "pytest markers are configured"
else
    print_status 1 "pytest markers are not configured properly"
fi
rm -f /tmp/pytest_markers.txt

# Generate a test report to verify reporting works
print_info "Testing report generation..."
python3 -m pytest tests/test_infrastructure.py::test_pytest_configuration --html=tests/reports/html/test-report.html --self-contained-html -q > /dev/null 2>&1
if [ -f "tests/reports/html/test-report.html" ]; then
    print_status 0 "HTML report generation works"
else
    print_status 1 "HTML report generation failed"
fi

echo ""
echo -e "${GREEN}🎉 All infrastructure validation checks passed!${NC}"
echo ""
echo "Next steps:"
echo "1. Start test services: make test-env-up"
echo "2. Run full test suite: make test"
echo "3. Run specific test categories: make test-unit, make test-integration, etc."
echo "4. View test reports in tests/reports/"
echo ""
echo "For more information, see tests/README.md"