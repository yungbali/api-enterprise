"""
Test the factory implementations to ensure they work correctly.
"""
import os
import pytest
from sqlalchemy.orm import Session

from tests.factories import (
    UserFactory, AdminUserFactory, APIKeyFactory,
    ReleaseFactory, TrackFactory, ReleaseAssetFactory,
    DeliveryPartnerFactory, PartnerConfigFactory,
    create_user_with_api_keys,
    create_single_release_with_track,
    create_partner_with_configs
)
from tests.utils import TestDataHelper, reset_all_mocks
from app.models.user import User, APIKey, UserRole
from app.models.release import Release, Track, ReleaseAsset
from app.models.partner import DeliveryPartner, PartnerConfig


@pytest.mark.unit
class TestUserFactories:
    """Test user-related factories."""
    
    def test_user_factory_creates_valid_user(self, db_session_commit: Session):
        """Test that UserFactory creates a valid user."""
        user = UserFactory()
        db_session_commit.add(user)
        db_session_commit.commit()
        
        assert user.id is not None
        assert user.email is not None
        assert "@" in user.email
        assert user.role == UserRole.VIEWER
        assert user.is_active is True
        assert user.is_superuser is False
    
    def test_admin_user_factory(self, db_session_commit: Session):
        """Test that AdminUserFactory creates an admin user."""
        admin = AdminUserFactory()
        db_session_commit.add(admin)
        db_session_commit.commit()
        
        assert admin.role == UserRole.ADMIN
        assert admin.is_superuser is True
        assert "admin" in admin.email
    
    def test_api_key_factory(self, db_session_commit: Session):
        """Test that APIKeyFactory creates a valid API key."""
        user = UserFactory()
        db_session_commit.add(user)
        db_session_commit.flush()
        
        api_key = APIKeyFactory(user_id=user.id)
        db_session_commit.add(api_key)
        db_session_commit.commit()
        
        assert api_key.id is not None
        assert api_key.user_id == user.id
        assert api_key.name is not None
        assert api_key.key_hash is not None
        assert api_key.prefix is not None
        assert api_key.is_active is True
    
    def test_create_user_with_api_keys(self, db_session_commit: Session):
        """Test utility function for creating user with API keys."""
        user, api_keys = create_user_with_api_keys(db_session_commit, num_keys=3)
        
        assert user.id is not None
        assert len(api_keys) == 3
        for api_key in api_keys:
            assert api_key.user_id == user.id


@pytest.mark.unit
class TestReleaseFactories:
    """Test release-related factories."""
    
    def test_release_factory_creates_valid_release(self, db_session_commit: Session):
        """Test that ReleaseFactory creates a valid release."""
        release = ReleaseFactory()
        db_session_commit.add(release)
        db_session_commit.commit()
        
        assert release.id is not None
        assert release.release_id is not None
        assert release.title is not None
        assert release.artist is not None
        assert release.status is not None
    
    def test_track_factory(self, db_session_commit: Session):
        """Test that TrackFactory creates a valid track."""
        release = ReleaseFactory()
        db_session_commit.add(release)
        db_session_commit.flush()
        
        track = TrackFactory(release_id=release.id)
        db_session_commit.add(track)
        db_session_commit.commit()
        
        assert track.id is not None
        assert track.release_id == release.id
        assert track.title is not None
        assert track.track_number is not None
        assert track.isrc is not None
    
    def test_release_asset_factory(self, db_session_commit: Session):
        """Test that ReleaseAssetFactory creates a valid asset."""
        release = ReleaseFactory()
        db_session_commit.add(release)
        db_session_commit.flush()
        
        asset = ReleaseAssetFactory(release_id=release.id)
        db_session_commit.add(asset)
        db_session_commit.commit()
        
        assert asset.id is not None
        assert asset.release_id == release.id
        assert asset.asset_type is not None
        assert asset.file_name is not None
        assert asset.file_url is not None
    
    def test_create_single_release_with_track(self, db_session_commit: Session):
        """Test utility function for creating release with track."""
        release, track = create_single_release_with_track(db_session_commit)
        
        assert release.id is not None
        assert track.id is not None
        assert track.release_id == release.id
        assert track.track_number == 1


@pytest.mark.unit
class TestPartnerFactories:
    """Test partner-related factories."""
    
    def test_delivery_partner_factory(self, db_session_commit: Session):
        """Test that DeliveryPartnerFactory creates a valid partner."""
        partner = DeliveryPartnerFactory()
        db_session_commit.add(partner)
        db_session_commit.commit()
        
        assert partner.id is not None
        assert partner.partner_id is not None
        assert partner.name is not None
        assert partner.api_base_url is not None
        assert partner.delivery_url is not None
        assert partner.status is not None
    
    def test_partner_config_factory(self, db_session_commit: Session):
        """Test that PartnerConfigFactory creates a valid config."""
        partner = DeliveryPartnerFactory()
        db_session_commit.add(partner)
        db_session_commit.flush()
        
        config = PartnerConfigFactory(partner_id=partner.id)
        db_session_commit.add(config)
        db_session_commit.commit()
        
        assert config.id is not None
        assert config.partner_id == partner.id
        assert config.config_key is not None
        assert config.config_value is not None
    
    def test_create_partner_with_configs(self, db_session_commit: Session):
        """Test utility function for creating partner with configs."""
        partner, configs = create_partner_with_configs(db_session_commit, num_configs=3)
        
        assert partner.id is not None
        assert len(configs) >= 1  # At least auth config
        for config in configs:
            assert config.partner_id == partner.id


@pytest.mark.unit
class TestTestDataHelper:
    """Test the TestDataHelper utility class."""
    
    def test_generate_isrc(self):
        """Test ISRC generation."""
        isrc = TestDataHelper.generate_isrc()
        assert len(isrc) == 12
        assert isrc[:2].isalpha()  # Country code
        assert isrc[2:5].isalpha()  # Registrant code
        assert isrc[5:7].isdigit()  # Year
        assert isrc[7:].isdigit()   # Designation
    
    def test_generate_upc(self):
        """Test UPC generation."""
        upc = TestDataHelper.generate_upc()
        assert len(upc) == 13
        assert upc.isdigit()
    
    def test_generate_grid(self):
        """Test GRid generation."""
        grid = TestDataHelper.generate_grid()
        assert grid.startswith("A1-")
        assert len(grid) == 13
    
    def test_generate_release_metadata(self):
        """Test release metadata generation."""
        metadata = TestDataHelper.generate_release_metadata()
        
        required_fields = [
            "title", "artist", "label", "genre", "release_date",
            "copyright_text", "description", "language", "territory"
        ]
        
        for field in required_fields:
            assert field in metadata
            assert metadata[field] is not None
    
    def test_generate_track_metadata(self):
        """Test track metadata generation."""
        metadata = TestDataHelper.generate_track_metadata(track_number=5)
        
        required_fields = [
            "title", "artist", "track_number", "duration_ms",
            "isrc", "explicit", "genre"
        ]
        
        for field in required_fields:
            assert field in metadata
            assert metadata[field] is not None
        
        assert metadata["track_number"] == 5
    
    def test_create_temp_audio_file(self):
        """Test temporary audio file creation."""
        file_path = TestDataHelper.create_temp_audio_file(format="mp3", size_mb=1)
        
        assert file_path.endswith(".mp3")
        assert os.path.exists(file_path)
        
        # Cleanup
        TestDataHelper.cleanup_temp_file(file_path)
        assert not os.path.exists(file_path)


@pytest.mark.unit
class TestMockServices:
    """Test the mock service framework."""
    
    def test_mock_service_manager(self):
        """Test mock service manager functionality."""
        from tests.utils import mock_service_manager, musicbrainz_mock
        
        # Test service registration
        assert mock_service_manager.get_mock('musicbrainz') is not None
        
        # Test reset functionality
        mock_service_manager.reset_all_mocks()
        assert musicbrainz_mock.call_count == 0
    
    def test_musicbrainz_mock_service(self):
        """Test MusicBrainz mock service."""
        from tests.utils import musicbrainz_mock
        
        # Setup mock response
        test_recording = {
            "id": "test-id",
            "title": "Test Song",
            "artist-credit": [{"artist": {"name": "Test Artist"}}],
            "length": 180000
        }
        musicbrainz_mock.setup_recording_response("test query", [test_recording])
        
        # Test response
        response = musicbrainz_mock.get_recording_response("test query")
        assert response["recordings"][0]["id"] == "test-id"
        assert response["recordings"][0]["title"] == "Test Song"
        
        # Test call tracking
        assert musicbrainz_mock.call_count == 1
        assert musicbrainz_mock.last_request == "recording:test query"
    
    def test_partner_api_mock_service(self):
        """Test partner API mock service."""
        from tests.utils import partner_api_mock
        
        # Setup successful response
        response = partner_api_mock.setup_partner_response("test-partner", success=True)
        assert response["status"] == "success"
        assert "delivery_id" in response
        
        # Setup failed response
        failed_response = partner_api_mock.setup_partner_response(
            "test-partner-2", success=False, error_code="VALIDATION_FAILED"
        )
        assert failed_response["status"] == "error"
        assert failed_response["error_code"] == "VALIDATION_FAILED"
    
    def test_reset_all_mocks(self):
        """Test global mock reset functionality."""
        from tests.utils import reset_all_mocks, musicbrainz_mock, partner_api_mock
        
        # Make some calls to generate state
        musicbrainz_mock.get_recording_response("test")
        partner_api_mock.setup_partner_response("test", success=True)
        
        # Reset all mocks
        reset_all_mocks()
        
        # Verify reset
        assert musicbrainz_mock.call_count == 0
        assert len(partner_api_mock.partner_responses) == 0


if __name__ == "__main__":
    pytest.main([__file__])