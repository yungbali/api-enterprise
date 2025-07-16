"""
Test helper utilities and functions.
"""
import asyncio
import json
import tempfile
import os
from typing import Dict, Any, List, Optional, Union
from datetime import datetime, timedelta
from unittest.mock import Mock, patch
import uuid

from faker import Faker
from sqlalchemy.orm import Session
from fastapi.testclient import TestClient
import httpx

fake = Faker()


class TestDataHelper:
    """Helper class for managing test data."""
    
    @staticmethod
    def create_temp_audio_file(format: str = "mp3", size_mb: int = 5) -> str:
        """Create a temporary audio file for testing."""
        with tempfile.NamedTemporaryFile(suffix=f".{format}", delete=False) as tmp_file:
            # Create fake audio data
            fake_data = b"fake audio data " * (size_mb * 1024 * 64)  # Approximate size
            tmp_file.write(fake_data)
            tmp_file.flush()
            return tmp_file.name
    
    @staticmethod
    def create_temp_image_file(format: str = "jpg", width: int = 3000, height: int = 3000) -> str:
        """Create a temporary image file for testing."""
        with tempfile.NamedTemporaryFile(suffix=f".{format}", delete=False) as tmp_file:
            # Create fake image data
            fake_data = b"fake image data " * 1024  # Simple fake image
            tmp_file.write(fake_data)
            tmp_file.flush()
            return tmp_file.name
    
    @staticmethod
    def cleanup_temp_file(file_path: str):
        """Clean up temporary file."""
        try:
            os.unlink(file_path)
        except FileNotFoundError:
            pass
    
    @staticmethod
    def generate_isrc() -> str:
        """Generate a valid ISRC code."""
        country = fake.country_code()
        registrant = fake.lexify(text="???").upper()
        year = fake.random_int(min=0, max=99)
        designation = fake.random_int(min=1, max=99999)
        return f"{country}{registrant}{year:02d}{designation:05d}"
    
    @staticmethod
    def generate_upc() -> str:
        """Generate a valid UPC code."""
        return fake.ean13()
    
    @staticmethod
    def generate_grid() -> str:
        """Generate a valid GRid identifier."""
        return f"A1-{fake.random_number(digits=10)}"
    
    @staticmethod
    def generate_release_metadata() -> Dict[str, Any]:
        """Generate comprehensive release metadata."""
        return {
            "title": fake.catch_phrase(),
            "artist": fake.name(),
            "label": f"{fake.word().title()} Records",
            "genre": fake.random_element(elements=[
                "Electronic", "Rock", "Pop", "Hip-Hop", "Jazz", "Classical"
            ]),
            "release_date": fake.date_between(start_date="-1y", end_date="+6m").isoformat(),
            "copyright_text": f"℗ {fake.year()} {fake.company()}",
            "description": fake.text(max_nb_chars=300),
            "language": fake.random_element(elements=["en", "es", "fr", "de"]),
            "territory": fake.random_element(elements=["US", "GB", "DE", "FR", "WW"])
        }
    
    @staticmethod
    def generate_track_metadata(track_number: int = 1) -> Dict[str, Any]:
        """Generate track metadata."""
        return {
            "title": fake.catch_phrase(),
            "artist": fake.name(),
            "track_number": track_number,
            "duration_ms": fake.random_int(min=120000, max=480000),
            "isrc": TestDataHelper.generate_isrc(),
            "explicit": fake.boolean(),
            "genre": fake.random_element(elements=[
                "Electronic", "Rock", "Pop", "Hip-Hop", "Jazz"
            ])
        }


class APITestHelper:
    """Helper class for API testing."""
    
    @staticmethod
    def create_auth_headers(token: str) -> Dict[str, str]:
        """Create authentication headers."""
        return {"Authorization": f"Bearer {token}"}
    
    @staticmethod
    def create_api_key_headers(api_key: str) -> Dict[str, str]:
        """Create API key headers."""
        return {"X-API-Key": api_key}
    
    @staticmethod
    def assert_response_structure(response_data: Dict[str, Any], expected_keys: List[str]):
        """Assert that response contains expected keys."""
        for key in expected_keys:
            assert key in response_data, f"Expected key '{key}' not found in response"
    
    @staticmethod
    def assert_error_response(response_data: Dict[str, Any], expected_status: int = 400):
        """Assert error response structure."""
        assert "error" in response_data or "detail" in response_data
        if "error" in response_data:
            assert "message" in response_data["error"]
    
    @staticmethod
    def assert_pagination_response(response_data: Dict[str, Any]):
        """Assert pagination response structure."""
        expected_keys = ["items", "total", "page", "size", "pages"]
        APITestHelper.assert_response_structure(response_data, expected_keys)
    
    @staticmethod
    def create_multipart_file_data(file_path: str, field_name: str = "file") -> Dict[str, Any]:
        """Create multipart file data for upload testing."""
        with open(file_path, "rb") as f:
            return {field_name: (os.path.basename(file_path), f.read(), "application/octet-stream")}


class DatabaseTestHelper:
    """Helper class for database testing."""
    
    @staticmethod
    def count_records(session: Session, model_class) -> int:
        """Count records in a table."""
        return session.query(model_class).count()
    
    @staticmethod
    def get_record_by_id(session: Session, model_class, record_id: int):
        """Get a record by ID."""
        return session.query(model_class).filter(model_class.id == record_id).first()
    
    @staticmethod
    def delete_all_records(session: Session, model_class):
        """Delete all records from a table."""
        session.query(model_class).delete()
        session.commit()
    
    @staticmethod
    def assert_record_exists(session: Session, model_class, **filters):
        """Assert that a record exists with given filters."""
        query = session.query(model_class)
        for key, value in filters.items():
            query = query.filter(getattr(model_class, key) == value)
        
        record = query.first()
        assert record is not None, f"Record not found with filters: {filters}"
        return record
    
    @staticmethod
    def assert_record_count(session: Session, model_class, expected_count: int):
        """Assert the number of records in a table."""
        actual_count = DatabaseTestHelper.count_records(session, model_class)
        assert actual_count == expected_count, f"Expected {expected_count} records, found {actual_count}"


class MockServiceHelper:
    """Helper class for creating mock services."""
    
    @staticmethod
    def create_mock_http_response(status_code: int = 200, json_data: Optional[Dict] = None, 
                                 text_data: Optional[str] = None) -> Mock:
        """Create a mock HTTP response."""
        mock_response = Mock()
        mock_response.status_code = status_code
        
        if json_data:
            mock_response.json.return_value = json_data
        if text_data:
            mock_response.text = text_data
        
        return mock_response
    
    @staticmethod
    def create_musicbrainz_mock_response(recording_id: str = None) -> Dict[str, Any]:
        """Create a mock MusicBrainz API response."""
        if not recording_id:
            recording_id = str(uuid.uuid4())
        
        return {
            "recordings": [{
                "id": recording_id,
                "title": fake.catch_phrase(),
                "artist-credit": [{"artist": {"name": fake.name()}}],
                "length": fake.random_int(min=120000, max=480000),
                "isrcs": [TestDataHelper.generate_isrc()]
            }]
        }
    
    @staticmethod
    def create_aws_s3_mock() -> Mock:
        """Create a mock AWS S3 client."""
        mock_s3 = Mock()
        
        # Mock common S3 operations
        mock_s3.upload_fileobj.return_value = None
        mock_s3.download_fileobj.return_value = None
        mock_s3.delete_object.return_value = {"DeleteMarker": True}
        mock_s3.head_object.return_value = {
            "ContentLength": fake.random_int(min=1000, max=100000000),
            "LastModified": fake.date_time(),
            "ETag": f'"{fake.md5()}"'
        }
        mock_s3.list_objects_v2.return_value = {
            "Contents": [
                {
                    "Key": f"test-file-{i}.mp3",
                    "Size": fake.random_int(min=1000000, max=50000000),
                    "LastModified": fake.date_time()
                }
                for i in range(3)
            ]
        }
        
        return mock_s3
    
    @staticmethod
    def create_partner_api_mock_response(success: bool = True) -> Dict[str, Any]:
        """Create a mock partner API response."""
        if success:
            return {
                "status": "success",
                "delivery_id": str(uuid.uuid4()),
                "message": "Release delivered successfully",
                "timestamp": datetime.utcnow().isoformat()
            }
        else:
            return {
                "status": "error",
                "error_code": "VALIDATION_FAILED",
                "message": "Invalid release metadata",
                "timestamp": datetime.utcnow().isoformat()
            }


class PerformanceTestHelper:
    """Helper class for performance testing."""
    
    @staticmethod
    def measure_execution_time(func, *args, **kwargs) -> tuple:
        """Measure function execution time."""
        start_time = datetime.utcnow()
        result = func(*args, **kwargs)
        end_time = datetime.utcnow()
        execution_time = (end_time - start_time).total_seconds()
        return result, execution_time
    
    @staticmethod
    async def measure_async_execution_time(coro) -> tuple:
        """Measure async function execution time."""
        start_time = datetime.utcnow()
        result = await coro
        end_time = datetime.utcnow()
        execution_time = (end_time - start_time).total_seconds()
        return result, execution_time
    
    @staticmethod
    def assert_execution_time(execution_time: float, max_time: float):
        """Assert that execution time is within acceptable limits."""
        assert execution_time <= max_time, f"Execution time {execution_time}s exceeded limit {max_time}s"
    
    @staticmethod
    def create_load_test_data(count: int) -> List[Dict[str, Any]]:
        """Create data for load testing."""
        return [TestDataHelper.generate_release_metadata() for _ in range(count)]


class SecurityTestHelper:
    """Helper class for security testing."""
    
    @staticmethod
    def create_sql_injection_payloads() -> List[str]:
        """Create SQL injection test payloads."""
        return [
            "'; DROP TABLE users; --",
            "' OR '1'='1",
            "' UNION SELECT * FROM users --",
            "'; INSERT INTO users (email) VALUES ('hacker@evil.com'); --",
            "' OR 1=1 --"
        ]
    
    @staticmethod
    def create_xss_payloads() -> List[str]:
        """Create XSS test payloads."""
        return [
            "<script>alert('XSS')</script>",
            "javascript:alert('XSS')",
            "<img src=x onerror=alert('XSS')>",
            "<svg onload=alert('XSS')>",
            "';alert('XSS');//"
        ]
    
    @staticmethod
    def create_invalid_auth_tokens() -> List[str]:
        """Create invalid authentication tokens for testing."""
        return [
            "invalid_token",
            "Bearer invalid",
            "",
            "expired_token_" + fake.uuid4(),
            "malformed.jwt.token"
        ]
    
    @staticmethod
    def assert_no_sensitive_data_in_response(response_data: Dict[str, Any]):
        """Assert that response doesn't contain sensitive data."""
        sensitive_fields = [
            "password", "hashed_password", "secret", "private_key",
            "api_key", "token", "client_secret"
        ]
        
        def check_dict(data, path=""):
            if isinstance(data, dict):
                for key, value in data.items():
                    current_path = f"{path}.{key}" if path else key
                    if any(sensitive in key.lower() for sensitive in sensitive_fields):
                        assert False, f"Sensitive field '{key}' found in response at {current_path}"
                    check_dict(value, current_path)
            elif isinstance(data, list):
                for i, item in enumerate(data):
                    check_dict(item, f"{path}[{i}]")
        
        check_dict(response_data)


class AsyncTestHelper:
    """Helper class for async testing."""
    
    @staticmethod
    async def run_concurrent_requests(client: httpx.AsyncClient, requests: List[Dict[str, Any]]) -> List[httpx.Response]:
        """Run multiple HTTP requests concurrently."""
        tasks = []
        for req in requests:
            method = req.get("method", "GET")
            url = req["url"]
            kwargs = {k: v for k, v in req.items() if k not in ["method", "url"]}
            
            if method.upper() == "GET":
                task = client.get(url, **kwargs)
            elif method.upper() == "POST":
                task = client.post(url, **kwargs)
            elif method.upper() == "PUT":
                task = client.put(url, **kwargs)
            elif method.upper() == "DELETE":
                task = client.delete(url, **kwargs)
            else:
                continue
            
            tasks.append(task)
        
        return await asyncio.gather(*tasks)
    
    @staticmethod
    async def assert_concurrent_safety(client: httpx.AsyncClient, requests: List[Dict[str, Any]]):
        """Assert that concurrent requests don't cause race conditions."""
        responses = await AsyncTestHelper.run_concurrent_requests(client, requests)
        
        # Check that all responses are successful or have expected error codes
        for response in responses:
            assert response.status_code in [200, 201, 400, 401, 403, 404, 422], \
                f"Unexpected status code: {response.status_code}"


class ValidationTestHelper:
    """Helper class for validation testing."""
    
    @staticmethod
    def create_invalid_email_addresses() -> List[str]:
        """Create invalid email addresses for testing."""
        return [
            "invalid-email",
            "@example.com",
            "user@",
            "user..name@example.com",
            "user@.com",
            ""
        ]
    
    @staticmethod
    def create_invalid_urls() -> List[str]:
        """Create invalid URLs for testing."""
        return [
            "not-a-url",
            "http://",
            "ftp://invalid",
            "javascript:alert('xss')",
            ""
        ]
    
    @staticmethod
    def create_boundary_test_strings() -> Dict[str, List[str]]:
        """Create strings for boundary testing."""
        return {
            "empty": [""],
            "very_short": ["a"],
            "normal": ["normal string"],
            "long": ["x" * 1000],
            "very_long": ["x" * 10000],
            "unicode": ["🎵 Music 🎶", "Café", "北京"],
            "special_chars": ["!@#$%^&*()", "<>&\"'"],
            "whitespace": [" ", "\t", "\n", "   "]
        }
    
    @staticmethod
    def assert_validation_error(response_data: Dict[str, Any], field_name: str):
        """Assert that validation error is returned for specific field."""
        assert "detail" in response_data or "errors" in response_data
        
        # Check if field is mentioned in error details
        error_text = json.dumps(response_data).lower()
        assert field_name.lower() in error_text, f"Field '{field_name}' not mentioned in validation error"


# Context managers for testing
class TemporaryFileContext:
    """Context manager for temporary files."""
    
    def __init__(self, suffix: str = ".tmp", content: bytes = b"test content"):
        self.suffix = suffix
        self.content = content
        self.file_path = None
    
    def __enter__(self):
        with tempfile.NamedTemporaryFile(suffix=self.suffix, delete=False) as tmp_file:
            tmp_file.write(self.content)
            tmp_file.flush()
            self.file_path = tmp_file.name
        return self.file_path
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        if self.file_path:
            TestDataHelper.cleanup_temp_file(self.file_path)


class MockEnvironmentContext:
    """Context manager for mocking environment variables."""
    
    def __init__(self, env_vars: Dict[str, str]):
        self.env_vars = env_vars
        self.original_values = {}
    
    def __enter__(self):
        for key, value in self.env_vars.items():
            self.original_values[key] = os.environ.get(key)
            os.environ[key] = value
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        for key in self.env_vars:
            if self.original_values[key] is None:
                os.environ.pop(key, None)
            else:
                os.environ[key] = self.original_values[key]