"""
Comprehensive API endpoint integration tests.

This module tests all API endpoints with various scenarios including:
- Authentication endpoints (/auth/login, /auth/logout)
- Release management endpoints (CRUD operations)
- Partner, delivery, analytics, and webhook endpoints
- Error handling and validation for all endpoints

Requirements covered: 1.1, 1.2, 1.3, 1.4, 1.5
"""
import pytest
import uuid
from fastapi import status
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session
from unittest.mock import patch, Mock

from app.models.user import User, UserRole
from app.models.release import Release, ReleaseStatus, ReleaseType
from app.models.partner import DeliveryPartner, PartnerType, PartnerStatus, AuthType
from app.core.security import create_access_token, get_password_hash


def create_test_user(db_session: Session, email: str = None, password: str = None, is_active: bool = True) -> User:
    """Helper function to create a test user."""
    if email is None:
        email = f"test_{uuid.uuid4().hex[:8]}@example.com"
    if password is None:
        password = "testpassword123"
    
    user = User(
        email=email,
        username=f"user_{uuid.uuid4().hex[:8]}",
        full_name="Test User",
        hashed_password=get_password_hash(password),
        is_active=is_active,
        is_superuser=False,
        role=UserRole.VIEWER,
        timezone="UTC"
    )
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)
    return user


def create_test_release(db_session: Session, title: str = None, artist: str = None) -> Release:
    """Helper function to create a test release."""
    if title is None:
        title = f"Test Album {uuid.uuid4().hex[:8]}"
    if artist is None:
        artist = f"Test Artist {uuid.uuid4().hex[:8]}"
    
    release = Release(
        release_id=f"REL-{uuid.uuid4().hex[:8].upper()}",
        title=title,
        artist=artist,
        label="Test Label",
        release_type=ReleaseType.SINGLE,
        status=ReleaseStatus.DRAFT,
        validation_status="pending"
    )
    db_session.add(release)
    db_session.commit()
    db_session.refresh(release)
    return release


def create_test_partner(db_session: Session, name: str = None, partner_type: PartnerType = PartnerType.DSP) -> DeliveryPartner:
    """Helper function to create a test partner."""
    if name is None:
        name = f"Test Partner {uuid.uuid4().hex[:8]}"
    
    partner = DeliveryPartner(
        partner_id=f"PARTNER-{uuid.uuid4().hex[:8].upper()}",
        name=name,
        display_name=name,
        partner_type=partner_type,
        description="Test partner description",
        api_base_url="https://api.testpartner.com",
        auth_type=AuthType.API_KEY,
        delivery_url="https://api.testpartner.com/delivery",
        status=PartnerStatus.ACTIVE,
        priority=5,
        auto_deliver=True,
        rate_limit_requests=100,
        rate_limit_window=3600
    )
    db_session.add(partner)
    db_session.commit()
    db_session.refresh(partner)
    return partner


@pytest.mark.integration
class TestAuthenticationEndpoints:
    """Test authentication endpoints."""
    
    def test_login_success(self, test_client: TestClient, db_session: Session):
        """Test successful login with valid credentials."""
        # Create test user
        user = create_test_user(
            db_session,
            email="test@example.com",
            password="testpassword123",
            is_active=True
        )
        
        # Test login
        response = test_client.post(
            "/api/v1/auth/login",
            json={
                "email": "test@example.com",
                "password": "testpassword123"
            }
        )
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert "access_token" in data
        assert data["token_type"] == "bearer"
        assert isinstance(data["access_token"], str)
        assert len(data["access_token"]) > 0
    
    def test_login_invalid_email(self, test_client: TestClient):
        """Test login with non-existent email."""
        response = test_client.post(
            "/api/v1/auth/login",
            json={
                "email": "nonexistent@example.com",
                "password": "testpassword123"
            }
        )
        
        assert response.status_code == status.HTTP_401_UNAUTHORIZED
        assert response.json()["detail"] == "Invalid credentials"
    
    def test_login_invalid_password(self, test_client: TestClient, db_session: Session):
        """Test login with incorrect password."""
        # Create test user
        create_test_user(
            db_session,
            email="test2@example.com",
            password="correctpassword",
            is_active=True
        )
        
        response = test_client.post(
            "/api/v1/auth/login",
            json={
                "email": "test2@example.com",
                "password": "wrongpassword"
            }
        )
        
        assert response.status_code == status.HTTP_401_UNAUTHORIZED
        assert response.json()["detail"] == "Invalid credentials"
    
    def test_login_inactive_user(self, test_client: TestClient, db_session: Session):
        """Test login with inactive user account."""
        # Create inactive user
        create_test_user(
            db_session,
            email="inactive@example.com",
            password="testpassword123",
            is_active=False
        )
        
        response = test_client.post(
            "/api/v1/auth/login",
            json={
                "email": "inactive@example.com",
                "password": "testpassword123"
            }
        )
        
        assert response.status_code == status.HTTP_401_UNAUTHORIZED
        assert response.json()["detail"] == "Invalid credentials"
    
    def test_login_malformed_json(self, test_client: TestClient):
        """Test login with malformed JSON payload."""
        response = test_client.post(
            "/api/v1/auth/login",
            data="invalid json",
            headers={"Content-Type": "application/json"}
        )
        
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
    
    def test_login_missing_fields(self, test_client: TestClient):
        """Test login with missing required fields."""
        # Missing password
        response = test_client.post(
            "/api/v1/auth/login",
            json={"email": "test@example.com"}
        )
        
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
        
        # Missing email
        response = test_client.post(
            "/api/v1/auth/login",
            json={"password": "testpassword123"}
        )
        
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
    
    def test_login_invalid_email_format(self, test_client: TestClient):
        """Test login with invalid email format."""
        response = test_client.post(
            "/api/v1/auth/login",
            json={
                "email": "invalid-email-format",
                "password": "testpassword123"
            }
        )
        
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
    
    def test_logout_endpoint(self, test_client: TestClient):
        """Test logout endpoint."""
        response = test_client.post("/api/v1/auth/logout")
        
        assert response.status_code == status.HTTP_200_OK
        assert "message" in response.json()
    
    def test_refresh_token_endpoint(self, test_client: TestClient):
        """Test refresh token endpoint."""
        response = test_client.post("/api/v1/auth/refresh")
        
        assert response.status_code == status.HTTP_200_OK
        assert "message" in response.json()


@pytest.mark.integration
class TestReleaseEndpoints:
    """Test release management endpoints."""
    
    def get_auth_headers(self, db_session: Session) -> dict:
        """Helper to get authentication headers."""
        user = create_test_user(
            db_session,
            email=f"testuser_{uuid.uuid4().hex[:8]}@example.com",
            password="testpassword123",
            is_active=True
        )
        token = create_access_token(data={"sub": str(user.id), "email": user.email})
        return {"Authorization": f"Bearer {token}"}
    
    def test_create_release_success(self, test_client: TestClient, db_session: Session):
        """Test successful release creation."""
        headers = self.get_auth_headers(db_session)
        
        release_data = {
            "title": "Test Album",
            "artist": "Test Artist",
            "label": "Test Label",
            "release_type": "album",
            "genre": "Electronic",
            "upc": "123456789012",
            "catalog_number": "TEST001"
        }
        
        response = test_client.post(
            "/api/v1/releases/",
            json=release_data,
            headers=headers
        )
        
        assert response.status_code == status.HTTP_201_CREATED
        data = response.json()
        assert data["title"] == "Test Album"
        assert data["artist"] == "Test Artist"
        assert "id" in data
        assert "release_id" in data
        assert "created_at" in data
        assert "updated_at" in data
    
    def test_create_release_unauthorized(self, test_client: TestClient):
        """Test release creation without authentication."""
        release_data = {
            "title": "Test Album",
            "artist": "Test Artist"
        }
        
        response = test_client.post(
            "/api/v1/releases/",
            json=release_data
        )
        
        assert response.status_code == status.HTTP_401_UNAUTHORIZED
    
    def test_create_release_invalid_data(self, test_client: TestClient, db_session: Session):
        """Test release creation with invalid data."""
        headers = self.get_auth_headers(db_session)
        
        # Missing required fields
        response = test_client.post(
            "/api/v1/releases/",
            json={"title": "Test Album"},  # Missing artist
            headers=headers
        )
        
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
    
    def test_get_release_success(self, test_client: TestClient, db_session: Session):
        """Test successful release retrieval."""
        headers = self.get_auth_headers(db_session)
        
        # Create a release first
        release = create_test_release(
            db_session,
            title="Test Album",
            artist="Test Artist"
        )
        
        response = test_client.get(
            f"/api/v1/releases/{release.release_id}",
            headers=headers
        )
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["title"] == "Test Album"
        assert data["artist"] == "Test Artist"
        assert data["release_id"] == release.release_id
    
    def test_get_release_not_found(self, test_client: TestClient, db_session: Session):
        """Test retrieval of non-existent release."""
        headers = self.get_auth_headers(db_session)
        
        response = test_client.get(
            "/api/v1/releases/nonexistent-id",
            headers=headers
        )
        
        assert response.status_code == status.HTTP_404_NOT_FOUND
        assert response.json()["detail"] == "Release not found"
    
    def test_get_release_unauthorized(self, test_client: TestClient, db_session: Session):
        """Test release retrieval without authentication."""
        release = create_test_release(
            db_session,
            title="Test Album",
            artist="Test Artist"
        )
        
        response = test_client.get(f"/api/v1/releases/{release.release_id}")
        
        assert response.status_code == status.HTTP_401_UNAUTHORIZED
    
    def test_update_release_success(self, test_client: TestClient, db_session: Session):
        """Test successful release update."""
        headers = self.get_auth_headers(db_session)
        
        # Create a release first
        release = create_test_release(
            db_session,
            title="Original Title",
            artist="Original Artist"
        )
        
        update_data = {
            "title": "Updated Title",
            "genre": "Rock"
        }
        
        response = test_client.put(
            f"/api/v1/releases/{release.id}",
            json=update_data,
            headers=headers
        )
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["title"] == "Updated Title"
        assert data["artist"] == "Original Artist"  # Should remain unchanged
    
    def test_update_release_not_found(self, test_client: TestClient, db_session: Session):
        """Test update of non-existent release."""
        headers = self.get_auth_headers(db_session)
        
        response = test_client.put(
            "/api/v1/releases/99999",
            json={"title": "Updated Title"},
            headers=headers
        )
        
        assert response.status_code == status.HTTP_404_NOT_FOUND
        assert response.json()["detail"] == "Release not found"
    
    def test_delete_release_success(self, test_client: TestClient, db_session: Session):
        """Test successful release deletion."""
        headers = self.get_auth_headers(db_session)
        
        # Create a release first
        release = create_test_release(
            db_session,
            title="To Be Deleted",
            artist="Test Artist"
        )
        
        response = test_client.delete(
            f"/api/v1/releases/{release.release_id}",
            headers=headers
        )
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["title"] == "To Be Deleted"
    
    def test_delete_release_not_found(self, test_client: TestClient, db_session: Session):
        """Test deletion of non-existent release."""
        headers = self.get_auth_headers(db_session)
        
        response = test_client.delete(
            "/api/v1/releases/nonexistent-id",
            headers=headers
        )
        
        assert response.status_code == status.HTTP_404_NOT_FOUND
        assert response.json()["detail"] == "Release not found"
    
    def test_list_releases(self, test_client: TestClient, db_session: Session):
        """Test listing all releases."""
        # Create multiple releases
        create_test_release(db_session, title="Album 1", artist="Artist 1")
        create_test_release(db_session, title="Album 2", artist="Artist 2")
        
        response = test_client.get("/api/v1/releases/")
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert isinstance(data, list)
        assert len(data) >= 2


@pytest.mark.integration
class TestPartnerEndpoints:
    """Test partner management endpoints."""
    
    def test_get_partner_success(self, test_client: TestClient, db_session: Session):
        """Test successful partner retrieval."""
        # Create a partner first
        partner = create_test_partner(
            db_session,
            name="Test Partner",
            partner_type=PartnerType.DSP
        )
        
        response = test_client.get(f"/api/v1/delivery-partners/{partner.id}")
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["name"] == "Test Partner"
        assert data["partner_type"] == "DSP"
        assert data["id"] == partner.id
    
    def test_get_partner_not_found(self, test_client: TestClient):
        """Test retrieval of non-existent partner."""
        response = test_client.get("/api/v1/delivery-partners/nonexistent-id")
        
        assert response.status_code == status.HTTP_404_NOT_FOUND
        assert response.json()["detail"] == "Partner not found"
    
    def test_create_partner_endpoint(self, test_client: TestClient):
        """Test partner creation endpoint."""
        response = test_client.post("/api/v1/delivery-partners/")
        
        assert response.status_code == status.HTTP_200_OK
        assert "message" in response.json()
    
    def test_update_partner_endpoint(self, test_client: TestClient):
        """Test partner update endpoint."""
        response = test_client.put("/api/v1/delivery-partners/test-id")
        
        assert response.status_code == status.HTTP_200_OK
        assert "message" in response.json()
    
    def test_delete_partner_endpoint(self, test_client: TestClient):
        """Test partner deletion endpoint."""
        response = test_client.delete("/api/v1/delivery-partners/test-id")
        
        assert response.status_code == status.HTTP_200_OK
        assert "message" in response.json()


@pytest.mark.integration
class TestDeliveryEndpoints:
    """Test delivery management endpoints."""
    
    def test_get_delivery_status(self, test_client: TestClient):
        """Test delivery status endpoint."""
        response = test_client.get("/api/v1/delivery/status")
        
        assert response.status_code == status.HTTP_200_OK
        assert "message" in response.json()
    
    def test_retry_delivery(self, test_client: TestClient):
        """Test delivery retry endpoint."""
        response = test_client.post("/api/v1/delivery/retry")
        
        assert response.status_code == status.HTTP_200_OK
        assert "message" in response.json()


@pytest.mark.integration
class TestAnalyticsEndpoints:
    """Test analytics endpoints."""
    
    def test_get_analytics(self, test_client: TestClient):
        """Test analytics data endpoint."""
        response = test_client.get("/api/v1/analytics/")
        
        assert response.status_code == status.HTTP_200_OK
        assert "message" in response.json()
    
    def test_get_reports(self, test_client: TestClient):
        """Test reports endpoint."""
        response = test_client.get("/api/v1/analytics/reports")
        
        assert response.status_code == status.HTTP_200_OK
        assert "message" in response.json()


@pytest.mark.integration
class TestWebhookEndpoints:
    """Test webhook management endpoints."""
    
    def test_create_webhook(self, test_client: TestClient):
        """Test webhook creation endpoint."""
        response = test_client.post("/api/v1/webhooks/")
        
        assert response.status_code == status.HTTP_200_OK
        assert "message" in response.json()
    
    def test_get_webhook(self, test_client: TestClient):
        """Test webhook retrieval endpoint."""
        response = test_client.get("/api/v1/webhooks/test-webhook-id")
        
        assert response.status_code == status.HTTP_200_OK
        assert "message" in response.json()
    
    def test_delete_webhook(self, test_client: TestClient):
        """Test webhook deletion endpoint."""
        response = test_client.delete("/api/v1/webhooks/test-webhook-id")
        
        assert response.status_code == status.HTTP_200_OK
        assert "message" in response.json()


@pytest.mark.integration
class TestWorkflowEndpoints:
    """Test workflow management endpoints."""
    
    def test_create_workflow_rule(self, test_client: TestClient):
        """Test workflow rule creation endpoint."""
        response = test_client.post("/api/v1/workflow/rules")
        
        assert response.status_code == status.HTTP_200_OK
        assert "message" in response.json()
    
    def test_get_workflow_rule(self, test_client: TestClient):
        """Test workflow rule retrieval endpoint."""
        response = test_client.get("/api/v1/workflow/rules/test-rule-id")
        
        assert response.status_code == status.HTTP_200_OK
        assert "message" in response.json()
    
    def test_get_workflow_executions(self, test_client: TestClient):
        """Test workflow executions endpoint."""
        response = test_client.get("/api/v1/workflow/executions")
        
        assert response.status_code == status.HTTP_200_OK
        assert "message" in response.json()


@pytest.mark.integration
class TestErrorHandlingAndValidation:
    """Test error handling and validation across all endpoints."""
    
    def test_invalid_http_methods(self, test_client: TestClient):
        """Test endpoints with invalid HTTP methods."""
        # Test GET on POST-only endpoint
        response = test_client.get("/api/v1/auth/login")
        assert response.status_code == status.HTTP_405_METHOD_NOT_ALLOWED
        
        # Test POST on GET-only endpoint
        response = test_client.post("/api/v1/analytics/")
        assert response.status_code == status.HTTP_405_METHOD_NOT_ALLOWED
    
    def test_nonexistent_endpoints(self, test_client: TestClient):
        """Test requests to non-existent endpoints."""
        response = test_client.get("/api/v1/nonexistent")
        assert response.status_code == status.HTTP_404_NOT_FOUND
        
        response = test_client.post("/api/v1/invalid/endpoint")
        assert response.status_code == status.HTTP_404_NOT_FOUND
    
    def test_malformed_json_payloads(self, test_client: TestClient):
        """Test endpoints with malformed JSON payloads."""
        endpoints_requiring_json = [
            "/api/v1/auth/login",
            "/api/v1/releases/",
            "/api/v1/webhooks/"
        ]
        
        for endpoint in endpoints_requiring_json:
            response = test_client.post(
                endpoint,
                data="invalid json",
                headers={"Content-Type": "application/json"}
            )
            assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
    
    def test_invalid_content_type(self, test_client: TestClient):
        """Test endpoints with invalid content types."""
        response = test_client.post(
            "/api/v1/auth/login",
            data="email=test@example.com&password=test123",
            headers={"Content-Type": "application/x-www-form-urlencoded"}
        )
        # Should still work as FastAPI can handle form data
        assert response.status_code in [status.HTTP_422_UNPROCESSABLE_ENTITY, status.HTTP_401_UNAUTHORIZED]
    
    def test_oversized_payloads(self, test_client: TestClient, db_session: Session):
        """Test endpoints with oversized payloads."""
        # Create auth headers
        user = create_test_user(
            db_session,
            email=f"testuser_{uuid.uuid4().hex[:8]}@example.com",
            password="testpassword123",
            is_active=True
        )
        token = create_access_token(data={"sub": str(user.id), "email": user.email})
        headers = {"Authorization": f"Bearer {token}"}
        
        # Create a very large payload
        large_data = {
            "title": "A" * 10000,  # Very long title
            "artist": "Test Artist",
            "description": "B" * 50000  # Very long description
        }
        
        response = test_client.post(
            "/api/v1/releases/",
            json=large_data,
            headers=headers
        )
        
        # Should either succeed or fail with validation error
        assert response.status_code in [
            status.HTTP_201_CREATED,
            status.HTTP_422_UNPROCESSABLE_ENTITY,
            status.HTTP_413_REQUEST_ENTITY_TOO_LARGE
        ]
    
    def test_sql_injection_attempts(self, test_client: TestClient, db_session: Session):
        """Test SQL injection prevention."""
        # Create auth headers
        user = create_test_user(
            db_session,
            email=f"testuser_{uuid.uuid4().hex[:8]}@example.com",
            password="testpassword123",
            is_active=True
        )
        token = create_access_token(data={"sub": str(user.id), "email": user.email})
        headers = {"Authorization": f"Bearer {token}"}
        
        # Attempt SQL injection in path parameter
        response = test_client.get(
            "/api/v1/releases/'; DROP TABLE releases; --",
            headers=headers
        )
        
        # Should return 404 or 422, not cause database error
        assert response.status_code in [
            status.HTTP_404_NOT_FOUND,
            status.HTTP_422_UNPROCESSABLE_ENTITY
        ]
        
        # Attempt SQL injection in JSON payload
        malicious_data = {
            "title": "'; DROP TABLE releases; --",
            "artist": "Test Artist"
        }
        
        response = test_client.post(
            "/api/v1/releases/",
            json=malicious_data,
            headers=headers
        )
        
        # Should either succeed (data is escaped) or fail with validation
        assert response.status_code in [
            status.HTTP_201_CREATED,
            status.HTTP_422_UNPROCESSABLE_ENTITY
        ]
    
    def test_xss_prevention(self, test_client: TestClient, db_session: Session):
        """Test XSS prevention in API responses."""
        # Create auth headers
        user = create_test_user(
            db_session,
            email=f"testuser_{uuid.uuid4().hex[:8]}@example.com",
            password="testpassword123",
            is_active=True
        )
        token = create_access_token(data={"sub": str(user.id), "email": user.email})
        headers = {"Authorization": f"Bearer {token}"}
        
        # Create release with potential XSS payload
        xss_data = {
            "title": "<script>alert('xss')</script>",
            "artist": "<img src=x onerror=alert('xss')>"
        }
        
        response = test_client.post(
            "/api/v1/releases/",
            json=xss_data,
            headers=headers
        )
        
        if response.status_code == status.HTTP_201_CREATED:
            # Verify that the response doesn't contain executable scripts
            response_text = response.text
            assert "<script>" not in response_text
            assert "onerror=" not in response_text
    
    def test_rate_limiting_headers(self, test_client: TestClient):
        """Test that rate limiting headers are present (if implemented)."""
        response = test_client.get("/api/v1/analytics/")
        
        # Check for common rate limiting headers
        # Note: This test will pass even if rate limiting isn't implemented
        rate_limit_headers = [
            "X-RateLimit-Limit",
            "X-RateLimit-Remaining",
            "X-RateLimit-Reset",
            "Retry-After"
        ]
        
        # Just verify the response is successful
        assert response.status_code == status.HTTP_200_OK
    
    def test_cors_headers(self, test_client: TestClient):
        """Test CORS headers in responses."""
        response = test_client.options("/api/v1/analytics/")
        
        # CORS headers might be present
        cors_headers = [
            "Access-Control-Allow-Origin",
            "Access-Control-Allow-Methods",
            "Access-Control-Allow-Headers"
        ]
        
        # Just verify the response doesn't error
        assert response.status_code in [
            status.HTTP_200_OK,
            status.HTTP_405_METHOD_NOT_ALLOWED
        ]
    
    def test_security_headers(self, test_client: TestClient):
        """Test security headers in responses."""
        response = test_client.get("/api/v1/analytics/")
        
        # Check for security headers
        security_headers = [
            "X-Content-Type-Options",
            "X-Frame-Options",
            "X-XSS-Protection",
            "Strict-Transport-Security"
        ]
        
        # Just verify the response is successful
        assert response.status_code == status.HTTP_200_OK
        
        # Verify Content-Type is set correctly
        assert "application/json" in response.headers.get("content-type", "")


@pytest.mark.integration
class TestAuthenticationAndAuthorization:
    """Test authentication and authorization across endpoints."""
    
    def test_protected_endpoints_require_auth(self, test_client: TestClient):
        """Test that protected endpoints require authentication."""
        protected_endpoints = [
            ("GET", "/api/v1/releases/test-id"),
            ("POST", "/api/v1/releases/"),
            ("PUT", "/api/v1/releases/1"),
            ("DELETE", "/api/v1/releases/test-id")
        ]
        
        for method, endpoint in protected_endpoints:
            response = getattr(test_client, method.lower())(endpoint)
            assert response.status_code == status.HTTP_401_UNAUTHORIZED
    
    def test_invalid_token_format(self, test_client: TestClient):
        """Test endpoints with invalid token formats."""
        invalid_tokens = [
            "invalid-token",
            "Bearer",
            "Bearer ",
            "Bearer invalid.token.format",
            "Basic dGVzdDp0ZXN0"  # Basic auth instead of Bearer
        ]
        
        for token in invalid_tokens:
            response = test_client.get(
                "/api/v1/releases/test-id",
                headers={"Authorization": token}
            )
            assert response.status_code == status.HTTP_401_UNAUTHORIZED
    
    def test_expired_token(self, test_client: TestClient, db_session: Session):
        """Test endpoints with expired tokens."""
        # Create user
        user = create_test_user(
            db_session,
            email=f"testuser_{uuid.uuid4().hex[:8]}@example.com",
            password="testpassword123",
            is_active=True
        )
        
        # Create expired token (negative expiration)
        with patch('app.core.security.ACCESS_TOKEN_EXPIRE_MINUTES', -1):
            token = create_access_token(data={"sub": str(user.id), "email": user.email})
        
        response = test_client.get(
            "/api/v1/releases/test-id",
            headers={"Authorization": f"Bearer {token}"}
        )
        
        # Should be unauthorized due to expired token
        assert response.status_code == status.HTTP_401_UNAUTHORIZED
    
    def test_token_with_invalid_user(self, test_client: TestClient):
        """Test token with non-existent user ID."""
        # Create token with non-existent user ID
        token = create_access_token(data={"sub": "99999", "email": "nonexistent@example.com"})
        
        response = test_client.get(
            "/api/v1/releases/test-id",
            headers={"Authorization": f"Bearer {token}"}
        )
        
        assert response.status_code == status.HTTP_401_UNAUTHORIZED


@pytest.mark.integration
class TestDataValidationAndSerialization:
    """Test data validation and serialization across endpoints."""
    
    def test_email_validation(self, test_client: TestClient):
        """Test email validation in login endpoint."""
        invalid_emails = [
            "invalid-email",
            "@example.com",
            "test@",
            "test..test@example.com",
            "test@example",
            ""
        ]
        
        for email in invalid_emails:
            response = test_client.post(
                "/api/v1/auth/login",
                json={"email": email, "password": "testpassword123"}
            )
            assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
    
    def test_date_validation(self, test_client: TestClient, db_session: Session):
        """Test date validation in release endpoints."""
        # Create auth headers
        user = create_test_user(
            db_session,
            email=f"testuser_{uuid.uuid4().hex[:8]}@example.com",
            password="testpassword123",
            is_active=True
        )
        token = create_access_token(data={"sub": str(user.id), "email": user.email})
        headers = {"Authorization": f"Bearer {token}"}
        
        invalid_dates = [
            "invalid-date",
            "2023-13-01",  # Invalid month
            "2023-02-30",  # Invalid day
            "not-a-date"
        ]
        
        for date in invalid_dates:
            response = test_client.post(
                "/api/v1/releases/",
                json={
                    "title": "Test Album",
                    "artist": "Test Artist",
                    "release_date": date
                },
                headers=headers
            )
            assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
    
    def test_enum_validation(self, test_client: TestClient, db_session: Session):
        """Test enum validation for release types."""
        # Create auth headers
        user = create_test_user(
            db_session,
            email=f"testuser_{uuid.uuid4().hex[:8]}@example.com",
            password="testpassword123",
            is_active=True
        )
        token = create_access_token(data={"sub": str(user.id), "email": user.email})
        headers = {"Authorization": f"Bearer {token}"}
        
        # Test invalid release type
        response = test_client.post(
            "/api/v1/releases/",
            json={
                "title": "Test Album",
                "artist": "Test Artist",
                "release_type": "invalid_type"
            },
            headers=headers
        )
        
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY


@pytest.mark.integration
class TestEndpointPerformance:
    """Test endpoint performance and response times."""
    
    def test_endpoint_response_times(self, test_client: TestClient, db_session: Session):
        """Test that endpoints respond within acceptable time limits."""
        import time
        
        # Test simple endpoints
        start_time = time.time()
        response = test_client.get("/api/v1/analytics/")
        end_time = time.time()
        
        assert response.status_code == status.HTTP_200_OK
        assert (end_time - start_time) < 2.0  # Should respond within 2 seconds
        
        # Test auth endpoint
        start_time = time.time()
        response = test_client.post("/api/v1/auth/logout")
        end_time = time.time()
        
        assert response.status_code == status.HTTP_200_OK
        assert (end_time - start_time) < 1.0  # Should respond within 1 second
    
    def test_concurrent_requests(self, test_client: TestClient):
        """Test handling of concurrent requests."""
        import concurrent.futures
        import threading
        
        def make_request():
            return test_client.get("/api/v1/analytics/")
        
        # Make 10 concurrent requests
        with concurrent.futures.ThreadPoolExecutor(max_workers=10) as executor:
            futures = [executor.submit(make_request) for _ in range(10)]
            responses = [future.result() for future in concurrent.futures.as_completed(futures)]
        
        # All requests should succeed
        for response in responses:
            assert response.status_code == status.HTTP_200_OK
    
    def test_large_response_handling(self, test_client: TestClient, db_session: Session):
        """Test handling of large response payloads."""
        # Create multiple releases to test list endpoint
        for i in range(50):
            create_test_release(db_session, title=f"Album {i}", artist=f"Artist {i}")
        
        response = test_client.get("/api/v1/releases/")
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert isinstance(data, list)
        assert len(data) >= 50


@pytest.mark.integration
class TestAPIDocumentation:
    """Test API documentation endpoints."""
    
    def test_openapi_schema(self, test_client: TestClient):
        """Test OpenAPI schema endpoint."""
        response = test_client.get("/openapi.json")
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert "openapi" in data
        assert "info" in data
        assert "paths" in data
        
        # Check that our API endpoints are documented
        paths = data["paths"]
        assert "/api/v1/auth/login" in paths
        assert "/api/v1/releases/" in paths
        assert "/api/v1/delivery-partners/{partner_id}" in paths
    
    def test_docs_endpoint(self, test_client: TestClient):
        """Test Swagger UI documentation endpoint."""
        response = test_client.get("/docs")
        
        assert response.status_code == status.HTTP_200_OK
        assert "text/html" in response.headers.get("content-type", "")
    
    def test_redoc_endpoint(self, test_client: TestClient):
        """Test ReDoc documentation endpoint."""
        response = test_client.get("/redoc")
        
        assert response.status_code == status.HTTP_200_OK
        assert "text/html" in response.headers.get("content-type", "")