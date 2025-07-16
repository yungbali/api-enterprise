"""
Test helper utilities and common functions.
"""
import asyncio
import json
import tempfile
import time
from typing import Any, Dict, List, Optional, Union
from unittest.mock import Mock, patch
from pathlib import Path

import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session


class TimerHelper:
    """Context manager for timing test operations."""
    
    def __init__(self, name: str = "operation"):
        self.name = name
        self.start_time = None
        self.end_time = None
        self.duration = None
    
    def __enter__(self):
        self.start_time = time.time()
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        self.end_time = time.time()
        self.duration = self.end_time - self.start_time
    
    def assert_duration_under(self, max_seconds: float):
        """Assert that the operation completed within the specified time."""
        assert self.duration is not None, "Timer was not used as context manager"
        assert self.duration < max_seconds, (
            f"{self.name} took {self.duration:.3f}s, expected under {max_seconds}s"
        )


class DatabaseTestHelper:
    """Helper class for database testing operations."""
    
    def __init__(self, db_session: Session):
        self.db = db_session
    
    def count_records(self, model_class) -> int:
        """Count records in a table."""
        return self.db.query(model_class).count()
    
    def create_record(self, model_class, **kwargs):
        """Create and persist a record."""
        record = model_class(**kwargs)
        self.db.add(record)
        self.db.commit()
        self.db.refresh(record)
        return record
    
    def get_record_by_id(self, model_class, record_id: int):
        """Get a record by ID."""
        return self.db.query(model_class).filter(model_class.id == record_id).first()
    
    def delete_all_records(self, model_class):
        """Delete all records from a table."""
        self.db.query(model_class).delete()
        self.db.commit()


class APITestHelper:
    """Helper class for API testing operations."""
    
    def __init__(self, client: TestClient):
        self.client = client
    
    def post_json(self, url: str, data: Dict[str, Any], headers: Optional[Dict[str, str]] = None) -> Dict[str, Any]:
        """Make a POST request with JSON data."""
        response = self.client.post(url, json=data, headers=headers or {})
        return {
            "status_code": response.status_code,
            "data": response.json() if response.content else None,
            "headers": dict(response.headers)
        }
    
    def get_json(self, url: str, params: Optional[Dict[str, Any]] = None, headers: Optional[Dict[str, str]] = None) -> Dict[str, Any]:
        """Make a GET request and return JSON response."""
        response = self.client.get(url, params=params or {}, headers=headers or {})
        return {
            "status_code": response.status_code,
            "data": response.json() if response.content else None,
            "headers": dict(response.headers)
        }
    
    def put_json(self, url: str, data: Dict[str, Any], headers: Optional[Dict[str, str]] = None) -> Dict[str, Any]:
        """Make a PUT request with JSON data."""
        response = self.client.put(url, json=data, headers=headers or {})
        return {
            "status_code": response.status_code,
            "data": response.json() if response.content else None,
            "headers": dict(response.headers)
        }
    
    def delete_json(self, url: str, headers: Optional[Dict[str, str]] = None) -> Dict[str, Any]:
        """Make a DELETE request."""
        response = self.client.delete(url, headers=headers or {})
        return {
            "status_code": response.status_code,
            "data": response.json() if response.content else None,
            "headers": dict(response.headers)
        }
    
    def assert_status_code(self, response: Dict[str, Any], expected_code: int):
        """Assert response status code."""
        assert response["status_code"] == expected_code, (
            f"Expected status {expected_code}, got {response['status_code']}. "
            f"Response: {response.get('data')}"
        )
    
    def assert_response_contains(self, response: Dict[str, Any], key: str, value: Any = None):
        """Assert response contains a key and optionally a specific value."""
        assert response["data"] is not None, "Response data is None"
        assert key in response["data"], f"Key '{key}' not found in response: {response['data']}"
        
        if value is not None:
            assert response["data"][key] == value, (
                f"Expected {key}={value}, got {response['data'][key]}"
            )


class FileTestHelper:
    """Helper class for file testing operations."""
    
    @staticmethod
    def create_temp_file(content: Union[str, bytes], suffix: str = ".tmp") -> str:
        """Create a temporary file with content."""
        with tempfile.NamedTemporaryFile(mode='wb' if isinstance(content, bytes) else 'w', 
                                       suffix=suffix, delete=False) as tmp_file:
            tmp_file.write(content)
            return tmp_file.name
    
    @staticmethod
    def create_temp_audio_file(duration_seconds: int = 30) -> str:
        """Create a temporary audio file for testing."""
        # Create a minimal MP3-like file for testing
        # This is not a real MP3, just dummy data with MP3 header-like bytes
        mp3_header = b'\xff\xfb\x90\x00'  # MP3 frame header
        dummy_data = b'\x00' * (duration_seconds * 1000)  # Dummy audio data
        content = mp3_header + dummy_data
        
        return FileTestHelper.create_temp_file(content, suffix=".mp3")
    
    @staticmethod
    def create_temp_image_file(width: int = 100, height: int = 100) -> str:
        """Create a temporary image file for testing."""
        # Create a minimal PNG-like file for testing
        png_header = b'\x89PNG\r\n\x1a\n'
        dummy_data = b'\x00' * (width * height * 3)  # Dummy image data
        content = png_header + dummy_data
        
        return FileTestHelper.create_temp_file(content, suffix=".png")


class MockServiceHelper:
    """Helper class for mocking external services."""
    
    @staticmethod
    def mock_successful_response(data: Dict[str, Any], status_code: int = 200):
        """Create a mock successful HTTP response."""
        mock_response = Mock()
        mock_response.status_code = status_code
        mock_response.json.return_value = data
        mock_response.text = json.dumps(data)
        mock_response.content = json.dumps(data).encode()
        return mock_response
    
    @staticmethod
    def mock_error_response(status_code: int = 500, error_message: str = "Internal Server Error"):
        """Create a mock error HTTP response."""
        mock_response = Mock()
        mock_response.status_code = status_code
        mock_response.json.return_value = {"error": error_message}
        mock_response.text = json.dumps({"error": error_message})
        mock_response.content = json.dumps({"error": error_message}).encode()
        mock_response.raise_for_status.side_effect = Exception(error_message)
        return mock_response
    
    @staticmethod
    def mock_timeout_response():
        """Create a mock timeout response."""
        mock_response = Mock()
        mock_response.side_effect = asyncio.TimeoutError("Request timed out")
        return mock_response


class AssertionHelper:
    """Helper class for common test assertions."""
    
    @staticmethod
    def assert_dict_contains(actual: Dict[str, Any], expected: Dict[str, Any]):
        """Assert that actual dictionary contains all key-value pairs from expected."""
        for key, value in expected.items():
            assert key in actual, f"Key '{key}' not found in {actual}"
            assert actual[key] == value, f"Expected {key}={value}, got {actual[key]}"
    
    @staticmethod
    def assert_list_contains_item(actual_list: List[Any], expected_item: Any):
        """Assert that list contains the expected item."""
        assert expected_item in actual_list, f"Item {expected_item} not found in {actual_list}"
    
    @staticmethod
    def assert_datetime_recent(dt, max_seconds_ago: int = 60):
        """Assert that datetime is recent (within max_seconds_ago)."""
        from datetime import datetime, timezone
        now = datetime.now(timezone.utc)
        if dt.tzinfo is None:
            dt = dt.replace(tzinfo=timezone.utc)
        
        diff = (now - dt).total_seconds()
        assert diff <= max_seconds_ago, f"Datetime {dt} is {diff}s ago, expected within {max_seconds_ago}s"
    
    @staticmethod
    def assert_email_format(email: str):
        """Assert that string is a valid email format."""
        import re
        email_pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        assert re.match(email_pattern, email), f"'{email}' is not a valid email format"
    
    @staticmethod
    def assert_uuid_format(uuid_string: str):
        """Assert that string is a valid UUID format."""
        import re
        uuid_pattern = r'^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$'
        assert re.match(uuid_pattern, uuid_string.lower()), f"'{uuid_string}' is not a valid UUID format"


class PerformanceTestHelper:
    """Helper class for performance testing."""
    
    @staticmethod
    def measure_execution_time(func, *args, **kwargs) -> tuple:
        """Measure function execution time and return (result, duration)."""
        start_time = time.time()
        result = func(*args, **kwargs)
        duration = time.time() - start_time
        return result, duration
    
    @staticmethod
    async def measure_async_execution_time(coro) -> tuple:
        """Measure async function execution time and return (result, duration)."""
        start_time = time.time()
        result = await coro
        duration = time.time() - start_time
        return result, duration
    
    @staticmethod
    def assert_performance_threshold(duration: float, threshold: float, operation_name: str = "operation"):
        """Assert that operation completed within performance threshold."""
        assert duration <= threshold, (
            f"{operation_name} took {duration:.3f}s, expected under {threshold}s"
        )


# Pytest fixtures using helpers
@pytest.fixture
def timer_helper():
    """Provide a timer helper instance."""
    return TimerHelper


@pytest.fixture
def db_helper(db_session):
    """Provide a database test helper."""
    return DatabaseTestHelper(db_session)


@pytest.fixture
def api_helper(test_client):
    """Provide an API test helper."""
    return APITestHelper(test_client)


@pytest.fixture
def file_helper():
    """Provide a file test helper."""
    return FileTestHelper


@pytest.fixture
def mock_helper():
    """Provide a mock service helper."""
    return MockServiceHelper


@pytest.fixture
def assert_helper():
    """Provide an assertion helper."""
    return AssertionHelper


@pytest.fixture
def perf_helper():
    """Provide a performance test helper."""
    return PerformanceTestHelper