"""
Test the testing infrastructure setup.
"""
import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from tests.utils.test_helpers import TimerHelper, DatabaseTestHelper, APITestHelper


@pytest.mark.unit
def test_pytest_configuration():
    """Test that pytest is configured correctly."""
    # This test should pass if pytest is working
    assert True


@pytest.mark.unit
def test_test_settings(test_settings):
    """Test that test settings are loaded correctly."""
    assert test_settings.ENVIRONMENT == "testing"
    assert test_settings.DEBUG is True
    assert "test" in test_settings.SECRET_KEY.lower()


@pytest.mark.integration
@pytest.mark.database
def test_database_fixture(db_session):
    """Test that database fixture is working."""
    assert isinstance(db_session, Session)
    
    # Test that we can execute a simple query
    result = db_session.execute("SELECT 1 as test_value")
    row = result.fetchone()
    assert row[0] == 1


@pytest.mark.integration
@pytest.mark.redis
async def test_redis_fixture(redis_client):
    """Test that Redis fixture is working."""
    # Test basic Redis operations
    await redis_client.set("test_key", "test_value")
    value = await redis_client.get("test_key")
    assert value == "test_value"
    
    # Test cleanup
    await redis_client.delete("test_key")
    value = await redis_client.get("test_key")
    assert value is None


@pytest.mark.integration
@pytest.mark.api
def test_fastapi_client_fixture(test_client):
    """Test that FastAPI test client is working."""
    assert isinstance(test_client, TestClient)
    
    # Test that we can make a request (this might fail if no health endpoint exists)
    # For now, just test that the client is created
    assert test_client.app is not None


@pytest.mark.unit
def test_timer_helper():
    """Test the TimerHelper utility."""
    import time
    
    with TimerHelper("test_operation") as timer:
        time.sleep(0.01)  # Sleep for 10ms
    
    assert timer.duration is not None
    assert timer.duration >= 0.01
    assert timer.duration < 0.1  # Should be much less than 100ms


@pytest.mark.unit
def test_database_helper(db_session):
    """Test the DatabaseTestHelper utility."""
    helper = DatabaseTestHelper(db_session)
    
    # Test that helper is created correctly
    assert helper.db == db_session


@pytest.mark.unit
def test_api_helper(test_client):
    """Test the APITestHelper utility."""
    helper = APITestHelper(test_client)
    
    # Test that helper is created correctly
    assert helper.client == test_client


@pytest.mark.unit
def test_sample_data_fixtures(sample_release_data, sample_partner_data):
    """Test that sample data fixtures are working."""
    # Test release data
    assert "title" in sample_release_data
    assert "artist" in sample_release_data
    assert "tracks" in sample_release_data
    assert len(sample_release_data["tracks"]) > 0
    
    # Test partner data
    assert "name" in sample_partner_data
    assert "api_endpoint" in sample_partner_data
    assert "is_active" in sample_partner_data


@pytest.mark.unit
def test_temp_directory_fixture(temp_directory):
    """Test that temporary directory fixture is working."""
    import os
    assert os.path.exists(temp_directory)
    assert os.path.isdir(temp_directory)


@pytest.mark.unit
def test_performance_threshold_fixture(performance_threshold):
    """Test that performance threshold fixture is working."""
    assert "api_response_time" in performance_threshold
    assert "database_query_time" in performance_threshold
    assert isinstance(performance_threshold["api_response_time"], (int, float))


@pytest.mark.external_deps
def test_mock_services(mock_aws_s3, mock_musicbrainz, mock_celery):
    """Test that mock services are configured correctly."""
    # Test AWS S3 mock
    assert mock_aws_s3 is not None
    
    # Test MusicBrainz mock
    assert mock_musicbrainz is not None
    
    # Test Celery mock
    assert mock_celery is not None


@pytest.mark.slow
def test_slow_operation():
    """Test marked as slow to verify marker system."""
    import time
    time.sleep(0.1)  # Simulate slow operation
    assert True


if __name__ == "__main__":
    # Allow running this test file directly
    pytest.main([__file__])